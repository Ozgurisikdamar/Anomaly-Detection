"""Synthetic frame source (numpy only — no OpenCV, no network).

Generates a deterministic sequence of frames with a few moving coloured blobs
on a gradient background. Useful for exercising the pipeline, for the tracking
demo (objects move frame to frame), and for latency/FPS benchmarking without any
real footage. Generic COCO detectors will usually find nothing here — that is
expected and honest; detection quality is evaluated on real labelled data, not
synthetic blobs.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np

from storeguard_vision.capture.base import Frame


class SyntheticFrameSource:
    def __init__(
        self,
        frames: int = 60,
        width: int = 640,
        height: int = 384,
        fps: float = 15.0,
        source_id: str = "synthetic",
        seed: int = 7,
    ) -> None:
        self.frames = frames
        self.width = width
        self.height = height
        self.fps = fps
        self.source_id = source_id
        self._seed = seed

    def _background(self) -> np.ndarray:
        # Vertical blue→dark gradient (BGR).
        grad = np.linspace(40, 120, self.height, dtype=np.uint8)
        bg = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        bg[:, :, 0] = grad[:, None]  # blue channel
        return bg

    def __iter__(self) -> Iterator[Frame]:
        rng = np.random.default_rng(self._seed)
        n_blobs = 3
        # Random start positions and velocities per blob (deterministic via seed).
        pos = rng.uniform([0, 0], [self.width, self.height], size=(n_blobs, 2))
        vel = rng.uniform(-6, 6, size=(n_blobs, 2))
        colours = np.array([[0, 0, 220], [0, 220, 0], [220, 160, 0]], dtype=np.uint8)
        radius = 28

        for i in range(self.frames):
            img = self._background()
            pos += vel
            # Bounce off edges.
            for b in range(n_blobs):
                for d, limit in enumerate((self.width, self.height)):
                    if pos[b, d] < radius or pos[b, d] > limit - radius:
                        vel[b, d] *= -1
                        pos[b, d] = np.clip(pos[b, d], radius, limit - radius)
                self._draw_blob(img, int(pos[b, 0]), int(pos[b, 1]), radius, colours[b])
            yield Frame(
                index=i, timestamp=i / self.fps, image=img, source_id=self.source_id
            )

    @staticmethod
    def _draw_blob(
        img: np.ndarray, cx: int, cy: int, r: int, colour: np.ndarray
    ) -> None:
        h, w = img.shape[:2]
        y0, y1 = max(0, cy - r), min(h, cy + r)
        x0, x1 = max(0, cx - r), min(w, cx + r)
        ys = np.arange(y0, y1)[:, None]
        xs = np.arange(x0, x1)[None, :]
        mask = (ys - cy) ** 2 + (xs - cx) ** 2 <= r * r
        img[y0:y1, x0:x1][mask] = colour

    def close(self) -> None:
        return None
