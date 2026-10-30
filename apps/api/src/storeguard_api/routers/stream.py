"""Server-Sent Events (SSE) endpoint for realtime event delivery."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from storeguard_api.deps import get_event_bus
from storeguard_api.event_bus import EventBus

router = APIRouter()

_KEEPALIVE_S = 15.0


async def _event_stream(request: Request, bus: EventBus) -> AsyncIterator[str]:
    queue = bus.subscribe()
    try:
        # Initial comment lets the client know the stream is open.
        yield ": connected\n\n"
        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=_KEEPALIVE_S)
                yield f"data: {json.dumps(message)}\n\n"
            except TimeoutError:
                yield ": keepalive\n\n"
    finally:
        bus.unsubscribe(queue)


@router.get("/stream/events", tags=["stream"])
async def stream_events(
    request: Request, bus: EventBus = Depends(get_event_bus)
) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(request, bus),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
