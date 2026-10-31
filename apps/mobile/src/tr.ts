/** Türkçe etiket ve metin katmanı (mobil). Web lib/tr.ts ile aynı amaç. */

export const EVENT_TYPE_TR: Record<string, string> = {
  SHELF_ITEM_REMOVED_UNRESOLVED: "Raftan alınan ürün — çözülmedi",
  SHELF_OCCLUSION_REVIEW: "Raf görüşü engellendi — inceleme",
  ITEM_PLACED_NOT_SCANNED: "Taranmamış ürün — incelenmeli",
  ITEM_MOVED_UNRESOLVED: "Ürün taşındı — çözülmedi",
  SCALE_MISMATCH_REVIEW: "Tartı uyuşmazlığı — inceleme",
  TRANSACTION_RECONCILIATION_REQUIRED: "İşlem mutabakatı gerekli",
  TRANSACTION_DATA_MISSING: "İşlem verisi eksik — BİLİNMİYOR",
  TRANSACTION_UNKNOWN: "İşlem sonucu BİLİNMİYOR",
};

export const SEVERITY_TR: Record<string, string> = {
  INFO: "Bilgi",
  REVIEW: "İnceleme",
  HIGH_REVIEW: "Öncelikli inceleme",
};

export const STATUS_TR: Record<string, string> = {
  OPEN: "Açık",
  ACKNOWLEDGED: "Alındı",
  RESOLVED: "Çözüldü",
  DISMISSED: "Kapatıldı",
};

export const STATE_TR: Record<string, string> = {
  ONLINE: "Çevrimiçi",
  DEGRADED: "Düşük",
  OFFLINE: "Çevrimdışı",
  UNKNOWN: "Bilinmiyor",
};

export const REASON_TR: Record<string, string> = {
  item_in_bagging_zone: "Ürün bagaj alanında gözlendi",
  no_matching_scan_in_window: "Zaman penceresinde eşleşen tarama yok",
  item_absent_over_threshold: "Ürün eşik süresi boyunca yok",
  person_interaction_nearby: "Yakında kişi etkileşimi",
  weight_outside_tolerance: "Ağırlık tolerans dışında",
  scanner_feed_unavailable: "Tarayıcı/POS akışı yok",
  scanner_feed_delayed: "Tarayıcı/POS akışı gecikti",
  zone_occluded: "Bölge görüşü engellendi",
  item_moved_without_transaction: "Ürün işlemsiz taşındı",
  unmatched_item_at_transaction_close: "İşlem kapanışında eşleşmeyen ürün",
  missing_or_contradictory_signals: "Eksik/çelişkili sinyaller",
};

export const EXPLANATION_TR: Record<string, string> = {
  SHELF_ITEM_REMOVED_UNRESOLVED:
    "Raf teşhir bölgesinden bir ürün alındı ve belirlenen süre içinde yerine dönmedi. " +
    "Bu bir hırsızlık kanıtı DEĞİLDİR — meşru alım, reyon dolumu veya görüş engeli olabilir. İnsan incelemesi gerekir.",
  SHELF_OCCLUSION_REVIEW:
    "Raf bölgesi başka müşteri tarafından kapatıldı. Alım iddia edilmez; bölge BİLİNMİYOR.",
  ITEM_PLACED_NOT_SCANNED:
    "Sağlıklı (SİMÜLE) POS oturumunda bagaj alanında ürün gözlendi ama pencerede eşleşen tarama yok. " +
    "İnceleme için işaretlendi — bir suçlama değildir.",
  ITEM_MOVED_UNRESOLVED:
    "Bir ürün, karşılık gelen işlem olmadan bagaj alanından çıktı. İnceleme gerekir; suçlama değildir.",
  SCALE_MISMATCH_REVIEW:
    "Simüle kararlı tartı ağırlığı, taranan ürün için tolerans dışında. Manav, istif, ambalaj veya dara olabilir — inceleme gerekir.",
  TRANSACTION_RECONCILIATION_REQUIRED:
    "İşlem kapanışında bir veya daha fazla gözlenen ürün tarama/iptal/ödeme/tartı ile mutabık kalmadı. Mutabakat gerekir.",
  TRANSACTION_DATA_MISSING:
    "Tarayıcı/POS akışı yok veya gecikti. Temel kurala göre bu BİLİNMİYOR'dur — taranmamış-ürün alarmı üretilmez.",
  TRANSACTION_UNKNOWN:
    "İşlem, eksik/çelişkili sinyallerle kapandı; sonuç BİLİNMİYOR. Hiçbir ihlal iddia edilmez.",
};

export const UI = {
  banner: "SİMÜLASYON · her alarm insan incelemesi gerektirir",
  login: {
    tagline: "Kayıp-önleme incelemesi — mobil demo",
    mockLabel: "Sahte giriş (yalnızca yerel demo)",
    enter: "Demoya gir",
    note:
      "Gerçek kimlik doğrulama yok. Üretim sürümü, kısa ömürlü medya erişimli kimlik doğrulamalı API kullanır ve kamera URL'lerini ifşa etmez.",
    footer: "Tüm veriler SİMÜLASYON · demo yapısı",
  },
  tabs: { inbox: "Alarmlar", cameras: "Kameralar" },
  inbox: { title: "Alarmlar", sub: "olay · tümü insan incelemesi gerektirir", live: "● canlı (5sn)", offline: "○ örnek · çevrimdışı", missing: "veri eksik" },
  detail: {
    back: "← Alarmlara dön",
    evidence: "Kanıt klibi",
    evidenceNote: "Kimlik doğrulamalı, kısa ömürlü URL · insan incelemesi gerekir. Bölge dışı karartılır.",
    noEvidence: "Bu olay için kanıt klibi yok.",
    eventId: "Olay ID",
    camera: "Kamera",
    zone: "Bölge",
    status: "Durum",
    humanReview: "İnsan incelemesi",
    required: "GEREKLİ",
    no: "hayır",
    ruleVersion: "Kural sürümü",
    reasonCodes: "Neden kodları",
    missingSignals: "Eksik sinyaller",
    reviewTitle: "İnceleme (API ile kalıcı)",
    reviewer: "inceleyen",
    reason: "gerekçe (doğrula/yanlış alarm için zorunlu)",
    ack: "İncelemeye al",
    resolve: "Doğrula",
    dismiss: "Yanlış alarm",
    reviewerRequired: "İnceleyen gerekli.",
    reasonRequired: "Doğrula/yanlış alarm için gerekçe zorunlu.",
    serverStatus: "Sunucu durumu",
  },
  cameras: { title: "Kameralar", sub: "SİMÜLASYON durumlar + çevrimdışı/hata notu" },
  sourceFileDemo: "DOSYA DEMO",
  sourceSimulated: "SİMÜLASYON",
};

export function trLabel(map: Record<string, string>, key: string | null | undefined): string {
  if (!key) return "—";
  return map[key] ?? key;
}
