"""Health endpoint."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from storeguard_api import PHASE, __version__

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    phase: str
    simulated_data: bool
    time: datetime


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="storeguard-api",
        version=__version__,
        phase=PHASE,
        simulated_data=True,
        time=datetime.now(tz=UTC),
    )
