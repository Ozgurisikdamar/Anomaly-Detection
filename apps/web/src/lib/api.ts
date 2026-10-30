/**
 * API client for the StoreGuard dashboard.
 *
 * Fetches from the FastAPI backend when reachable and falls back to the bundled
 * SIMULATED sample so the scaffold always renders. `loadEvents` etc. return both
 * the data and a `source` flag the UI surfaces ("live API" vs "sample/offline").
 */
import type {
  AnomalyEvent,
  Camera,
  CameraStreamStatus,
  CheckoutSession,
} from "@storeguard/contracts";

import {
  SAMPLE_CAMERAS,
  SAMPLE_CHECKOUTS,
  SAMPLE_EVENTS,
  SAMPLE_STATUS,
} from "./sample";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type DataSource = "live" | "sample";

export interface Loaded<T> {
  data: T;
  source: DataSource;
}

async function tryFetch<T>(path: string, fallback: T): Promise<Loaded<T>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`status ${res.status}`);
    return { data: (await res.json()) as T, source: "live" };
  } catch {
    return { data: fallback, source: "sample" };
  }
}

export function loadEvents(): Promise<Loaded<AnomalyEvent[]>> {
  return tryFetch<AnomalyEvent[]>("/api/v1/events", SAMPLE_EVENTS);
}

export async function loadEvent(
  id: string,
): Promise<Loaded<AnomalyEvent | undefined>> {
  const fallback = SAMPLE_EVENTS.find((e) => e.event_id === id);
  return tryFetch<AnomalyEvent | undefined>(`/api/v1/events/${id}`, fallback);
}

export function loadCheckouts(): Promise<Loaded<CheckoutSession[]>> {
  return tryFetch<CheckoutSession[]>("/api/v1/checkouts", SAMPLE_CHECKOUTS);
}

export function loadCameras(): Promise<Loaded<Camera[]>> {
  return tryFetch<Camera[]>("/api/v1/cameras", SAMPLE_CAMERAS);
}

export function loadCameraStatus(id: string): Promise<Loaded<CameraStreamStatus>> {
  const fallback =
    SAMPLE_STATUS[id] ??
    ({
      camera_id: id,
      state: "UNKNOWN",
      fps: null,
      frame_age_ms: null,
      last_frame_at: null,
      reconnect_count: 0,
      simulated: true,
    } as CameraStreamStatus);
  return tryFetch<CameraStreamStatus>(`/api/v1/cameras/${id}/status`, fallback);
}
