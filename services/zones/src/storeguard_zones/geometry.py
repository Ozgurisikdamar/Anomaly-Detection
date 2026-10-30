"""Polygon zone geometry and YAML loading."""

from __future__ import annotations

from pathlib import Path

import yaml
from storeguard_contracts import CameraZone, ZoneType

Point = tuple[float, float]
Polygon = list[tuple[float, float]]


def point_in_polygon(point: Point, polygon: Polygon) -> bool:
    """Ray-casting point-in-polygon test.

    Points on the exact boundary are not guaranteed either way (standard for ray
    casting); callers needing edge-inclusive tests should add a tolerance.
    """
    if len(polygon) < 3:
        return False
    x, y = point
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def zones_containing(point: Point, zones: list[CameraZone]) -> list[str]:
    """Return the ids of zones whose polygon contains ``point``."""
    return [z.zone_id for z in zones if point_in_polygon(point, z.polygon)]


def load_zones(yaml_path: str | Path) -> list[CameraZone]:
    """Load zones from a ``zones.example.yaml``-shaped file into CameraZone."""
    data = yaml.safe_load(Path(yaml_path).read_text()) or {}
    out: list[CameraZone] = []
    for raw in data.get("zones", []):
        out.append(
            CameraZone(
                zone_id=raw["zone_id"],
                camera_id=raw["camera_id"],
                zone_type=ZoneType(raw["zone_type"]),
                label=raw.get("label", raw["zone_id"]),
                polygon=[(float(p[0]), float(p[1])) for p in raw.get("polygon", [])],
            )
        )
    return out
