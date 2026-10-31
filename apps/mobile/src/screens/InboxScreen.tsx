import { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import type { AnomalyEvent } from "@storeguard/contracts";

import { fetchEvents, sourceLabel, type DataSource } from "../api";
import { colors } from "../theme";
import { EVENT_TYPE_TR, STATUS_TR, trLabel, UI } from "../tr";
import { SeverityBadge, SourceTag } from "../ui";

const POLL_MS = 5000;

export function InboxScreen({ onOpen }: { onOpen: (e: AnomalyEvent) => void }) {
  const [events, setEvents] = useState<AnomalyEvent[] | null>(null);
  const [source, setSource] = useState<DataSource>("sample");
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const r = await fetchEvents();
    setEvents(r.data);
    setSource(r.source);
  }, []);

  // In-app realtime refresh by polling (RN has no EventSource); plus pull-to-refresh.
  const savedLoad = useRef(load);
  savedLoad.current = load;
  useEffect(() => {
    void savedLoad.current();
    const id = setInterval(() => void savedLoad.current(), POLL_MS);
    return () => clearInterval(id);
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  if (!events) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={colors.accent} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.wrap}
      contentContainerStyle={{ padding: 16 }}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>{UI.inbox.title}</Text>
        <Text style={styles.source}>{source === "live" ? UI.inbox.live : UI.inbox.offline}</Text>
      </View>
      <Text style={styles.sub}>
        {events.length} {UI.inbox.sub}
      </Text>

      {events.map((e) => (
        <Pressable key={e.event_id} style={styles.row} onPress={() => onOpen(e)}>
          <View style={styles.rowTop}>
            <SeverityBadge severity={e.severity} />
            <SourceTag label={sourceLabel(e)} />
            {e.missing_data_flags.length > 0 ? (
              <Text style={styles.missing}>{UI.inbox.missing}</Text>
            ) : null}
          </View>
          <Text style={styles.type}>{trLabel(EVENT_TYPE_TR, e.event_type)}</Text>
          <Text style={styles.meta}>
            {e.camera_id} · {trLabel(STATUS_TR, e.status)}
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
  rowTop: { flexDirection: "row", alignItems: "center", gap: 8, flexWrap: "wrap" },
  missing: { color: colors.muted, fontSize: 10, backgroundColor: colors.edge, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  type: { color: colors.text, fontWeight: "700", marginTop: 8 },
  meta: { color: colors.muted, fontSize: 12, marginTop: 2 },
});
