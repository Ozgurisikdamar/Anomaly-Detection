"""Zone geometry + loading tests (pure; no OpenCV)."""

from __future__ import annotations

from pathlib import Path

from storeguard_contracts import ZoneType

from storeguard_zones.geometry import load_zones, point_in_polygon, zones_containing

_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
_CONFIG = Path(__file__).resolve().parents[3] / "configs" / "zones.example.yaml"


def test_point_in_polygon_inside_outside() -> None:
    assert point_in_polygon((0.5, 0.5), _SQUARE) is True
    assert point_in_polygon((1.5, 0.5), _SQUARE) is False
    assert point_in_polygon((0.5, -0.1), _SQUARE) is False


def test_point_in_polygon_degenerate() -> None:
    assert point_in_polygon((0.5, 0.5), [(0.0, 0.0), (1.0, 1.0)]) is False


def test_load_zones_from_example() -> None:
    zones = load_zones(_CONFIG)
    assert len(zones) >= 4
    by_id = {z.zone_id: z for z in zones}
    shelf = by_id["zone_shelf_01_display"]
    assert shelf.zone_type == ZoneType.SHELF_DISPLAY
    assert len(shelf.polygon) == 4
    # All coordinates are normalized to [0, 1].
    for z in zones:
        for x, y in z.polygon:
            assert 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0


def test_zones_containing() -> None:
    zones = load_zones(_CONFIG)
    # A point inside the shelf display polygon.
    hits = zones_containing((0.3, 0.4), zones)
    assert "zone_shelf_01_display" in hits
