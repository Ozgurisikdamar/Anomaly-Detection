"use client";

import { useMemo, useState } from "react";

import type { CheckoutSession } from "@storeguard/contracts";

import { CHECKOUT_STATE_TR, trLabel, TXN_KIND_TR } from "@/lib/tr";

import { CctvScene } from "./CctvScene";
import { CorrelationStrip } from "./CorrelationStrip";

function hhmmss(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleTimeString("tr-TR", { hour12: false });
}

type TimelineRow = { t: string; kind: "camera" | "scan" | "scale" | "txn"; text: string };

function buildTimeline(s: CheckoutSession): TimelineRow[] {
  const rows: TimelineRow[] = [];
  if (s.state === "BAGGING_OBSERVED" || s.scans.length > 0) {
    rows.push({ t: hhmmss(s.updated_at), kind: "camera", text: "Ürün bagaj alanına kondu" });
  }
  for (const sc of s.scans) {
    rows.push({
      t: hhmmss(sc.occurred_at),
      kind: "scan",
      text: `Barkod okutuldu · ${sc.sku} ×${sc.quantity}`,
    });
  }
  for (const se of s.scale_events) {
    const exp = se.expected_weight_g != null ? ` (beklenen ${se.expected_weight_g} g)` : "";
    rows.push({
      t: hhmmss(se.occurred_at),
      kind: "scale",
      text: `Tartı ölçümü · ${se.stable_weight_g ?? "—"} g${exp}`,
    });
  }
  for (const tx of s.transaction_events) {
    rows.push({ t: hhmmss(tx.occurred_at), kind: "txn", text: `İşlem · ${trLabel(TXN_KIND_TR, tx.kind)}` });
  }
  return rows.sort((a, b) => a.t.localeCompare(b.t));
}

const DOT: Record<TimelineRow["kind"], string> = {
  camera: "bg-sky-400",
  scan: "bg-emerald-400",
  scale: "bg-violet-400",
  txn: "bg-amber-400",
};

export function CheckoutConsole({ sessions }: { sessions: CheckoutSession[] }) {
  const [sel, setSel] = useState(sessions[0]?.terminal_id ?? "");
  const active = useMemo(
    () => sessions.find((s) => s.terminal_id === sel) ?? sessions[0],
    [sessions, sel],
  );

  if (!active) {
    return <p className="text-sm text-muted">Gösterilecek self-checkout oturumu yok.</p>;
  }

  const timeline = buildTimeline(active);
  const itemQty = active.scans.reduce((n, s) => n + s.quantity, 0);
  const cameraItems = active.scans.length + (active.state === "BAGGING_OBSERVED" ? 1 : 0);

  return (
    <div className="grid gap-4 lg:grid-cols-[18rem_1fr]">
      {/* İşlem-video tablosu: oturum listesi */}
      <aside className="rounded-xl border border-edge bg-panel">
        <div className="border-b border-edge px-3 py-2 text-xs font-semibold uppercase tracking-wide text-muted">
          İşlemler
        </div>
        <table className="w-full text-left text-xs">
          <thead className="text-[10px] uppercase text-muted">
            <tr>
              <th className="px-3 py-2">Terminal</th>
              <th className="px-3 py-2">Durum</th>
              <th className="px-3 py-2">Tarama</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr
                key={s.terminal_id}
                onClick={() => setSel(s.terminal_id)}
                className={`cursor-pointer border-t border-edge ${
                  s.terminal_id === active.terminal_id ? "bg-accent/15" : "hover:bg-ink/60"
                }`}
              >
                <td className="px-3 py-2 font-medium text-fg">{s.terminal_id}</td>
                <td className="px-3 py-2 text-muted">{trLabel(CHECKOUT_STATE_TR, s.state)}</td>
                <td className="px-3 py-2 text-fg">{s.scans.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </aside>

      {/* Olay Analizi */}
      <div className="space-y-4">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-2">
            <CctvScene kind="checkout" seed={active.session_id ?? active.terminal_id} />
            <p className="text-xs text-muted">
              {active.terminal_id} · oturum {active.session_id ?? "—"} ·{" "}
              {trLabel(CHECKOUT_STATE_TR, active.state)} · stilize DEMO sahnesi
            </p>
          </div>

          <div className="rounded-xl border border-edge bg-panel p-4">
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted">
              İşlem Bilgisi
            </h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted">Tarama sayısı</span>
                <span className="text-fg">{active.scans.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Ürün adedi</span>
                <span className="text-fg">{itemQty}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Tartı olayı</span>
                <span className="text-fg">{active.scale_events.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Durum</span>
                <span className="text-fg">{trLabel(CHECKOUT_STATE_TR, active.state)}</span>
              </div>
            </div>
            {active.scans.length === 0 ? (
              <div className="mt-3 rounded border border-slate-500/30 bg-slate-500/10 px-2 py-1 text-xs text-muted">
                ⚠ Tarayıcı akışı yok — durum BİLİNMİYOR; taranmamış ürün alarmı üretilmez.
              </div>
            ) : null}
          </div>
        </div>

        <CorrelationStrip cameraItems={cameraItems} posScans={active.scans.length} />

        <div className="rounded-xl border border-edge bg-panel p-4">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted">
            Olay Zaman Çizelgesi
          </h3>
          {timeline.length === 0 ? (
            <p className="text-sm text-muted">Bu oturum için olay yok.</p>
          ) : (
            <ol className="space-y-2">
              {timeline.map((row, i) => (
                <li key={i} className="flex items-center gap-3 text-sm">
                  <span className={`h-2 w-2 shrink-0 rounded-full ${DOT[row.kind]}`} />
                  <span className="w-20 shrink-0 font-mono text-xs text-muted">{row.t}</span>
                  <span className="text-fg">{row.text}</span>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  );
}
