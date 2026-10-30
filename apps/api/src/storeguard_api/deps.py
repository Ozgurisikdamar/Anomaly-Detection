"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from storeguard_api.event_bus import EventBus
from storeguard_api.evidence import EvidenceStore


def get_repository(request: Request) -> Any:
    """Return the process-wide repository (in-memory seed or SQL-backed)."""
    return request.app.state.repository


def get_event_bus(request: Request) -> EventBus:
    """Return the process-wide realtime event bus."""
    return request.app.state.event_bus  # type: ignore[no-any-return]


def get_evidence_store(request: Request) -> EvidenceStore:
    """Return the process-wide evidence media store / URL signer."""
    return request.app.state.evidence_store  # type: ignore[no-any-return]
