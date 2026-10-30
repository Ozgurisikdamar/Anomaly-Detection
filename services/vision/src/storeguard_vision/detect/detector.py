"""YOLO detector + tracker wrapper (ultralytics).

CPU-first by default. ``ultralytics`` and ``torch`` are imported lazily so the
package can be imported without the heavy ML stack installed.

Privacy: this wrapper exposes only class/box/score and an ephemeral, per-source
track id. It performs no face recognition or identity embedding.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Detection:
    cls_id: int
    label: str
    confidence: float
    xyxy: tuple[float, float, float, float]
    track_id: int | None = None


class YoloDetector:
    def __init__(
        self,
        weights: str,
        imgsz: int = 640,
        device: str = "cpu",
        conf: float = 0.25,
        tracker: str = "bytetrack.yaml",
    ) -> None:
        from ultralytics import YOLO  # lazy (ml extra)

        self.weights = weights
        self.imgsz = imgsz
        self.device = device
        self.conf = conf
        self.tracker = tracker
        self._model = YOLO(weights)
        self.names: dict[int, str] = dict(self._model.names)

    def _to_detections(self, result) -> list[Detection]:
        out: list[Detection] = []
        boxes = getattr(result, "boxes", None)
        if boxes is None or boxes.xyxy is None:
            return out
        xyxy = boxes.xyxy.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)
        conf = boxes.conf.cpu().numpy()
        has_ids = getattr(boxes, "id", None) is not None
        ids = boxes.id.cpu().numpy().astype(int) if has_ids else None
        for i in range(len(cls)):
            track_id = int(ids[i]) if ids is not None else None
            out.append(
                Detection(
                    cls_id=int(cls[i]),
                    label=self.names.get(int(cls[i]), str(cls[i])),
                    confidence=float(conf[i]),
                    xyxy=tuple(float(v) for v in xyxy[i]),  # type: ignore[arg-type]
                    track_id=track_id,
                )
            )
        return out

    def infer(self, image) -> list[Detection]:
        """Single-image detection (no tracking state)."""
        results = self._model.predict(
            image, imgsz=self.imgsz, device=self.device, conf=self.conf, verbose=False
        )
        return self._to_detections(results[0])  # type: ignore[index]

    def track(self, image):
        """Detection + tracking; maintains per-source state across calls."""
        results = self._model.track(
            image,
            imgsz=self.imgsz,
            device=self.device,
            conf=self.conf,
            tracker=self.tracker,
            persist=True,
            verbose=False,
        )
        return self._to_detections(results[0])  # type: ignore[index]
