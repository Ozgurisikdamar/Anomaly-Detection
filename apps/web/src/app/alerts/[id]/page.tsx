import Link from "next/link";

import { CctvScene, sceneKind } from "@/components/CctvScene";
import { ReviewActions } from "@/components/ReviewActions";
import { API_BASE, loadEvent } from "@/lib/api";
import {
  EVENT_TYPE_TR,
  eventSourceLabel,
  EXPLANATION_TR,
  MISSING_FLAG_TR,
  REASON_TR,
  STATUS_TR,
  trLabel,
  UI,
  ZONE_TYPE_TR,
} from "@/lib/tr";
import { Panel, SeverityBadge, SourcePill } from "@/lib/ui";

export const dynamic = "force-dynamic";

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-1 text-sm">
      <span className="text-muted">{label}</span>
      <span className="text-right text-slate-100">{value}</span>
    </div>
  );
}

export default async function EventDetailPage({ params }: { params: { id: string } }) {
  const { data: event, source } = await loadEvent(params.id);

  if (!event) {
    return (
      <div className="space-y-4">
        <Link href="/alerts" className="text-sm text-accent hover:underline">
          {UI.common.backToAlerts}
        </Link>
        <p className="text-slate-300">Olay bulunamadı.</p>
      </div>
    );
  }

  const conf = event.confidence;
  const url =
    event.evidence?.[0]?.available && event.evidence[0].url
      ? `${API_BASE}${event.evidence[0].url}`
      : null;
  const explanation = EXPLANATION_TR[event.event_type] ?? event.explanation;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <Link href="/alerts" className="text-sm text-accent hover:underline">
          {UI.common.backToAlerts}
        </Link>
        <SourcePill source={source} />
      </div>

      <header className="flex flex-wrap items-center gap-3">
        <SeverityBadge severity={event.severity} />
        <h1 className="text-2xl font-bold text-white">{trLabel(EVENT_TYPE_TR, event.event_type)}</h1>
        <span
          className={`rounded px-2 py-0.5 text-xs ${
            eventSourceLabel(event.model_version) === "DOSYA DEMO"
              ? "bg-accent/20 text-accent"
              : "bg-amber-500/15 text-amber-200"
          }`}
        >
          {eventSourceLabel(event.model_version)}
        </span>
      </header>

      <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-sm text-amber-100/90">
        {UI.neutralNote} {explanation}
      </div>

      {/* 3 kolon konsol: Kayıt · Olay Detayı · İnceleme */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Sol: kayıt / kamera görüntüsü */}
        <section className="space-y-3 lg:row-span-2">
          <Panel title="Kayıt">
            <CctvScene kind={sceneKind(event.camera_id)} seed={event.event_id} evidenceUrl={url} />
            <p className="mt-2 text-xs text-muted">
              {url
                ? "Kimlik doğrulamalı, kısa ömürlü bir URL üzerinden sunulur (ham yol asla paylaşılmaz). Yapılandırılmış bölge dışındaki alan karartılır."
                : "Bu olay için kanıt klibi yok; stilize DEMO sahnesi gösteriliyor."}
            </p>
          </Panel>
          <Panel title="Neden kodları & eksik sinyaller">
            <div className="mb-2 flex flex-wrap gap-2">
              {event.reason_codes.map((r) => (
                <span key={r} className="rounded bg-edge px-2 py-0.5 text-xs text-slate-200">
                  {trLabel(REASON_TR, r)}
                </span>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {event.missing_data_flags.length === 0 ? (
                <span className="text-xs text-muted">eksik veri bayrağı yok</span>
              ) : (
                event.missing_data_flags.map((m) => (
                  <span key={m} className="rounded bg-slate-500/20 px-2 py-0.5 text-xs text-slate-300">
                    ⚠ {trLabel(MISSING_FLAG_TR, m)}
                  </span>
                ))
              )}
            </div>
          </Panel>
        </section>

        {/* Orta: olay detayı + güven */}
        <section className="space-y-4">
          <Panel title="Olay Detayı">
            <Row label="Olay ID" value={event.event_id} />
            <Row label="Durum" value={trLabel(STATUS_TR, event.status)} />
            <Row label="Kamera" value={event.camera_id} />
            <Row label="Bölge" value={event.zone_id ? trLabel(ZONE_TYPE_TR, event.zone_id) : "—"} />
            <Row
              label="Algılandı"
              value={new Date(event.detected_at).toLocaleString("tr-TR", { hour12: false })}
            />
            <Row label="İnsan incelemesi" value={event.human_review_required ? "GEREKLİ" : "hayır"} />
          </Panel>
          <Panel title="Güven bileşenleri">
            <Row label="Dedektör" value={conf.detector ?? "— (yok)"} />
            <Row label="İz kalitesi" value={conf.track_quality ?? "— (yok)"} />
            <Row label="Bölge kesinliği" value={conf.zone_certainty ?? "— (yok)"} />
            <Row label="POS senkronizasyonu" value={conf.pos_synchronization ?? "— (yok)"} />
            <Row label="Kural kanıtı" value={conf.rule_evidence ?? "— (yok)"} />
          </Panel>
        </section>

        {/* Sağ: inceleme aksiyonları + sürümler */}
        <section className="space-y-4">
          <Panel title="İnceleme">
            <ReviewActions eventId={event.event_id} status={event.status} />
          </Panel>
          <Panel title="Sürümler">
            <Row label="Model sürümü" value={event.model_version ?? "—"} />
            <Row label="İzleyici sürümü" value={event.tracker_version ?? "—"} />
            <Row label="Kural sürümü" value={event.rule_version ?? "—"} />
          </Panel>
        </section>
      </div>
    </div>
  );
}
