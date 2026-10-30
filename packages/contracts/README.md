# StoreGuard shared contracts

Shared data contracts for the core entities and the anomaly **event contract**
(roadmap section 3), used by the backend, web dashboard and mobile app.

## Source of truth

- **Python / Pydantic** — `python/src/storeguard_contracts/` is the **source of
  truth**. Validation, defaults and invariants live here.
- **TypeScript** — `ts/index.ts` is a **hand-maintained mirror** of the same
  shapes for the web and mobile clients. Enum string values and field names
  must match the Pydantic models exactly.

Automatic generation of the TS types from the Pydantic schema is a Phase 7
(hardening) item; until then the two are kept in sync by hand and a contract
test (`apps/api/tests/test_contracts.py`) guards the invariants on the Python
side.

## Invariants encoded

- `AnomalyEvent.human_review_required` defaults to `True`.
- Event types are **neutral and observable** — `*_UNRESOLVED`, `*_REVIEW`,
  `*_DATA_MISSING`, `*_UNKNOWN`. No type asserts theft or intent.
- Integration-derived signals (`ScanEvent`, `ScaleEvent`, `TransactionEvent`)
  and `CheckoutSession` carry `simulated` — in Phase 0 these are always `True`.
- No field identifies a person. `track_refs` are ephemeral, camera-local
  pseudonymous IDs only.
- Missing integration data is surfaced via `missing_data_flags` and must drive a
  `TRANSACTION_DATA_MISSING` / `TRANSACTION_UNKNOWN` event, never a violation.

## Install (Python)

Installed editable into the shared backend virtualenv; see the root `Makefile`
(`make setup`) and `requirements-dev.txt`.
