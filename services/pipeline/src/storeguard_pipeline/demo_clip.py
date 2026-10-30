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
