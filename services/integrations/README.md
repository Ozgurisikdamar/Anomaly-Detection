# services/integrations — SIMULATED POS / scanner / scale

**Phase 0 contains simulators only. There is no real integration here.**

Retail self-checkout anomaly rules require transaction signals (scans, scale
readings, terminal/payment state) that a camera cannot observe on its own. To
demonstrate the reconciliation logic without a real POS, this package produces
**deterministic, clearly-labelled simulated** events.

Every generated event carries `simulated=True`, and the package exposes
`SIMULATED_LABEL = "SIMULATED"` for the UI banner.

## What is NOT here (by design)
- No connection to any real POS/ERP, scanner hardware, or scale telemetry.
- No credentials, endpoints, or vendor SDKs.

## Replacing with a real integration (later phase)
Real adapters implement the same `storeguard_contracts` types
(`ScanEvent`, `ScaleEvent`, `TransactionEvent`) behind an adapter interface and
live in separate modules. Until a real feed is validated (event synchronization
and sensor coverage), the system must emit `TRANSACTION_DATA_MISSING` /
`TRANSACTION_UNKNOWN` rather than a non-scan or mismatch alert.
