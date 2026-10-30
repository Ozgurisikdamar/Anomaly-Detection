| Model | Backend | imgsz | frames | trials | p50 ms | p95 ms | mean ms | FPS | CPU % | RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|
| yolo26n | pytorch | 640 | 24 | 3 | 43.86 | 57.82 | 45.69 | 21.89 | 280.0 | 799.5 |
| yolo26n | onnx | 640 | 24 | 3 | 37.91 | 58.13 | 40.31 | 24.81 | 366.6 | 909.1 |
| yolo26n | openvino | 640 | 24 | 3 | 21.53 | 24.95 | 21.8 | 45.87 | 304.6 | 1015.2 |
| yolo11n | pytorch | 640 | 24 | 3 | 41.06 | 50.42 | 41.93 | 23.85 | 277.1 | 982.6 |
| yolo11n | onnx | 640 | 24 | 3 | 44.98 | 62.45 | 47.44 | 21.08 | 1182.8 | 1059.1 |
| yolo11n | openvino | 640 | 24 | 3 | 20.27 | 24.26 | 20.95 | 47.74 | 304.1 | 1033.5 |

> Environment (this machine, NOT the owner's target hardware): Intel(R) Xeon(R) Processor @ 2.10GHz x4 · torch 2.15.0+cu132 (threads=2) · ultralytics 8.4.193 · onnxruntime 1.31.1 · openvino 2026.4.1-22982-e213a147257-releases/2026/4 · py 3.13.17

> THROUGHPUT only — no labelled retail data, so no accuracy or model-selection claim.
