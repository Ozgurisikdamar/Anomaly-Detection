# ADR 0004 — Simulated POS/scanner/scale boundary

- Status: Accepted
- Date: 2026-10-30

## Context
Self-checkout anomaly rules need transaction signals (scans, scale readings,
terminal/payment state) that a camera cannot observe. The demo has no real POS,
and a demo must never be mistaken for a live integration. The core product rule
is that missing integration data is UNKNOWN, never a violation.

## Decision
Isolate all POS/scanner/scale behavior behind a dedicated
`services/integrations` package that, in Phase 0, contains **simulators only**.
Every generated signal carries `simulated=True` and the UI shows a `SIMULATED`
label. The contracts (`ScanEvent`, `ScaleEvent`, `TransactionEvent`,
`CheckoutSession`) include a `simulated` field. When a scanner/POS feed is
absent or late, the system emits `TRANSACTION_DATA_MISSING` /
`TRANSACTION_UNKNOWN` — **never** `ITEM_PLACED_NOT_SCANNED`.

## Consequences
- A reviewer can never confuse demo data with a real integration.
- Real adapters later implement the same contract types behind the same
  boundary and replace the simulators; rules require validated event
  synchronization and sensor coverage before emitting non-scan/mismatch alerts.
- The seed intentionally includes a "scanner feed unavailable" terminal and a
  `TRANSACTION_DATA_MISSING` event to demonstrate the rule.

## Alternatives rejected
- **Faking a "real" integration in the UI**: misleading and unsafe.
- **Inferring non-payment from video alone**: forbidden — video cannot know an
  item was scanned or weighed.
