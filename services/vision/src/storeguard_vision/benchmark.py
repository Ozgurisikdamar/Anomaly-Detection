"""CPU benchmark harness — STUB for Phase 0.

This module fixes the *interface* and *result shape* of the detector/tracker
benchmark so Phase 1 can fill it in without changing callers. It deliberately
does nothing that touches a model: calling :func:`run_benchmark` raises
``NotImplementedError``. No weights are downloaded, no inference is performed.

Phase 1 will implement this to compare, on the real target CPU and clips:
YOLO26n vs YOLO11n vs an OpenVINO/ONNX-exported candidate, with ByteTrack as the
tracking baseline (BoT-SORT / TrackTrack compared). See ``benchmark_plan.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ModelCandidate(str, Enum):
    YOLO26N = "yolo26n"
    YOLO11N = "yolo11n"
    # Export-based CPU candidates (built from one of the above in Phase 1).
    ONNX_EXPORT = "onnx-export"
    OPENVINO_EXPORT = "openvino-export"


class Tracker(str, Enum):
    BYTETRACK = "bytetrack"  # efficient fixed-camera baseline
    BOTSORT = "botsort"
    TRACKTRACK = "tracktrack"


@dataclass(frozen=True)
class BenchmarkConfig:
    """Inputs for a single benchmark run."""

    model: ModelCandidate
    tracker: Tracker = Tracker.BYTETRACK
    input_size: int = 640
    clip_path: str | None = None
    frame_sample_stride: int = 1
    device: str = "cpu"


@dataclass
class BenchmarkResult:
    """Measured outputs. Every field is measured in Phase 1, never invented."""

    model: ModelCandidate
    tracker: Tracker
    # Latency distribution (ms).
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    fps: float | None = None
    frame_age_p95_ms: float | None = None
    # Quality (filled once a labelled eval set exists).
    precision: float | None = None
    recall: float | None = None
    id_switches: int | None = None
    # Resource use.
    cpu_percent: float | None = None
    ram_mb: float | None = None
    notes: list[str] = field(default_factory=list)


def run_benchmark(config: BenchmarkConfig) -> BenchmarkResult:
    """Phase 1 entry point. Not implemented in Phase 0.

    Raises:
        NotImplementedError: always, in Phase 0.
    """
    raise NotImplementedError(
        "Phase 0 scaffold: the vision benchmark is not implemented and no model "
        "is run here. Implement in Phase 1 (offline vision workbench). "
        f"Requested config: {config!r}"
    )
