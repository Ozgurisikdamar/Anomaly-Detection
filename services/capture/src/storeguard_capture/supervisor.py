"""Supervised camera reader: background capture, bounded latest-frame buffer,
health state and reconnect with backoff.

Design goals (roadmap Phase 2):
- Capture runs on its own thread; consumers read the *latest* frame and never
  block or back up the reader (the buffer holds exactly one frame).
- Health is explicit: ONLINE / DEGRADED / OFFLINE, and UNKNOWN until the first
  frame or whenever the reader cannot be trusted.
- Reconnects use exponential backoff and bump ``reconnect_count``.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from storeguard_contracts import CameraStreamState, CameraStreamStatus

# A factory returns a fresh, iterable frame source each (re)connect.
SourceFactory = Callable[[], Iterable[Any]]


@dataclass
class CameraHealth:
    """Point-in-time health snapshot (all real, never simulated)."""

    camera_id: str
    state: CameraStreamState
    frame_age_ms: float | None
    fps: float | None
    reconnect_count: int
    connected: bool


class SupervisedCamera:
    def __init__(
        self,
        source_factory: SourceFactory,
        camera_id: str,
        degraded_age_ms: float = 500.0,
        offline_age_ms: float = 2000.0,
        initial_backoff_s: float = 0.1,
        max_backoff_s: float = 8.0,
        fps_window: int = 30,
    ) -> None:
        self.source_factory = source_factory
        self.camera_id = camera_id
        self.degraded_age_ms = degraded_age_ms
        self.offline_age_ms = offline_age_ms
        self.initial_backoff_s = initial_backoff_s
        self.max_backoff_s = max_backoff_s

        self._lock = threading.Lock()
        self._latest: Any | None = None
        self._last_frame_mono: float | None = None
        self._frame_times: deque[float] = deque(maxlen=fps_window)
        self._reconnect_count = 0
        self._connected = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    # --- lifecycle -------------------------------------------------------
    def start(self) -> SupervisedCamera:
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, name=f"cam-{self.camera_id}", daemon=True
        )
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def __enter__(self) -> SupervisedCamera:
        return self.start()

    def __exit__(self, *exc: object) -> None:
        self.stop()

    # --- capture loop ----------------------------------------------------
    def _run(self) -> None:
        backoff = self.initial_backoff_s
        while not self._stop.is_set():
            source: Any | None = None
            try:
                source = self.source_factory()
                for frame in source:
                    if self._stop.is_set():
                        return
                    now = time.monotonic()
                    with self._lock:
                        self._latest = frame  # bounded buffer: keep only latest
                        self._last_frame_mono = now
                        self._frame_times.append(now)
                        self._connected = True
                    backoff = self.initial_backoff_s  # healthy read resets backoff
                # Source ended without error — treat as a disconnect.
                raise ConnectionError("source ended")
            except Exception:
                if self._stop.is_set():
                    return
                with self._lock:
                    self._connected = False
                    self._reconnect_count += 1
                if self._stop.wait(backoff):  # interruptible backoff
                    return
                backoff = min(self.max_backoff_s, backoff * 2)
            finally:
                self._close_source(source)

    @staticmethod
    def _close_source(source: Any | None) -> None:
        close = getattr(source, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass

    # --- reads -----------------------------------------------------------
    def latest(self) -> Any | None:
        with self._lock:
            return self._latest

    @property
    def frame_age_ms(self) -> float | None:
        with self._lock:
            if self._last_frame_mono is None:
                return None
            return (time.monotonic() - self._last_frame_mono) * 1000.0

    @property
    def reconnect_count(self) -> int:
        with self._lock:
            return self._reconnect_count

    @property
    def fps(self) -> float | None:
        with self._lock:
            if len(self._frame_times) < 2:
                return None
            span = self._frame_times[-1] - self._frame_times[0]
            if span <= 0:
                return None
            return (len(self._frame_times) - 1) / span

    def _state(self, age_ms: float | None, connected: bool) -> CameraStreamState:
        if age_ms is None:
            return CameraStreamState.UNKNOWN
        if age_ms > self.offline_age_ms or not connected:
            return CameraStreamState.OFFLINE
        if age_ms > self.degraded_age_ms:
            return CameraStreamState.DEGRADED
        return CameraStreamState.ONLINE

    def health(self) -> CameraHealth:
        with self._lock:
            connected = self._connected
            reconnects = self._reconnect_count
        age = self.frame_age_ms
        return CameraHealth(
            camera_id=self.camera_id,
            state=self._state(age, connected),
            frame_age_ms=round(age, 1) if age is not None else None,
            fps=round(self.fps, 2) if self.fps is not None else None,
            reconnect_count=reconnects,
            connected=connected,
        )

    def status(self) -> CameraStreamStatus:
        """Real (non-simulated) status for the API/contracts."""
        h = self.health()
        return CameraStreamStatus(
            camera_id=self.camera_id,
            state=h.state,
            fps=h.fps,
            frame_age_ms=h.frame_age_ms,
            last_frame_at=datetime.now(tz=UTC) if h.connected else None,
            reconnect_count=h.reconnect_count,
            simulated=False,
        )
