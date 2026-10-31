import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import type { AnomalyEvent } from "@storeguard/contracts";

import {
  API_BASE,
  acknowledgeEvent,
  dismissEvent,
  fetchEvent,
  resolveEvent,
  sourceLabel,
} from "../api";
import { colors } from "../theme";
import {
  EVENT_TYPE_TR,
  EXPLANATION_TR,
  REASON_TR,
  STATUS_TR,
  trLabel,
  UI,
} from "../tr";
import { Button, SeverityBadge, SimulatedTag, SourceTag } from "../ui";

export function EventDetailScreen({
  event,
  onBack,
}: {
  event: AnomalyEvent;
  onBack: () => void;
}) {
  // Server-authoritative: the passed event is only the initial render; we refetch.
  const [current, setCurrent] = useState<AnomalyEvent>(event);
  const [reviewer, setReviewer] = useState("mobile-reviewer");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);

  const refresh = useCallback(async () => {
    const { data } = await fetchEvent(event.event_id);
    if (data) setCurrent(data);
  }, [event.event_id]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function run(action: "acknowledge" | "resolve" | "dismiss") {
    if (!reviewer.trim()) {
      setMessage({ ok: false, text: UI.detail.reviewerRequired });
      return;
    }
    if (action !== "acknowledge" && !reason.trim()) {
      setMessage({ ok: false, text: UI.detail.reasonRequired });
      return;
    }
    setBusy(true);
    setMessage(null);
    const res =
      action === "acknowledge"
        ? await acknowledgeEvent(current.event_id, reviewer.trim())
        : action === "resolve"
          ? await resolveEvent(current.event_id, reviewer.trim(), reason.trim())
          : await dismissEvent(current.event_id, reviewer.trim(), reason.trim());
    setBusy(false);
    if (res.ok) {
      setCurrent(res.event);
      setMessage({ ok: true, text: `${UI.detail.serverStatus}: ${trLabel(STATUS_TR, res.event.status)}` });
    } else {
      setMessage({ ok: false, text: res.error });
      void refresh(); // stay server-authoritative even on failure
    }
  }

  const ref = current.evidence?.[0];
  const evidenceUri = ref?.available && ref.url ? `${API_BASE}${ref.url}` : null;

  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.back} onPress={onBack}>
        {UI.detail.back}
      </Text>

      <View style={styles.badges}>
        <SeverityBadge severity={current.severity} />
        <SourceTag label={sourceLabel(current)} />
        {current.simulated ? <SimulatedTag /> : null}
      </View>
      <Text style={styles.title}>{trLabel(EVENT_TYPE_TR, current.event_type)}</Text>
      <Text style={styles.explain}>
        {EXPLANATION_TR[current.event_type] ?? current.explanation}
      </Text>

      <View style={styles.card}>
        <Row label={UI.detail.eventId} value={current.event_id} />
        <Row label={UI.detail.camera} value={current.camera_id} />
        <Row label={UI.detail.zone} value={current.zone_id ?? "—"} />
        <Row label={UI.detail.status} value={trLabel(STATUS_TR, current.status)} />
        <Row
          label={UI.detail.humanReview}
          value={current.human_review_required ? UI.detail.required : UI.detail.no}
        />
        <Row label={UI.detail.ruleVersion} value={current.rule_version ?? "—"} />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>{UI.detail.evidence}</Text>
        {evidenceUri ? (
          <>
            <Image source={{ uri: evidenceUri }} style={styles.evidence} resizeMode="contain" />
            <Text style={styles.note}>{UI.detail.evidenceNote}</Text>
          </>
        ) : (
          <Text style={styles.note}>{UI.detail.noEvidence}</Text>
        )}
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>{UI.detail.reasonCodes}</Text>
        <Text style={styles.codes}>
          {current.reason_codes.map((r) => trLabel(REASON_TR, r)).join(", ") || "—"}
        </Text>
        {current.missing_data_flags.length > 0 ? (
          <>
            <Text style={[styles.cardTitle, { marginTop: 10 }]}>{UI.detail.missingSignals}</Text>
            <Text style={styles.warn}>
              ⚠ {current.missing_data_flags.map((m) => trLabel(REASON_TR, m)).join(", ")}
            </Text>
          </>
        ) : null}
      </View>

      <Text style={styles.cardTitle}>{UI.detail.reviewTitle}</Text>
      <TextInput
        style={styles.input}
        value={reviewer}
        onChangeText={setReviewer}
        placeholder={UI.detail.reviewer}
        placeholderTextColor={colors.muted}
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        value={reason}
        onChangeText={setReason}
        placeholder={UI.detail.reason}
        placeholderTextColor={colors.muted}
      />
      <View style={styles.actions}>
        <Button label={UI.detail.ack} onPress={() => void run("acknowledge")} />
        <Button label={UI.detail.resolve} tone="accent" onPress={() => void run("resolve")} />
        <Button label={UI.detail.dismiss} onPress={() => void run("dismiss")} />
      </View>
      {busy ? <ActivityIndicator color={colors.accent} style={{ marginTop: 10 }} /> : null}
      {message ? (
        <Text style={[styles.msg, { color: message.ok ? colors.accent : colors.amber }]}>
          {message.text}
        </Text>
      ) : null}
    </ScrollView>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.ink },
  back: { color: colors.accent, marginBottom: 12 },
  badges: { flexDirection: "row", gap: 8, marginBottom: 8, flexWrap: "wrap" },
  title: { color: "#fff", fontSize: 20, fontWeight: "800" },
  explain: { color: colors.text, marginTop: 8, lineHeight: 20, fontSize: 13 },
  card: { backgroundColor: colors.panel, borderColor: colors.edge, borderWidth: 1, borderRadius: 12, padding: 14, marginTop: 14 },
  cardTitle: { color: colors.muted, fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginTop: 14, marginBottom: 6 },
  codes: { color: colors.text, fontSize: 13 },
  warn: { color: colors.amber, fontSize: 13 },
  evidence: { width: "100%", height: 180, borderRadius: 8, backgroundColor: colors.ink },
  row: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 4 },
  rowLabel: { color: colors.muted, fontSize: 13 },
  rowValue: { color: colors.text, fontSize: 13, flexShrink: 1, textAlign: "right", marginLeft: 12 },
  input: { backgroundColor: colors.panel, borderColor: colors.edge, borderWidth: 1, borderRadius: 8, color: colors.text, paddingHorizontal: 12, paddingVertical: 10, marginTop: 8, fontSize: 13 },
  actions: { flexDirection: "row", gap: 8, marginTop: 10 },
  note: { color: colors.muted, fontSize: 11, marginTop: 8, lineHeight: 16 },
  msg: { fontSize: 13, marginTop: 10, fontWeight: "600" },
});
