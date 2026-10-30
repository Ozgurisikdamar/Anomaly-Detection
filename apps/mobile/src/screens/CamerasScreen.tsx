import { ScrollView, StyleSheet, Text, View } from "react-native";

import { SAMPLE_CAMERAS } from "../sample";
import { colors, stateColor } from "../theme";

export function CamerasScreen() {
  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.title}>Camera health</Text>
      <Text style={styles.sub}>SIMULATED health · real FPS / frame-age arrive in Phase 2</Text>

      {SAMPLE_CAMERAS.map((c) => (
        <View key={c.camera_id} style={styles.row}>
          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{c.name}</Text>
            <Text style={styles.meta}>
              {c.camera_id} · {c.kind}
            </Text>
          </View>
          <View style={{ alignItems: "flex-end" }}>
            <Text style={[styles.state, { color: stateColor[c.state] ?? colors.muted }]}>
              ● {c.state}
            </Text>
            <Text style={styles.meta}>FPS {c.fps ?? "—"}</Text>
          </View>
        </View>
      ))}

      <View style={styles.offline}>
        <Text style={styles.offlineTitle}>Offline / error state</Text>
        <Text style={styles.offlineText}>
          When the device loses the API, the app shows the last known SIMULATED data with a
          clear banner and never fabricates live status.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.ink },
  title: { color: "#fff", fontSize: 22, fontWeight: "800" },
  sub: { color: colors.muted, marginBottom: 12, marginTop: 2 },
  row: { flexDirection: "row", backgroundColor: colors.panel, borderColor: colors.edge, borderWidth: 1, borderRadius: 12, padding: 14, marginBottom: 10 },
  name: { color: colors.text, fontWeight: "700" },
  meta: { color: colors.muted, fontSize: 12, marginTop: 2 },
  state: { fontWeight: "700" },
  offline: { marginTop: 14, borderColor: colors.edge, borderWidth: 1, borderStyle: "dashed", borderRadius: 12, padding: 14 },
  offlineTitle: { color: colors.muted, fontSize: 12, textTransform: "uppercase", letterSpacing: 1 },
  offlineText: { color: colors.text, fontSize: 13, marginTop: 6, lineHeight: 18 },
});
