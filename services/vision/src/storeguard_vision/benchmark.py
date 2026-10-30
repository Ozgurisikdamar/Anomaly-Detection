"""CPU benchmark harness (Phase 1 — implemented).

Measures, on the real machine, a detector candidate over a frame source:
per-frame inference latency (p50/p95), single-stream FPS, process CPU% and peak
RSS. Precision/recall and tracking ID-switch counts require a labelled eval set
and are left as ``None`` with an explanatory note (never invented).

Model execution requires the optional ``ml`` extra (ultralytics/opencv/psutil).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ModelCandidate(str, Enum):
    YOLO26N = "yolo26n"
    YOLO11N = "yolo11n"
    # Export-based CPU candidates — benchmarked in a follow-up (see notes).
    ONNX_EXPORT = "onnx-export"
    OPENVINO_EXPORT = "openvino-export"


class Tracker(str, Enum):
    BYTETRACK = "bytetrack"  # efficient fixed-camera baseline
    BOTSORT = "botsort"
    TRACKTRACK = "tracktrack"


# Candidate -> ultralytics weights file (downloaded on first use).
_WEIGHTS = {
    ModelCandidate.YOLO26N: "yolo26n.pt",
    ModelCandidate.YOLO11N: "yolo11n.pt",
}


@dataclass(frozen=True)
class BenchmarkConfig:
    """Inputs for a single benchmark run."""

    model: ModelCandidate
    tracker: Tracker = Tracker.BYTETRACK
    input_size: int = 640
    clip_path: str | None = None
    frame_sample_stride: int = 1
    device: str = "cpu"
    frames: int = 60
    warmup: int = 5
    conf: float = 0.25


@dataclass
class BenchmarkResult:
    """Measured outputs. Quality fields stay None without a labelled eval set."""

    model: ModelCandidate
    tracker: Tracker
    device: str = "cpu"
    input_size: int = 640
    frames: int = 0
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    latency_mean_ms: float | None = None
    fps: float | None = None
    frame_age_p95_ms: float | None = None
    precision: float | None = None
    recall: float | None = None
    id_switches: int | None = None
    total_detections: int | None = None
    cpu_percent: float | None = None
    ram_mb: float | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["model"] = self.model.value
        d["tracker"] = self.tracker.value
        return d


def _load_frames(config: BenchmarkConfig) -> list:
    """Materialize frames from the configured source (file or synthetic)."""
    from storeguard_vision.capture.base import FrameSource
    from storeguard_vision.capture.file_source import FileFrameSource
    from storeguard_vision.capture.synthetic import SyntheticFrameSource

    src: FrameSource
    if config.clip_path:
        src = FileFrameSource(config.clip_path, max_frames=config.frames)
    else:
        src = SyntheticFrameSource(
            frames=config.frames, width=config.input_size, height=384
        )
    frames = list(src)
    src.close()
    if config.frame_sample_stride > 1:
        frames = frames[:: config.frame_sample_stride]
    # If a small image set is given, repeat it up to `frames` for a stable sample.
    if frames and len(frames) < config.frames:
        reps = (config.frames // len(frames)) + 1
        frames = (frames * reps)[: config.frames]
    return frames


def run_benchmark(config: BenchmarkConfig) -> BenchmarkResult:
    """Run the benchmark and return measured metrics."""
    if config.model not in _WEIGHTS:
        raise NotImplementedError(
            f"Benchmark for {config.model.value!r} (export candidate) is a follow-up; "
            "Phase 1 measures the .pt candidates (yolo26n, yolo11n)."
        )

    from storeguard_vision.detect.detector import YoloDetector
    from storeguard_vision.metrics import LatencyStats, ResourceSampler

    detector = YoloDetector(
        weights=_WEIGHTS[config.model],
        imgsz=config.input_size,
        device=config.device,
        conf=config.conf,
    )
    frames = _load_frames(config)
    if not frames:
        raise RuntimeError("no frames to benchmark")

    # Warmup (not measured) to exclude first-call graph/alloc costs.
    for i in range(min(config.warmup, len(frames))):
        detector.infer(frames[i].image)

    latencies: list[float] = []
    total_dets = 0
    with ResourceSampler() as sampler:
        for frame in frames:
            t0 = time.perf_counter()
            dets = detector.infer(frame.image)
            latencies.append((time.perf_counter() - t0) * 1000.0)
            total_dets += len(dets)

    stats = LatencyStats.from_samples(latencies)
    return BenchmarkResult(
        model=config.model,
        tracker=config.tracker,
        device=config.device,
        input_size=config.input_size,
        frames=len(frames),
        latency_p50_ms=round(stats.p50_ms, 2),
        latency_p95_ms=round(stats.p95_ms, 2),
        latency_mean_ms=round(stats.mean_ms, 2),
        fps=round(stats.fps, 2),
        total_detections=total_dets,
        cpu_percent=(
            round(sampler.avg_cpu_percent, 1) if sampler.avg_cpu_percent else None
        ),
        ram_mb=round(sampler.peak_rss_mb, 1) if sampler.peak_rss_mb else None,
        notes=[
            "CPU single-stream inference latency measured on this machine.",
            "precision/recall and id_switches require a labelled eval set (not run).",
            f"source={'file:' + config.clip_path if config.clip_path else 'synthetic'}",
        ],
    )
