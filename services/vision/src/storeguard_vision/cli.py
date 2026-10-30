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
    Backend,
    BenchmarkConfig,
    BenchmarkResult,
    ModelCandidate,
    Tracker,
)


def _save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def cmd_benchmark(args: argparse.Namespace) -> int:
    from storeguard_vision.benchmark import benchmark_env, run_benchmark

    models = [ModelCandidate(m) for m in args.models]
    backends = [Backend(b) for b in args.backends]
    out = Path(args.out)
    results: list[BenchmarkResult] = []
    for m in models:
        for backend in backends:
            cfg = BenchmarkConfig(
                model=m,
                backend=backend,
                tracker=Tracker.BYTETRACK,
                input_size=args.imgsz,
                clip_path=args.clip,
                frames=args.frames,
                trials=args.trials,
                device=args.device,
                export_dir=str(out / "exports"),
            )
            print(
                f"[benchmark] {m.value}/{backend.value} imgsz={args.imgsz} "
                f"frames={args.frames} trials={args.trials} ...",
                flush=True,
            )
            res = run_benchmark(cfg)
            results.append(res)
            print(
                f"  -> p50={res.latency_p50_ms}ms p95={res.latency_p95_ms}ms "
                f"fps={res.fps} cpu={res.cpu_percent}% rss={res.ram_mb}MB",
                flush=True,
            )

    _save_json(
        out / "benchmark.json",
        {"env": benchmark_env(), "results": [r.to_dict() for r in results]},
    )
    _write_markdown(out / "benchmark.md", results, benchmark_env())
    print(f"[benchmark] wrote {out/'benchmark.json'} and {out/'benchmark.md'}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    from storeguard_vision.benchmark import _WEIGHTS
    from storeguard_vision.export import export_model

    out = Path(args.out) / "exports"
    for m in (ModelCandidate(x) for x in args.models):
        for backend in (Backend(b) for b in args.backends):
            print(f"[export] {m.value} -> {backend.value} ...", flush=True)
            path = export_model(_WEIGHTS[m], backend, args.imgsz, str(out))
            print(f"  -> {path}", flush=True)
    return 0


def cmd_streams(args: argparse.Namespace) -> int:
    from storeguard_vision.benchmark import benchmark_env, run_streams

    out = Path(args.out)
    rows = []
    for n in args.streams:
        print(f"[streams] {args.model} n={n} frames={args.frames} ...", flush=True)
        r = run_streams(
            ModelCandidate(args.model),
            n_streams=n,
            frames=args.frames,
            input_size=args.imgsz,
            device=args.device,
            clip_path=args.clip,
        )
        rows.append(r)
        print(
            f"  -> p50={r['latency_p50_ms']}ms p95={r['latency_p95_ms']}ms "
            f"agg_fps={r['aggregate_fps']} cpu={r['cpu_percent']}% rss={r['ram_mb']}MB",
            flush=True,
        )
    _save_json(out / "streams.json", {"env": benchmark_env(), "results": rows})
    lines = [
        "| Model | streams | frames/stream | p50 ms | p95 ms | agg FPS | CPU % | RSS MB |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['model']} | {r['n_streams']} | {r['frames_per_stream']} | "
            f"{r['latency_p50_ms']} | {r['latency_p95_ms']} | {r['aggregate_fps']} | "
            f"{r['cpu_percent']} | {r['ram_mb']} |"
        )
    (out / "streams.md").write_text("\n".join(lines) + "\n")
    print(f"[streams] wrote {out/'streams.json'} and {out/'streams.md'}")
    return 0


def _write_markdown(
    path: Path, results: list[BenchmarkResult], env: dict | None = None
) -> None:
    lines = [
        "| Model | Backend | imgsz | frames | trials "
        "| p50 ms | p95 ms | mean ms | FPS | CPU % | RSS MB |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.model.value} | {r.backend.value} | {r.input_size} | {r.frames} | "
            f"{r.trials} | {r.latency_p50_ms} | {r.latency_p95_ms} | {r.latency_mean_ms} | "
            f"{r.fps} | {r.cpu_percent} | {r.ram_mb} |"
        )
    if env:
        parts = [
            f"{env.get('cpu_model') or env.get('processor')} x{env.get('cpu_count')}",
            f"torch {env.get('torch')} (threads={env.get('torch_num_threads')})",
            f"ultralytics {env.get('ultralytics')}",
            f"onnxruntime {env.get('onnxruntime')}",
            f"openvino {env.get('openvino')}",
            f"py {env.get('python')}",
        ]
        lines.append("")
        lines.append(
            "> Environment (this machine, NOT the owner's target hardware): "
            + " · ".join(parts)
        )
        lines.append("")
        lines.append(
            "> THROUGHPUT only — no labelled retail data, so no accuracy or "
            "model-selection claim."
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
    b.add_argument(
        "--backends",
        nargs="+",
        default=["pytorch"],
        help="pytorch onnx openvino (exports on demand)",
    )
    b.add_argument("--clip", default=None, help="video/image/dir; omitted = synthetic")
    b.add_argument("--frames", type=int, default=60)
    b.add_argument("--trials", type=int, default=1)
    b.add_argument("--imgsz", type=int, default=640)
    b.add_argument("--device", default="cpu")
    b.add_argument("--out", default="runs")
    b.set_defaults(func=cmd_benchmark)

    e = sub.add_parser("export", help="export models to onnx/openvino (cached)")
    e.add_argument("--models", nargs="+", default=["yolo26n", "yolo11n"])
    e.add_argument("--backends", nargs="+", default=["onnx", "openvino"])
    e.add_argument("--imgsz", type=int, default=640)
    e.add_argument("--out", default="runs")
    e.set_defaults(func=cmd_export)

    s = sub.add_parser("streams", help="multi-stream CPU/latency scaling")
    s.add_argument("--model", default="yolo26n")
    s.add_argument("--streams", nargs="+", type=int, default=[1, 2, 4])
    s.add_argument("--frames", type=int, default=30)
    s.add_argument("--clip", default=None)
    s.add_argument("--imgsz", type=int, default=640)
    s.add_argument("--device", default="cpu")
    s.add_argument("--out", default="runs")
    s.set_defaults(func=cmd_streams)

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
