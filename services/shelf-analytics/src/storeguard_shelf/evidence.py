"""Render a short evidence montage for a shelf-removal candidate.

Offline demo evidence: a few synthetic frames (present -> person interaction ->
absent) with the shelf ROI drawn, stitched into a strip. This stands in for an
evidence clip; a real deployment attaches an authenticated short clip via a
short-lived URL (never a raw storage path). OpenCV is the optional ``ml`` extra.
"""

from __future__ import annotations

from pathlib import Path

from storeguard_contracts import EvidenceRef

# Normalized shelf ROI (matches the demo's zone_shelf_01_display).
_ROI = (0.12, 0.25, 0.55, 0.80)  # x0, y0, x1, y1


def render_evidence_montage(
    out_path: str | Path, evidence_id: str = "ev_shelf_01"
) -> EvidenceRef:
    import cv2
    import numpy as np

    h, w = 240, 320
    panels = []
    specs = [
        ("product present", True, False),
        ("person interaction", True, True),
        ("product absent", False, False),
    ]
    for label, present, person in specs:
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:, :, 0] = np.linspace(40, 100, h, dtype=np.uint8)[:, None]  # bg gradient
        x0, y0 = int(_ROI[0] * w), int(_ROI[1] * h)
        x1, y1 = int(_ROI[2] * w), int(_ROI[3] * h)
        cv2.rectangle(img, (x0, y0), (x1, y1), (255, 170, 79), 2)  # shelf ROI
        if present:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            cv2.rectangle(
                img, (cx - 24, cy - 18), (cx + 24, cy + 18), (74, 222, 128), -1
            )
        if person:
            cv2.rectangle(img, (x1 - 6, y0), (x1 + 40, y1), (81, 196, 245), 2)
            cv2.putText(
                img,
                "person",
                (x1 - 4, y0 + 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (81, 196, 245),
                1,
                cv2.LINE_AA,
            )
        cv2.putText(
            img,
            label,
            (8, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (230, 236, 247),
            1,
            cv2.LINE_AA,
        )
        panels.append(img)

    strip = np.hstack(panels)
    cv2.putText(
        strip,
        "SIMULATED evidence (human review required)",
        (8, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (245, 196, 81),
        1,
        cv2.LINE_AA,
    )
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), strip)
    return EvidenceRef(evidence_id=evidence_id, kind="clip", available=True)
