import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, severityColor } from "./theme";
import { SEVERITY_TR, trLabel } from "./tr";

export function SeverityBadge({ severity }: { severity: string }) {
  const c = severityColor[severity] ?? colors.muted;
  return (
    <View style={[styles.badge, { borderColor: c }]}>
      <Text style={[styles.badgeText, { color: c }]}>{trLabel(SEVERITY_TR, severity)}</Text>
    </View>
  );
}

export function SimulatedTag() {
  return (
    <View style={[styles.badge, { borderColor: colors.amber }]}>
      <Text style={[styles.badgeText, { color: colors.amber }]}>SİMÜLASYON</Text>
    </View>
  );
}

export function SourceTag({ label }: { label: string }) {
  const c = label === "DOSYA DEMO" ? colors.accent : colors.amber;
  return (
    <View style={[styles.badge, { borderColor: c }]}>
      <Text style={[styles.badgeText, { color: c }]}>{label}</Text>
    </View>
  );
}

export function Button({
  label,
  onPress,
  tone = "default",
}: {
  label: string;
  onPress?: () => void;
  tone?: "default" | "accent";
}) {
  return (
    <Pressable
      onPress={onPress}
      style={[styles.button, tone === "accent" ? { backgroundColor: colors.accent } : null]}
    >
      <Text style={styles.buttonText}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  badge: {
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
    alignSelf: "flex-start",
  },
  badgeText: { fontSize: 11, fontWeight: "600" },
  button: {
    backgroundColor: colors.edge,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    alignItems: "center",
  },
  buttonText: { color: colors.text, fontWeight: "600", fontSize: 13 },
});
