"""Deterministic replay scenarios 1–3 (roadmap §5) and a false-alert metric.

Scenario 1 (removal):      visible -> person interacts -> disappears beyond
                           threshold -> ONE SHELF_ITEM_REMOVED_UNRESOLVED.
Scenario 2 (occlusion):    shopper blocks the shelf -> NO removal; occlusion
                           review; zone UNKNOWN.
Scenario 3 (replenishment):staff restock (approved) -> baseline update; NO alert.
"""

from __future__ import annotations

from dataclasses import dataclass

from storeguard_contracts import AnomalyEvent, EventType

from storeguard_shelf.model import ShelfRules, ShelfTick
from storeguard_shelf.monitor import ShelfMonitor

STORE_ID = "store_demo_01"
CAMERA_ID = "cam_shelf_01"
ZONE_ID = "zone_shelf_01_display"


def _tick(t: float, present: bool, **kw: object) -> ShelfTick:
    return ShelfTick(t=t, zone_id=ZONE_ID, camera_id=CAMERA_ID, product_present=present, **kw)  # type: ignore[arg-type]


def scenario_removal() -> list[ShelfTick]:
    ticks = [_tick(float(t), True) for t in range(0, 5)]  # baseline (5 obs)
    ticks.append(_tick(5.0, True, person_interaction=True, track_ref="trk_s1"))
    ticks.append(_tick(6.0, False, person_interaction=True, track_ref="trk_s1"))
    ticks += [_tick(float(t), False) for t in range(7, 10)]  # absent -> fires at t=9
    return ticks


def scenario_occlusion() -> list[ShelfTick]:
    ticks = [_tick(float(t), True) for t in range(0, 5)]  # baseline
    # Shopper blocks the shelf: occluded + apparently absent.
    ticks += [_tick(float(t), False, occluded=True) for t in range(5, 10)]
    return ticks


def scenario_replenishment() -> list[ShelfTick]:
    ticks = [_tick(float(t), True) for t in range(0, 5)]  # baseline
    ticks += [_tick(5.0, False), _tick(6.0, False)]  # staff removes stock (short)
    ticks.append(_tick(7.0, True, approved_replenishment=True))  # authorized restock
    ticks += [_tick(8.0, True), _tick(9.0, True)]
    return ticks


@dataclass
class ScenarioResult:
    name: str
    expected_removal: bool
    events: list[AnomalyEvent]
    removal_count: int
    occlusion_count: int
    false_alerts: int


def run_scenario(
    name: str,
    ticks: list[ShelfTick],
    expected_removal: bool,
    rules: ShelfRules | None = None,
) -> ScenarioResult:
    mon = ShelfMonitor(STORE_ID, rules)
    events: list[AnomalyEvent] = []
    for t in ticks:
        events.extend(mon.process(t))
    removals = sum(
        e.event_type == EventType.SHELF_ITEM_REMOVED_UNRESOLVED for e in events
    )
    occl = sum(e.event_type == EventType.SHELF_OCCLUSION_REVIEW for e in events)
    # A false alert is a removal where none was warranted, or a duplicate beyond
    # the single expected candidate.
    false_alerts = max(0, removals - 1) if expected_removal else removals
    return ScenarioResult(name, expected_removal, events, removals, occl, false_alerts)


def run_all() -> list[ScenarioResult]:
    return [
        run_scenario("shelf-removal", scenario_removal(), expected_removal=True),
        run_scenario("shelf-occlusion", scenario_occlusion(), expected_removal=False),
        run_scenario(
            "shelf-replenishment", scenario_replenishment(), expected_removal=False
        ),
    ]


def total_false_alerts(results: list[ScenarioResult]) -> int:
    return sum(r.false_alerts for r in results)
