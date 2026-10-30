import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import type { AnomalyEvent } from "@storeguard/contracts";

import { fetchEvents, type DataSource } from "../api";
import { colors } from "../theme";
import { SeverityBadge } from "../ui";

export function InboxScreen({ onOpen }: { onOpen: (e: AnomalyEvent) => void }) {
  const [events, setEvents] = useState<AnomalyEvent[] | null>(null);
  const [source, setSource] = useState<DataSource>("sample");

  useEffect(() => {
    let active = true;
    fetchEvents().then((r) => {
      if (!active) return;
      setEvents(r.data);
      setSource(r.source);
    });
    return () => {
      active = false;
    };
  }, []);

  if (!events) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={colors.accent} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16 }}>
      <View style={styles.header}>
        <Text style={styles.title}>Alerts inbox</Text>
        <Text style={styles.source}>{source === "live" ? "live API" : "sample / offline"}</Text>
      </View>
      <Text style={styles.sub}>{events.length} events · all require human review</Text>

      {events.map((e) => (
        <Pressable key={e.event_id} style={styles.row} onPress={() => onOpen(e)}>
          <View style={styles.rowTop}>
            <SeverityBadge severity={e.severity} />
            {e.missing_data_flags.length > 0 ? (
              <Text style={styles.missing}>missing data</Text>
            ) : null}
          </View>
          <Text style={styles.type}>{e.event_type}</Text>
          <Text style={styles.meta}>
            {e.camera_id} · {e.status}
          </Text>
        </Pressable>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.ink },
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.ink },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { color: "#fff", fontSize: 22, fontWeight: "800" },
  source: { color: colors.muted, fontSize: 12 },
  sub: { color: colors.muted, marginBottom: 12, marginTop: 2 },
  row: { backgroundColor: colors.panel, borderColor: colors.edge, borderWidth: 1, borderRadius: 12, padding: 14, marginBottom: 10 },
  rowTop: { flexDirection: "row", alignItems: "center", gap: 8 },
  missing: { color: colors.muted, fontSize: 10, backgroundColor: colors.edge, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  type: { color: colors.text, fontWeight: "700", marginTop: 8 },
  meta: { color: colors.muted, fontSize: 12, marginTop: 2 },
});
