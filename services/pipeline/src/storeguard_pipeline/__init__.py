"""StoreGuard pipeline coordinator (P1 vertical slice).

Composes capture -> detector/tracker -> zone mapping -> shelf FSM -> event
publication into one end-to-end pipeline that runs on a FILE DEMO clip (and,
optionally, RTSP). Each camera gets its **own** YOLO detector/tracker instance,
so ByteTrack `persist` state is never shared across streams.

Honesty of product presence: person detection uses the real COCO YOLO detector
(a person is a person, not an SKU). Product occupancy comes from an explicitly
labelled `DemoProductDetector` (a colour-marker stand-in), **never** presented
as supermarket SKU recognition. Source is labelled FILE DEMO.
"""

from storeguard_pipeline.coordinator import (
    CameraConfig,
    PipelineCoordinator,
    PipelineResult,
)

__all__ = ["CameraConfig", "PipelineCoordinator", "PipelineResult"]
__version__ = "0.1.0"
