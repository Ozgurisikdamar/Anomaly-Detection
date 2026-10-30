"""StoreGuard shared data contracts.

This package is the single source of truth for the core entities and the
anomaly event contract. The TypeScript types under ``packages/contracts/ts``
mirror these shapes and are kept in sync by hand.

Product invariants enforced by these contracts:
- Events describe *observable operational anomalies*, never criminal intent.
- ``AnomalyEvent.human_review_required`` defaults to ``True`` and cannot be
  silently disabled.
- Integration-derived signals (POS/scanner/scale) carry ``simulated`` so demo
  data is never confused with a real integration.
- Missing integration data is represented explicitly and must map to an
  ``UNKNOWN`` / ``*_DATA_MISSING`` event, never to a violation.
"""

from storeguard_contracts.checkout import (
    CheckoutSession,
    ScaleEvent,
    ScanEvent,
    TransactionEvent,
)
from storeguard_contracts.entities import (
    Camera,
    CameraStreamStatus,
    CameraZone,
    Store,
)
from storeguard_contracts.enums import (
    CameraStreamState,
    CheckoutState,
    EventStatus,
    EventType,
    ReviewDecision,
    Severity,
    ZoneType,
)
from storeguard_contracts.events import (
    AnomalyEvent,
    ConfidenceComponents,
    EvidenceRef,
    ReviewOutcome,
)

__all__ = [
    "AnomalyEvent",
    "Camera",
    "CameraStreamState",
    "CameraStreamStatus",
    "CameraZone",
    "CheckoutSession",
    "CheckoutState",
    "ConfidenceComponents",
    "EventStatus",
    "EventType",
    "EvidenceRef",
    "ReviewDecision",
    "ReviewOutcome",
    "ScaleEvent",
    "ScanEvent",
    "Severity",
    "Store",
    "TransactionEvent",
    "ZoneType",
]

__version__ = "0.1.0"
