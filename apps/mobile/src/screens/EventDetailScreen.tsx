import { useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import type { AnomalyEvent } from "@storeguard/contracts";

import { colors } from "../theme";
import { Button, SeverityBadge, SimulatedTag } from "../ui";

export function EventDetailScreen({
  event,
  onBack,
}: {
  event: AnomalyEvent;
  onBack: () => void;
}) {
  const [decision, setDecision] = useState<string | null>(null);

  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.back} onPress={onBack}>
        ← Back to inbox
      </Text>

      <View style={styles.badges}>
        <SeverityBadge severity={event.severity} />
        {event.simulated ? <SimulatedTag /> : null}
      </View>
      <Text style={styles.title}>{event.event_type}</Text>
      <Text style={styles.explain}>{event.explanation}</Text>

      <View style={styles.card}>
        <Row label="Event ID" value={event.event_id} />
        <Row label="Camera" value={event.camera_id} />
        <Row label="Zone" value={event.zone_id ?? "—"} />
        <Row label="Status" value={decision ? `${event.status} → ${decision}` : event.status} />
        <Row label="Human review" value={event.human_review_required ? "REQUIRED" : "no"} />
        <Row label="Rule version" value={event.rule_version ?? "—"} />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Reason codes</Text>
        <Text style={styles.codes}>{event.reason_codes.join(", ") || "—"}</Text>
        {event.missing_data_flags.length > 0 ? (
          <>
            <Text style={[styles.cardTitle, { marginTop: 10 }]}>Missing signals</Text>
            <Text style={styles.warn}>⚠ {event.missing_data_flags.join(", ")}</Text>
          </>
        ) : null}
      </View>

      <Text style={styles.cardTitle}>Review action</Text>
      <View style={styles.actions}>
        <Button label="Acknowledge" onPress={() => setDecision("ACKNOWLEDGED")} />
        <Button label="Resolve" tone="accent" onPress={() => setDecision("RESOLVED")} />
        <Button label="Dismiss" onPress={() => setDecision("DISMISSED")} />
      </View>
      <Text style={styles.note}>
        Local demo action only (not yet persisted). The API exposes acknowledge / resolve /
        dismiss with an audit trail.
      </Text>
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
  badges: { flexDirection: "row", gap: 8, marginBottom: 8 },
  title: { color: "#fff", fontSize: 20, fontWeight: "800" },
  explain: { color: colors.text, marginTop: 8, lineHeight: 20, fontSize: 13 },
  card: { backgroundColor: colors.panel, borderColor: colors.edge, borderWidth: 1, borderRadius: 12, padding: 14, marginTop: 14 },
  cardTitle: { color: colors.muted, fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginTop: 14, marginBottom: 6 },
  codes: { color: colors.text, fontSize: 13 },
  warn: { color: colors.amber, fontSize: 13 },
  row: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 4 },
  rowLabel: { color: colors.muted, fontSize: 13 },
  rowValue: { color: colors.text, fontSize: 13, flexShrink: 1, textAlign: "right", marginLeft: 12 },
  actions: { flexDirection: "row", gap: 8 },
  note: { color: colors.muted, fontSize: 11, marginTop: 10, lineHeight: 16 },
});
