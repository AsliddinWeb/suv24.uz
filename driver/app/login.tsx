import { useMemo, useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { LinearGradient } from "expo-linear-gradient";
import { useAuth } from "@/stores/auth";
import { useTheme } from "@/stores/theme";
import type { ColorsScheme } from "@/theme/colors";

export default function LoginScreen() {
  const { login } = useAuth();
  const { colors, isDark } = useTheme();
  const styles = useMemo(() => makeStyles(colors), [colors]);

  const [phone, setPhone] = useState("+998933333333");
  const [password, setPassword] = useState("driver1234");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    if (!phone || !password) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      Alert.alert("Diqqat", "Telefon va parolni kiriting");
      return;
    }
    setLoading(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    try {
      await login(phone, password);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (e: any) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      const msg = e?.response?.data?.detail || "Kirish xatosi";
      Alert.alert("Xatolik", msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.header}>
        <LinearGradient
          colors={[colors.brand, colors.brandDark]}
          style={styles.logo}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Text style={styles.logoText}>S</Text>
        </LinearGradient>
        <Text style={styles.title}>Suv24 Haydovchi</Text>
        <Text style={styles.subtitle}>Hisobingizga kiring</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.field}>
          <Text style={styles.label}>Telefon raqam</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="call" size={18} color={colors.textMuted} style={styles.inputIcon} />
            <TextInput
              value={phone}
              onChangeText={setPhone}
              placeholder="+998..."
              placeholderTextColor={colors.textSubtle}
              autoCapitalize="none"
              keyboardType="phone-pad"
              style={styles.input}
            />
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Parol</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="lock-closed" size={18} color={colors.textMuted} style={styles.inputIcon} />
            <TextInput
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPwd}
              autoCapitalize="none"
              placeholderTextColor={colors.textSubtle}
              style={[styles.input, { flex: 1 }]}
            />
            <Pressable onPress={() => setShowPwd(!showPwd)} style={styles.eyeBtn}>
              <Ionicons
                name={showPwd ? "eye-off" : "eye"}
                size={20}
                color={colors.textMuted}
              />
            </Pressable>
          </View>
        </View>

        <Pressable
          onPress={onSubmit}
          disabled={loading}
          style={({ pressed }) => [
            styles.submitBtn,
            pressed && { opacity: 0.85 },
            loading && { opacity: 0.6 },
          ]}
        >
          <LinearGradient
            colors={[colors.brand, colors.brandDark]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={StyleSheet.absoluteFill}
          />
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Text style={styles.submitText}>Kirish</Text>
              <Ionicons name="arrow-forward" size={18} color="#fff" />
            </>
          )}
        </Pressable>

        <View style={styles.devHint}>
          <View style={styles.devHintHeader}>
            <Ionicons name="flash" size={13} color={colors.warning} />
            <Text style={styles.devHintLabel}>Dev credentials</Text>
          </View>
          <Text style={styles.devHintText}>+998933333333 / driver1234</Text>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const makeStyles = (c: ColorsScheme) =>
  StyleSheet.create({
    container: { flex: 1, backgroundColor: c.bg, padding: 24, justifyContent: "center" },
    header: { alignItems: "center", marginBottom: 40 },
    logo: {
      width: 76,
      height: 76,
      borderRadius: 22,
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 18,
      shadowColor: c.brand,
      shadowOpacity: 0.4,
      shadowRadius: 24,
      shadowOffset: { width: 0, height: 12 },
      elevation: 12,
    },
    logoText: { color: "#fff", fontSize: 38, fontWeight: "900" },
    title: { fontSize: 26, fontWeight: "800", color: c.text, letterSpacing: -0.5 },
    subtitle: { fontSize: 14, color: c.textMuted, marginTop: 6 },
    form: { gap: 18 },
    field: { gap: 8 },
    label: { fontSize: 13, fontWeight: "600", color: c.textMuted, letterSpacing: 0.3 },
    inputWrap: {
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: c.card,
      borderWidth: 1,
      borderColor: c.border,
      borderRadius: 14,
      paddingHorizontal: 14,
      height: 52,
      shadowColor: c.shadow,
      shadowOpacity: 0.5,
      shadowRadius: 8,
      shadowOffset: { width: 0, height: 2 },
      elevation: 2,
    },
    inputIcon: { marginRight: 10 },
    input: { flex: 1, fontSize: 15, color: c.text, paddingVertical: 0 },
    eyeBtn: { padding: 6 },
    submitBtn: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      height: 54,
      borderRadius: 14,
      marginTop: 10,
      overflow: "hidden",
      shadowColor: c.brand,
      shadowOpacity: 0.35,
      shadowRadius: 16,
      shadowOffset: { width: 0, height: 8 },
      elevation: 6,
    },
    submitText: { color: "#fff", fontSize: 16, fontWeight: "700", letterSpacing: 0.3 },
    devHint: {
      marginTop: 28,
      padding: 14,
      borderRadius: 12,
      backgroundColor: c.warningSoft,
      borderWidth: 1,
      borderColor: c.warning + "30",
    },
    devHintHeader: { flexDirection: "row", alignItems: "center", gap: 5 },
    devHintLabel: {
      fontSize: 11,
      fontWeight: "700",
      color: c.warning,
      textTransform: "uppercase",
      letterSpacing: 0.8,
    },
    devHintText: {
      fontSize: 13,
      color: c.text,
      marginTop: 4,
      fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
    },
  });
