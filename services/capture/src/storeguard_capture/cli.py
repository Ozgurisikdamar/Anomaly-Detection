"""Capture CLI.

    python -m storeguard_capture.cli camera-demo

Runs a SupervisedCamera over a controllable in-process source, injects an
outage, and prints a health / frame-age / reconnect timeline — demonstrating
disconnect → OFFLINE → reconnect → ONLINE without any real camera.
"""

from __future__ import annotations

import argparse
import time

from storeguard_capture.supervisor import SupervisedCamera
from storeguard_capture.testing import CameraController

# RTSP URLs carry credentials; only pass via --url (server-side), never commit.


def cmd_camera_demo(args: argparse.Namespace) -> int:
    ctrl = CameraController(fps=args.fps)
    cam = SupervisedCamera(
        ctrl.factory,
        camera_id="cam_demo",
        degraded_age_ms=200.0,
        offline_age_ms=600.0,
        initial_backoff_s=0.1,
        max_backoff_s=1.0,
    )
    print(f"{'t(s)':>5}  {'state':<9} {'age_ms':>8} {'fps':>6} {'reconnects':>10}")

    def sample(t0: float) -> None:
        h = cam.health()
        age = f"{h.frame_age_ms:.0f}" if h.frame_age_ms is not None else "-"
        fps = f"{h.fps:.1f}" if h.fps is not None else "-"
        print(
            f"{time.monotonic() - t0:5.1f}  {h.state.value:<9} {age:>8} {fps:>6} "
            f"{h.reconnect_count:>10}"
        )

    with cam:
        t0 = time.monotonic()
        # Phase A: healthy
        for _ in range(8):
            time.sleep(0.15)
            sample(t0)
        print("--- inject outage ---")
        ctrl.set_down()
        for _ in range(10):
            time.sleep(0.15)
            sample(t0)
        print("--- recover ---")
        ctrl.set_up()
        for _ in range(8):
            time.sleep(0.15)
            sample(t0)
    return 0


def cmd_rtsp_check(args: argparse.Namespace) -> int:
    """Validate a real/synthetic RTSP stream through SupervisedCamera.

    Prints a health timeline (state, frame age, FPS, reconnects) and a summary of
    frames decoded. The URL comes from the operator (server-side secret) and is
    never printed. Reconnect/backoff fires automatically if the stream drops.
    """
    from storeguard_capture.rtsp import RtspFrameSource

    cam = SupervisedCamera(
        lambda: RtspFrameSource(args.url, open_timeout_s=args.open_timeout),
        camera_id=args.camera_id,
        degraded_age_ms=args.degraded_age_ms,
        offline_age_ms=args.offline_age_ms,
    )
    print(f"[rtsp-check] connecting to {args.camera_id} for {args.seconds}s ...")
    print(f"{'t(s)':>5}  {'state':<9} {'age_ms':>8} {'fps':>6} {'reconnects':>10}")
    decoded = 0
    last_index = -1
    with cam:
        t0 = time.monotonic()
        while time.monotonic() - t0 < args.seconds:
            time.sleep(args.interval)
            h = cam.health()
            frame = cam.latest()
            if frame is not None and getattr(frame, "index", last_index) != last_index:
                last_index = frame.index
                decoded += 1
            age = f"{h.frame_age_ms:.0f}" if h.frame_age_ms is not None else "-"
            fps = f"{h.fps:.1f}" if h.fps is not None else "-"
            print(
                f"{time.monotonic() - t0:5.1f}  {h.state.value:<9} {age:>8} {fps:>6} "
                f"{h.reconnect_count:>10}"
            )
    print(
        f"[rtsp-check] done: samples_with_new_frame={decoded} "
        f"reconnects={cam.reconnect_count}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-capture")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser(
        "camera-demo", help="supervised camera health/reconnect timeline"
    )
    d.add_argument("--fps", type=float, default=20.0)
    d.set_defaults(func=cmd_camera_demo)

    r = sub.add_parser(
        "rtsp-check", help="validate an RTSP stream via SupervisedCamera (real camera)"
    )
    r.add_argument("--url", required=True, help="rtsp://... (server-side secret)")
    r.add_argument("--camera-id", default="cam_rtsp")
    r.add_argument("--seconds", type=float, default=15.0)
    r.add_argument("--interval", type=float, default=0.5)
    r.add_argument("--open-timeout", type=float, default=10.0)
    r.add_argument("--degraded-age-ms", type=float, default=500.0)
    r.add_argument("--offline-age-ms", type=float, default=2000.0)
    r.set_defaults(func=cmd_rtsp_check)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
