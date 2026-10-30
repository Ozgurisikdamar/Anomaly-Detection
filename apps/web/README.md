# apps/web — StoreGuard dashboard (Next.js scaffold)

Phase 0 scaffold of the review dashboard. **All data shown is SIMULATED.**

## Pages
- **Overview** — KPI tiles (cameras online, open reviews, terminals; latency is a
  Phase 1 placeholder) and latest events.
- **Alerts inbox** — filterable event table; each row opens the detail.
- **Event detail** — explanation, confidence components, reason codes, missing
  signals, model/rule versions and (placeholder) review actions.
- **Cameras** — simulated health grid with preview/zone placeholders.
- **Checkout monitor** — per-terminal state machine + SIMULATED scan/scale feed,
  including the "scanner feed unavailable → UNKNOWN" case.

No face thumbnails, identity search, or demographic UI exist by design.

## Data source
Server components fetch from the API (`NEXT_PUBLIC_API_BASE`, default
`http://localhost:8000`). If the API is unreachable the page falls back to the
bundled SIMULATED sample (`src/lib/sample.ts`) and shows a "sample / offline"
pill, so the scaffold always renders.

Shared types come from `@storeguard/contracts` (`packages/contracts/ts`).

## Develop
```bash
npm install
npm run dev        # http://localhost:3000
npm run lint
npm run typecheck
npm run build
```
