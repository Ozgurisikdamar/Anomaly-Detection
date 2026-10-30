"""Benchmark API tests.

The dataclass/enum and export-candidate guard tests need no ML stack. The real
run is covered by a guarded integration test that skips when ultralytics is not
installed, so CI (which does not install the `ml` extra) stays fast while a full
local/`ml` environment still exercises inference.
"""

from __future__ import annotations

import importlib.util

import pytest

from storeguard_vision import BENCHMARK_IMPLEMENTED
from storeguard_vision.benchmark import (
    BenchmarkConfig,
    ModelCandidate,
    Tracker,
    run_benchmark,
)

_HAS_ML = importlib.util.find_spec("ultralytics") is not None


def test_phase1_implemented_flag() -> None:
    assert BENCHMARK_IMPLEMENTED is True


def test_candidates_preserved() -> None:
    # Benchmark plan preserved: YOLO26n and YOLO11n are both candidates.
    assert ModelCandidate.YOLO26N.value == "yolo26n"
    assert ModelCandidate.YOLO11N.value == "yolo11n"
    assert Tracker.BYTETRACK in set(Tracker)


def test_export_candidate_not_implemented() -> None:
    cfg = BenchmarkConfig(model=ModelCandidate.ONNX_EXPORT)
    with pytest.raises(NotImplementedError):
        run_benchmark(cfg)


@pytest.mark.skipif(not _HAS_ML, reason="ultralytics (ml extra) not installed")
def test_run_benchmark_synthetic_smoke() -> None:
    # Tiny synthetic run; downloads yolo11n weights on first use.
    cfg = BenchmarkConfig(
        model=ModelCandidate.YOLO11N, frames=3, warmup=1, input_size=320
    )
    res = run_benchmark(cfg)
    assert res.frames == 3
    assert res.latency_p50_ms is not None and res.latency_p50_ms > 0
    assert res.fps is not None and res.fps > 0
