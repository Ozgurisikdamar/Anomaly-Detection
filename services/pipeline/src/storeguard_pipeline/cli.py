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
# Self-checkout zones (match configs/zones.example.yaml).
BAG_POLY = [(0.50, 0.30), (0.85, 0.30), (0.85, 0.75), (0.50, 0.75)]
SCAN_POLY = [(0.15, 0.30), (0.45, 0.30), (0.45, 0.65), (0.15, 0.65)]


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
        print(f"    {e.event_type.value:30} sev={e.severity.value:11} reasons={e.reason_codes}")

    if args.api_base:
        for e in result.events:
            try:
                code = _post_event(args.api_base, e.model_dump_json())
                print(f"[pipeline] POST {e.event_id} -> {code}")
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"[pipeline] POST {e.event_id} failed: {exc}")
    return 0


def _build_feed(feed_mode: str, terminal_id: str, session_id: str):  # noqa: ANN202
    """Build a SIMULATED POS feed for a demo mode.

    healthy  -> feed up and on time, but the bagged item was never scanned.
    missing  -> feed down for the whole session (UNKNOWN: unavailable).
    delayed  -> feed up but delivery lagging across the item window (UNKNOWN: delayed).
    """
    from storeguard_integrations.pos_feed import SimulatedPosFeed

    if feed_mode == "missing":
        return SimulatedPosFeed(terminal_id, session_id, available=False)
    if feed_mode == "delayed":
        # Lag covers the item's bagging window so the scan can't correlate in time.
        return SimulatedPosFeed(terminal_id, session_id, degraded_window=(0.3, 5.0)).add_scan(
            "SKU-DEMO", occurred_at_s=0.8, delivery_delay_s=10.0
        )
    # healthy: no scan for the placed item -> headline non-scan review event.
    return SimulatedPosFeed(terminal_id, session_id)


def cmd_checkout_pipeline_demo(args: argparse.Namespace) -> int:
    from storeguard_pipeline.checkout_coordinator import (
        CheckoutCameraConfig,
        CheckoutPipelineCoordinator,
    )
    from storeguard_pipeline.demo_clip import make_checkout_demo_clip

    out = Path(args.out)
    clip_dir = make_checkout_demo_clip(out / "checkout_clip", frames=args.frames)
    print(f"[checkout] FILE DEMO clip: {clip_dir} ({args.frames} frames)")

    feed = _build_feed(args.feed, args.terminal_id, args.session_id)
    print(f"[checkout] SIMULATED POS feed mode: {args.feed}")

    cfg = CheckoutCameraConfig(
        camera_id=args.camera_id,
        store_id=args.store_id,
        terminal_id=args.terminal_id,
        session_id=args.session_id,
        source_dir=str(clip_dir),
        bagging_polygon=BAG_POLY,
        scan_polygon=SCAN_POLY,
        source_label="FILE DEMO",
        weights=args.weights,
    )
    result = CheckoutPipelineCoordinator().run(cfg, feed, out)

    print(f"[checkout] source={result.source_label} camera={result.camera_id}")
    print(f"[checkout] metrics: {json.dumps(result.metrics)}")
    non_scan = sum(1 for e in result.events if e.event_type.value == "ITEM_PLACED_NOT_SCANNED")
    print(
        f"[checkout] events produced: {len(result.events)} " f"(ITEM_PLACED_NOT_SCANNED={non_scan})"
    )
    for e in result.events:
        print(f"    {e.event_type.value:34} sev={e.severity.value:11} reasons={e.reason_codes}")

    if args.feed in ("missing", "delayed") and non_scan:
        print("[checkout] SAFETY VIOLATION: non-scan alert on an unhealthy feed!")
        return 1

    if args.api_base:
        for e in result.events:
            try:
                code = _post_event(args.api_base, e.model_dump_json())
                print(f"[checkout] POST {e.event_id} -> {code}")
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"[checkout] POST {e.event_id} failed: {exc}")
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

    c = sub.add_parser(
        "checkout-pipeline-demo",
        help="checkout file clip + SIMULATED POS feed -> correlation -> checkout FSM -> events",
    )
    c.add_argument("--out", default="runs/checkout")
    c.add_argument("--frames", type=int, default=24)
    c.add_argument(
        "--feed",
        choices=["healthy", "missing", "delayed"],
        default="healthy",
        help="SIMULATED POS feed health for the demo",
    )
    c.add_argument("--camera-id", default="cam_sco_01")
    c.add_argument("--store-id", default="store_demo_01")
    c.add_argument("--terminal-id", default="term_01")
    c.add_argument("--session-id", default="sess_demo_01")
    c.add_argument("--weights", default="yolo26n.pt")
    c.add_argument("--api-base", default=None, help="e.g. http://localhost:8000")
    c.set_defaults(func=cmd_checkout_pipeline_demo)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
