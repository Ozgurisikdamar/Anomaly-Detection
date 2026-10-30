"""Zones CLI.

    python -m storeguard_zones.cli zones-demo --config configs/zones.example.yaml --out runs

Draws the configured zones onto a synthetic frame and saves a PNG.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from storeguard_zones.geometry import load_zones


def cmd_zones_demo(args: argparse.Namespace) -> int:
    import cv2
    import numpy as np

    from storeguard_zones.overlay import draw_zones

    zones = load_zones(args.config)
    if args.camera:
        zones = [z for z in zones if z.camera_id == args.camera]

    # Synthetic "shelf" backdrop (gradient) so the overlay is legible.
    h, w = args.height, args.width
    grad = np.linspace(40, 110, h, dtype=np.uint8)
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:, :, 0] = grad[:, None]
    frame[:, :, 1] = (grad[:, None] * 0.4).astype(np.uint8)

    img = draw_zones(frame, zones)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dst = out / f"zones_{args.camera or 'all'}.png"
    cv2.imwrite(str(dst), img)
    print(f"[zones-demo] {len(zones)} zone(s) -> {dst}")
    for z in zones:
        print(f"  {z.zone_id} [{z.zone_type.value}] {len(z.polygon)} points")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="storeguard-zones")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("zones-demo", help="render configured zones onto a frame")
    d.add_argument("--config", default="configs/zones.example.yaml")
    d.add_argument("--camera", default=None, help="filter to one camera_id")
    d.add_argument("--width", type=int, default=960)
    d.add_argument("--height", type=int, default=540)
    d.add_argument("--out", default="runs")
    d.set_defaults(func=cmd_zones_demo)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
