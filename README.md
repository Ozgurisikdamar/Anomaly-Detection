# StoreGuard — Retail Loss Prevention Demo

A human-in-the-loop computer vision demo for shelf/aisle monitoring and self-checkout transaction anomaly detection.

## Start here
- [Demo implementation roadmap](docs/STOREGUARD_DEMO_ROADMAP.md)

## Product principles
- Detect observable operational anomalies; do not infer criminal intent or label people.
- Shelf disappearance is unresolved until corroborated; occlusion and replenishment must be handled.
- Self-checkout non-scan detection requires synchronized camera + scanner/POS data. Scale mismatch requires scale telemetry.
- Missing integration data means UNKNOWN, never a violation.
- Every event requires human review.
- Privacy by design: no face recognition, no biometric identification, pseudonymous camera-local tracks, controlled retention.

## Planned demo
- CPU-first local inference with RTSP and offline file/synthetic sources.
- YOLO26n benchmark baseline vs YOLO11n, tracking benchmark and measured selection.
- Web dashboard and React Native mobile client.
- Simulated scanner/POS/scale feed clearly labelled as simulated until real integrations are provided.

## Implementation
Follow the phase gates in the roadmap. Claude Code should implement Phase 0 only first, report results, and wait for review.
