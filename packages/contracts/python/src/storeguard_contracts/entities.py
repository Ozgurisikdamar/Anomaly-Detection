"""Core store / camera entities."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from storeguard_contracts.enums import CameraStreamState, ZoneType


class Store(BaseModel):
    """A physical store/site."""

    store_id: str
    name: str
    timezone: str = "Europe/Istanbul"


class CameraZone(BaseModel):
    """A polygon/ROI configured on a camera.

    ``polygon`` is a list of normalized ``[x, y]`` points in ``[0, 1]`` so the
    overlay renders independently of resolution.
    """

    zone_id: str
    camera_id: str
    zone_type: ZoneType
    label: str
    polygon: list[tuple[float, float]] = Field(default_factory=list)


class Camera(BaseModel):
    """A camera registered to a store. RTSP credentials are never exposed here."""

    camera_id: str
    store_id: str
    name: str
    kind: str = Field(description="e.g. 'shelf', 'checkout'")
    # Placeholder source descriptor; real RTSP URLs/credentials stay server-side.
    source_kind: str = Field(default="synthetic", description="synthetic | file | rtsp")
    zones: list[CameraZone] = Field(default_factory=list)


class CameraStreamStatus(BaseModel):
    """Health snapshot for a camera stream.

    All metrics are placeholders in Phase 0 and flagged ``simulated``. Real FPS
    and frame-age are measured in Phase 2.
    """

    camera_id: str
    state: CameraStreamState = CameraStreamState.UNKNOWN
    fps: float | None = None
    frame_age_ms: float | None = None
    last_frame_at: datetime | None = None
    reconnect_count: int = 0
    simulated: bool = True
