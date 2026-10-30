"""Measurement helpers: latency percentiles and a resource sampler.

Pure-Python latency math (no heavy deps) so it is unit-testable in CI. The
resource sampler uses psutil (optional ``ml`` extra) and is only started during
an actual benchmark run.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Self


def percentile(values: list[float], p: float) -> float:
    """Linear-interpolated percentile (p in [0, 100]). Empty -> 0.0."""
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    s = sorted(values)
    rank = (p / 100.0) * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    frac = rank - lo
    return float(s[lo] + (s[hi] - s[lo]) * frac)


@dataclass
class LatencyStats:
    count: int
    mean_ms: float
    p50_ms: float
    p95_ms: float
    fps: float  # single-stream throughput derived from mean latency

    @classmethod
    def from_samples(cls, latencies_ms: list[float]) -> LatencyStats:
        if not latencies_ms:
            return cls(0, 0.0, 0.0, 0.0, 0.0)
        mean = sum(latencies_ms) / len(latencies_ms)
        return cls(
            count=len(latencies_ms),
            mean_ms=mean,
            p50_ms=percentile(latencies_ms, 50),
            p95_ms=percentile(latencies_ms, 95),
            fps=(1000.0 / mean) if mean > 0 else 0.0,
        )


class ResourceSampler:
    """Background sampler for process CPU% and RSS (MB). Context manager."""

    def __init__(self, interval_s: float = 0.2) -> None:
        self.interval_s = interval_s
        self._cpu: list[float] = []
        self._rss_mb: list[float] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> Self:
        # psutil is part of the optional `ml` extra; imported lazily.
        import psutil  # type: ignore[import-untyped]

        proc = psutil.Process()
        proc.cpu_percent(None)  # prime

        def loop() -> None:
            while not self._stop.is_set():
                self._cpu.append(proc.cpu_percent(None))
                self._rss_mb.append(proc.memory_info().rss / (1024 * 1024))
                time.sleep(self.interval_s)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    @property
    def avg_cpu_percent(self) -> float | None:
        return sum(self._cpu) / len(self._cpu) if self._cpu else None

    @property
    def peak_rss_mb(self) -> float | None:
        return max(self._rss_mb) if self._rss_mb else None
