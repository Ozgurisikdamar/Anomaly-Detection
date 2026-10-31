/**
 * Korelasyon şeridi: "Kamera: N ürün ↔ POS: M tarama ↔ Fark: K".
 *
 * P2 korelasyon mantığının tek bakışta anlaşılır görseli. Değerler oturumdan
 * türetilen DEMO gösterimidir; gerçek korelasyon self-checkout analiz hattında
 * çalışır. Dil tarafsızdır — "fark incelenmeli", suçlama değil.
 */
export function CorrelationStrip({
  cameraItems,
  posScans,
}: {
  cameraItems: number;
  posScans: number;
}) {
  const delta = cameraItems - posScans;
  const matched = delta === 0;

  const Box = ({ i, muted }: { i: number; muted?: boolean }) => (
    <span
      key={i}
      className={`h-6 w-6 rounded ${muted ? "bg-slate-600/40" : "bg-amber-500/50"}`}
    />
  );

  return (
    <div className="rounded-xl border border-edge bg-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-muted">
          Kamera ↔ POS korelasyonu
        </h3>
        <span className="rounded border border-slate-500/40 bg-slate-500/10 px-1.5 py-0.5 text-[10px] text-slate-300">
          SİMÜLASYON
        </span>
      </div>

      <div className="flex items-stretch gap-3">
        {/* Kamera tarafı */}
        <div className="flex-1 rounded-lg border border-edge bg-ink p-3">
          <div className="text-xs text-muted">KAMERA GÖRÜYOR</div>
          <div className="mt-1 text-lg font-bold text-white">{cameraItems} ürün</div>
          <div className="mt-2 flex flex-wrap gap-1">
            {Array.from({ length: cameraItems }).map((_, i) => (
              <Box key={i} i={i} />
            ))}
          </div>
        </div>

        {/* Motor */}
        <div className="flex flex-col items-center justify-center px-1 text-center">
          <div className="text-[10px] text-muted">KORELASYON</div>
          <div className="text-xl text-accent">→</div>
          <div className="text-[10px] text-muted">MOTORU</div>
        </div>

        {/* POS tarafı */}
        <div className="flex-1 rounded-lg border border-edge bg-ink p-3">
          <div className="text-xs text-muted">POS KAYDI</div>
          <div className="mt-1 text-lg font-bold text-white">{posScans} tarama</div>
          <div className="mt-2 flex flex-wrap gap-1">
            {Array.from({ length: posScans }).map((_, i) => (
              <Box key={i} i={i} muted />
            ))}
          </div>
        </div>
      </div>

      <div
        className={`mt-3 rounded-lg px-3 py-2 text-sm font-medium ${
          matched
            ? "bg-emerald-500/10 text-emerald-200"
            : "bg-rose-500/10 text-rose-200"
        }`}
      >
        {matched
          ? "Fark: 0 · kamera ve POS eşleşti"
          : `Fark: ${delta} · ${delta > 0 ? "taranmamış olası ürün — incelenmeli" : "fazladan tarama — incelenmeli"}`}
      </div>
    </div>
  );
}
