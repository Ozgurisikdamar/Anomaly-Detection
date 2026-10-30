# StoreGuard — Deployment, security & demo runbook

Operational guide for running StoreGuard, benchmarking the CPU detectors,
validating a real camera, and the security/privacy posture required before any
real-store deployment. This is a **demo build**: non-vision signals (POS /
scanner / scale) are SIMULATED and labelled; shelf/checkout events come from a
FILE DEMO vision pipeline. Nothing here authorises deploying against real people
without the legal review below.

---

## 1. Clean-clone demo walkthrough

Prerequisites: Python 3.11+ and Node 22+. (Docker optional — see §2.)

```bash
make setup                 # venv + editable installs (light; no ML stack)
make setup-ml              # vision ML/accel extra: ultralytics + opencv + onnx/openvino
```

Run the API in DB mode + the two file-demo scenarios (shelf and self-checkout),
then review in the web + mobile clients:

```bash
# Postgres via Docker (or set STOREGUARD_DATABASE_URL=sqlite:///./demo.db instead):
make demo            # shelf: FILE DEMO clip -> YOLO+ByteTrack -> shelf FSM -> event -> API
make demo-checkout   # self-checkout: camera bagging observation <-> SIMULATED POS -> event

make dev-web         # dashboard at http://localhost:3000  (Alerts inbox = live via SSE)
make setup-mobile && make dev-mobile   # Expo app; on a device set EXPO_PUBLIC_API_BASE (see §5)
```

What to look for: a shelf `SHELF_ITEM_REMOVED_UNRESOLVED` and a checkout
`ITEM_PLACED_NOT_SCANNED` appear in the web Alerts inbox; each event's detail
shows a **zone-masked evidence clip** served via a short-lived authenticated URL;
acknowledging/resolving/dismissing persists server-side and is reflected in the
other client after refresh. A missing **or** delayed POS feed yields
`TRANSACTION_DATA_MISSING` (UNKNOWN) — never a non-scan. Evidence/metrics live
under `runs/`.

## 2. Docker Compose

`docker-compose.yml` brings up `postgres` + `api` + `web`:

```bash
make compose-config          # validate
docker compose up --build    # api :8000, web :3000, postgres :5432
```

The API image is intentionally light (no ML stack): the vision pipeline runs as
a separate process/host and POSTs events to the API. (In a CPU-only sandbox
without a Docker daemon, substitute the SQLite `STOREGUARD_DATABASE_URL` above.)

## 3. CPU benchmark & model acceleration

```bash
make export-models       # YOLO26n/YOLO11n -> ONNX + OpenVINO IR (cached, runs/exports)
make benchmark           # PyTorch vs ONNX vs OpenVINO x both models -> runs/benchmark.{json,md}
make benchmark-streams   # multi-stream CPU/latency scaling (1/2/4 cameras) -> runs/streams.{json,md}
```

OpenVINO targets Intel CPUs. Results are **throughput only** (latency/FPS/CPU/RSS)
and describe the machine they ran on — they are **not** an accuracy or
model-selection claim; that requires a labelled retail dataset (see §7). Always
re-run on the actual target hardware before choosing a model/backend.

## 4. Real RTSP camera validation

```bash
URL='rtsp://user:pass@camera-host:554/stream' make rtsp-check
```

`rtsp-check` drives the stream through `SupervisedCamera` and prints a health
timeline (state, frame age, FPS, reconnect count). The URL is a **server-side
secret** — pass it via the environment, never commit it, and it is never printed
or sent to a client. The reader enforces open/read timeouts and keeps only the
latest frame; a dropped stream triggers exponential-backoff reconnect and the
state transitions ONLINE → OFFLINE → ONLINE on recovery.

## 5. Networking & secrets (env)

Copy `.env.example` to `.env`. Key variables:
- `STOREGUARD_DATABASE_URL` — Postgres (prod) or SQLite (offline).
- `STOREGUARD_EVIDENCE_SECRET` — HMAC secret that signs short-lived evidence
  URLs. **Change it in production**; rotate periodically. `STOREGUARD_EVIDENCE_DIR`
  / `STOREGUARD_EVIDENCE_URL_TTL_S` control the media store and URL lifetime.
- `NEXT_PUBLIC_API_BASE` / `EXPO_PUBLIC_API_BASE` — client → API base. On a
  **physical phone, `localhost` is the phone itself**; set the Expo base to the
  dev host's LAN IP (e.g. `http://192.168.1.42:8000`) and allow that origin in
  the API CORS list.
- RTSP URLs/credentials are passed to the capture process via a secret, never
  committed or exposed to clients.

---

## 5a. Hosting the web dashboard on Netlify

Netlify hosts **only the web dashboard** (`apps/web`, Next.js). The FastAPI backend
and the Python vision pipeline run elsewhere (a VM / Render / Fly / Railway) — Netlify
cannot run them.

The repo ships a root `netlify.toml` (base `apps/web`, the official
`@netlify/plugin-nextjs` runtime — the app is SSR, not a static export). To deploy:

1. **Host the API** somewhere public (HTTPS). Set its `STOREGUARD_CORS_ORIGINS_EXTRA`
   to the Netlify site origin, e.g.
   `STOREGUARD_CORS_ORIGINS_EXTRA=https://your-site.netlify.app` (comma-separated;
   merged with the localhost defaults by `settings.allowed_origins`).
2. In Netlify → **Site settings → Environment variables**, set
   `NEXT_PUBLIC_API_BASE` to that public API URL. (It is deliberately not committed.)
3. Connect the repo in Netlify and deploy; the Next plugin builds `apps/web`.

Without steps 1–2 the dashboard still deploys but shows **SIMULATED sample data**
(offline fallback) — no live events, SSE, or working review, since the browser can't
reach the API. The Expo mobile app and the vision pipeline are deployed separately
(not Netlify).

## 6. Security & privacy posture (required before real deployment)

This demo must not be pointed at real people until the following are in place.

- **KVKK (and GDPR-equivalent) legal review & lawful basis.** Processing CCTV of
  identifiable people requires a documented lawful basis, a DPIA, signage/notice,
  and data-subject rights handling. No real identifiable footage belongs in this
  repository, in screenshots, or in logs without that review and approval.
- **No biometric identification.** No face recognition, no person re-identification
  across cameras, no demographic inference. Track IDs are camera-local and
  ephemeral (a detector with `persist=True` is never shared across streams).
- **Retention & lifecycle.** Evidence clips and events have a bounded retention
  with automatic deletion; evidence is stored in access-controlled object storage
  (not a world-readable path) and referenced only via short-lived signed URLs.
- **Role-based access control.** Reviewer identity must be real authentication
  (the current `reviewer` field and the shared-secret evidence token are
  **demo-grade only**). Review actions are server-authoritative, audited, and
  reject invalid/duplicate state transitions (409).
- **TLS everywhere.** API, web, mobile and RTSP/Posix integrations over TLS; no
  plaintext credentials or media in transit.
- **Secret management.** DB creds, the evidence HMAC secret, and RTSP camera
  credentials come from a secret manager / environment, never source control.
- **Network segmentation.** Cameras and POS integrations sit on a segmented
  network; the API is not exposed unauthenticated to the internet.
- **Audit trail.** Every review decision is persisted with actor, action, target
  and timestamp (see the `audit_logs` table); retained per policy.

## 7. Honest limitations

- Non-vision POS/scanner/scale signals are **SIMULATED**; the `PosFeed` interface
  is where a real integration plugs in.
- Product presence is a **labelled demo detector**, not SKU recognition; person
  detection is real COCO. COCO classes are not supermarket SKUs.
- Benchmarks are **throughput only**, on whatever machine ran them, over demo/
  sample clips — not retail accuracy and not a model-selection decision.
- Real retail-camera validation and target-hardware benchmarking are owner tasks
  (see `docs/reports/REPO_AUDIT_P4_REPORT.md`); the FILE DEMO path is the
  validated fallback.
