"""Vision workbench CLI.

    python -m storeguard_vision.cli benchmark --clip <path> --frames 60 --out runs
    python -m storeguard_vision.cli annotate  --model yolo26n --clip <img|dir> --out runs
    python -m storeguard_vision.cli track     --model yolo26n --image <img> --out runs

Requires the optional `ml` extra (ultralytics/opencv/psutil). No model runs at
import time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from storeguard_vision.benchmark import (
    BenchmarkConfig,
    BenchmarkResult,
    ModelCandidate,
    Tracker,
)


def _save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def cmd_benchmark(args: argparse.Namespace) -> int:
    from storeguard_vision.benchmark import run_benchmark

    models = [ModelCandidate(m) for m in args.models]
    out = Path(args.out)
    results: list[BenchmarkResult] = []
    for m in models:
        cfg = BenchmarkConfig(
            model=m,
            tracker=Tracker.BYTETRACK,
            input_size=args.imgsz,
            clip_path=args.clip,
            frames=args.frames,
            device=args.device,
        )
        print(
            f"[benchmark] {m.value} imgsz={args.imgsz} frames={args.frames} ...",
            flush=True,
        )
        res = run_benchmark(cfg)
        results.append(res)
        print(
            f"  -> p50={res.latency_p50_ms}ms p95={res.latency_p95_ms}ms "
            f"fps={res.fps} cpu={res.cpu_percent}% rss={res.ram_mb}MB dets={res.total_detections}",
            flush=True,
        )

    _save_json(out / "benchmark.json", [r.to_dict() for r in results])
    _write_markdown(out / "benchmark.md", results)
    print(f"[benchmark] wrote {out/'benchmark.json'} and {out/'benchmark.md'}")
    return 0


def _write_markdown(path: Path, results: list[BenchmarkResult]) -> None:
    lines = [
        "| Model | imgsz | frames | p50 ms | p95 ms | mean ms | FPS | CPU % | RSS MB | dets |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.model.value} | {r.input_size} | {r.frames} | {r.latency_p50_ms} | "
            f"{r.latency_p95_ms} | {r.latency_mean_ms} | {r.fps} | {r.cpu_percent} | "
            f"{r.ram_mb} | {r.total_detections} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def cmd_annotate(args: argparse.Namespace) -> int:
    import cv2

    from storeguard_vision.annotate import annotate
    from storeguard_vision.capture.file_source import FileFrameSource
    from storeguard_vision.detect.detector import YoloDetector

    weights = f"{args.model}.pt"
    detector = YoloDetector(weights=weights, imgsz=args.imgsz, device=args.device)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    saved = 0
    for frame in FileFrameSource(args.clip, max_frames=args.max):
        dets = detector.infer(frame.image)
        img = annotate(frame.image, dets)
        dst = out / f"annotated_{args.model}_{frame.index:03d}.png"
        cv2.imwrite(str(dst), img)
        saved += 1
        print(f"  {dst.name}: {len(dets)} detections")
    print(f"[annotate] saved {saved} frame(s) to {out}")
    return 0


def _build_moving_sequence(image_path: str, frames: int, canvas_w: int, canvas_h: int):
    """Place a sample image on a canvas and slide it to create motion for tracking."""
    import cv2
    import numpy as np

    sample = cv2.imread(image_path)
    if sample is None:
        raise FileNotFoundError(image_path)
    # Scale sample to fit within half the canvas width.
    scale = min((canvas_w * 0.5) / sample.shape[1], (canvas_h * 0.9) / sample.shape[0])
    sample = cv2.resize(
        sample, (int(sample.shape[1] * scale), int(sample.shape[0] * scale))
    )
    sh, sw = sample.shape[:2]
    seq = []
    for i in range(frames):
        canvas = np.full((canvas_h, canvas_w, 3), 60, dtype=np.uint8)
        x = int((canvas_w - sw) * (i / max(1, frames - 1)))
        y = (canvas_h - sh) // 2
        canvas[y : y + sh, x : x + sw] = sample
        seq.append(canvas)
    return seq


def cmd_track(args: argparse.Namespace) -> int:
    import cv2

    from storeguard_vision.annotate import annotate
    from storeguard_vision.detect.detector import YoloDetector

    detector = YoloDetector(
        weights=f"{args.model}.pt", imgsz=args.imgsz, device=args.device
    )
    seq = _build_moving_sequence(args.image, args.frames, args.canvas_w, args.canvas_h)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ids_seen: set[int] = set()
    for i, img in enumerate(seq):
        dets = detector.track(img)
        for d in dets:
            if d.track_id is not None:
                ids_seen.add(d.track_id)
        if i % max(1, args.save_every) == 0:
            dst = out / f"track_{args.model}_{i:03d}.png"
            cv2.imwrite(str(dst), annotate(img, dets))
    print(f"[track] {len(seq)} frames; distinct track ids seen: {sorted(ids_seen)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-vision")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("benchmark", help="measure latency/FPS/resources on CPU")
    b.add_argument("--models", nargs="+", default=["yolo26n", "yolo11n"])
    b.add_argument("--clip", default=None, help="video/image/dir; omitted = synthetic")
    b.add_argument("--frames", type=int, default=60)
    b.add_argument("--imgsz", type=int, default=640)
    b.add_argument("--device", default="cpu")
    b.add_argument("--out", default="runs")
    b.set_defaults(func=cmd_benchmark)

    a = sub.add_parser("annotate", help="save annotated detections for a source")
    a.add_argument("--model", default="yolo26n")
    a.add_argument("--clip", required=True)
    a.add_argument("--imgsz", type=int, default=640)
    a.add_argument("--device", default="cpu")
    a.add_argument("--max", type=int, default=4)
    a.add_argument("--out", default="runs")
    a.set_defaults(func=cmd_annotate)

    t = sub.add_parser("track", help="tracking demo with persistent IDs")
    t.add_argument("--model", default="yolo26n")
    t.add_argument("--image", required=True, help="sample image slid across a canvas")
    t.add_argument("--frames", type=int, default=24)
    t.add_argument("--canvas-w", type=int, default=960)
    t.add_argument("--canvas-h", type=int, default=540)
    t.add_argument("--imgsz", type=int, default=640)
    t.add_argument("--device", default="cpu")
    t.add_argument("--save-every", type=int, default=6)
    t.add_argument("--out", default="runs")
    t.set_defaults(func=cmd_track)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
