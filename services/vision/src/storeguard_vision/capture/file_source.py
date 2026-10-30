"""File frame source: read a video file or a directory of images via OpenCV.

OpenCV is imported lazily so importing the package stays light; `cv2` is part of
the optional ``ml`` extra.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from storeguard_vision.capture.base import Frame

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv"}


class FileFrameSource:
    """Iterate frames from a video file or an image directory.

    ``path`` may be a single video, a single image, or a directory of images
    (read in sorted filename order). ``max_frames`` bounds a long video.
    """

    def __init__(
        self,
        path: str | Path,
        source_id: str = "file",
        max_frames: int | None = None,
        fps: float = 15.0,
    ) -> None:
        self.path = Path(path)
        self.source_id = source_id
        self.max_frames = max_frames
        self.fps = fps
        if not self.path.exists():
            raise FileNotFoundError(self.path)

    def _image_paths(self) -> list[Path]:
        if self.path.is_dir():
            return sorted(
                p for p in self.path.iterdir() if p.suffix.lower() in _IMAGE_EXTS
            )
        if self.path.suffix.lower() in _IMAGE_EXTS:
            return [self.path]
        return []

    def __iter__(self) -> Iterator[Frame]:
        import cv2  # lazy: part of the ml extra

        images = self._image_paths()
        if images:
            for i, p in enumerate(images):
                if self.max_frames is not None and i >= self.max_frames:
                    break
                img = cv2.imread(str(p))
                if img is None:
                    continue
                yield Frame(
                    index=i, timestamp=i / self.fps, image=img, source_id=self.source_id
                )
            return

        if self.path.suffix.lower() in _VIDEO_EXTS:
            cap = cv2.VideoCapture(str(self.path))
            try:
                i = 0
                while True:
                    if self.max_frames is not None and i >= self.max_frames:
                        break
                    ok, img = cap.read()
                    if not ok:
                        break
                    yield Frame(
                        index=i,
                        timestamp=i / self.fps,
                        image=img,
                        source_id=self.source_id,
                    )
                    i += 1
            finally:
                cap.release()
            return

        raise ValueError(f"Unsupported source path: {self.path}")

    def close(self) -> None:
        return None
