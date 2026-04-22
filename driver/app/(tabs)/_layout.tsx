import { View, Platform } from "react-native";
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useTheme } from "@/stores/theme";

function TabIcon({
  name,
  color,
  focused,
  brand,
}: {
  name: keyof typeof Ionicons.glyphMap;
  color: string;
  focused: boolean;
  brand: string;
}) {
  return (
    <View style={{ alignItems: "center", justifyContent: "center", width: 56 }}>
      <Ionicons name={name} size={26} color={color} />
      <View
        style={{
          marginTop: 4,
          height: 4,
          width: 4,
          borderRadius: 2,
          backgroundColor: focused ? brand : "transparent",
        }}
      />
    </View>
  );
}

export default function TabsLayout() {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const baseBottom = Platform.OS === "ios" ? insets.bottom : Math.max(insets.bottom, 8);

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.brand,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: {
          backgroundColor: colors.card,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          height: 64 + baseBottom,
          paddingBottom: baseBottom + 6,
          paddingTop: 10,
          shadowColor: colors.shadow,
          shadowOpacity: 0.08,
          shadowRadius: 12,
          shadowOffset: { width: 0, height: -2 },
          elevation: 12,
        },
        tabBarItemStyle: { paddingVertical: 2 },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "700",
          letterSpacing: 0.2,
          marginTop: -2,
        },
        headerStyle: {
          backgroundColor: colors.card,
          borderBottomColor: colors.border,
          borderBottomWidth: 1,
        },
        headerTitleStyle: { fontWeight: "800", fontSize: 18, color: colors.text },
        headerShadowVisible: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Bugun",
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "list" : "list-outline"} color={color} focused={focused} brand={colors.brand} />
          ),
          headerTitle: "Buyurtmalar",
        }}
      />
      <Tabs.Screen
        name="bottles"
        options={{
          title: "Idish",
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "water" : "water-outline"} color={color} focused={focused} brand={colors.brand} />
          ),
          headerTitle: "Idish balansi",
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profil",
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? "person" : "person-outline"} color={color} focused={focused} brand={colors.brand} />
          ),
          headerTitle: "Profil",
        }}
      />
    </Tabs>
  );
}
