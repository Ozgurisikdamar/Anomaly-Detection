"""Self-checkout endpoints (SIMULATED feeds)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from storeguard_contracts import CheckoutSession

from storeguard_api.deps import get_repository
from storeguard_api.repository import InMemoryRepository, NotFoundError

router = APIRouter()


@router.get("/checkouts", response_model=list[CheckoutSession], tags=["checkouts"])
def list_checkouts(
    repo: InMemoryRepository = Depends(get_repository),
) -> list[CheckoutSession]:
    return repo.list_checkouts()


@router.get(
    "/checkouts/{terminal_id}/state",
    response_model=CheckoutSession,
    tags=["checkouts"],
)
def checkout_state(
    terminal_id: str,
    repo: InMemoryRepository = Depends(get_repository),
) -> CheckoutSession:
    try:
        return repo.get_checkout(terminal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="terminal not found") from exc
