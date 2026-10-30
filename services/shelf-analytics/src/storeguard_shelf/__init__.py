"""StoreGuard shelf analytics (Phase 3).

A transparent finite-state machine over per-shelf-zone occupancy observations
that emits *observable* anomaly events — never an accusation:

- A1: establish an occupancy baseline from N stable observations; update it only
  through approved replenishment or the stable-observation policy. A removal is
  NEVER silently learned as a new baseline.
- A2: a product leaving a shelf ROI beyond a configurable interval becomes a
  ``SHELF_ITEM_REMOVED_UNRESOLVED`` candidate ONLY when the zone is not occluded
  and the camera is healthy; otherwise it is occlusion/offline-suppressed and
  surfaced as ``SHELF_OCCLUSION_REVIEW`` / UNKNOWN.
- A3: a nearby person interaction is attached as supplementary association
  evidence (score components), never identity; crowded/occluded → UNKNOWN.

Every emitted event requires human review and is flagged simulated in the demo.
"""

from storeguard_shelf.model import ShelfRules, ShelfTick
from storeguard_shelf.monitor import ShelfMonitor

__all__ = ["ShelfMonitor", "ShelfRules", "ShelfTick"]
__version__ = "0.1.0"
