# services/zones — polygon geometry + overlay (Phase 2)

Per-camera polygon/ROI zones as normalized `[x, y]` points in `[0, 1]`
(resolution-independent). Zones encode geometry only — never identity.

- `load_zones(yaml)` → `list[CameraZone]` (reads `configs/zones.example.yaml`).
- `point_in_polygon(point, polygon)` — ray-casting membership test.
- `zones_containing(point, zones)` — zone ids whose polygon contains a point.
- `draw_zones(image, zones)` — filled + outlined overlay with labels (`ml` extra).

```bash
python -m storeguard_zones.cli zones-demo --camera cam_shelf_01 --out runs
```

Geometry/loading are pure (numpy + pyyaml) and unit-tested; overlay rendering
needs OpenCV (`pip install -e "services/zones[ml]"`).
