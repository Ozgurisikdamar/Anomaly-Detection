"""Pure-Python metric tests (no ML stack required)."""

from __future__ import annotations

from storeguard_vision.metrics import LatencyStats, percentile


def test_percentile_basic() -> None:
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert percentile(data, 50) == 30.0
    assert percentile(data, 0) == 10.0
    assert percentile(data, 100) == 50.0


def test_percentile_empty_and_single() -> None:
    assert percentile([], 95) == 0.0
    assert percentile([7.0], 95) == 7.0


def test_latency_stats() -> None:
    s = LatencyStats.from_samples([40.0, 50.0, 60.0])
    assert s.count == 3
    assert s.mean_ms == 50.0
    assert s.p50_ms == 50.0
    assert round(s.fps, 1) == 20.0  # 1000 / 50ms


def test_latency_stats_empty() -> None:
    s = LatencyStats.from_samples([])
    assert s.count == 0 and s.fps == 0.0
