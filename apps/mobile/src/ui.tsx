import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, severityColor } from "./theme";

export function SeverityBadge({ severity }: { severity: string }) {
  const c = severityColor[severity] ?? colors.muted;
  return (
    <View style={[styles.badge, { borderColor: c }]}>
      <Text style={[styles.badgeText, { color: c }]}>{severity}</Text>
    </View>
  );
}

export function SimulatedTag() {
  return (
    <View style={[styles.badge, { borderColor: colors.amber }]}>
      <Text style={[styles.badgeText, { color: colors.amber }]}>SIMULATED</Text>
    </View>
  );
}

export function SourceTag({ label }: { label: "FILE DEMO" | "SIMULATED" }) {
  const c = label === "FILE DEMO" ? colors.accent : colors.amber;
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
