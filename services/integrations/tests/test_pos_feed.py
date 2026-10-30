"""Tests for the POS feed adapter: delivery timing, health, correlation keys."""

from __future__ import annotations

import pytest
from storeguard_contracts import ScanEvent

from storeguard_integrations.pos_feed import (
    PosFeed,
    SimulatedPosFeed,
    validate_message,
)
from storeguard_integrations.simulated import simulate_scan_event


def test_simulated_feed_is_a_posfeed() -> None:
    assert isinstance(SimulatedPosFeed("t", "s"), PosFeed)


def test_message_delivered_after_delay_and_only_once() -> None:
    feed = SimulatedPosFeed("term_01", "sess_01").add_scan(
        "SKU-1", occurred_at_s=1.0, delivery_delay_s=0.5
    )
    assert feed.drain(1.0) == []  # not yet delivered
    delivered = feed.drain(2.0)
    assert len(delivered) == 1
    assert delivered[0].lateness_s == pytest.approx(0.5)
    assert feed.drain(3.0) == []  # already drained


def test_delivered_message_carries_correlation_keys() -> None:
    feed = SimulatedPosFeed("term_01", "sess_01").add_scan("SKU-1", 0.0)
    msg = feed.drain(0.0)[0].message
    assert isinstance(msg, ScanEvent)
    assert msg.terminal_id == "term_01"
    assert msg.session_id == "sess_01"
    assert msg.simulated is True


def test_down_feed_is_unavailable_and_delivers_nothing() -> None:
    feed = SimulatedPosFeed("t", "s", available=False).add_scan("SKU-1", 0.0)
    assert feed.available(5.0) is False
    assert feed.drain(10.0) == []


def test_degraded_window() -> None:
    feed = SimulatedPosFeed("t", "s", degraded_window=(2.0, 6.0))
    assert feed.degraded(1.0) is False
    assert feed.degraded(3.0) is True
    assert feed.degraded(7.0) is False


def test_validate_accepts_real_contract_and_rejects_missing_key() -> None:
    validate_message(simulate_scan_event("t", "s", "SKU-1"))

    class _Bad:
        terminal_id = "t"
        session_id = ""  # missing correlation key
        occurred_at = None

    with pytest.raises(ValueError):
        validate_message(_Bad())
