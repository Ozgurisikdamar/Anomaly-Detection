import { StyleSheet, Text, View } from "react-native";

import { colors } from "../theme";
import { UI } from "../tr";
import { Button } from "../ui";

export function LoginScreen({ onEnter }: { onEnter: () => void }) {
  return (
    <View style={styles.wrap}>
      <Text style={styles.logo}>StoreGuard</Text>
      <Text style={styles.sub}>{UI.login.tagline}</Text>

      <View style={styles.card}>
        <Text style={styles.label}>{UI.login.mockLabel}</Text>
        <Text style={styles.value}>reviewer@demo.local</Text>
        <View style={{ height: 14 }} />
        <Button label={UI.login.enter} tone="accent" onPress={onEnter} />
        <Text style={styles.note}>{UI.login.note}</Text>
      </View>

      <Text style={styles.footer}>{UI.login.footer}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.ink, alignItems: "center", justifyContent: "center", padding: 24 },
  logo: { color: "#fff", fontSize: 30, fontWeight: "800" },
  sub: { color: colors.muted, marginTop: 6, marginBottom: 28 },
  card: { width: "100%", maxWidth: 360, backgroundColor: colors.panel, borderColor: colors.edge, borderWidth: 1, borderRadius: 14, padding: 18 },
  label: { color: colors.muted, fontSize: 12, textTransform: "uppercase", letterSpacing: 1 },
  value: { color: colors.text, fontSize: 16, marginTop: 4 },
  note: { color: colors.muted, fontSize: 11, marginTop: 12, lineHeight: 16 },
  footer: { color: colors.muted, fontSize: 11, marginTop: 24 },
});
