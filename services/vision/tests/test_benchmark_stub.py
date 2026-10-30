"""Tests asserting the Phase 0 vision harness is a non-executing stub."""

from __future__ import annotations

import pytest

from storeguard_vision import PHASE_0_STUB
from storeguard_vision.benchmark import (
    BenchmarkConfig,
    ModelCandidate,
    Tracker,
    run_benchmark,
)


def test_phase0_is_stub() -> None:
    assert PHASE_0_STUB is True


def test_candidates_present() -> None:
    # The benchmark plan is preserved: YOLO26n and YOLO11n are both candidates.
    assert ModelCandidate.YOLO26N.value == "yolo26n"
    assert ModelCandidate.YOLO11N.value == "yolo11n"
    assert Tracker.BYTETRACK in set(Tracker)


def test_run_benchmark_not_implemented_in_phase0() -> None:
    cfg = BenchmarkConfig(model=ModelCandidate.YOLO26N)
    with pytest.raises(NotImplementedError):
        run_benchmark(cfg)
