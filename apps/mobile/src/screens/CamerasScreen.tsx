import { ScrollView, StyleSheet, Text, View } from "react-native";

import { SAMPLE_CAMERAS } from "../sample";
import { colors, stateColor } from "../theme";
import { STATE_TR, trLabel, UI } from "../tr";

const KIND_TR: Record<string, string> = { shelf: "Raf", checkout: "Self-checkout" };

export function CamerasScreen() {
  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.title}>{UI.cameras.title}</Text>
      <Text style={styles.sub}>{UI.cameras.sub}</Text>

      {SAMPLE_CAMERAS.map((c) => (
        <View key={c.camera_id} style={styles.row}>
          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{c.name}</Text>
            <Text style={styles.meta}>
              {c.camera_id} · {KIND_TR[c.kind] ?? c.kind}
            </Text>
          </View>
          <View style={{ alignItems: "flex-end" }}>
            <Text style={[styles.state, { color: stateColor[c.state] ?? colors.muted }]}>
              ● {trLabel(STATE_TR, c.state)}
            </Text>
            <Text style={styles.meta}>FPS {c.fps ?? "—"}</Text>
          </View>
        </View>
      ))}

      <View style={styles.offline}>
        <Text style={styles.offlineTitle}>Çevrimdışı / hata durumu</Text>
        <Text style={styles.offlineText}>
          Cihaz API'yi kaybettiğinde uygulama, son bilinen SİMÜLASYON verisini net bir bant ile
          gösterir ve asla sahte canlı durum üretmez.
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
