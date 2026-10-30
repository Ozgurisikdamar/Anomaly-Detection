"""RtspFrameSource + SupervisedCamera decode/reconnect validation.

Guarded by OpenCV (the ``ml`` extra): skipped in light CI. Uses a short clip
written with cv2.VideoWriter and opened through RtspFrameSource (OpenCV opens any
source), so it exercises the real decode + health + reconnect path without a
network RTSP server (a live RTSP server / real camera is owner-blocked).
"""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path

import pytest

_HAS_CV2 = importlib.util.find_spec("cv2") is not None
pytestmark = pytest.mark.skipif(not _HAS_CV2, reason="opencv (ml extra) not installed")


def _write_clip(path: Path, frames: int = 30) -> Path:
    import cv2
    import numpy as np

    w, h = 160, 120
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 15.0, (w, h))
    for i in range(frames):
        img = np.full((h, w, 3), (i * 7) % 255, dtype=np.uint8)
        writer.write(img)
    writer.release()
    return path


def test_decode_and_reconnect_via_supervisor(tmp_path: Path) -> None:
    from storeguard_capture.rtsp import RtspFrameSource
    from storeguard_capture.supervisor import SupervisedCamera

    clip = _write_clip(tmp_path / "clip.mp4")
    cam = SupervisedCamera(
        lambda: RtspFrameSource(str(clip)),
        camera_id="cam_test",
        initial_backoff_s=0.02,
        max_backoff_s=0.1,
    )
    decoded = False
    with cam:
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            if cam.latest() is not None:
                decoded = True
                break
            time.sleep(0.05)
        # The short clip ends and is reopened, so the supervisor reconnects.
        time.sleep(1.0)
        reconnects = cam.reconnect_count

    assert decoded, "no frame decoded from the source"
    assert reconnects >= 1, "reconnect/backoff loop did not fire on source end"
