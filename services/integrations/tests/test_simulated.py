"""Tests that integration simulators always flag their output as simulated."""

from __future__ import annotations

from storeguard_integrations.simulated import (
    simulate_scale_event,
    simulate_scan_event,
    simulate_transaction_event,
)


def test_scan_is_simulated() -> None:
    scan = simulate_scan_event("t1", "s1", "SKU-1001")
    assert scan.simulated is True
    assert scan.scan_id.startswith("scan_")


def test_scale_is_simulated() -> None:
    scale = simulate_scale_event(
        "t1", "s1", stable_weight_g=320.0, expected_weight_g=325.0
    )
    assert scale.simulated is True


def test_transaction_is_simulated() -> None:
    txn = simulate_transaction_event("t1", "s1", kind="completed")
    assert txn.simulated is True
