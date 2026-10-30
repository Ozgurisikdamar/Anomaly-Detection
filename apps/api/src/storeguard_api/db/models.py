"""SQLAlchemy ORM models for the core entities (roadmap section 3).

These are the persistence counterpart of the Pydantic contracts. They are not
used by the Phase 0 request path (which runs from the in-memory seed) but exist
so the schema is explicit and the initial Alembic migration is meaningful.
No identity/biometric columns exist by design.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = "stores"

    store_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(String, default="Europe/Istanbul")

    cameras: Mapped[list[Camera]] = relationship(back_populates="store")


class Camera(Base):
    __tablename__ = "cameras"

    camera_id: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.store_id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    source_kind: Mapped[str] = mapped_column(String, default="synthetic")

    store: Mapped[Store] = relationship(back_populates="cameras")
    zones: Mapped[list[CameraZone]] = relationship(back_populates="camera")


class CameraZone(Base):
    __tablename__ = "camera_zones"

    zone_id: Mapped[str] = mapped_column(String, primary_key=True)
    camera_id: Mapped[str] = mapped_column(
        ForeignKey("cameras.camera_id"), nullable=False
    )
    zone_type: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    # Polygon stored as JSON text for portability in the demo.
    polygon_json: Mapped[str] = mapped_column(Text, default="[]")

    camera: Mapped[Camera] = relationship(back_populates="zones")


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(String, nullable=False)
    camera_id: Mapped[str] = mapped_column(String, nullable=False)
    zone_id: Mapped[str | None] = mapped_column(String, nullable=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False, default="REVIEW")
    status: Mapped[str] = mapped_column(String, nullable=False, default="OPEN")

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    tracker_version: Mapped[str | None] = mapped_column(String, nullable=True)
    rule_version: Mapped[str | None] = mapped_column(String, nullable=True)

    explanation: Mapped[str] = mapped_column(Text, default="")
    # JSON-encoded lists/objects kept simple for the demo schema.
    reason_codes_json: Mapped[str] = mapped_column(Text, default="[]")
    missing_data_flags_json: Mapped[str] = mapped_column(Text, default="[]")
    confidence_json: Mapped[str] = mapped_column(Text, default="{}")
    track_refs_json: Mapped[str] = mapped_column(Text, default="[]")

    human_review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    simulated: Mapped[bool] = mapped_column(Boolean, default=True)


class CheckoutSessionRow(Base):
    __tablename__ = "checkout_sessions"

    terminal_id: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str] = mapped_column(String, default="IDLE")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    simulated: Mapped[bool] = mapped_column(Boolean, default=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    target: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
