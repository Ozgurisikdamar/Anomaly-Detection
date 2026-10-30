# CPU detection/tracking benchmark plan (Phase 1)

> Preserved from the roadmap. Executed in Phase 1, not Phase 0. No numbers in
> this document are measured yet — they are placeholders to be filled on the
> real target machine. Do not invent results.

## Goal
Select a detector + tracker for CPU-only local inference on the target hardware
using **measured** evidence, not assumptions.

## Candidates
| Candidate | Role |
|---|---|
| YOLO26n | Initial detector candidate (not pre-approved winner) |
| YOLO11n | Comparison detector |
| ONNX export (of the chosen base) | CPU latency candidate |
| OpenVINO export (of the chosen base) | CPU latency candidate |

Trackers: **ByteTrack** (baseline), **BoT-SORT**, **TrackTrack**. Per-camera
isolated state; short-lived camera-local pseudonymous IDs only.

## Fixed conditions
- Device: CPU only (`device="cpu"`).
- Same representative clips (synthetic + authorized samples), same resolution
  and the same frame-sampling stride across all candidates.
- Capture kept independent of inference; bounded latest-frame queue.

## Metrics to record (per candidate)
| Metric | Notes |
|---|---|
| Latency p50 / p95 (ms) | per-frame inference |
| FPS | sustained, not peak |
| Frame age p95 (ms) | end-to-end staleness |
| Precision / Recall | per class + per camera angle; needs labelled eval set |
| ID switches / fragmentation | tracking continuity |
| CPU % / RAM (MB) | sustained resource use |

## Procedure
1. Export/prepare each candidate; record versions and licensing notes.
2. Warm up, then run N frames per clip; collect latency distribution.
3. Evaluate quality against a labelled eval set split by store/camera/time
   (never adjacent random frames).
4. Record resource utilization during sustained runs.
5. Choose on the full table, prioritizing stability + latency on the target CPU.

## Output
A reproducible report committed under `docs/reports/` with the raw command
outputs and the selection rationale. Generic COCO weights do **not** recognize
arbitrary supermarket SKUs — a custom retail product detector / embedding
retrieval path is documented separately before any SKU-level claim.

## Harness
`storeguard_vision.benchmark.run_benchmark(BenchmarkConfig)` is the entry point.
In Phase 0 it raises `NotImplementedError` by design.
