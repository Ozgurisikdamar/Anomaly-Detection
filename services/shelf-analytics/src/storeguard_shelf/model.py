"""Input observations, rules, and per-zone state for the shelf monitor."""

from __future__ import annotations

from dataclasses import dataclass, field

from storeguard_contracts import CameraStreamState


@dataclass
class ShelfTick:
    """One observation of a shelf ROI at time ``t`` (seconds).

    ``product_present`` is the per-zone occupancy observation (in a full system
    it is derived from the detector + zone geometry; here it is provided directly
    so the rule logic is testable in replay without live SKU detection).
    """

    t: float
    zone_id: str
    camera_id: str
    product_present: bool
    occluded: bool = False
    camera_state: CameraStreamState = CameraStreamState.ONLINE
    person_interaction: bool = False
    approved_replenishment: bool = False
    crowded: bool = False
    track_ref: str | None = None


@dataclass(frozen=True)
class ShelfRules:
    """Thresholds governing baseline, removal and de-duplication."""

    baseline_min_observations: int = 5
    removal_interval_s: float = 3.0
    cooldown_s: float = 10.0


@dataclass
class ZoneState:
    """Mutable per-zone state tracked across ticks."""

    baseline_established: bool = False
    stable_present_count: int = 0
    present: bool | None = None
    absence_start_t: float | None = None
    interaction_during_absence: bool = False
    crowded_during_absence: bool = False
    last_removal_event_t: float | None = None
    last_occlusion_event_t: float | None = None
    reason_tags: list[str] = field(default_factory=list)
