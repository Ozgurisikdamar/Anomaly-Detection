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
    Backend,
    BenchmarkConfig,
    BenchmarkResult,
    ModelCandidate,
    Tracker,
    benchmark_env,
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


def test_backend_enum_and_config_shape() -> None:
    # P4 backend dimension (no ML needed to construct).
    assert {b.value for b in Backend} == {"pytorch", "onnx", "openvino"}
    cfg = BenchmarkConfig(
        model=ModelCandidate.YOLO26N, backend=Backend.OPENVINO, trials=3
    )
    assert cfg.backend is Backend.OPENVINO and cfg.trials == 3
    res = BenchmarkResult(model=ModelCandidate.YOLO26N, tracker=Tracker.BYTETRACK)
    assert res.to_dict()["backend"] == "pytorch"


def test_benchmark_env_captures_runtime() -> None:
    env = benchmark_env()
    assert env["python"] and "cpu_count" in env  # best-effort, never raises


@pytest.mark.skipif(not _HAS_ML, reason="ultralytics (ml extra) not installed")
def test_run_benchmark_synthetic_smoke() -> None:
    # Tiny synthetic run; uses yolo11n weights on disk/first use.
    cfg = BenchmarkConfig(
        model=ModelCandidate.YOLO11N, frames=3, warmup=1, trials=2, input_size=320
    )
    res = run_benchmark(cfg)
    assert res.frames == 3 and res.trials == 2
    assert res.latency_p50_ms is not None and res.latency_p50_ms > 0
    assert res.fps is not None and res.fps > 0
