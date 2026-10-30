"""Stores and cameras endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from storeguard_contracts import Camera, CameraStreamStatus, Store

from storeguard_api.deps import get_repository
from storeguard_api.repository import InMemoryRepository, NotFoundError

router = APIRouter()


@router.get("/stores", response_model=list[Store], tags=["stores"])
def list_stores(repo: InMemoryRepository = Depends(get_repository)) -> list[Store]:
    return repo.list_stores()


@router.get("/cameras", response_model=list[Camera], tags=["cameras"])
def list_cameras(
    store_id: str | None = None,
    repo: InMemoryRepository = Depends(get_repository),
) -> list[Camera]:
    return repo.list_cameras(store_id=store_id)


@router.get(
    "/cameras/{camera_id}/status",
    response_model=CameraStreamStatus,
    tags=["cameras"],
)
def camera_status(
    camera_id: str,
    repo: InMemoryRepository = Depends(get_repository),
) -> CameraStreamStatus:
    try:
        return repo.get_camera_status(camera_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="camera not found") from exc
