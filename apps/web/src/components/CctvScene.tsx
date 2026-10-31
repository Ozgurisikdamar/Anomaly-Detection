/**
 * Stilize DEMO "kamera görüntüsü".
 *
 * Foto-gerçekçi değil, açıkça SİMÜLASYON: şematik bir mağaza reyonu veya
 * self-checkout sahnesi, bölge overlay'leri, köşe-ayraçlı bounding box'lar,
 * zaman damgası ve "SİMÜLASYON · DEMO" filigranı. Gerçek kanıt klibi (imzalı GIF)
 * verilirse onun yerine o gösterilir. Hook kullanmaz — sunucu bileşenlerinde de
 * çalışır. Dil tarafsız: "Kişi" ve "Ürün · DEMO" — asla suçlama.
 */

type Zone = {
  zone_id: string;
  zone_type: string;
  polygon: [number, number][];
};

const ZONE_COLOURS: Record<string, string> = {
  SHELF_DISPLAY: "#4f8cff",
  PICKUP_INTERACTION: "#4ade80",
  SCAN_AREA: "#ff8c4f",
  BAGGING_SCALE_AREA: "#816bff",
  OCCLUSION_UNKNOWN: "#94a3b8",
  AISLE_EXIT: "#f5c451",
  BASKET_CART_AREA: "#00c8ff",
  EXIT_SIDE: "#51c4f5",
};

const W = 320;
const H = 180;

function seedFrom(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0) / 4294967295;
}

function Brackets({ x, y, w, h, color }: { x: number; y: number; w: number; h: number; color: string }) {
  const L = Math.min(10, w / 3, h / 3);
  const seg = (pts: string) => (
    <polyline points={pts} fill="none" stroke={color} strokeWidth={1.6} strokeLinecap="round" />
  );
  return (
    <g>
      {seg(`${x},${y + L} ${x},${y} ${x + L},${y}`)}
      {seg(`${x + w - L},${y} ${x + w},${y} ${x + w},${y + L}`)}
      {seg(`${x},${y + h - L} ${x},${y + h} ${x + L},${y + h}`)}
      {seg(`${x + w - L},${y + h} ${x + w},${y + h} ${x + w},${y + h - L}`)}
    </g>
  );
}

function Person({ x, h = 70 }: { x: number; h?: number }) {
  const y = H - h - 6;
  const w = h * 0.42;
  return (
    <g fill="#0a0f1a" stroke="#1b2740" strokeWidth={0.8} opacity={0.92}>
      <circle cx={x + w / 2} cy={y + w * 0.4} r={w * 0.28} />
      <rect x={x + w * 0.1} y={y + w * 0.6} width={w * 0.8} height={h - w * 0.6} rx={w * 0.25} />
    </g>
  );
}

function ShelfScene() {
  const rows = [0.18, 0.4, 0.62];
  const products = ["#3b4a63", "#4b5d7a", "#5a6f93", "#8a5a3b", "#3b6b5a", "#6b3b5a"];
  return (
    <g>
      {/* arka duvar + zemin */}
      <rect x={0} y={0} width={W} height={H * 0.82} fill="#141d2e" />
      <rect x={0} y={H * 0.82} width={W} height={H * 0.18} fill="#0e1524" />
      {rows.map((ry, ri) => (
        <g key={ri}>
          <rect x={14} y={H * ry} width={W - 28} height={4} fill="#223049" />
          {Array.from({ length: 8 }).map((_, i) => (
            <rect
              key={i}
              x={20 + i * ((W - 48) / 8)}
              y={H * ry - 16}
              width={(W - 48) / 8 - 5}
              height={16}
              fill={products[(i + ri) % products.length]}
              opacity={0.9}
            />
          ))}
        </g>
      ))}
    </g>
  );
}

function CheckoutScene() {
  const products = ["#8a5a3b", "#3b6b5a", "#4b5d7a", "#6b3b5a", "#5a6f93"];
  return (
    <g>
      <rect x={0} y={0} width={W} height={H} fill="#121a2b" />
      {/* tezgâh/konveyör */}
      <rect x={0} y={H * 0.56} width={W} height={H * 0.2} fill="#1c2740" />
      <rect x={0} y={H * 0.56} width={W} height={3} fill="#2b3a5a" />
      {Array.from({ length: 6 }).map((_, i) => (
        <rect
          key={i}
          x={26 + i * 40}
          y={H * 0.56 - 14}
          width={26}
          height={14}
          rx={2}
          fill={products[i % products.length]}
          opacity={0.92}
        />
      ))}
      {/* kiosk */}
      <rect x={W - 70} y={H * 0.2} width={54} height={44} rx={3} fill="#0e1524" stroke="#2b3a5a" />
    </g>
  );
}

export function CctvScene({
  kind = "shelf",
  zones = [],
  seed = "",
  evidenceUrl,
  live = false,
  timestamp,
  className = "",
}: {
  kind?: "shelf" | "checkout";
  zones?: Zone[];
  seed?: string;
  evidenceUrl?: string | null;
  live?: boolean;
  timestamp?: string;
  className?: string;
}) {
  const r = seedFrom(seed || kind);
  const ts =
    timestamp ??
    new Date().toLocaleString("tr-TR", { hour12: false }).replace(",", "");

  // Gerçek kanıt klibi varsa onu göster (yine de çerçeve + filigran).
  const inner = evidenceUrl ? (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={evidenceUrl} alt="Kanıt klibi (DEMO)" className="h-full w-full object-cover" />
  ) : (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid slice" className="h-full w-full">
      {kind === "checkout" ? <CheckoutScene /> : <ShelfScene />}

      {/* bölge overlay'leri */}
      {zones.map((z) => {
        const c = ZONE_COLOURS[z.zone_type] ?? "#c8c8c8";
        const pts = z.polygon.map(([x, y]) => `${x * W},${y * H}`).join(" ");
        return <polygon key={z.zone_id} points={pts} fill={c} fillOpacity={0.14} stroke={c} strokeWidth={1} strokeDasharray="4 3" />;
      })}

      {/* kişi (gerçek COCO 'kişi' karşılığı, nötr) */}
      <Person x={20 + r * (W * 0.5)} />
      <Brackets x={18 + r * (W * 0.5)} y={H - 80} w={40} h={74} color="#4f8cff" />
      <rect x={18 + r * (W * 0.5)} y={H - 92} width={34} height={11} fill="#0b1220" opacity={0.8} />
      <text x={21 + r * (W * 0.5)} y={H - 83} fill="#9cc0ff" fontSize={8}>Kişi</text>

      {/* ürün kutusu (DOSYA DEMO dedektörü) */}
      <g>
        <Brackets
          x={kind === "checkout" ? W * 0.62 : W * 0.3}
          y={kind === "checkout" ? H * 0.42 : H * 0.34}
          w={34}
          h={26}
          color="#f5c451"
        />
        <rect
          x={kind === "checkout" ? W * 0.62 : W * 0.3}
          y={(kind === "checkout" ? H * 0.42 : H * 0.34) - 12}
          width={74}
          height={11}
          fill="#0b1220"
          opacity={0.8}
        />
        <text
          x={(kind === "checkout" ? W * 0.62 : W * 0.3) + 3}
          y={(kind === "checkout" ? H * 0.42 : H * 0.34) - 3}
          fill="#ffe29a"
          fontSize={8}
        >
          Ürün · DEMO
        </text>
      </g>

      {/* scanline dokusu */}
      {Array.from({ length: 30 }).map((_, i) => (
        <rect key={i} x={0} y={i * 6} width={W} height={1} fill="#000" opacity={0.08} />
      ))}

      {/* filigran */}
      <text
        x={W / 2}
        y={H / 2}
        fill="#ffffff"
        fillOpacity={0.09}
        fontSize={26}
        fontWeight={800}
        textAnchor="middle"
        transform={`rotate(-16 ${W / 2} ${H / 2})`}
      >
        SİMÜLASYON · DEMO
      </text>
    </svg>
  );

  return (
    <div className={`relative overflow-hidden rounded-lg border border-edge bg-black ${className}`}>
      <div className="aspect-video w-full">{inner}</div>
      {/* üst bar: zaman damgası + CANLI/KAYIT */}
      <div className="pointer-events-none absolute inset-x-0 top-0 flex items-center justify-between px-2 py-1 text-[10px]">
        <span className="rounded bg-black/55 px-1.5 py-0.5 font-mono text-slate-200">{ts}</span>
        <span
          className={`flex items-center gap-1 rounded px-1.5 py-0.5 font-medium ${
            live ? "bg-rose-600/80 text-white" : "bg-black/55 text-slate-200"
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${live ? "bg-white" : "bg-slate-400"}`} />
          {live ? "CANLI" : "KAYIT"}
        </span>
      </div>
    </div>
  );
}

/** camera_id / event'ten sahne türünü tahmin et. */
export function sceneKind(cameraId?: string | null): "shelf" | "checkout" {
  return cameraId && cameraId.includes("sco") ? "checkout" : "shelf";
}
