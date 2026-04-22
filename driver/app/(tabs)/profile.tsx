import { useMemo } from "react";
import { View, Text, StyleSheet, Pressable, Alert, ScrollView, Image, Linking } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { LinearGradient } from "expo-linear-gradient";
import Constants from "expo-constants";
import { useAuth } from "@/stores/auth";
import { useTheme, useThemeStore, type ThemeMode } from "@/stores/theme";
import type { ColorsScheme } from "@/theme/colors";
import { resolveMediaUrl } from "@/api/companies";

export default function ProfileScreen() {
  const { colors, mode } = useTheme();
  const setMode = useThemeStore((s) => s.setMode);
  const { user, company, logout } = useAuth();
  const styles = useMemo(() => makeStyles(colors), [colors]);

  const brandName = company?.short_name || company?.name || "Suv24";
  const supportPhone = company?.support_phone || company?.phone || null;
  const logoUrl = resolveMediaUrl(company?.logo_url);

  function onLogout() {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    Alert.alert("Chiqish", "Hisobdan chiqmoqchimisiz?", [
      { text: "Bekor qilish", style: "cancel" },
      { text: "Chiqish", style: "destructive", onPress: () => logout() },
    ]);
  }

  function changeMode(next: ThemeMode) {
    Haptics.selectionAsync();
    setMode(next);
  }

  const initial = user?.full_name?.slice(0, 1).toUpperCase() || "?";

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ padding: 16, paddingBottom: 32 }}
    >
      {/* Hero */}
      <LinearGradient
        colors={[colors.brand, colors.brandDark]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.hero}
      >
        <View style={styles.heroDecor} />
        {logoUrl ? <Image source={{ uri: logoUrl }} style={styles.companyLogo} /> : null}
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{initial}</Text>
        </View>
        <Text style={styles.name}>{user?.full_name}</Text>
        <Text style={styles.phone}>{user?.phone}</Text>
        <View style={styles.roleBadge}>
          <Ionicons name="car" size={12} color={colors.brand} />
          <Text style={[styles.roleText, { color: colors.brand }]}>
            {brandName.toUpperCase()} · HAYDOVCHI
          </Text>
        </View>
      </LinearGradient>

      {/* Theme */}
      <Text style={styles.sectionTitle}>KO'RINISH</Text>
      <View style={styles.card}>
        <ThemeOption mode="system" label="Tizim" icon="phone-portrait" current={mode} onSelect={changeMode} colors={colors} styles={styles} />
        <View style={styles.divider} />
        <ThemeOption mode="light" label="Kunduzgi" icon="sunny" current={mode} onSelect={changeMode} colors={colors} styles={styles} />
        <View style={styles.divider} />
        <ThemeOption mode="dark" label="Tungi" icon="moon" current={mode} onSelect={changeMode} colors={colors} styles={styles} />
      </View>

      {/* Info */}
      <Text style={styles.sectionTitle}>HISOB</Text>
      <View style={styles.card}>
        <InfoRow icon="person" label="Ism" value={user?.full_name ?? ""} colors={colors} styles={styles} />
        <View style={styles.divider} />
        <InfoRow icon="call" label="Telefon" value={user?.phone ?? ""} colors={colors} styles={styles} />
      </View>

      {/* Company */}
      {company && (
        <>
          <Text style={styles.sectionTitle}>KOMPANIYA</Text>
          <View style={styles.card}>
            <InfoRow icon="business" label="Nomi" value={company.name} colors={colors} styles={styles} />
            {supportPhone ? (
              <>
                <View style={styles.divider} />
                <Pressable
                  onPress={() => {
                    Haptics.selectionAsync();
                    Linking.openURL(`tel:${supportPhone}`);
                  }}
                >
                  <InfoRow
                    icon="headset"
                    label="Qo'llab-quvvatlash"
                    value={supportPhone}
                    colors={colors}
                    styles={styles}
                  />
                </Pressable>
              </>
            ) : null}
            {company.address ? (
              <>
                <View style={styles.divider} />
                <InfoRow icon="location" label="Manzil" value={company.address} colors={colors} styles={styles} />
              </>
            ) : null}
          </View>
        </>
      )}

      {/* Logout */}
      <Pressable
        onPress={onLogout}
        style={({ pressed }) => [
          styles.logoutBtn,
          pressed && { transform: [{ scale: 0.98 }], opacity: 0.9 },
        ]}
      >
        <View style={styles.logoutIcon}>
          <Ionicons name="log-out-outline" size={22} color={colors.danger} />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={[styles.logoutText, { color: colors.danger }]}>Hisobdan chiqish</Text>
          <Text style={styles.logoutSub}>Seansni yakunlash</Text>
        </View>
        <Ionicons name="chevron-forward" size={20} color={colors.danger} />
      </Pressable>

      <Text style={styles.version}>
        {brandName} · Suv24 Haydovchi · v{Constants.expoConfig?.version || "0.1.0"}
      </Text>
    </ScrollView>
  );
}

function ThemeOption({
  mode,
  current,
  label,
  icon,
  onSelect,
  colors,
  styles,
}: {
  mode: ThemeMode;
  current: ThemeMode;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  onSelect: (m: ThemeMode) => void;
  colors: ColorsScheme;
  styles: ReturnType<typeof makeStyles>;
}) {
  const active = current === mode;
  return (
    <Pressable onPress={() => onSelect(mode)} style={styles.row}>
      <View style={[styles.rowIcon, { backgroundColor: active ? colors.brand : colors.slate50 }]}>
        <Ionicons name={icon} size={18} color={active ? "#fff" : colors.textMuted} />
      </View>
      <Text style={styles.rowLabel}>{label}</Text>
      {active && <Ionicons name="checkmark-circle" size={22} color={colors.brand} />}
    </Pressable>
  );
}

function InfoRow({
  icon,
  label,
  value,
  colors,
  styles,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
  colors: ColorsScheme;
  styles: ReturnType<typeof makeStyles>;
}) {
  return (
    <View style={styles.row}>
      <View style={[styles.rowIcon, { backgroundColor: colors.slate50 }]}>
        <Ionicons name={icon} size={18} color={colors.textMuted} />
      </View>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue} numberOfLines={1}>
        {value}
      </Text>
    </View>
  );
}

const makeStyles = (c: ColorsScheme) =>
  StyleSheet.create({
    container: { flex: 1, backgroundColor: c.bg },
    hero: {
      padding: 24,
      borderRadius: 24,
      alignItems: "center",
      overflow: "hidden",
      shadowColor: c.brand,
      shadowOpacity: 0.3,
      shadowRadius: 16,
      shadowOffset: { width: 0, height: 8 },
      elevation: 6,
    },
    heroDecor: {
      position: "absolute",
      top: -60,
      right: -60,
      width: 200,
      height: 200,
      borderRadius: 100,
      backgroundColor: "rgba(255,255,255,0.1)",
    },
    companyLogo: {
      width: 48,
      height: 48,
      borderRadius: 12,
      backgroundColor: "rgba(255,255,255,0.15)",
      marginBottom: 10,
    },
    avatar: {
      width: 84,
      height: 84,
      borderRadius: 42,
      backgroundColor: "rgba(255,255,255,0.2)",
      borderWidth: 3,
      borderColor: "#fff",
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 14,
    },
    avatarText: { color: "#fff", fontSize: 34, fontWeight: "900" },
    name: { fontSize: 22, fontWeight: "800", color: "#fff", letterSpacing: -0.5 },
    phone: { fontSize: 14, color: "rgba(255,255,255,0.85)", marginTop: 3 },
    roleBadge: {
      marginTop: 12,
      backgroundColor: "#fff",
      paddingHorizontal: 14,
      paddingVertical: 6,
      borderRadius: 20,
      flexDirection: "row",
      alignItems: "center",
      gap: 5,
    },
    roleText: { fontSize: 11, fontWeight: "800", letterSpacing: 1 },
    sectionTitle: {
      fontSize: 11,
      fontWeight: "800",
      color: c.textMuted,
      letterSpacing: 1.2,
      paddingHorizontal: 4,
      marginTop: 22,
      marginBottom: 10,
    },
    card: {
      backgroundColor: c.card,
      borderRadius: 16,
      borderWidth: 1,
      borderColor: c.border,
      overflow: "hidden",
    },
    row: {
      flexDirection: "row",
      alignItems: "center",
      padding: 14,
      gap: 12,
    },
    rowIcon: {
      width: 36,
      height: 36,
      borderRadius: 10,
      alignItems: "center",
      justifyContent: "center",
    },
    rowLabel: { fontSize: 15, color: c.text, fontWeight: "600", flex: 1 },
    rowValue: { fontSize: 14, color: c.textMuted, maxWidth: "55%", textAlign: "right" },
    divider: { height: 1, backgroundColor: c.border, marginLeft: 62 },
    logoutBtn: {
      marginTop: 28,
      backgroundColor: c.card,
      borderWidth: 1,
      borderColor: c.danger + "30",
      flexDirection: "row",
      alignItems: "center",
      gap: 12,
      paddingHorizontal: 18,
      paddingVertical: 16,
      borderRadius: 16,
      shadowColor: c.danger,
      shadowOpacity: 0.12,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: 4 },
      elevation: 2,
    },
    logoutIcon: {
      width: 40,
      height: 40,
      borderRadius: 12,
      backgroundColor: c.danger + "18",
      alignItems: "center",
      justifyContent: "center",
    },
    logoutText: { fontSize: 16, fontWeight: "700" },
    logoutSub: { fontSize: 12, color: c.textMuted, marginTop: 2 },
    version: {
      textAlign: "center",
      paddingVertical: 28,
      fontSize: 12,
      color: c.textMuted,
    },
  });
