"""In-process async event bus for realtime fan-out (SSE).

A deliberately small pub/sub: each SSE client gets a bounded queue; publishers
(event ingest and review actions) push a JSON-able message to every subscriber.
No Kafka/Redis — this is a single-host demo. Messages that would overflow a slow
client's queue are dropped for that client (realtime is best-effort; the REST
list endpoint remains the source of truth).
"""

from __future__ import annotations

import asyncio


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict]] = set()

    def subscribe(self) -> asyncio.Queue[dict]:
        q: asyncio.Queue[dict] = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[dict]) -> None:
        self._subscribers.discard(q)

    def publish(self, message: dict) -> None:
        for q in list(self._subscribers):
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                # Best-effort realtime: drop for this slow client.
                pass

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)
