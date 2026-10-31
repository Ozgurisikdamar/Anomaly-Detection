import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";

import type { AnomalyEvent } from "@storeguard/contracts";

import { CamerasScreen } from "./src/screens/CamerasScreen";
import { EventDetailScreen } from "./src/screens/EventDetailScreen";
import { InboxScreen } from "./src/screens/InboxScreen";
import { LoginScreen } from "./src/screens/LoginScreen";
import { colors } from "./src/theme";
import { UI } from "./src/tr";

type Tab = "inbox" | "cameras";

export default function App() {
  const [authed, setAuthed] = useState(false);
  const [tab, setTab] = useState<Tab>("inbox");
  const [selected, setSelected] = useState<AnomalyEvent | null>(null);

  let body: React.ReactNode;
  if (!authed) {
    body = <LoginScreen onEnter={() => setAuthed(true)} />;
  } else if (selected) {
    body = <EventDetailScreen event={selected} onBack={() => setSelected(null)} />;
  } else if (tab === "inbox") {
    body = <InboxScreen onOpen={setSelected} />;
  } else {
    body = <CamerasScreen />;
  }

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="light" />
      {/* Non-negotiable: demo data is always visibly labelled. */}
      <View style={styles.banner}>
        <Text style={styles.bannerText}>{UI.banner}</Text>
      </View>

      <View style={{ flex: 1 }}>{body}</View>

      {authed && !selected ? (
        <View style={styles.tabbar}>
          <TabButton label={UI.tabs.inbox} active={tab === "inbox"} onPress={() => setTab("inbox")} />
          <TabButton label={UI.tabs.cameras} active={tab === "cameras"} onPress={() => setTab("cameras")} />
        </View>
      ) : null}
    </SafeAreaView>
  );
}

function TabButton({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }) {
  return (
    <Pressable style={styles.tab} onPress={onPress}>
      <Text style={[styles.tabText, active ? { color: colors.accent } : null]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.ink },
  banner: { backgroundColor: "rgba(245,196,81,0.15)", paddingVertical: 6, alignItems: "center" },
  bannerText: { color: colors.amber, fontSize: 11, fontWeight: "600" },
  tabbar: { flexDirection: "row", borderTopColor: colors.edge, borderTopWidth: 1, backgroundColor: colors.panel },
  tab: { flex: 1, paddingVertical: 14, alignItems: "center" },
  tabText: { color: colors.muted, fontWeight: "700" },
});
