# apps/mobile — StoreGuard mobile (Expo + React Native)

Phase 0 scaffold of the reviewer mobile app. **All data is SIMULATED.**

## Screens
- **Mock login** — local demo only, no real auth.
- **Alert inbox** — events from the API (falls back to SIMULATED sample offline).
- **Event detail** — explanation, reason codes, missing signals, and
  acknowledge / resolve / dismiss actions (local demo state in Phase 0).
- **Camera health** — simulated states + an offline/error state note.

A lightweight state navigator is used instead of a navigation library to keep
the Phase 0 scaffold minimal; this is replaced in Phase 6.

## Privacy / security notes (enforced in design)
- No raw RTSP credentials or camera URLs are exposed to the device.
- Evidence is delivered via an authenticated API with short-lived access (later).
- No face thumbnails, identity search, or demographic data.

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
