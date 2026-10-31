import { CheckoutConsole } from "@/components/CheckoutConsole";
import { loadCheckouts } from "@/lib/api";
import { SourcePill } from "@/lib/ui";

export const dynamic = "force-dynamic";

export default async function CheckoutsPage() {
  const { data: checkouts, source } = await loadCheckouts();

  return (
    <div className="space-y-5">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Self-checkout · Olay Analizi</h1>
          <p className="text-sm text-muted">
            Terminal bazlı durum makinesi · SİMÜLASYON POS / tarayıcı / tartı akışları.
          </p>
        </div>
        <SourcePill source={source} />
      </header>

      <div className="rounded-lg border border-edge bg-panel p-3 text-xs text-muted">
        Taranmamış-ürün inceleme olayları; kamera bagaj-alanı gözlemleri ile (SİMÜLASYON) tarayıcı/POS
        akışının terminal, oturum ve eşzamanlı UTC zamanına göre eşleştirilmesiyle üretilir. Eksik{" "}
        <em>veya</em> gecikmiş POS akışı{" "}
        <span className="text-slate-200">İşlem verisi eksik</span> (BİLİNMİYOR) sonucunu verir — asla
        taranmamış-ürün alarmı değil. Tartı uyuşmazlığı, tartı telemetrisi gerektirir.
      </div>

      <CheckoutConsole sessions={checkouts} />
    </div>
  );
}
