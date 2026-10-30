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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-capture")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser(
        "camera-demo", help="supervised camera health/reconnect timeline"
    )
    d.add_argument("--fps", type=float, default=20.0)
    d.set_defaults(func=cmd_camera_demo)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
