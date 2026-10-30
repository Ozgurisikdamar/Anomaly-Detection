"""POS / scanner / scale feed adapter interface + a SIMULATED implementation.

A checkout camera can observe an item in the bagging zone, but **video alone can
never assert that the item was scanned, weighed or voided** — that knowledge
exists only in the POS/scanner/scale integration. This module defines the
adapter the correlation layer consumes, so a real POS integration can later
replace the simulator behind the exact same interface and contract types.

Everything the ``SimulatedPosFeed`` emits carries ``simulated=True`` and is a
shared Pydantic contract (``ScanEvent`` / ``ScaleEvent`` / ``TransactionEvent``).
NOT a real integration.

Feed health has two independent signals the correlation layer must honour:

* ``available(now)`` — is the feed connected at all. A down feed means UNKNOWN.
* ``degraded(now)`` — is delivery lagging beyond tolerance (a heartbeat/lag
  signal, not clairvoyance about individual scans). A lagging feed is also
  UNKNOWN.

In both cases an unmatched bagging item must resolve to
``TRANSACTION_DATA_MISSING`` — never ``ITEM_PLACED_NOT_SCANNED``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias, runtime_checkable

from storeguard_contracts import ScaleEvent, ScanEvent, TransactionEvent

from storeguard_integrations.simulated import (
    simulate_scale_event,
    simulate_scan_event,
    simulate_transaction_event,
)

PosMessage: TypeAlias = ScanEvent | ScaleEvent | TransactionEvent


@dataclass
class DeliveredMessage:
    """A POS message as delivered to the correlation layer at a point in time."""

    message: PosMessage
    occurred_at_s: float
    delivered_at_s: float

    @property
    def lateness_s(self) -> float:
        return max(0.0, self.delivered_at_s - self.occurred_at_s)


def validate_message(msg: object) -> PosMessage:
    """Contract validation for any (real or simulated) feed message.

    A usable POS message must carry the correlation keys: ``terminal_id``,
    ``session_id`` and an ``occurred_at`` UTC timestamp. Raises ``ValueError``
    otherwise so a malformed real-feed adapter fails loudly.
    """
    for attr in ("terminal_id", "session_id", "occurred_at"):
        if getattr(msg, attr, None) in (None, ""):
            raise ValueError(f"POS message missing correlation key: {attr}")
    if not isinstance(msg, (ScanEvent, ScaleEvent, TransactionEvent)):
        raise TypeError(f"POS message is not a known contract type: {type(msg)!r}")
    return msg


@runtime_checkable
class PosFeed(Protocol):
    """Adapter a real or simulated POS/scanner/scale integration implements.

    The correlation layer drives the feed on a session clock (seconds from
    session start) so observations and messages share one timeline.
    """

    def available(self, now: float) -> bool:
        """Is the feed connected at ``now``."""

    def degraded(self, now: float) -> bool:
        """Is delivery lagging beyond tolerance at ``now`` (late/degraded)."""

    def drain(self, now: float) -> list[DeliveredMessage]:
        """Messages delivered at or before ``now`` and not yet returned."""


@dataclass
class _Scripted:
    occurred_at_s: float
    delivery_delay_s: float
    message: PosMessage

    @property
    def delivered_at_s(self) -> float:
        return self.occurred_at_s + self.delivery_delay_s


class SimulatedPosFeed:
    """A SIMULATED POS feed built from a scripted, time-stamped timeline.

    * ``available`` False models a down feed for the whole session.
    * ``degraded_window`` ``(from_s, until_s)`` models a delivery-lag outage in
      which the feed is up but lagging (``degraded`` True) — a late feed.
    * each message has a ``delivery_delay_s`` so a scan can be delivered later
      than it occurred.

    Not a real integration: every message carries ``simulated=True``.
    """

    def __init__(
        self,
        terminal_id: str,
        session_id: str,
        *,
        available: bool = True,
        degraded_window: tuple[float, float] | None = None,
    ) -> None:
        self.terminal_id = terminal_id
        self.session_id = session_id
        self._available = available
        self._degraded_window = degraded_window
        self._scripted: list[_Scripted] = []
        self._delivered: set[int] = set()

    # --- scripting -------------------------------------------------------
    def add_scan(
        self, sku: str, occurred_at_s: float, *, delivery_delay_s: float = 0.0
    ) -> SimulatedPosFeed:
        msg = simulate_scan_event(self.terminal_id, self.session_id, sku)
        self._scripted.append(_Scripted(occurred_at_s, delivery_delay_s, msg))
        return self

    def add_scale(
        self,
        occurred_at_s: float,
        *,
        stable_weight_g: float | None,
        expected_weight_g: float | None = None,
        delivery_delay_s: float = 0.0,
    ) -> SimulatedPosFeed:
        msg = simulate_scale_event(
            self.terminal_id,
            self.session_id,
            stable_weight_g=stable_weight_g,
            expected_weight_g=expected_weight_g,
        )
        self._scripted.append(_Scripted(occurred_at_s, delivery_delay_s, msg))
        return self

    def add_transaction(
        self, kind: str, occurred_at_s: float, *, delivery_delay_s: float = 0.0
    ) -> SimulatedPosFeed:
        msg = simulate_transaction_event(self.terminal_id, self.session_id, kind)
        self._scripted.append(_Scripted(occurred_at_s, delivery_delay_s, msg))
        return self

    # --- PosFeed ---------------------------------------------------------
    def available(self, now: float) -> bool:
        return self._available

    def degraded(self, now: float) -> bool:
        if self._degraded_window is None:
            return False
        lo, hi = self._degraded_window
        return lo <= now <= hi

    def drain(self, now: float) -> list[DeliveredMessage]:
        if not self._available:
            return []
        out: list[DeliveredMessage] = []
        for i, s in enumerate(self._scripted):
            if i in self._delivered or s.delivered_at_s > now:
                continue
            self._delivered.add(i)
            validate_message(s.message)
            out.append(DeliveredMessage(s.message, s.occurred_at_s, s.delivered_at_s))
        return out


# Re-export the contract types used by consumers that import from here.
__all__ = [
    "DeliveredMessage",
    "PosFeed",
    "PosMessage",
    "SimulatedPosFeed",
    "validate_message",
]
