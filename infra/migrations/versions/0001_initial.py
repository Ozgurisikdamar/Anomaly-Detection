"""initial core-entity schema

Mirrors storeguard_api.db.models. No identity/biometric columns by design.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("store_id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("timezone", sa.String(), nullable=False, server_default="Europe/Istanbul"),
    )
    op.create_table(
        "cameras",
        sa.Column("camera_id", sa.String(), primary_key=True),
        sa.Column("store_id", sa.String(), sa.ForeignKey("stores.store_id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("source_kind", sa.String(), nullable=False, server_default="synthetic"),
    )
    op.create_table(
        "camera_zones",
        sa.Column("zone_id", sa.String(), primary_key=True),
        sa.Column("camera_id", sa.String(), sa.ForeignKey("cameras.camera_id"), nullable=False),
        sa.Column("zone_type", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("polygon_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.create_table(
        "anomaly_events",
        sa.Column("event_id", sa.String(), primary_key=True),
        sa.Column("store_id", sa.String(), nullable=False),
        sa.Column("camera_id", sa.String(), nullable=False),
        sa.Column("zone_id", sa.String(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False, server_default="REVIEW"),
        sa.Column("status", sa.String(), nullable=False, server_default="OPEN"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(), nullable=True),
        sa.Column("tracker_version", sa.String(), nullable=True),
        sa.Column("rule_version", sa.String(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("reason_codes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("missing_data_flags_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("confidence_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("track_refs_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("human_review_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
    )
    op.create_table(
        "checkout_sessions",
        sa.Column("terminal_id", sa.String(), primary_key=True),
        sa.Column("store_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=False, server_default="IDLE"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("checkout_sessions")
    op.drop_table("anomaly_events")
    op.drop_table("camera_zones")
    op.drop_table("cameras")
    op.drop_table("stores")
