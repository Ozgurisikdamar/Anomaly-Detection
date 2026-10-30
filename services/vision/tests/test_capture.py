"""Synthetic capture tests (numpy only — no ML stack)."""

from __future__ import annotations

from storeguard_vision.capture import Frame, SyntheticFrameSource


def test_synthetic_yields_requested_frames() -> None:
    src = SyntheticFrameSource(frames=10, width=320, height=192)
    frames = list(src)
    assert len(frames) == 10
    assert all(isinstance(f, Frame) for f in frames)


def test_synthetic_frame_shape_and_dtype() -> None:
    src = SyntheticFrameSource(frames=3, width=320, height=192)
    f = next(iter(src))
    assert f.image.shape == (192, 320, 3)
    assert str(f.image.dtype) == "uint8"
    assert f.width == 320 and f.height == 192


def test_synthetic_is_deterministic() -> None:
    a = list(SyntheticFrameSource(frames=4, seed=1))
    b = list(SyntheticFrameSource(frames=4, seed=1))
    assert (a[-1].image == b[-1].image).all()


def test_indices_and_timestamps_monotonic() -> None:
    frames = list(SyntheticFrameSource(frames=5, fps=10.0))
    assert [f.index for f in frames] == [0, 1, 2, 3, 4]
    assert frames[1].timestamp > frames[0].timestamp
