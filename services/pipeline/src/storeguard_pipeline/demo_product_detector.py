"""DEMO product-presence detector — NOT supermarket SKU recognition.

This is a deliberately simple colour-marker detector used only so the FILE DEMO
clip has an honest, explicitly-labelled product-occupancy signal. Generic COCO
YOLO classes are not SKUs; real product recognition needs a lawful labelled
dataset and a trained detector/embedding. Do not present this as SKU detection.
"""

from __future__ import annotations

LABEL = "DEMO-PRODUCT-DETECTOR"


def product_present_in_roi(
    image, roi_norm: tuple[float, float, float, float], min_fraction: float = 0.01
) -> bool:
    """True if a green product marker occupies the normalized ROI.

    ``roi_norm`` is (x0, y0, x1, y1) in [0, 1]. Colour thresholding only — a
    stand-in for a real product detector, clearly labelled as such.
    """
    import cv2
    import numpy as np

    h, w = image.shape[:2]
    x0, y0 = int(roi_norm[0] * w), int(roi_norm[1] * h)
    x1, y1 = int(roi_norm[2] * w), int(roi_norm[3] * h)
    roi = image[y0:y1, x0:x1]
    if roi.size == 0:
        return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([40, 80, 80]), np.array([80, 255, 255]))
    fraction = float(mask.mean()) / 255.0
    return fraction >= min_fraction
