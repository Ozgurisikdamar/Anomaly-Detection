"""SupervisedCamera tests: health transitions, frame-age, reconnect, buffer.

Deterministic and camera-free: uses the in-process CameraController. Generous
timeouts keep it stable on slow CI without being flaky.
"""

from __future__ import annotations

import time

from storeguard_contracts import CameraStreamState

from storeguard_capture.supervisor import SupervisedCamera
from storeguard_capture.testing import CameraController


def _wait_until(pred, timeout: float = 6.0, interval: float = 0.05) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if pred():
            return True
        time.sleep(interval)
    return False


def test_unknown_before_any_frame() -> None:
    cam = SupervisedCamera(CameraController().factory, camera_id="cam_x")
    h = cam.health()  # not started
    assert h.state == CameraStreamState.UNKNOWN
    assert h.frame_age_ms is None


def test_online_offline_reconnect_cycle() -> None:
    ctrl = CameraController(fps=50.0)
    cam = SupervisedCamera(
        ctrl.factory,
        camera_id="cam_x",
        degraded_age_ms=100.0,
        offline_age_ms=300.0,
        initial_backoff_s=0.05,
        max_backoff_s=0.2,
    )
    with cam:
        assert _wait_until(lambda: cam.health().state == CameraStreamState.ONLINE)
        assert cam.status().simulated is False
        assert cam.latest() is not None

        reconnects_before = cam.reconnect_count
        ctrl.set_down()  # inject outage
        assert _wait_until(lambda: cam.health().state == CameraStreamState.OFFLINE)
        # frame-age keeps growing while down
        age1 = cam.frame_age_ms
        time.sleep(0.2)
        assert cam.frame_age_ms is not None and cam.frame_age_ms >= (age1 or 0)
        # the supervisor keeps retrying -> reconnect attempts increase
        assert _wait_until(lambda: cam.reconnect_count > reconnects_before)

        ctrl.set_up()  # recover
        assert _wait_until(lambda: cam.health().state == CameraStreamState.ONLINE)


def test_bounded_buffer_tracks_latest() -> None:
    ctrl = CameraController(fps=100.0)
    cam = SupervisedCamera(ctrl.factory, camera_id="cam_x")
    with cam:
        assert _wait_until(lambda: cam.latest() is not None)
        first = cam.latest()
        time.sleep(0.2)
        second = cam.latest()
        # Only the latest frame is retained, and it advances over time
        # (capture runs independently of any consumer; no backlog).
        assert second is not None and first is not None
        assert second.index >= first.index
        assert cam._frame_times.maxlen is not None  # bounded FPS window
