/**
 * Offline SIMULATED sample for the mobile scaffold (mirrors the API seed).
 * Lets the app render without the backend — useful for review and screenshots.
 * All data is SIMULATED; no real camera / POS / scale.
 */
import type { AnomalyEvent } from "@storeguard/contracts";

export const SAMPLE_EVENTS: AnomalyEvent[] = [
  {
    event_id: "evt_sco_not_scanned_01",
    store_id: "store_demo_01",
    camera_id: "cam_sco_01",
    zone_id: "zone_sco_01_bag",
    event_type: "ITEM_PLACED_NOT_SCANNED",
    severity: "HIGH_REVIEW",
    status: "OPEN",
    occurred_at: "2026-10-30T09:08:00Z",
    detected_at: "2026-10-30T09:08:00Z",
    created_at: "2026-10-30T09:08:00Z",
    track_refs: ["trk_b1c2"],
    evidence: [],
    model_version: "scaffold-0 (no model run)",
    tracker_version: "scaffold-0",
    rule_version: "phase0-demo",
    confidence: { detector: 0.82, track_quality: 0.74, zone_certainty: 0.88, pos_synchronization: 0.9, rule_evidence: 0.7 },
    reason_codes: ["item_in_bagging_zone", "no_matching_scan_in_window"],
    missing_data_flags: [],
    explanation:
      "An item was observed in the bagging zone with no matching scan within the window on a HEALTHY simulated POS session. Flagged for review — not an accusation.",
    human_review_required: true,
    review: null,
    simulated: true,
  },
  {
    event_id: "evt_shelf_removed_01",
    store_id: "store_demo_01",
    camera_id: "cam_shelf_01",
    zone_id: "zone_shelf_01_display",
    event_type: "SHELF_ITEM_REMOVED_UNRESOLVED",
    severity: "REVIEW",
    status: "OPEN",
    occurred_at: "2026-10-30T09:02:00Z",
    detected_at: "2026-10-30T09:02:00Z",
    created_at: "2026-10-30T09:02:00Z",
    track_refs: ["trk_a3f9"],
    evidence: [],
    model_version: "scaffold-0 (no model run)",
    tracker_version: "scaffold-0",
    rule_version: "phase0-demo",
    confidence: { detector: 0.71, track_quality: 0.63, zone_certainty: 0.8, pos_synchronization: null, rule_evidence: 0.55 },
    reason_codes: ["item_absent_over_threshold", "person_interaction_nearby"],
    missing_data_flags: [],
    explanation:
      "An item left Shelf A display zone and did not reappear within the configured interval. This is NOT proof of theft — it may be a legitimate pickup, replenishment or occlusion. Requires human review.",
    human_review_required: true,
    review: null,
    simulated: true,
  },
  {
    event_id: "evt_sco_data_missing_01",
    store_id: "store_demo_01",
    camera_id: "cam_sco_02",
    zone_id: null,
    event_type: "TRANSACTION_DATA_MISSING",
    severity: "INFO",
    status: "OPEN",
    occurred_at: "2026-10-30T09:13:00Z",
    detected_at: "2026-10-30T09:13:00Z",
    created_at: "2026-10-30T09:13:00Z",
    track_refs: [],
    evidence: [],
    model_version: "scaffold-0 (no model run)",
    tracker_version: "scaffold-0",
    rule_version: "phase0-demo",
    confidence: { detector: null, track_quality: null, zone_certainty: null, pos_synchronization: null, rule_evidence: null },
    reason_codes: ["scanner_feed_unavailable"],
    missing_data_flags: ["scanner_feed_unavailable", "camera_offline"],
    explanation:
      "Scanner/POS feed was unavailable for SCO 2 (camera also OFFLINE). Per the core rule, missing integration data is UNKNOWN — NO non-scan alert is emitted. Integration warning only.",
    human_review_required: true,
    review: null,
    simulated: true,
  },
];

export const SAMPLE_CAMERAS = [
  { camera_id: "cam_shelf_01", name: "Aisle 3 — Shelf A", kind: "shelf", state: "ONLINE", fps: 11.8 },
  { camera_id: "cam_shelf_02", name: "Aisle 5 — Shelf C", kind: "shelf", state: "DEGRADED", fps: 4.1 },
  { camera_id: "cam_sco_01", name: "Self-checkout 1", kind: "checkout", state: "ONLINE", fps: 14.2 },
  { camera_id: "cam_sco_02", name: "Self-checkout 2", kind: "checkout", state: "OFFLINE", fps: null },
];
