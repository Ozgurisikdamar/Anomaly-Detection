# services/capture — supervised camera (Phase 2)

Per-camera capture supervision: a background reader with a **bounded
latest-frame buffer**, explicit **health state**, **frame-age**, FPS and
**reconnect with exponential backoff**.

- `SupervisedCamera(source_factory, camera_id, ...)` — runs any `FrameSource`
  factory (synthetic / file / RTSP) on its own thread. Consumers call
  `latest()` / `health()` / `status()`; the reader never backs up (buffer holds
  one frame).
- `RtspFrameSource(url)` — OpenCV RTSP/file adapter (`ml` extra). URLs/credentials
  are server-side only, never exposed to clients. Not run against a live camera
  in this environment.
- `storeguard_capture.testing.CameraController` — deterministic in-process source
  for tests/demos (connects while "up", raises while "down").

Health: `ONLINE` (fresh), `DEGRADED` (frame-age past the soft threshold),
`OFFLINE` (past the hard threshold or disconnected), `UNKNOWN` (no frame yet).
`status()` returns a real `CameraStreamStatus` with `simulated=False`.

```bash
python -m storeguard_capture.cli camera-demo   # health/reconnect timeline
```

Install the RTSP adapter with `pip install -e "services/capture[ml]"`. The
supervision/health logic itself needs no OpenCV and is unit-tested without a
camera.
