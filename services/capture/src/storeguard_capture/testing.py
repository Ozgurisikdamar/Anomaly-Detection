"""Deterministic in-process camera source for tests and demos.

No network and no OpenCV: a controllable source that produces frames while "up"
and raises while "down", so the supervisor's disconnect → OFFLINE → reconnect →
ONLINE path and frame-age/reconnect metrics can be tested without a real camera.
"""

from __future__ import annotations

import time
from collections.abc import Iterator

import numpy as np
from storeguard_vision.capture.base import Frame


class CameraController:
    """Shared switch deciding whether the (re)created source connects."""

    def __init__(self, fps: float = 50.0, frame_size: int = 16) -> None:
        self.up = True
        self.fps = fps
        self.frame_size = frame_size

    def set_up(self) -> None:
        self.up = True

    def set_down(self) -> None:
        self.up = False

    def factory(self) -> ControlledSource:
        # Mimic a connect attempt: fails immediately while down.
        if not self.up:
            raise ConnectionError("camera down (connect failed)")
        return ControlledSource(self)


class ControlledSource:
    source_id = "controlled"

    def __init__(self, controller: CameraController) -> None:
        self._ctrl = controller
        self._i = 0

    def __iter__(self) -> Iterator[Frame]:
        n = self._ctrl.frame_size
        while True:
            if not self._ctrl.up:
                raise ConnectionError("camera down (mid-stream)")
            img = np.zeros((n, n, 3), dtype=np.uint8)
            yield Frame(
                index=self._i,
                timestamp=time.time(),
                image=img,
                source_id=self.source_id,
            )
            self._i += 1
            time.sleep(1.0 / self._ctrl.fps)

    def close(self) -> None:
        return None
