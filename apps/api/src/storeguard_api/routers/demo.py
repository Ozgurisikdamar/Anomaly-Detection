"""Demo-only scenario endpoint.

Returns a deterministic SIMULATED description of the roadmap demo scenarios
(section 5). Phase 0 does not execute any vision/ML — this only returns the
scripted scenario metadata so the UI can present the demo catalog.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

_SCENARIOS: dict[str, dict[str, str]] = {
    "shelf-removal": {
        "title": "Shelf item removed (unresolved)",
        "expected_event": "SHELF_ITEM_REMOVED_UNRESOLVED",
    },
    "shelf-occlusion": {
        "title": "Shelf occlusion — no removal alleged",
        "expected_event": "SHELF_OCCLUSION_REVIEW",
    },
    "sco-normal": {
        "title": "Self-checkout normal — paid, no alert",
        "expected_event": "NONE",
    },
    "sco-non-scan": {
        "title": "Self-checkout item not scanned (healthy POS)",
        "expected_event": "ITEM_PLACED_NOT_SCANNED",
    },
    "sco-feed-missing": {
        "title": "Self-checkout scanner feed unavailable",
        "expected_event": "TRANSACTION_DATA_MISSING",
    },
    "sco-scale-mismatch": {
        "title": "Weight mismatch review",
        "expected_event": "SCALE_MISMATCH_REVIEW",
    },
}


class ScenarioRunResponse(BaseModel):
    scenario_id: str
    title: str
    expected_event: str
    status: str = "scripted"
    simulated: bool = True
    note: str = "Phase 0 scaffold: no vision/ML executed. Scenario metadata only."


@router.post(
    "/demo/scenarios/{scenario_id}/run",
    response_model=ScenarioRunResponse,
    tags=["demo"],
)
def run_scenario(scenario_id: str) -> ScenarioRunResponse:
    spec = _SCENARIOS.get(scenario_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="unknown scenario")
    return ScenarioRunResponse(
        scenario_id=scenario_id,
        title=spec["title"],
        expected_event=spec["expected_event"],
    )
