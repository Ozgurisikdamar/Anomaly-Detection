"""Deterministic SIMULATED POS / scanner / scale event generators.

NOT a real integration. These exist so the demo has transaction signals to
reconcile against video observations. Video alone can never know an item was
scanned or weighed — that knowledge comes only from an integration, and here
that integration is faked.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from storeguard_contracts import ScaleEvent, ScanEvent, TransactionEvent


def _now() -> datetime:
    return datetime.now(tz=UTC)


def simulate_scan_event(
    terminal_id: str,
    session_id: str,
    sku: str,
    quantity: int = 1,
    occurred_at: datetime | None = None,
) -> ScanEvent:
    """Produce a SIMULATED scanner/POS scan."""
    return ScanEvent(
        scan_id=f"scan_{uuid4().hex[:8]}",
        terminal_id=terminal_id,
        session_id=session_id,
        sku=sku,
        quantity=quantity,
        occurred_at=occurred_at or _now(),
        simulated=True,
    )


def simulate_scale_event(
    terminal_id: str,
    session_id: str,
    stable_weight_g: float | None,
    expected_weight_g: float | None = None,
    placement: str = "placed",
    occurred_at: datetime | None = None,
) -> ScaleEvent:
    """Produce a SIMULATED scale reading."""
    return ScaleEvent(
        scale_id=f"scale_{uuid4().hex[:8]}",
        terminal_id=terminal_id,
        session_id=session_id,
        stable_weight_g=stable_weight_g,
        expected_weight_g=expected_weight_g,
        placement=placement,
        calibration_ok=True,
        occurred_at=occurred_at or _now(),
        simulated=True,
    )


def simulate_transaction_event(
    terminal_id: str,
    session_id: str,
    kind: str,
    occurred_at: datetime | None = None,
) -> TransactionEvent:
    """Produce a SIMULATED terminal/transaction lifecycle event."""
    return TransactionEvent(
        transaction_id=f"txn_{uuid4().hex[:8]}",
        terminal_id=terminal_id,
        session_id=session_id,
        kind=kind,
        occurred_at=occurred_at or _now(),
        simulated=True,
    )
