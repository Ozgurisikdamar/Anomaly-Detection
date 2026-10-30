# apps/mobile — StoreGuard mobile (Expo + React Native)

Reviewer mobile app. Non-vision data is **SIMULATED**; shelf/checkout events come
from the FILE DEMO vision pipeline, labelled per event.

## Screens
- **Mock login** — local demo only, no real auth.
- **Alert inbox** — events from the API with in-app realtime refresh (polling
  every 5 s + pull-to-refresh); per-event FILE DEMO / SIMULATED source tag.
  Falls back to the SIMULATED sample offline.
- **Event detail** — refetches by id (server-authoritative), renders the
  authenticated short-lived **evidence clip** (GIF), and performs **real**
  acknowledge / resolve / dismiss against the API (reviewer required; reason
  required for resolve/dismiss) with server status + error (e.g. a 409 on an
  invalid transition) shown.
- **Camera health** — simulated states + an offline/error state note.

A lightweight state navigator is used instead of a navigation library to keep
the scaffold minimal; this is replaced in a later phase.

## Privacy / security notes (enforced in design)
- No raw RTSP credentials or camera URLs are exposed to the device.
- Evidence is fetched only through an authenticated, short-lived API URL; the
  area outside the configured zone is dimmed.
- No face thumbnails, identity search, or demographic data.

## Networking on a physical device (important)
`EXPO_PUBLIC_API_BASE` defaults to `http://localhost:8000`, which on a **physical
phone resolves to the phone itself**, not your dev machine. On a real device set
it to your dev host's **LAN IP**, e.g.:

```bash
EXPO_PUBLIC_API_BASE=http://192.168.1.42:8000 npm run start
```

and ensure the API's CORS origins and the host firewall allow that origin. A
simulator/emulator on the same machine can use `localhost`.

## Develop
```bash
npm install
npm run typecheck
npm run web            # run in a browser (react-native-web)
npm run export:web     # static web build (used for screenshots in CI)
npm run start          # Expo dev server for device / emulator
```

`EXPO_PUBLIC_API_BASE` sets the backend URL (default `http://localhost:8000`).
Shared types come from `@storeguard/contracts` (`packages/contracts/ts`).
