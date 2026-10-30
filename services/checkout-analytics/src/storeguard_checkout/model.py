"""Rules and per-terminal state for the checkout monitor."""

from __future__ import annotations

from dataclasses import dataclass, field

from storeguard_contracts import (
    CheckoutState,
    ScaleEvent,
    ScanEvent,
    TransactionEvent,
)


@dataclass(frozen=True)
class CheckoutRules:
    scan_match_window_s: float = 8.0
    scale_tolerance_g: float = 15.0
    # A POS/scanner message delivered later than this (relative to the item
    # observation) is treated as a *degraded* feed: the outcome is UNKNOWN /
    # data-missing, never a non-scan. Configurable per terminal/SKU later.
    feed_lateness_window_s: float = 5.0


@dataclass
class PendingItem:
    """An item observed in the bagging zone awaiting scan reconciliation."""

    item_id: str
    t: float
    expected_sku: str | None = None
    matched: bool = False
    voided: bool = False
    alerted: bool = False
    moved_out: bool = False


@dataclass
class TerminalState:
    terminal_id: str
    camera_id: str
    store_id: str
    session_id: str | None = None
    state: CheckoutState = CheckoutState.IDLE
    scanner_available: bool = True
    camera_ok: bool = True
    # A healthy feed is available AND on time. A late/delayed POS feed sets this
    # (correlation layer decides lateness) so the FSM cannot raise a non-scan.
    feed_degraded: bool = False
    pending: list[PendingItem] = field(default_factory=list)
    # Scans seen but not yet matched to a bagging item (sku, t).
    unmatched_scans: list[tuple[str, float]] = field(default_factory=list)
    scans: list[ScanEvent] = field(default_factory=list)
    scale_events: list[ScaleEvent] = field(default_factory=list)
    transaction_events: list[TransactionEvent] = field(default_factory=list)
    feed_was_unavailable: bool = False
    updated_at: float = 0.0
