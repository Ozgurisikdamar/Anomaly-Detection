"""The anomaly event contract (roadmap section 3)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from storeguard_contracts.enums import EventStatus, EventType, ReviewDecision, Severity


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class ConfidenceComponents(BaseModel):
    """Multidimensional confidence. A single scalar score is intentionally avoided.

    Each component is in ``[0, 1]`` or ``None`` when the signal is unavailable
    (which must be surfaced, not silently treated as high confidence).
    """

    detector: float | None = None
    track_quality: float | None = None
    zone_certainty: float | None = None
    pos_synchronization: float | None = None
    rule_evidence: float | None = None


class EvidenceRef(BaseModel):
    """Reference to an evidence clip. Never a raw storage path on the wire."""

    evidence_id: str
    kind: str = "clip"
    # Resolved to a short-lived authenticated URL by the API; not a disk path.
    available: bool = False


class ReviewOutcome(BaseModel):
    """A recorded human-review decision."""

    decision: ReviewDecision
    reviewer: str
    note: str | None = None
    decided_at: datetime = Field(default_factory=_utcnow)


class AnomalyEvent(BaseModel):
    """An observable operational anomaly requiring human review.

    Invariants:
    - ``human_review_required`` is always True in this demo.
    - ``missing_data_flags`` lists signals that were unavailable; when a rule
      depends on a missing signal the ``event_type`` must be a
      ``*_DATA_MISSING`` / ``*_UNKNOWN`` type, never a violation.
    - No field identifies a person. ``track_refs`` are ephemeral, camera-local
      pseudonymous IDs only.
    """

    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    store_id: str
    camera_id: str
    zone_id: str | None = None
    event_type: EventType
    severity: Severity = Severity.REVIEW
    status: EventStatus = EventStatus.OPEN

    occurred_at: datetime = Field(default_factory=_utcnow)
    detected_at: datetime = Field(default_factory=_utcnow)
    created_at: datetime = Field(default_factory=_utcnow)

    # Ephemeral, camera-local pseudonymous track references (not identity).
    track_refs: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    # Versioning for reproducibility / audit.
    model_version: str | None = None
    tracker_version: str | None = None
    rule_version: str | None = None

    confidence: ConfidenceComponents = Field(default_factory=ConfidenceComponents)
    reason_codes: list[str] = Field(default_factory=list)
    missing_data_flags: list[str] = Field(default_factory=list)

    # Human-readable explanation shown in the review UI.
    explanation: str = ""

    human_review_required: bool = True
    review: ReviewOutcome | None = None

    # True when any contributing signal came from a simulated integration.
    simulated: bool = True
