# services/checkout-analytics — self-checkout MVP (Phase 4)

A per-terminal state machine + reconciliation engine comparing **SIMULATED**
scanner/POS/scale signals with camera observations. Emits observable anomalies
only — never theft.

## Rules (roadmap §4.B)
- **B1 non-scan** — an item in the bagging zone with no matching scan within
  `scan_match_window_s` becomes `ITEM_PLACED_NOT_SCANNED` **only** when the
  scanner/POS feed and camera are healthy. If the feed is unavailable/late →
  `TRANSACTION_DATA_MISSING` (UNKNOWN), **never** a non-scan alert.
- **B2 scale mismatch** — compares stable vs expected weight when both exist;
  outside tolerance → `SCALE_MISMATCH_REVIEW` (produce lookup / stacking / tare /
  override are review reasons, never theft). No telemetry → no mismatch alert.
- **B3 item moved** — item leaving the bagging zone with no transaction →
  `ITEM_MOVED_UNRESOLVED`.
- **B4 reconciliation** — at transaction close, unmatched items →
  `TRANSACTION_RECONCILIATION_REQUIRED`; missing/contradictory signals →
  `TRANSACTION_UNKNOWN`. Authorized voids resolve items with no alert.

## Scenarios (replay, roadmap §5)
`storeguard_checkout.scenarios.run_all()`:

| Scenario | Expected |
|---|---|
| sco-normal | no alert |
| sco-non-scan | `ITEM_PLACED_NOT_SCANNED` (healthy feed) |
| sco-feed-missing | `TRANSACTION_DATA_MISSING`, **never** non-scan |
| sco-weight-mismatch | `SCALE_MISMATCH_REVIEW` |
| sco-void | no alert (resolved) |

```bash
python -m storeguard_checkout.cli checkout-demo
```

Pure Python + the shared contracts; signals come from the SIMULATED
`storeguard_integrations` generators. Video alone can never know an item was
scanned or weighed — that knowledge only ever comes from an integration, and
here that integration is simulated.
