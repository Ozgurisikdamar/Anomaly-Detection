# ADR 0001 — Modular monolith first (no microservices/Kafka/Kubernetes in MVP)

- Status: Accepted
- Date: 2026-10-30

## Context
StoreGuard is a single-host CPU demo. The roadmap explicitly warns against
starting with Kubernetes, Kafka or microservices for a one-host demo, while
still wanting clean boundaries for later extraction.

## Decision
Build a **modular monolith**: a FastAPI backend plus clearly separated Python
packages (`packages/contracts`, `services/vision`, `services/integrations`) and
separate `apps/web` and `apps/mobile` clients. Modules communicate through the
shared contracts and in-process calls. Persistence is a single PostgreSQL
instance (Alembic migrations); Redis/queues are added only if measured
throughput requires them.

## Consequences
- Fast local setup; one process to run the API, Docker Compose for the demo.
- Module boundaries (capture / vision / zones / shelf / checkout / integrations
  / events) are kept explicit so they can be extracted into services later.
- No premature distributed-systems complexity. Later production scale
  (per-camera workers, GPU nodes, DeepStream, object storage) is documented but
  not built now.

## Alternatives rejected
- **Microservices + message bus now**: operational overhead unjustified for a
  one-host CPU demo.
- **Single undivided app**: would make later extraction and testing harder; we
  keep package boundaries from day one instead.
