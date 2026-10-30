/**
 * StoreGuard shared TypeScript types.
 *
 * This file MIRRORS the Pydantic models in
 * `packages/contracts/python/src/storeguard_contracts` which are the single
 * source of truth. Keep the two in sync by hand (a generator is a Phase 7
 * hardening item). Identifiers and enum string values must match exactly.
 *
 * Product invariants mirrored here:
 * - Events describe observable anomalies, never intent.
 * - `human_review_required` is always true.
 * - Integration signals carry `simulated`.
 * - Missing data is explicit and maps to *_DATA_MISSING / *_UNKNOWN types.
 */

export type Severity = "INFO" | "REVIEW" | "HIGH_REVIEW";

export type EventStatus = "OPEN" | "ACKNOWLEDGED" | "RESOLVED" | "DISMISSED";

export type EventType =
  | "SHELF_ITEM_REMOVED_UNRESOLVED"
  | "SHELF_OCCLUSION_REVIEW"
  | "ITEM_PLACED_NOT_SCANNED"
  | "ITEM_MOVED_UNRESOLVED"
  | "SCALE_MISMATCH_REVIEW"
  | "TRANSACTION_RECONCILIATION_REQUIRED"
  | "TRANSACTION_DATA_MISSING"
  | "TRANSACTION_UNKNOWN";

export type ReviewDecision =
  | "CONFIRMED_OPERATIONAL_ANOMALY"
  | "FALSE_POSITIVE"
  | "INSUFFICIENT_EVIDENCE"
  | "RESOLVED_BY_STAFF";

export type CameraStreamState = "ONLINE" | "DEGRADED" | "OFFLINE" | "UNKNOWN";

export type ZoneType =
  | "SHELF_DISPLAY"
  | "PICKUP_INTERACTION"
  | "OCCLUSION_UNKNOWN"
  | "AISLE_EXIT"
  | "SCAN_AREA"
  | "BAGGING_SCALE_AREA"
  | "BASKET_CART_AREA"
  | "EXIT_SIDE";

export type CheckoutState =
  | "IDLE"
  | "SESSION_ACTIVE"
  | "ITEM_PRESENTED"
  | "SCAN_OBSERVED"
  | "BAGGING_OBSERVED"
  | "SCALE_STABLE"
  | "PAYMENT_PENDING"
  | "PAID"
  | "SESSION_CLOSED";

export interface Store {
  store_id: string;
  name: string;
  timezone: string;
}

export interface CameraZone {
  zone_id: string;
  camera_id: string;
  zone_type: ZoneType;
  label: string;
  polygon: [number, number][];
}

export interface Camera {
  camera_id: string;
  store_id: string;
  name: string;
  kind: string;
  source_kind: string;
  zones: CameraZone[];
}

export interface CameraStreamStatus {
  camera_id: string;
  state: CameraStreamState;
  fps: number | null;
  frame_age_ms: number | null;
  last_frame_at: string | null;
  reconnect_count: number;
  simulated: boolean;
}

export interface ConfidenceComponents {
  detector: number | null;
  track_quality: number | null;
  zone_certainty: number | null;
  pos_synchronization: number | null;
  rule_evidence: number | null;
}

export interface EvidenceRef {
  evidence_id: string;
  kind: string;
  available: boolean;
  // Short-lived authenticated URL minted by the API at read time; never a path.
  url?: string | null;
  expires_at?: string | null;
}

export interface ReviewOutcome {
  decision: ReviewDecision;
  reviewer: string;
  note: string | null;
  decided_at: string;
}

export interface AnomalyEvent {
  event_id: string;
  store_id: string;
  camera_id: string;
  zone_id: string | null;
  event_type: EventType;
  severity: Severity;
  status: EventStatus;
  occurred_at: string;
  detected_at: string;
  created_at: string;
  track_refs: string[];
  evidence: EvidenceRef[];
  model_version: string | null;
  tracker_version: string | null;
  rule_version: string | null;
  confidence: ConfidenceComponents;
  reason_codes: string[];
  missing_data_flags: string[];
  explanation: string;
  human_review_required: boolean;
  review: ReviewOutcome | null;
  simulated: boolean;
}

export interface ScanEvent {
  scan_id: string;
  terminal_id: string;
  session_id: string;
  sku: string;
  quantity: number;
  occurred_at: string;
  voided: boolean;
  simulated: boolean;
}

export interface ScaleEvent {
  scale_id: string;
  terminal_id: string;
  session_id: string;
  stable_weight_g: number | null;
  expected_weight_g: number | null;
  placement: string;
  calibration_ok: boolean;
  occurred_at: string;
  simulated: boolean;
}

export interface TransactionEvent {
  transaction_id: string;
  terminal_id: string;
  session_id: string;
  kind: string;
  occurred_at: string;
  simulated: boolean;
}

export interface CheckoutSession {
  terminal_id: string;
  store_id: string;
  session_id: string | null;
  state: CheckoutState;
  scans: ScanEvent[];
  scale_events: ScaleEvent[];
  transaction_events: TransactionEvent[];
  updated_at: string;
  simulated: boolean;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  phase: string;
  simulated_data: boolean;
  time: string;
}
