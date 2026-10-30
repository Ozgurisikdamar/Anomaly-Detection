/**
 * Mobile API client.
 *
 * Reads from the backend over an AUTHENTICATED API (no raw RTSP/credentials are
 * ever exposed to the device). Falls back to the bundled SIMULATED sample when
 * the API is unreachable, so the scaffold always renders.
 */
import type { AnomalyEvent } from "@storeguard/contracts";

import { SAMPLE_EVENTS } from "./sample";

// In a real build this comes from secure config; never hardcode camera URLs.
export const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE ?? "http://localhost:8000";

export type DataSource = "live" | "sample";

export async function fetchEvents(): Promise<{ data: AnomalyEvent[]; source: DataSource }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/events`);
    if (!res.ok) throw new Error(String(res.status));
    return { data: (await res.json()) as AnomalyEvent[], source: "live" };
  } catch {
    return { data: SAMPLE_EVENTS, source: "sample" };
  }
}
