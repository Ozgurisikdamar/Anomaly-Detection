# StoreGuard — Phase 4 Report

> Self-checkout MVP. A per-terminal state machine + reconciliation engine
> compares SIMULATED scanner/POS/scale signals with camera observations and
> emits observable anomalies only. Scenarios 4–8 pass deterministic replay tests,
> and the core safety rule holds: **no non-scan alert when the POS feed is
> unavailable**. Awaiting review before Phase 5.

- **Branch:** `feat/storeguard-demo-foundation`
- **Phase 4 commit:** `__PHASE4_SHA__`
- **Date:** 2026-10-30

## 1. What was built — `services/checkout-analytics`
`CheckoutMonitor` implements roadmap §4.B over the terminal state machine
(IDLE → SESSION_ACTIVE → SCAN_OBSERVED → BAGGING_OBSERVED → SCALE_STABLE →
PAYMENT_PENDING → PAID/SESSION_CLOSED):

- **B1 non-scan** — an item in the bagging zone with no matching scan within
  `scan_match_window_s` (8 s) becomes `ITEM_PLACED_NOT_SCANNED` **only** when the
  scanner/POS feed and camera are healthy. If the feed is unavailable/late →
  `TRANSACTION_DATA_MISSING` (UNKNOWN), **never** a non-scan alert.
- **B2 scale mismatch** — stable vs expected weight compared when both exist;
  outside tolerance (15 g) → `SCALE_MISMATCH_REVIEW` (produce lookup / stacking /
  tare / override, never theft). No telemetry → no mismatch alert.
- **B3 item moved** — item leaving the bagging zone with no transaction →
  `ITEM_MOVED_UNRESOLVED`.
- **B4 reconciliation** — unmatched items at close →
  `TRANSACTION_RECONCILIATION_REQUIRED`; missing/contradictory signals →
  `TRANSACTION_UNKNOWN`. Authorized voids resolve items with no alert.

Signals are produced by the SIMULATED `storeguard_integrations` generators
(`simulate_scan_event` / `simulate_scale_event` / `simulate_transaction_event`),
each flagged `simulated=True`. Emitted anomalies use the shared `AnomalyEvent`
contract (human_review_required = True).

## 2. Acceptance (roadmap §11, Phase 4)
| Criterion | Evidence |
|---|---|
| Checkout terminal state machine | `monitor.py` state transitions; `CheckoutSession` snapshot |
| Simulated scanner/POS/scale adapters | `storeguard_integrations.simulated` used throughout |
| Item detection + scan reconciliation window | B1 window matching; scenarios 4–6 |
| Weight mismatch + unavailable-integration behavior | B2 (scenario 7) + B1 feed-missing (scenario 6) |
| Scenarios 4–8 pass deterministic tests | 7 passing tests in `services/checkout-analytics/tests` |
| **Never emit non-scan when POS feed unavailable** | metric = **0** (below) |

## 3. Scenario replay results (actual `checkout-demo` output)
```
=== Self-checkout scenarios (replay, SIMULATED signals) ===
- sco-normal             -> [] (no alert — correct)
- sco-non-scan           -> ['ITEM_PLACED_NOT_SCANNED']   sev=HIGH_REVIEW
- sco-feed-missing       -> ['TRANSACTION_DATA_MISSING']  sev=INFO   (NOT a non-scan)
- sco-weight-mismatch    -> ['SCALE_MISMATCH_REVIEW']     sev=REVIEW
- sco-void               -> [] (no alert — correct)

CRITICAL: non-scan alerts while POS feed unavailable = 0 (must be 0)
OK
```

- **Scenario 4 (normal):** scan → bagging (matched) → scale in tolerance → paid →
  no alert.
- **Scenario 5 (non-scan):** item in bagging, no scan within window, **healthy
  feed** → `ITEM_PLACED_NOT_SCANNED` (HIGH_REVIEW).
- **Scenario 6 (feed unavailable):** item in bagging, scanner feed down →
  `TRANSACTION_DATA_MISSING` (UNKNOWN); **no** non-scan alert. *(core rule)*
- **Scenario 7 (weight mismatch):** scanned item, stable weight 500 g vs expected
  325 g (>15 g) → `SCALE_MISMATCH_REVIEW`.
- **Scenario 8 (void/removal):** authorized void + item removed → resolved; no
  alert.

## 4. Verification (actual)
```
ruff   → All checks passed!
black  → 67 files left unchanged
mypy   → Success: no issues found in 54 source files
pytest → 53 passed, 1 warning   (46 prior + 7 new checkout scenarios)
checkout-demo → output above (critical metric 0 / OK)
```

## 5. Notes / honest scope
- **All transaction signals are SIMULATED.** Video alone can never know an item
  was scanned or weighed — that knowledge only ever comes from an integration,
  and here that integration is faked (`storeguard_integrations`). Real adapters
  replace the simulators behind the same contract types in a later phase, and
  only after event-synchronization and sensor coverage are validated.
- Occupancy / bagging-zone observations are provided as inputs (derived from the
  detector + zones in a full pipeline), as in Phase 3.
- Thresholds (`CheckoutRules`: 8 s window, 15 g tolerance) are conservative demo
  defaults; real tuning needs measured data (false alerts per checkout-hour).
- No identity, no face recognition; nothing asserts theft — every event is a
  human-review task describing an observable anomaly.

## 6. Status
Phase 4 acceptance met: terminal state machine, simulated scanner/scale
reconciliation, weight-mismatch and unavailable-integration behavior, with
scenarios 4–8 passing deterministic replay tests and **zero** non-scan alerts when
the POS feed is unavailable. **Stopping here and awaiting product-owner review
before Phase 5** (web dashboard: camera grid, event inbox/detail, checkout
monitor, review actions, real-time updates — wiring the Phase 1–4 engines into a
browser-operated end-to-end demo).
