"""Pipeline CLI.

    python -m storeguard_pipeline.cli pipeline-demo --out runs [--api-base URL]

Generates a FILE DEMO shelf clip, runs the real detector/tracker -> zones ->
shelf FSM pipeline, prints the produced events + measured metrics, and (if
--api-base is given) POSTs each event to the API ingest endpoint so it appears
in the web dashboard in real time.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

from storeguard_pipeline.coordinator import CameraConfig, PipelineCoordinator

SHELF_POLY = [(0.10, 0.20), (0.55, 0.20), (0.55, 0.70), (0.10, 0.70)]
PICKUP_POLY = [(0.55, 0.20), (0.90, 0.20), (0.90, 0.80), (0.55, 0.80)]


def _post_event(api_base: str, event_json: str) -> int:
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/api/v1/events",
        data=event_json.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 - local demo URL
        return int(resp.status)


def cmd_pipeline_demo(args: argparse.Namespace) -> int:
    from storeguard_pipeline.demo_clip import make_demo_clip

    out = Path(args.out)
    clip_dir = make_demo_clip(out / "demo_clip", frames=args.frames)
    print(f"[pipeline] FILE DEMO clip: {clip_dir} ({args.frames} frames)")

    cfg = CameraConfig(
        camera_id=args.camera_id,
        store_id=args.store_id,
        source_dir=str(clip_dir),
        shelf_zone_id="zone_shelf_01_display",
        shelf_polygon=SHELF_POLY,
        pickup_polygon=PICKUP_POLY,
        source_label="FILE DEMO",
        weights=args.weights,
    )
    result = PipelineCoordinator().run_camera(cfg, out)

    print(f"[pipeline] source={result.source_label} camera={result.camera_id}")
    print(f"[pipeline] metrics: {json.dumps(result.metrics)}")
    print(f"[pipeline] events produced: {len(result.events)}")
    for e in result.events:
        print(
            f"    {e.event_type.value:30} sev={e.severity.value:11} reasons={e.reason_codes}"
        )

    if args.api_base:
        for e in result.events:
            try:
                code = _post_event(args.api_base, e.model_dump_json())
                print(f"[pipeline] POST {e.event_id} -> {code}")
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"[pipeline] POST {e.event_id} failed: {exc}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser(
        "pipeline-demo", help="file clip -> detector -> zones -> shelf FSM -> events"
    )
    d.add_argument("--out", default="runs/pipeline")
    d.add_argument("--frames", type=int, default=24)
    d.add_argument("--camera-id", default="cam_shelf_01")
    d.add_argument("--store-id", default="store_demo_01")
    d.add_argument("--weights", default="yolo26n.pt")
    d.add_argument("--api-base", default=None, help="e.g. http://localhost:8000")
    d.set_defaults(func=cmd_pipeline_demo)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
