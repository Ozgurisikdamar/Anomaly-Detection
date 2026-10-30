"""Generate a deterministic FILE DEMO shelf clip (frames written as PNGs).

The scene composites:
- a shelf background with the display ROI drawn,
- a **colour product marker** inside the ROI, present for the first part of the
  clip and removed afterwards (read by the labelled DemoProductDetector — not an
  SKU detector),
- a **real person image** (ultralytics' bundled sample) sweeping across the
  frame, so the real COCO YOLO detector + ByteTrack actually fire on a person.

No video is committed; frames are generated at runtime (gitignored output).
"""

from __future__ import annotations

from pathlib import Path

# Shelf display ROI (normalized), matches configs/zones.example.yaml.
SHELF_ROI = (0.10, 0.20, 0.55, 0.70)  # x0, y0, x1, y1
# Self-checkout bagging/scale ROI (normalized), matches zone_sco_01_bag.
BAG_ROI = (0.50, 0.30, 0.85, 0.75)  # x0, y0, x1, y1


def _person_image():  # noqa: ANN202
    import cv2
    from ultralytics.utils import ASSETS

    img = cv2.imread(str(Path(ASSETS) / "zidane.jpg"))
    if img is None:  # pragma: no cover - asset always present with ultralytics
        raise FileNotFoundError("ultralytics sample image not found")
    return img


def make_demo_clip(
    out_dir: str | Path,
    frames: int = 24,
    width: int = 960,
    height: int = 540,
    remove_at: int = 12,
) -> Path:
    """Write ``frames`` PNGs to ``out_dir`` and return the directory path."""
    import cv2
    import numpy as np

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    person = _person_image()
    pscale = (height * 0.55) / person.shape[0]
    person = cv2.resize(
        person, (int(person.shape[1] * pscale), int(person.shape[0] * pscale))
    )
    ph, pw = person.shape[:2]

    x0, y0 = int(SHELF_ROI[0] * width), int(SHELF_ROI[1] * height)
    x1, y1 = int(SHELF_ROI[2] * width), int(SHELF_ROI[3] * height)

    for i in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = np.linspace(55, 110, height, dtype=np.uint8)[:, None]  # bg
        cv2.rectangle(frame, (x0, y0), (x1, y1), (255, 170, 79), 2)  # shelf ROI

        # Product marker present until remove_at.
        if i < remove_at:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            cv2.rectangle(
                frame, (cx - 40, cy - 30), (cx + 40, cy + 30), (60, 200, 60), -1
            )

        # Person sweeps left -> right, passing the shelf around the removal.
        px = int((width - pw) * (i / max(1, frames - 1)))
        py = height - ph
        frame[py : py + ph, px : px + pw] = person

        cv2.putText(
            frame,
            "FILE DEMO (synthetic scene)",
            (8, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (245, 196, 81),
            2,
            cv2.LINE_AA,
        )
        cv2.imwrite(str(out / f"frame_{i:03d}.png"), frame)

    return out


def make_checkout_demo_clip(
    out_dir: str | Path,
    frames: int = 24,
    width: int = 960,
    height: int = 540,
    place_at: int = 8,
) -> Path:
    """Write a FILE DEMO self-checkout clip and return the directory path.

    Scene: a self-checkout with the bagging/scale ROI drawn; a colour product
    marker **appears in the bagging ROI** from ``place_at`` onwards (an item
    placed in the bagging area, read by the labelled DemoProductDetector — not an
    SKU detector); a real person image is present so the COCO YOLO detector +
    ByteTrack fire on a person. Whether that bagged item was scanned is NOT in
    the video — that comes only from the (simulated) POS feed.
    """
    import cv2
    import numpy as np

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    person = _person_image()
    pscale = (height * 0.6) / person.shape[0]
    person = cv2.resize(
        person, (int(person.shape[1] * pscale), int(person.shape[0] * pscale))
    )
    ph, pw = person.shape[:2]

    bx0, by0 = int(BAG_ROI[0] * width), int(BAG_ROI[1] * height)
    bx1, by1 = int(BAG_ROI[2] * width), int(BAG_ROI[3] * height)

    for i in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = np.linspace(55, 110, height, dtype=np.uint8)[:, None]  # bg
        cv2.rectangle(frame, (bx0, by0), (bx1, by1), (120, 220, 120), 2)  # bagging ROI

        # Item placed in the bagging area from place_at onwards (stays there).
        if i >= place_at:
            cx, cy = (bx0 + bx1) // 2, (by0 + by1) // 2
            cv2.rectangle(
                frame, (cx - 45, cy - 32), (cx + 45, cy + 32), (60, 200, 60), -1
            )

        # Person stands at the terminal (left side), slight sway for track motion.
        px = int(width * 0.05) + (i % 4)
        py = height - ph
        frame[py : py + ph, max(0, px) : max(0, px) + pw] = person

        cv2.putText(
            frame,
            "FILE DEMO self-checkout (synthetic scene)",
            (8, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (245, 196, 81),
            2,
            cv2.LINE_AA,
        )
        cv2.imwrite(str(out / f"frame_{i:03d}.png"), frame)

    return out
