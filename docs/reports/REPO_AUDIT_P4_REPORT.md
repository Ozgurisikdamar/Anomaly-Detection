# StoreGuard — Repo Audit follow-up: P4 (camera validation, acceleration, deployment)

> Responds to `docs/REPO_AUDIT_AND_NEXT_WORK.md` §P4. Scope of this run: **P4
> only**. Branch `feat/storeguard-demo-foundation`; `main` untouched; no
> force-push. Builds on approved P0–P3.

- **Date:** 2026-10-30
- **Base:** `6dce5a3` (P3 report commit)
- **Commits (this run):**
  - `4a4d8a3` feat(vision): benchmark backend dimension + model export + env capture
  - `033a29c` feat(capture): enforce RTSP timeouts + rtsp-check validation CLI
  - `e41b9d4` feat(vision): multi-stream CPU/latency scaling benchmark
  - `2643437` feat(vision): accel deps + export/benchmark/streams/rtsp Make targets + guarded tests
  - _(this commit)_ docs: DEPLOYMENT.md (security/KVKK + runbook) + this report + README

**P4 is the phase the audit flags as partly owner-blocked** (it needs a real
retail camera and the owner's target hardware). This run does a best-effort,
honestly-labelled P4 in a cloud **Intel Xeon (4-core)** sandbox and marks the
true-camera / target-hardware / labelled-accuracy parts as owner-blocked. User
decisions: ONNX + OpenVINO benchmark; local synthetic RTSP validation.

---

## 1. CPU acceleration benchmark — PyTorch vs ONNX vs OpenVINO

`make export-models && make benchmark` (24-frame FILE DEMO clip, imgsz 640, 3
trials pooled). Full data: `assets/p4_benchmark.{json,md}`.

| Model | Backend | p50 ms | p95 ms | mean ms | FPS | CPU % | RSS MB |
|---|---|---|---|---|---|---|---|
| yolo26n | pytorch | 43.86 | 57.82 | 45.69 | 21.89 | 280.0 | 799.5 |
| yolo26n | onnx | 37.91 | 58.13 | 40.31 | 24.81 | 366.6 | 909.1 |
| yolo26n | **openvino** | **21.53** | 24.95 | 21.80 | **45.87** | 304.6 | 1015.2 |
| yolo11n | pytorch | 41.06 | 50.42 | 41.93 | 23.85 | 277.1 | 982.6 |
| yolo11n | onnx | 44.98 | 62.45 | 47.44 | 21.08 | 1182.8 | 1059.1 |
| yolo11n | **openvino** | **20.27** | 24.26 | 20.95 | **47.74** | 304.1 | 1033.5 |

- **OpenVINO ≈ 2× faster than PyTorch** on this Intel CPU for both models
  (p50 ~44→~21 ms; FPS ~22→~46). This is the expected OpenVINO benefit on Intel
  and the headline P4 result.
- ONNX was roughly PyTorch-parity here; the yolo11n/onnx row shows ~1183 % CPU —
  onnxruntime default thread over-subscription on a 4-core box (a tuning note,
  not a model property).
- **Environment (this machine, NOT the owner's target hardware):** Intel(R)
  Xeon(R) @ 2.10GHz ×4 · torch 2.15.0 (threads=2) · ultralytics 8.4.193 ·
  onnxruntime 1.31.1 · openvino 2026.4.1 · py 3.13.17.
- **THROUGHPUT only** — demo/sample clips, no labelled retail data, so **no
  accuracy or model-selection claim** (per audit §6). Re-run on the real target
  CPU with labelled clips before selecting a model/backend.

## 2. Multi-stream CPU / latency scaling

`make benchmark-streams` (yolo26n, demo clip; N isolated detectors in parallel
threads). Full data: `assets/p4_streams.{json,md}`.

| streams | p50 ms | p95 ms | aggregate FPS | CPU % | RSS MB |
|---|---|---|---|---|---|
| 1 | 59.76 | 71.10 | 16.38 | 138.8 | 823.4 |
| 2 | 86.63 | 102.05 | 22.86 | 217.7 | 872.5 |
| 4 | 137.61 | 200.89 | 27.33 | 286.1 | 997.4 |

As concurrent cameras rise on 4 cores, per-stream latency grows (~60→~138 ms p50)
while aggregate throughput climbs then saturates (16→27 FPS) and CPU approaches
the core count — the expected contention curve. Sizing on real hardware is an
owner task.

## 3. RTSP capture validation

The capture path (`RtspFrameSource` + `SupervisedCamera`) was hardened and
validated with **real OpenCV decoding**:
- `RtspFrameSource` now opens via the FFMPEG backend and enforces open/read
  timeouts (`CAP_PROP_OPEN/READ_TIMEOUT_MSEC`) and `BUFFERSIZE=1` — the previous
  `open_timeout_s` was ignored.
- `storeguard-capture rtsp-check` drove a stream through `SupervisedCamera` and
  produced a health timeline showing **UNKNOWN → ONLINE → OFFLINE → ONLINE**
  (decode + state machine + exponential-backoff reconnect + recovery); a guarded
  integration test (`services/capture/tests/test_rtsp.py`) asserts decode +
  reconnect and is skipped in light CI.
- Against an `rtsp://` endpoint (FFMPEG backend) the reconnect/backoff loop fired
  as designed (reconnect counter incrementing while unreachable).

**Owner-blocked:** a live RTSP **server** decode in this sandbox needed a
third-party server binary (mediamtx) that could not be run here, and no real
retail camera exists. The real-camera acceptance (codec/resolution/FPS/network/
reconnect against an actual stream) is validated on the owner's side with
`make rtsp-check URL=...`; the FILE DEMO path remains the validated fallback
(audit §P4.1).

## 4. Deployment & security docs

`docs/DEPLOYMENT.md` (new): clean-clone demo walkthrough (shelf + checkout, web +
mobile review, where evidence/metrics live), Docker Compose quickstart, the
ML/benchmark/export/RTSP ops, and the **security posture the audit requires** —
KVKK legal review + lawful basis, no biometrics, retention/lifecycle, RBAC, TLS,
secret management (DB creds, the evidence HMAC secret, RTSP credentials), network
segmentation, and the audit trail.

## 5. Tests
All new benchmark/capture tests are ml/tool-guarded (skipped in light CI, so CI
stays fast): `services/vision/tests/test_export.py` (ONNX + OpenVINO export +
benchmark) and `services/capture/tests/test_rtsp.py` (decode + reconnect). The
non-ML benchmark-config/env tests run unconditionally. Full suite green locally.

## Test matrix (audit §7) — P4 rows
| Test | Status |
|---|---|
| CPU latency p50/p95, FPS, CPU/RAM measured | ✅ PyTorch/ONNX/OpenVINO × 26n/11n, 3 trials, env captured |
| YOLO26n vs YOLO11n on representative clips | ⚠️ throughput on demo clips only; labelled-accuracy owner-blocked |
| OpenVINO/ONNX export + benchmark after baseline | ✅ exported + benchmarked (OpenVINO ~2× on Intel) |
| Number of streams / multi-stream | ✅ 1/2/4 scaling measured |
| RTSP against a camera; codec/FPS/reconnect | ⚠️ code path + reconnect validated locally; real camera owner-blocked |
| Docker Compose quickstart + demo controls + docs | ✅ documented (compose validated; daemon unavailable here to run) |
| KVKK/retention/RBAC/TLS/secrets/network/audit | ✅ documented in DEPLOYMENT.md |

## Limitations / owner-blocked (stated, not skipped)
- Numbers are **this cloud Intel Xeon**, not the owner's target hardware;
  throughput only, no accuracy/selection claim (no labelled retail data).
- Real retail RTSP camera + its codec/resolution/FPS/network behaviour not
  exercised; a live RTSP server could not be stood up in this sandbox (external
  binary blocked). FILE DEMO is the validated fallback.
- Docker daemon unavailable here — compose is validated (`compose config`) and
  documented, not run.
- Real per-user auth and the production security items in DEPLOYMENT.md remain to
  be implemented before any real deployment.

## Status
P4 best-effort complete: ONNX + OpenVINO export and a PyTorch/ONNX/OpenVINO CPU
throughput benchmark (OpenVINO ~2× on this Intel CPU), multi-stream scaling, a
hardened + validated RTSP capture path, and the deployment/security/KVKK +
clean-clone runbook — with the real-camera, target-hardware and labelled-accuracy
parts honestly marked owner-blocked. This completes the P0–P4 work package; the
remaining items are the owner-side validations documented above.
