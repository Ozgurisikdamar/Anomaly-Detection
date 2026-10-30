"""Evidence media: pipeline upload + authenticated short-lived retrieval.

The pipeline (a separate process) uploads an event's evidence clip here; clients
only ever receive a short-lived signed URL (minted when an event is read) and
fetch the bytes through the GET endpoint, which verifies the token. No raw
filesystem path or RTSP credential is ever exposed.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from storeguard_api.deps import get_evidence_store, get_repository
from storeguard_api.evidence import EvidenceStore
from storeguard_api.repository import NotFoundError

router = APIRouter()


@router.post("/events/{event_id}/evidence", status_code=201, tags=["evidence"])
def upload_evidence(
    event_id: str,
    file: UploadFile = File(...),
    repo: Any = Depends(get_repository),
    store: EvidenceStore = Depends(get_evidence_store),
) -> dict[str, str | bool]:
    """Store an evidence clip for an event's first EvidenceRef (pipeline → API)."""
    try:
        event = repo.get_event(event_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="event not found") from exc
    if not event.evidence:
        raise HTTPException(status_code=400, detail="event has no evidence reference")
    evidence_id = event.evidence[0].evidence_id
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty evidence upload")
    store.save(evidence_id, data)
    return {"evidence_id": evidence_id, "stored": True}


@router.get("/evidence/{evidence_id}", tags=["evidence"])
def get_evidence(
    evidence_id: str,
    exp: int,
    sig: str,
    store: EvidenceStore = Depends(get_evidence_store),
) -> FileResponse:
    """Serve evidence bytes iff the short-lived signed token verifies."""
    if not store.verify(evidence_id, exp, sig):
        raise HTTPException(status_code=403, detail="invalid or expired evidence token")
    if not store.exists(evidence_id):
        raise HTTPException(status_code=404, detail="evidence not found")
    return FileResponse(
        store.path(evidence_id),
        media_type="image/gif",
        headers={"Cache-Control": "private, max-age=60"},
    )
