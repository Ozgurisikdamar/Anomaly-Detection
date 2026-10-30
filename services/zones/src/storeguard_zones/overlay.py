"""Draw zone polygons onto a frame (OpenCV, optional ``ml`` extra)."""

from __future__ import annotations

from storeguard_contracts import CameraZone

# Per zone-type colour (BGR).
_ZONE_COLOURS: dict[str, tuple[int, int, int]] = {
    "SHELF_DISPLAY": (255, 170, 79),
    "PICKUP_INTERACTION": (128, 222, 74),
    "OCCLUSION_UNKNOWN": (160, 160, 160),
    "AISLE_EXIT": (245, 196, 81),
    "SCAN_AREA": (255, 140, 79),
    "BAGGING_SCALE_AREA": (129, 107, 255),
    "BASKET_CART_AREA": (0, 200, 255),
    "EXIT_SIDE": (81, 196, 245),
}


def draw_zones(image, zones: list[CameraZone], alpha: float = 0.25):
    """Return a copy of ``image`` with each zone's polygon filled + outlined.

    Polygons are normalized ``[0, 1]`` and scaled to the image size here.
    """
    import cv2
    import numpy as np

    out = image.copy()
    h, w = out.shape[:2]
    overlay = out.copy()
    for z in zones:
        if len(z.polygon) < 3:
            continue
        pts = np.array([[int(x * w), int(y * h)] for x, y in z.polygon], dtype=np.int32)
        colour = _ZONE_COLOURS.get(z.zone_type.value, (200, 200, 200))
        cv2.fillPoly(overlay, [pts], colour)
        cv2.polylines(out, [pts], isClosed=True, color=colour, thickness=2)
        cx, cy = int(pts[:, 0].mean()), int(pts[:, 1].mean())
        cv2.putText(
            out,
            z.label,
            (cx - 40, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (16, 24, 40),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            out,
            z.label,
            (cx - 40, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            colour,
            1,
            cv2.LINE_AA,
        )
    cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0, out)
    return out
