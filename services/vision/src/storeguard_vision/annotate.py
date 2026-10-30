"""Draw detection/track overlays on a frame (OpenCV, optional `ml` extra)."""

from __future__ import annotations

from storeguard_vision.detect.detector import Detection

# Deterministic palette for track-id colouring (BGR).
_PALETTE = [
    (79, 140, 255),
    (74, 222, 128),
    (81, 196, 245),
    (129, 107, 255),
    (0, 200, 255),
    (180, 120, 0),
]


def annotate(image, detections: list[Detection]):
    """Return a copy of ``image`` with boxes, labels, scores and track ids drawn."""
    import cv2  # lazy (ml extra)

    out = image.copy()
    for det in detections:
        x1, y1, x2, y2 = (int(v) for v in det.xyxy)
        key = det.track_id if det.track_id is not None else det.cls_id
        colour = _PALETTE[key % len(_PALETTE)]
        cv2.rectangle(out, (x1, y1), (x2, y2), colour, 2)
        tag = f"{det.label} {det.confidence:.2f}"
        if det.track_id is not None:
            tag = f"#{det.track_id} {tag}"
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (x1, y1 - th - 6), (x1 + tw + 4, y1), colour, -1)
        cv2.putText(
            out,
            tag,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (16, 24, 40),
            1,
            cv2.LINE_AA,
        )
    return out
