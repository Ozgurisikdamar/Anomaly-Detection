"use client";

import { useState } from "react";

import { STATUS_TR, trLabel } from "@/lib/tr";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

type Action = "acknowledge" | "resolve" | "dismiss";

export function ReviewActions({ eventId, status }: { eventId: string; status: string }) {
  const [reviewer, setReviewer] = useState("web-reviewer");
  const [reason, setReason] = useState("");
  const [current, setCurrent] = useState(status);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function act(action: Action) {
    setErr(null);
    setMsg(null);
    if (!reviewer.trim()) {
      setErr("İnceleyen gerekli.");
      return;
    }
    if ((action === "resolve" || action === "dismiss") && !reason.trim()) {
      setErr("Doğrulamak veya yanlış alarm işaretlemek için gerekçe zorunlu.");
      return;
    }
    const body: Record<string, unknown> = { reviewer };
    if (action === "resolve") {
      body.decision = "CONFIRMED_OPERATIONAL_ANOMALY";
      body.note = reason;
    } else if (action === "dismiss") {
      body.note = reason;
    }
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/events/${eventId}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      const updated = await res.json();
      setCurrent(updated.status);
      setMsg(`Kaydedildi: durum artık "${trLabel(STATUS_TR, updated.status)}" (${reviewer}).`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "istek başarısız");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="text-sm text-fg">
        Mevcut durum: <span className="font-semibold">{trLabel(STATUS_TR, current)}</span>
      </div>
      <input
        value={reviewer}
        onChange={(e) => setReviewer(e.target.value)}
        placeholder="inceleyen"
        className="w-full rounded-md border border-edge bg-ink px-2 py-1 text-sm text-fg"
      />
      <input
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="gerekçe (doğrula/yanlış alarm için zorunlu)"
        className="w-full rounded-md border border-edge bg-ink px-2 py-1 text-sm text-fg"
      />
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => act("acknowledge")}
          disabled={busy}
          className="rounded-lg border border-edge bg-edge px-3 py-1.5 text-xs text-fg disabled:opacity-50"
        >
          İncelemeye al
        </button>
        <button
          onClick={() => act("resolve")}
          disabled={busy}
          className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50"
        >
          Doğrula
        </button>
        <button
          onClick={() => act("dismiss")}
          disabled={busy}
          className="rounded-lg border border-edge bg-edge px-3 py-1.5 text-xs text-fg disabled:opacity-50"
        >
          Yanlış alarm
        </button>
      </div>
      {msg ? <p className="text-xs text-emerald-700 dark:text-emerald-300">{msg}</p> : null}
      {err ? <p className="text-xs text-rose-700 dark:text-rose-300">⚠ {err}</p> : null}
      <p className="text-[11px] text-muted">
        Aksiyonlar API'yi çağırır (inceleyen + gerekçe zorunlu) ve sunucuda kalıcı olur.
      </p>
    </div>
  );
}
