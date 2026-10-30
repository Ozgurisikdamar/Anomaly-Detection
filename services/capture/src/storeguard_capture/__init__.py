"""StoreGuard capture layer (Phase 2).

A supervised, per-camera reader that:
- runs capture in a background thread, independent of any consumer;
- keeps a **bounded latest-frame buffer** (maxlen=1) so a slow consumer can never
  back up capture into an unbounded queue;
- tracks a **health state** (ONLINE/DEGRADED/OFFLINE/UNKNOWN), **frame-age**, FPS
  and a **reconnect count**, and reconnects with exponential backoff.

RTSP/file capture uses OpenCV (optional ``ml`` extra); the supervision/health
logic itself is pure Python + numpy and is unit-tested without any camera.
Camera credentials/URLs stay server-side and are never exposed to clients.
"""

from storeguard_capture.supervisor import CameraHealth, SupervisedCamera

__all__ = ["CameraHealth", "SupervisedCamera"]
__version__ = "0.1.0"
