import { useMemo, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import Animated, { FadeInDown } from "react-native-reanimated";
import { driversApi } from "@/api/drivers";
import { useTheme } from "@/stores/theme";
import type { ColorsScheme } from "@/theme/colors";

export default function BottlesScreen() {
  const { colors } = useTheme();
  const styles = useMemo(() => makeStyles(colors), [colors]);

  const meQuery = useQuery({
    queryKey: ["driver-me"],
    queryFn: () => driversApi.me(),
  });

  const driverId = meQuery.data?.id;

  const bottlesQuery = useQuery({
    queryKey: ["bottles", driverId],
    queryFn: () => driversApi.myBottles(driverId!),
    enabled: !!driverId,
  });

  const loading = meQuery.isLoading || bottlesQuery.isLoading;
  const [pulling, setPulling] = useState(false);

  async function onRefresh() {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setPulling(true);
    try {
      await Promise.all([
        meQuery.refetch(),
        driverId ? bottlesQuery.refetch() : Promise.resolve(),
      ]);
    } finally {
      setPulling(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={colors.brand} />
      </View>
    );
  }

  const bottles = bottlesQuery.data || [];
  const totalFull = bottles.reduce((sum, b) => sum + b.full_count, 0);
  const totalEmpty = bottles.reduce((sum, b) => sum + b.empty_count, 0);

  return (
    <View style={styles.container}>
      <FlatList
        data={bottles}
        keyExtractor={(b) => b.id}
        refreshControl={
          <RefreshControl
            refreshing={pulling}
            onRefresh={onRefresh}
            tintColor={colors.brand}
          />
        }
        contentContainerStyle={{ padding: 16, gap: 12 }}
        ListHeaderComponent={
          <LinearGradient
            colors={[colors.brand, colors.brandDark]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.hero}
          >
            <View style={styles.heroDecor} />
            <Text style={styles.heroTitle}>Idish balansingiz</Text>
            <Text style={styles.heroSub}>
              Har yetkazish va qaytarish avtomatik hisoblanadi
            </Text>
            <View style={styles.heroStats}>
              <View style={styles.heroStatBox}>
                <Text style={styles.heroStatValue}>{totalFull}</Text>
                <Text style={styles.heroStatLabel}>TO'LA</Text>
              </View>
              <View style={styles.heroStatDivider} />
              <View style={styles.heroStatBox}>
                <Text style={styles.heroStatValue}>{totalEmpty}</Text>
                <Text style={styles.heroStatLabel}>BO'SH</Text>
              </View>
            </View>
          </LinearGradient>
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <View style={styles.emptyIcon}>
              <Ionicons name="water-outline" size={40} color={colors.brand} />
            </View>
            <Text style={styles.emptyText}>Hozircha idish yo'q</Text>
            <Text style={styles.emptySub}>
              Ombordan idish oling (admin panelidan yuklash)
            </Text>
          </View>
        }
        renderItem={({ item, index }) => (
          <Animated.View
            entering={FadeInDown.delay(Math.min(index, 6) * 40).duration(300)}
            style={styles.card}
          >
            <View style={styles.cardHead}>
              <View style={styles.bottleIcon}>
                <Ionicons name="water" size={20} color={colors.brand} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.productName}>{item.product_name}</Text>
                <Text style={styles.productVolume}>{item.volume_liters} litr</Text>
              </View>
            </View>
            <View style={styles.counts}>
              <View
                style={[
                  styles.countBox,
                  {
                    backgroundColor: colors.successSoft,
                    borderColor: colors.success + "40",
                  },
                ]}
              >
                <Text style={styles.countLabel}>To'la</Text>
                <Text style={[styles.countValue, { color: colors.success }]}>
                  {item.full_count}
                </Text>
              </View>
              <View
                style={[
                  styles.countBox,
                  { backgroundColor: colors.slate50, borderColor: colors.border },
                ]}
              >
                <Text style={styles.countLabel}>Bo'sh</Text>
                <Text style={[styles.countValue, { color: colors.text }]}>
                  {item.empty_count}
                </Text>
              </View>
            </View>
          </Animated.View>
        )}
      />
    </View>
  );
}

const makeStyles = (c: ColorsScheme) =>
  StyleSheet.create({
    container: { flex: 1, backgroundColor: c.bg },
    loading: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: c.bg,
    },
    hero: {
      padding: 20,
      borderRadius: 20,
      marginBottom: 12,
      overflow: "hidden",
      shadowColor: c.brand,
      shadowOpacity: 0.3,
      shadowRadius: 16,
      shadowOffset: { width: 0, height: 8 },
      elevation: 6,
    },
    heroDecor: {
      position: "absolute",
      top: -50,
      right: -50,
      width: 180,
      height: 180,
      borderRadius: 90,
      backgroundColor: "rgba(255,255,255,0.1)",
    },
    heroTitle: { color: "#fff", fontSize: 20, fontWeight: "800", letterSpacing: -0.5 },
    heroSub: { color: "rgba(255,255,255,0.85)", fontSize: 13, marginTop: 4 },
    heroStats: {
      marginTop: 16,
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: "rgba(255,255,255,0.15)",
      borderRadius: 14,
      padding: 12,
    },
    heroStatBox: { flex: 1, alignItems: "center" },
    heroStatDivider: { width: 1, height: 32, backgroundColor: "rgba(255,255,255,0.25)" },
    heroStatValue: { color: "#fff", fontSize: 26, fontWeight: "900" },
    heroStatLabel: {
      color: "rgba(255,255,255,0.85)",
      fontSize: 10,
      fontWeight: "700",
      letterSpacing: 1,
      marginTop: 2,
    },
    card: {
      backgroundColor: c.card,
      borderRadius: 14,
      padding: 14,
      borderWidth: 1,
      borderColor: c.border,
      gap: 10,
    },
    cardHead: { flexDirection: "row", alignItems: "center", gap: 12 },
    bottleIcon: {
      width: 40,
      height: 40,
      borderRadius: 10,
      backgroundColor: c.brandSoft,
      alignItems: "center",
      justifyContent: "center",
    },
    productName: { fontSize: 15, fontWeight: "700", color: c.text },
    productVolume: { fontSize: 12, color: c.textMuted, marginTop: 2 },
    counts: { flexDirection: "row", gap: 10 },
    countBox: { flex: 1, padding: 12, borderRadius: 10, borderWidth: 1 },
    countLabel: {
      fontSize: 11,
      color: c.textMuted,
      fontWeight: "600",
      textTransform: "uppercase",
    },
    countValue: { fontSize: 26, fontWeight: "800", marginTop: 2 },
    empty: { alignItems: "center", padding: 48, gap: 8 },
    emptyIcon: {
      width: 72,
      height: 72,
      borderRadius: 36,
      backgroundColor: c.brandSoft,
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 12,
    },
    emptyText: { fontSize: 15, fontWeight: "600", color: c.text, marginTop: 8 },
    emptySub: { fontSize: 13, color: c.textMuted, textAlign: "center" },
  });
