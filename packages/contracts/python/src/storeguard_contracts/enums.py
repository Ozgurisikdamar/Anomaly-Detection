"""Enumerations for the StoreGuard contracts.

Event-type names are deliberately neutral and describe observable states
("UNRESOLVED", "NOT_SCANNED", "REVIEW", "MISSING"). They never assert theft,
intent, or guilt. Keep these identifiers in sync with the TypeScript mirror.
"""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    """Alert severity. Never a statement about a person, only review priority."""

    INFO = "INFO"
    REVIEW = "REVIEW"
    HIGH_REVIEW = "HIGH_REVIEW"


class EventStatus(str, Enum):
    """Lifecycle of an anomaly event in the human-review queue."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class EventType(str, Enum):
    """Observable operational anomaly types (roadmap sections 4.A / 4.B).

    These are *not* accusations. Anything that could be legitimate
    (occlusion, replenishment, missing integration data) maps to an
    ``*_UNRESOLVED``, ``*_REVIEW``, or ``*_MISSING`` / ``*_UNKNOWN`` type.
    """

    # Shelf / aisle
    SHELF_ITEM_REMOVED_UNRESOLVED = "SHELF_ITEM_REMOVED_UNRESOLVED"
    SHELF_OCCLUSION_REVIEW = "SHELF_OCCLUSION_REVIEW"
    # Self-checkout
    ITEM_PLACED_NOT_SCANNED = "ITEM_PLACED_NOT_SCANNED"
    ITEM_MOVED_UNRESOLVED = "ITEM_MOVED_UNRESOLVED"
    SCALE_MISMATCH_REVIEW = "SCALE_MISMATCH_REVIEW"
    TRANSACTION_RECONCILIATION_REQUIRED = "TRANSACTION_RECONCILIATION_REQUIRED"
    # Explicit missing / unknown states — never a violation
    TRANSACTION_DATA_MISSING = "TRANSACTION_DATA_MISSING"
    TRANSACTION_UNKNOWN = "TRANSACTION_UNKNOWN"


class ReviewDecision(str, Enum):
    """Outcome of a human review. Describes the event, not legal guilt."""

    CONFIRMED_OPERATIONAL_ANOMALY = "CONFIRMED_OPERATIONAL_ANOMALY"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    RESOLVED_BY_STAFF = "RESOLVED_BY_STAFF"


class CameraStreamState(str, Enum):
    """Health of a camera stream. UNKNOWN when the reader cannot be trusted."""

    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class ZoneType(str, Enum):
    """Polygon/ROI zone categories for shelf and checkout cameras."""

    SHELF_DISPLAY = "SHELF_DISPLAY"
    PICKUP_INTERACTION = "PICKUP_INTERACTION"
    OCCLUSION_UNKNOWN = "OCCLUSION_UNKNOWN"
    AISLE_EXIT = "AISLE_EXIT"
    SCAN_AREA = "SCAN_AREA"
    BAGGING_SCALE_AREA = "BAGGING_SCALE_AREA"
    BASKET_CART_AREA = "BASKET_CART_AREA"
    EXIT_SIDE = "EXIT_SIDE"


class CheckoutState(str, Enum):
    """Self-checkout terminal state machine (roadmap section 4.B)."""

    IDLE = "IDLE"
    SESSION_ACTIVE = "SESSION_ACTIVE"
    ITEM_PRESENTED = "ITEM_PRESENTED"
    SCAN_OBSERVED = "SCAN_OBSERVED"
    BAGGING_OBSERVED = "BAGGING_OBSERVED"
    SCALE_STABLE = "SCALE_STABLE"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    SESSION_CLOSED = "SESSION_CLOSED"
