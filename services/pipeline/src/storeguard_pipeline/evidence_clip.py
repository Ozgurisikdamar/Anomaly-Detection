"""Build a bounded, zone-masked animated-GIF evidence clip from real frames.

Privacy by design: everything outside the configured zone polygon is dimmed, so
the clip foregrounds the reviewed area rather than the whole scene. The clip is a
short pre/post window of the actual buffered frames (not a synthetic montage),
captioned FILE DEMO / human-review. It is written keyed by ``evidence_id`` so the
API evidence store (which keys by the same id) can serve it after upload.

Output is an animated GIF: it plays inline in a web ``<img>`` and a React Native
``<Image>`` with zero extra client dependencies.
"""

from __future__ import annotations

from pathlib import Path

from storeguard_contracts import EvidenceRef

Polygon = list[tuple[float, float]]

# Bounded clip: at most this many frames, ending at the event.
_MAX_FRAMES = 12
_FRAME_W = 480
_FRAME_H = 270
_DIM = 0.35  # brightness retained outside the zone


def _zone_mask(h: int, w: int, polygon: Polygon | None):  # noqa: ANN202
    import cv2
    import numpy as np

    if not polygon:
        return None
    pts = np.array([(int(x * w), int(y * h)) for x, y in polygon], dtype=np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask


def _compose(frame, mask, polygon: Polygon | None):  # noqa: ANN202
    import cv2
    import numpy as np

    img = cv2.resize(frame, (_FRAME_W, _FRAME_H))
    if mask is not None:
        dimmed = (img.astype(np.float32) * _DIM).astype(np.uint8)
        m3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) > 0
        out = np.where(m3, img, dimmed)
        if polygon:
            pts = np.array(
                [(int(x * _FRAME_W), int(y * _FRAME_H)) for x, y in polygon],
                dtype=np.int32,
            )
            cv2.polylines(out, [pts], True, (245, 196, 81), 1, cv2.LINE_AA)
    else:
        out = img
    cv2.putText(
        out,
        "FILE DEMO evidence - human review required",
        (8, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (245, 196, 81),
        1,
        cv2.LINE_AA,
    )
    return out


def save_evidence_gif(
    frames: list,
    out_dir: str | Path,
    evidence_id: str,
    zone_polygon: Polygon | None = None,
) -> EvidenceRef:
    """Write a zone-masked animated GIF for ``evidence_id``; return its EvidenceRef."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not frames:
        return EvidenceRef(evidence_id=evidence_id, kind="clip", available=False)

    import cv2
    from PIL import Image

    window = frames[-_MAX_FRAMES:]
    h, w = window[0].shape[:2]
    mask = _zone_mask(_FRAME_H, _FRAME_W, zone_polygon)
    pil_frames = [
        Image.fromarray(
            cv2.cvtColor(_compose(f, mask, zone_polygon), cv2.COLOR_BGR2RGB)
        )
        for f in window
    ]
    dst = out / f"{evidence_id}.gif"
    pil_frames[0].save(
        dst,
        save_all=True,
        append_images=pil_frames[1:],
        duration=180,
        loop=0,
        optimize=True,
    )
    return EvidenceRef(evidence_id=evidence_id, kind="clip", available=True)
