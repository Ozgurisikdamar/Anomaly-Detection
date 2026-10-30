import type { AnomalyEvent } from "@storeguard/contracts";

import { SAMPLE_EVENTS } from "./sample";

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

export async function fetchEvent(
  id: string,
): Promise<{ data: AnomalyEvent | null; source: DataSource }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/events/${id}`);
    if (!res.ok) throw new Error(String(res.status));
    return { data: (await res.json()) as AnomalyEvent, source: "live" };
  } catch {
    const fallback = SAMPLE_EVENTS.find((e) => e.event_id === id) ?? null;
    return { data: fallback, source: "sample" };
  }
}

export type ReviewResult =
  | { ok: true; event: AnomalyEvent }
  | { ok: false; error: string; status?: number };

async function postReview(
  id: string,
  action: "acknowledge" | "resolve" | "dismiss",
  body: Record<string, unknown>,
): Promise<ReviewResult> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/events/${id}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      // Surface the server's reason (e.g. a 409 invalid-transition detail).
      let detail = `HTTP ${res.status}`;
      try {
        const j = await res.json();
        if (j?.detail) detail = String(j.detail);
      } catch {
        /* ignore non-JSON error bodies */
      }
      return { ok: false, error: detail, status: res.status };
    }
    return { ok: true, event: (await res.json()) as AnomalyEvent };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "network error" };
  }
}

export function acknowledgeEvent(id: string, reviewer: string): Promise<ReviewResult> {
  return postReview(id, "acknowledge", { reviewer });
}

export function resolveEvent(
  id: string,
  reviewer: string,
  note: string,
): Promise<ReviewResult> {
  return postReview(id, "resolve", {
    reviewer,
    decision: "CONFIRMED_OPERATIONAL_ANOMALY",
    note,
  });
}

export function dismissEvent(
  id: string,
  reviewer: string,
  note: string,
): Promise<ReviewResult> {
  return postReview(id, "dismiss", { reviewer, note });
}

// Honest per-event provenance: shelf/checkout detections come from the FILE DEMO
// vision pipeline (model_version is set); seeded events are SIMULATED. POS/scale
// are always simulated.
export function sourceLabel(event: AnomalyEvent): "FILE DEMO" | "SIMULATED" {
  return event.model_version ? "FILE DEMO" : "SIMULATED";
}
