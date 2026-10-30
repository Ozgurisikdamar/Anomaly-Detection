"""Frame and FrameSource abstractions."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np


@dataclass
class Frame:
    """A single captured frame.

    ``image`` is an HxWx3 BGR ``uint8`` array (OpenCV convention). ``timestamp``
    is a monotonic-ish source time in seconds; ``index`` is the 0-based frame
    number; ``source_id`` identifies the camera/source (never a person).
    """

    index: int
    timestamp: float
    image: np.ndarray
    source_id: str

    @property
    def height(self) -> int:
        return int(self.image.shape[0])

    @property
    def width(self) -> int:
        return int(self.image.shape[1])


@runtime_checkable
class FrameSource(Protocol):
    """A finite or bounded iterable of frames for the offline workbench."""

    source_id: str

    def __iter__(self) -> Iterator[Frame]: ...

    def close(self) -> None: ...
