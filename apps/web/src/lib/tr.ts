/**
 * Türkçe etiket ve metin katmanı.
 *
 * Arayüz tamamen Türkçe; depolanan veriler (olay tipleri, enum'lar, açıklamalar)
 * İngilizce kalır ve burada görüntülenirken Türkçeye çevrilir. Böylece backend/
 * kontratlar değişmeden UI Türkçeleşir.
 */

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

export const DECISION_TR: Record<string, string> = {
  CONFIRMED_OPERATIONAL_ANOMALY: "Operasyonel anomali doğrulandı",
  FALSE_POSITIVE: "Yanlış alarm",
  INSUFFICIENT_EVIDENCE: "Yetersiz kanıt",
  RESOLVED_BY_STAFF: "Personel çözdü",
};

export const ZONE_TYPE_TR: Record<string, string> = {
  SHELF_DISPLAY: "Raf teşhir",
  PICKUP_INTERACTION: "Alım etkileşimi",
  OCCLUSION_UNKNOWN: "Görüş engeli (bilinmiyor)",
  AISLE_EXIT: "Reyon çıkışı",
  SCAN_AREA: "Tarama alanı",
  BAGGING_SCALE_AREA: "Bagaj/tartı alanı",
  BASKET_CART_AREA: "Sepet/araba alanı",
  EXIT_SIDE: "Çıkış tarafı",
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

export const MISSING_FLAG_TR: Record<string, string> = {
  scanner_feed_unavailable: "Tarayıcı/POS akışı yok",
  scanner_feed_delayed: "Tarayıcı/POS akışı gecikti",
  camera_offline: "Kamera çevrimdışı",
  shelf_zone_occluded: "Raf bölgesi görüş engeli",
};

/** Olay tipine göre tarafsız Türkçe açıklama (backend'in İngilizce metni yerine). */
export const EXPLANATION_TR: Record<string, string> = {
  SHELF_ITEM_REMOVED_UNRESOLVED:
    "Raf teşhir bölgesinden bir ürün alındı ve belirlenen süre içinde yerine dönmedi. " +
    "Bu bir hırsızlık kanıtı DEĞİLDİR — meşru bir alım, reyon dolumu veya görüş engeli olabilir. " +
    "İnsan incelemesi gerekir.",
  SHELF_OCCLUSION_REVIEW:
    "Raf bölgesi başka bir müşteri tarafından kapatıldı. Alım iddia edilmez; " +
    "görüş engeli süresince bölge BİLİNMİYOR olarak işaretlenir.",
  ITEM_PLACED_NOT_SCANNED:
    "Sağlıklı (SİMÜLE) bir POS oturumunda, bagaj alanında bir ürün gözlendi ama zaman " +
    "penceresinde eşleşen tarama bulunamadı. İnceleme için işaretlendi — bir suçlama değildir.",
  ITEM_MOVED_UNRESOLVED:
    "Bir ürün, karşılık gelen bir işlem olmadan bagaj alanından çıktı. İnceleme gerekir; suçlama değildir.",
  SCALE_MISMATCH_REVIEW:
    "Simüle edilen kararlı tartı ağırlığı, taranan ürün için tolerans dışında kaldı. " +
    "Manav ürünü, istifleme, ambalaj veya dara olabilir — inceleme gerekir.",
  TRANSACTION_RECONCILIATION_REQUIRED:
    "İşlem kapanışında bir veya daha fazla gözlenen ürün; tarama, iptal, ödeme ve tartı ile " +
    "mutabık kalmadı. Mutabakat incelemesi gerekir.",
  TRANSACTION_DATA_MISSING:
    "Tarayıcı/POS akışı yok veya gecikti; tarama doğrulanamadı. Temel kurala göre bu durum " +
    "BİLİNMİYOR'dur — taranmamış ürün alarmı ÜRETİLMEZ. Yalnızca entegrasyon uyarısı.",
  TRANSACTION_UNKNOWN:
    "İşlem, eksik/çelişkili entegrasyon sinyalleriyle kapandı; sonuç BİLİNMİYOR. Hiçbir ihlal iddia edilmez.",
};

export const CHECKOUT_STATE_TR: Record<string, string> = {
  IDLE: "Boşta",
  SESSION_ACTIVE: "Oturum aktif",
  ITEM_PRESENTED: "Ürün sunuldu",
  SCAN_OBSERVED: "Tarama gözlendi",
  BAGGING_OBSERVED: "Bagaj gözlendi",
  SCALE_STABLE: "Tartı kararlı",
  PAYMENT_PENDING: "Ödeme bekliyor",
  PAID: "Ödendi",
  SESSION_CLOSED: "Oturum kapandı",
};

export const TXN_KIND_TR: Record<string, string> = {
  payment_authorized: "Ödeme onaylandı",
  payment_declined: "Ödeme reddedildi",
  completed: "Tamamlandı",
  void: "İptal",
  attendant_override: "Görevli onayı",
};

export const SOURCE_TR: Record<string, string> = {
  live: "canlı (SSE)",
  sample: "örnek · çevrimdışı",
};

/** Kaynak rozeti (kamera kaynağı / olay sağlayıcısı). */
export const SOURCE_BADGE_TR: Record<string, string> = {
  rtsp: "CANLI",
  file: "DOSYA DEMO",
  synthetic: "SİMÜLASYON",
  LIVE: "CANLI",
  "FILE DEMO": "DOSYA DEMO",
  SIMULATED: "SİMÜLASYON",
};

export const UI = {
  appName: "StoreGuard",
  tagline: "Kayıp-önleme demo",
  banner:
    "SİMÜLASYON · Gerçek kamera, POS, tarayıcı veya tartı bağlı değil. " +
    "Her alarm bir insan-inceleme görevidir; kimse etiketlenmez.",
  sidebarNote:
    "Demo yapısı. Raf/checkout olayları DOSYA DEMO görüntü hattından (YOLO + ByteTrack) gelir; " +
    "POS/tartı SİMÜLASYON.",
  neutralNote: "İnceleme görevidir; bir suçlama değildir.",
  nav: {
    overview: "Genel Bakış",
    alerts: "Alarmlar",
    cameras: "Kameralar",
    checkouts: "Self-checkout",
  },
  common: {
    camera: "Kamera",
    zone: "Bölge",
    status: "Durum",
    detected: "Algılandı",
    humanReview: "İnsan incelemesi",
    required: "GEREKLİ",
    no: "hayır",
    backToAlerts: "← Alarmlara dön",
    none: "yok",
    simulated: "SİMÜLASYON",
    live: "CANLI",
    recording: "KAYIT",
  },
};

/** Güvenli çeviri: haritada yoksa ham anahtarı döndürür. */
export function trLabel(map: Record<string, string>, key: string | null | undefined): string {
  if (!key) return "—";
  return map[key] ?? key;
}

/** Olayın kaynak etiketi: görüntü hattı → DOSYA DEMO, diğer → SİMÜLASYON. */
export function eventSourceLabel(modelVersion?: string | null): string {
  if (modelVersion && /yolo|DEMO-PRODUCT-DETECTOR/i.test(modelVersion)) return "DOSYA DEMO";
  return "SİMÜLASYON";
}

/** ISO tarihten "11 saat önce" biçiminde göreli Türkçe zaman. */
export function relativeTimeTr(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "—";
  const s = Math.max(0, Math.floor((Date.now() - then) / 1000));
  if (s < 60) return "az önce";
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} dakika önce`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} saat önce`;
  const d = Math.floor(h / 24);
  return `${d} gün önce`;
}
