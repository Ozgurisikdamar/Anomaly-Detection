# services/shelf-analytics — shelf event MVP (Phase 3)

A transparent finite-state machine over per-shelf-zone occupancy observations.
It emits **observable** anomalies only, each requiring human review — never an
accusation.

## Rules (roadmap §4.A)
- **A1 baseline** — establish occupancy after N stable observations; update only
  via approved replenishment or the stable-observation policy. A removal is
  **never** silently learned as a new baseline.
- **A2 unresolved removal** — a product absent from the ROI beyond
  `removal_interval_s` becomes `SHELF_ITEM_REMOVED_UNRESOLVED` **only** when the
  zone is not occluded and the camera is healthy; otherwise it is suppressed and
  surfaced as `SHELF_OCCLUSION_REVIEW` with the zone marked UNKNOWN.
- **A3 association** — a nearby person interaction is attached as supplementary
  association evidence (score components, ephemeral track ref), never identity;
  crowded/occluded → association UNKNOWN.
- De-duplication via a cooldown window.

## Scenarios (replay)
`storeguard_shelf.scenarios.run_all()` runs the three roadmap scenarios and
records a **false-alert count** (removals emitted when none was warranted):

| Scenario | Expectation |
|---|---|
| shelf-removal | exactly one removal candidate (with person association) |
| shelf-occlusion | no removal; occlusion review; zone UNKNOWN |
| shelf-replenishment | no alert; controlled baseline update |

```bash
python -m storeguard_shelf.cli shelf-demo --out runs   # timeline + evidence + mock review
```

The rule logic is pure (numpy + contracts) and unit-tested in replay; the
evidence montage uses OpenCV (`pip install -e "services/shelf-analytics[ml]"`).
Occupancy observations (`product_present` per zone) come from the detector
(Phase 1) + zone geometry (Phase 2) in a later integration; here they are
provided directly so the rules are testable without live SKU detection.
