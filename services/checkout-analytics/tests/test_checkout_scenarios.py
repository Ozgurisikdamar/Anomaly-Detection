"""Replay tests for self-checkout scenarios 4–8 (no ML stack)."""

from __future__ import annotations

from storeguard_checkout.scenarios import (
    non_scan_on_unhealthy_feed,
    non_scan_when_feed_unavailable,
    run_all,
    scenario_attendant_override,
    scenario_delayed_feed,
    scenario_feed_missing,
    scenario_multiple_items,
    scenario_non_scan,
    scenario_normal,
    scenario_session_reset,
    scenario_void,
    scenario_weight_mismatch,
)


def test_normal_no_alert() -> None:
    assert scenario_normal().types == []


def test_non_scan_with_healthy_feed() -> None:
    r = scenario_non_scan()
    assert r.types == ["ITEM_PLACED_NOT_SCANNED"]
    assert r.events[0].severity.value == "HIGH_REVIEW"
    assert r.events[0].human_review_required is True


def test_feed_missing_is_unknown_never_non_scan() -> None:
    r = scenario_feed_missing()
    # The core safety rule: no non-scan when the POS feed is unavailable.
    assert "ITEM_PLACED_NOT_SCANNED" not in r.types
    assert r.types == ["TRANSACTION_DATA_MISSING"]
    assert "scanner_feed_unavailable" in r.events[0].missing_data_flags


def test_weight_mismatch_review() -> None:
    r = scenario_weight_mismatch()
    assert r.types == ["SCALE_MISMATCH_REVIEW"]
    # Never an accusation.
    assert "thief" not in r.events[0].explanation.lower()


def test_void_resolved_no_alert() -> None:
    assert scenario_void().types == []


def test_delayed_feed_is_unknown_never_non_scan() -> None:
    r = scenario_delayed_feed()
    # A late/degraded feed is UNKNOWN, exactly like a missing one — never a non-scan.
    assert "ITEM_PLACED_NOT_SCANNED" not in r.types
    assert r.types == ["TRANSACTION_DATA_MISSING"]
    assert "scanner_feed_delayed" in r.events[0].missing_data_flags


def test_attendant_override_resolved_no_alert() -> None:
    assert scenario_attendant_override().types == []


def test_multiple_items_exactly_one_non_scan() -> None:
    r = scenario_multiple_items()
    assert r.types.count("ITEM_PLACED_NOT_SCANNED") == 1
    assert len(r.events) == 1


def test_session_reset_no_non_scan_leak() -> None:
    r = scenario_session_reset()
    # The abandoned item reconciles for review; it must NEVER become a non-scan,
    # and nothing leaks into the fresh (normally scanned) session.
    assert "ITEM_PLACED_NOT_SCANNED" not in r.types
    assert r.types == ["TRANSACTION_RECONCILIATION_REQUIRED"]


def test_critical_metric_zero() -> None:
    results = run_all()
    assert non_scan_when_feed_unavailable(results) == 0
    # Stronger: zero non-scan across every unhealthy feed (unavailable OR delayed).
    assert non_scan_on_unhealthy_feed(results) == 0


def test_all_events_simulated_and_reviewable() -> None:
    for r in run_all():
        for e in r.events:
            assert e.simulated is True
            assert e.human_review_required is True
