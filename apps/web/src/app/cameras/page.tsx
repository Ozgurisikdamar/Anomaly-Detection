import type { Camera, CameraStreamStatus } from "@storeguard/contracts";

import { loadCameras, loadCameraStatus } from "@/lib/api";
import { SOURCE_BADGE_TR, trLabel, ZONE_TYPE_TR } from "@/lib/tr";
import { SourcePill, StateDot } from "@/lib/ui";

const KIND_TR: Record<string, string> = { shelf: "Raf", checkout: "Self-checkout" };

export const dynamic = "force-dynamic";

const ZONE_COLOURS: Record<string, string> = {
  SHELF_DISPLAY: "#4f8cff",
  PICKUP_INTERACTION: "#4ade80",
  OCCLUSION_UNKNOWN: "#94a3b8",
  AISLE_EXIT: "#f5c451",
  SCAN_AREA: "#ff8c4f",
  BAGGING_SCALE_AREA: "#816bff",
  BASKET_CART_AREA: "#00c8ff",
  EXIT_SIDE: "#51c4f5",
};

const VW = 100;
const VH = 56;

// Kamera kaynağını ayırt edici, dürüst bir rozete eşle.
const SOURCE_BADGE_CLS: Record<string, string> = {
  rtsp: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
  file: "border-amber-500/40 bg-amber-500/10 text-amber-200",
  synthetic: "border-slate-500/40 bg-slate-500/10 text-slate-300",
};

function SourceBadge({ sourceKind }: { sourceKind: string }) {
  const cls = SOURCE_BADGE_CLS[sourceKind] ?? SOURCE_BADGE_CLS.synthetic;
  return (
    <span className={`rounded-full border px-2 py-0.5 text-[10px] ${cls}`}>
      {trLabel(SOURCE_BADGE_TR, sourceKind)}
    </span>
  );
}

function ZoneOverlay({ camera }: { camera: Camera }) {
  return (
    <svg
      viewBox={`0 0 ${VW} ${VH}`}
      preserveAspectRatio="none"
      className="h-32 w-full rounded-lg border border-edge bg-ink"
    >
      {camera.zones.length === 0 ? (
        <text x={VW / 2} y={VH / 2} fill="#8394b4" fontSize="4" textAnchor="middle">
          bölge tanımlı değil
        </text>
      ) : (
        camera.zones.map((z) => {
          const colour = ZONE_COLOURS[z.zone_type] ?? "#c8c8c8";
          const pts = z.polygon.map(([x, y]) => `${x * VW},${y * VH}`).join(" ");
          const cx = (z.polygon.reduce((s, p) => s + p[0], 0) / z.polygon.length) * VW;
          const cy = (z.polygon.reduce((s, p) => s + p[1], 0) / z.polygon.length) * VH;
          return (
            <g key={z.zone_id}>
              <polygon points={pts} fill={colour} fillOpacity={0.22} stroke={colour} strokeWidth={0.6} />
              <text x={cx} y={cy} fill={colour} fontSize="3.4" textAnchor="middle">
                {trLabel(ZONE_TYPE_TR, z.zone_type)}
              </text>
            </g>
          );
        })
      )}
    </svg>
  );
}

function StatusRow({ status }: { status: CameraStreamStatus }) {
  return (
    <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-muted">
      <span>kare yaşı: {status.frame_age_ms != null ? `${status.frame_age_ms} ms` : "—"}</span>
      <span>FPS: {status.fps ?? "—"}</span>
      <span>yeniden bağlanma: {status.reconnect_count}</span>
    </div>
  );
}

export default async function CamerasPage() {
  const { data: cameras, source } = await loadCameras();
  const statuses = await Promise.all(cameras.map((c) => loadCameraStatus(c.camera_id)));
  const statusById = new Map(statuses.map((s) => [s.data.camera_id, s.data]));

  return (
    <div className="space-y-5">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Kameralar</h1>
          <p className="text-sm text-muted">
            Bölge poligonları + akış sağlığı / kare yaşı. Değerler SİMÜLASYON'dur; gerçek sağlık
            motoru <code className="text-slate-300">services/capture</code>.
          </p>
        </div>
        <SourcePill source={source} />
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cameras.map((c) => {
          const st = statusById.get(c.camera_id);
          return (
            <div key={c.camera_id} className="rounded-xl border border-edge bg-panel p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{c.name}</span>
                    <SourceBadge sourceKind={c.source_kind} />
                  </div>
                  <div className="text-xs text-muted">
                    {c.camera_id} · {KIND_TR[c.kind] ?? c.kind} · {c.zones.length} bölge
                  </div>
                </div>
                <StateDot state={st?.state ?? "UNKNOWN"} />
              </div>
              <div className="mt-3">
                <ZoneOverlay camera={c} />
              </div>
              {st ? <StatusRow status={st} /> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
