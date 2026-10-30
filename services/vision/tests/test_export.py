"""Export + accelerated-backend benchmark (guarded by the ml/accel extras).

Skipped in light CI. Where ultralytics + onnxruntime + openvino are installed,
exports YOLO11n to each backend and runs a tiny benchmark through the same
YoloDetector, proving the exported model loads and benchmarks on CPU.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from storeguard_vision.benchmark import (
    Backend,
    BenchmarkConfig,
    ModelCandidate,
    run_benchmark,
)

_HAS_ULTRA = importlib.util.find_spec("ultralytics") is not None
_HAS_ORT = importlib.util.find_spec("onnxruntime") is not None
_HAS_OV = importlib.util.find_spec("openvino") is not None


@pytest.mark.skipif(
    not (_HAS_ULTRA and _HAS_ORT), reason="ultralytics+onnxruntime not installed"
)
def test_onnx_export_and_benchmark(tmp_path: Path) -> None:
    cfg = BenchmarkConfig(
        model=ModelCandidate.YOLO11N,
        backend=Backend.ONNX,
        frames=2,
        warmup=1,
        input_size=320,
        export_dir=str(tmp_path / "exports"),
    )
    res = run_benchmark(cfg)
    assert res.backend is Backend.ONNX
    assert res.fps is not None and res.fps > 0
    assert (tmp_path / "exports" / "yolo11n.onnx").is_file()


@pytest.mark.skipif(
    not (_HAS_ULTRA and _HAS_OV), reason="ultralytics+openvino not installed"
)
def test_openvino_export_and_benchmark(tmp_path: Path) -> None:
    cfg = BenchmarkConfig(
        model=ModelCandidate.YOLO11N,
        backend=Backend.OPENVINO,
        frames=2,
        warmup=1,
        input_size=320,
        export_dir=str(tmp_path / "exports"),
    )
    res = run_benchmark(cfg)
    assert res.backend is Backend.OPENVINO
    assert res.fps is not None and res.fps > 0
    assert (tmp_path / "exports" / "yolo11n_openvino_model").is_dir()
