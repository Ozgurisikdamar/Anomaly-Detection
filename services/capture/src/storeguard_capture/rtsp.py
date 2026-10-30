"""RTSP / file frame source via OpenCV (optional ``ml`` extra).

Thin adapter implementing the ``storeguard_vision.capture.base.FrameSource``
protocol. The URL/credentials are supplied by server-side config and never
exposed to clients. Not exercised against a live camera in this environment.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

from storeguard_vision.capture.base import Frame


class RtspFrameSource:
    """Read frames from an RTSP URL (or any OpenCV-openable source)."""

    def __init__(
        self, url: str, source_id: str = "rtsp", open_timeout_s: float = 10.0
    ) -> None:
        self.url = url
        self.source_id = source_id
        self.open_timeout_s = open_timeout_s
        self._cap: Any = None  # cv2.VideoCapture; cv2 is a lazy (ml) import

    def __iter__(self) -> Iterator[Frame]:
        import cv2  # lazy (ml extra)

        # Use the FFMPEG backend so the open/read timeouts are honoured (the
        # default backend ignores them), and keep only the latest frame so a slow
        # consumer never reads stale buffered frames from a live camera.
        timeout_ms = str(int(self.open_timeout_s * 1000))
        self._cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        for prop in ("CAP_PROP_OPEN_TIMEOUT_MSEC", "CAP_PROP_READ_TIMEOUT_MSEC"):
            prop_id = getattr(cv2, prop, None)
            if prop_id is not None:
                self._cap.set(prop_id, float(timeout_ms))
        buf = getattr(cv2, "CAP_PROP_BUFFERSIZE", None)
        if buf is not None:
            self._cap.set(buf, 1)
        if not self._cap.isOpened():
            raise ConnectionError(f"could not open stream: {self.source_id}")
        i = 0
        while True:
            ok, img = self._cap.read()
            if not ok:
                raise ConnectionError(f"stream read failed: {self.source_id}")
            yield Frame(
                index=i, timestamp=time.time(), image=img, source_id=self.source_id
            )
            i += 1

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
