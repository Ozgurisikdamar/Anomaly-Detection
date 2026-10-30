"""StoreGuard zone geometry and overlay (Phase 2).

Polygon/ROI zones are configured per camera as normalized ``[x, y]`` points in
``[0, 1]`` (resolution-independent). This package loads them from YAML, tests
point-in-polygon membership, and draws overlays. Zones never encode identity.
"""

from storeguard_zones.geometry import (
    load_zones,
    point_in_polygon,
    zones_containing,
)

__all__ = ["load_zones", "point_in_polygon", "zones_containing"]
__version__ = "0.1.0"
