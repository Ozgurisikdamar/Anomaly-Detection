"""Deterministic replay scenarios 4–8 + P2 correlation scenarios (roadmap §5).

4  normal          -> no alert
5  non-scan        -> ITEM_PLACED_NOT_SCANNED (healthy POS feed)
6  feed missing    -> TRANSACTION_DATA_MISSING (UNKNOWN), never a non-scan
7  weight mismatch -> SCALE_MISMATCH_REVIEW
8  void/removal    -> resolved, no alert
9  delayed feed    -> TRANSACTION_DATA_MISSING (UNKNOWN), never a non-scan
10 attendant override -> resolved, no alert
11 multiple items  -> exactly one non-scan for the single unscanned item
12 session reset   -> abandoned item reconciles; no non-scan leaks to next session

All POS/scanner/scale signals are SIMULATED.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from storeguard_contracts import AnomalyEvent
from storeguard_integrations.simulated import (
    simulate_scale_event,
    simulate_scan_event,
    simulate_transaction_event,
)

from storeguard_checkout.model import CheckoutRules
from storeguard_checkout.monitor import CheckoutMonitor

STORE = "store_demo_01"
CAM = "cam_sco_01"
TERM = "term_01"
SESS = "sess_01"
WINDOW = CheckoutRules().scan_match_window_s


@dataclass
class ScenarioResult:
    name: str
    events: list[AnomalyEvent]
    types: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.types = [e.event_type.value for e in self.events]


def scenario_normal() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_scan(simulate_scan_event(TERM, SESS, "SKU-1001"))
    ev += m.observe_bagging_item(
        TERM, SESS, "item1", t=2, camera_id=CAM, expected_sku="SKU-1001"
    )
    ev += m.observe_scale(
        simulate_scale_event(TERM, SESS, stable_weight_g=330.0, expected_weight_g=325.0)
    )
    ev += m.observe_transaction(
        simulate_transaction_event(TERM, SESS, "payment_authorized")
    )
    ev += m.observe_transaction(simulate_transaction_event(TERM, SESS, "completed"))
    ev += m.finalize(TERM, t=6)
    return ScenarioResult("sco-normal", ev)


def scenario_non_scan() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=1, camera_id=CAM)  # no scan
    ev += m.advance(TERM, t=1 + WINDOW + 1)  # window expires, feed healthy
    return ScenarioResult("sco-non-scan", ev)


def scenario_feed_missing() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    m.set_scanner_available(TERM, False)  # scanner/POS feed down
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=1, camera_id=CAM)
    ev += m.advance(TERM, t=1 + WINDOW + 1)  # must NOT be a non-scan
    return ScenarioResult("sco-feed-missing", ev)


def scenario_weight_mismatch() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_scan(simulate_scan_event(TERM, SESS, "SKU-2002"))
    ev += m.observe_bagging_item(
        TERM, SESS, "item1", t=2, camera_id=CAM, expected_sku="SKU-2002"
    )
    ev += m.observe_scale(
        simulate_scale_event(TERM, SESS, stable_weight_g=500.0, expected_weight_g=325.0)
    )
    ev += m.observe_transaction(simulate_transaction_event(TERM, SESS, "completed"))
    ev += m.finalize(TERM, t=5)
    return ScenarioResult("sco-weight-mismatch", ev)


def scenario_void() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_scan(simulate_scan_event(TERM, SESS, "SKU-1001"))
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=2, camera_id=CAM)
    ev += m.observe_transaction(
        simulate_transaction_event(TERM, SESS, "void")
    )  # authorized void
    ev += m.observe_item_moved_out(TERM, SESS, "item1", t=3)  # item returned to cart
    ev += m.observe_transaction(simulate_transaction_event(TERM, SESS, "completed"))
    ev += m.finalize(TERM, t=4)
    return ScenarioResult("sco-void", ev)


def scenario_delayed_feed() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    m.set_feed_degraded(TERM)  # POS/scanner delivery lagging (late feed)
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=1, camera_id=CAM)
    ev += m.advance(TERM, t=1 + WINDOW + 1)  # late feed must NOT be a non-scan
    return ScenarioResult("sco-delayed-feed", ev)


def scenario_attendant_override() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=2, camera_id=CAM)  # no scan yet
    ev += m.observe_transaction(
        simulate_transaction_event(TERM, SESS, "attendant_override")
    )  # staff resolves the item
    ev += m.observe_transaction(simulate_transaction_event(TERM, SESS, "completed"))
    ev += m.finalize(TERM, t=4)
    return ScenarioResult("sco-attendant-override", ev)


def scenario_multiple_items() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=1, camera_id=CAM)
    ev += m.observe_bagging_item(TERM, SESS, "item2", t=1, camera_id=CAM)
    ev += m.observe_bagging_item(TERM, SESS, "item3", t=1, camera_id=CAM)
    ev += m.observe_scan(simulate_scan_event(TERM, SESS, "SKU-A"))  # matches item1
    ev += m.observe_scan(simulate_scan_event(TERM, SESS, "SKU-B"))  # matches item2
    ev += m.advance(TERM, t=1 + WINDOW + 1)  # item3 unscanned, healthy feed
    return ScenarioResult("sco-multiple-items", ev)


def scenario_session_reset() -> ScenarioResult:
    m = CheckoutMonitor(STORE)
    ev: list[AnomalyEvent] = []
    m.start_session(TERM, SESS, CAM, t=0)
    ev += m.observe_bagging_item(TERM, SESS, "item1", t=1, camera_id=CAM)  # no scan
    ev += m.reset_session(TERM, t=2)  # terminal abandoned/reset before window expiry
    # A fresh session with a normally scanned item must be clean.
    m.start_session(TERM, "sess_02", CAM, t=3)
    ev += m.observe_scan(simulate_scan_event(TERM, "sess_02", "SKU-X"))
    ev += m.observe_bagging_item(TERM, "sess_02", "item2", t=4, camera_id=CAM)
    ev += m.observe_transaction(
        simulate_transaction_event(TERM, "sess_02", "completed")
    )
    ev += m.finalize(TERM, t=6)
    return ScenarioResult("sco-session-reset", ev)


def run_all() -> list[ScenarioResult]:
    return [
        scenario_normal(),
        scenario_non_scan(),
        scenario_feed_missing(),
        scenario_weight_mismatch(),
        scenario_void(),
        scenario_delayed_feed(),
        scenario_attendant_override(),
        scenario_multiple_items(),
        scenario_session_reset(),
    ]


def non_scan_when_feed_unavailable(results: list[ScenarioResult]) -> int:
    """Critical safety metric: non-scan alerts emitted while the POS feed was down."""
    r = next((x for x in results if x.name == "sco-feed-missing"), None)
    return 0 if r is None else r.types.count("ITEM_PLACED_NOT_SCANNED")


def non_scan_on_unhealthy_feed(results: list[ScenarioResult]) -> int:
    """Non-scan alerts emitted on any unhealthy feed (unavailable OR delayed)."""
    unhealthy = {"sco-feed-missing", "sco-delayed-feed"}
    return sum(
        r.types.count("ITEM_PLACED_NOT_SCANNED") for r in results if r.name in unhealthy
    )
