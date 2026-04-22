import { useMemo, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Pressable,
  Alert,
  TextInput,
  Linking,
  Modal,
  KeyboardAvoidingView,
  Platform,
  Dimensions,
} from "react-native";
import { useLocalSearchParams, Stack, router } from "expo-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import Animated, { FadeInDown } from "react-native-reanimated";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ordersApi } from "@/api/orders";
import { paymentsApi } from "@/api/payments";
import { useTheme } from "@/stores/theme";
import { orderStatusColor, orderStatusLabel, type ColorsScheme } from "@/theme/colors";
import { formatDateTime, formatMoney } from "@/utils/format";
import SwipeToConfirm from "@/components/SwipeToConfirm";
import type { OrderDetailOut, PaymentMethod } from "@/types/api";

export default function OrderDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const qc = useQueryClient();
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const styles = useMemo(() => makeStyles(colors), [colors]);

  const orderQ = useQuery({
    queryKey: ["order", id],
    queryFn: () => ordersApi.get(id!),
    enabled: !!id,
  });

  const order = orderQ.data;
  const customer = order?.customer;
  const address = order?.address;

  const startM = useMutation({
    mutationFn: () => ordersApi.start(id!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["order", id] });
      qc.invalidateQueries({ queryKey: ["orders"] });
    },
  });

  const [deliverOpen, setDeliverOpen] = useState(false);
  const [failOpen, setFailOpen] = useState(false);

  const swipeWidth = Dimensions.get("window").width - 32;

  if (orderQ.isLoading || !order) {
    return (
      <>
        <Stack.Screen options={{ title: "Buyurtma" }} />
        <View style={styles.loading}>
          <ActivityIndicator size="large" color={colors.brand} />
        </View>
      </>
    );
  }

  const paid = parseFloat(order.paid_amount || "0");
  const total = parseFloat(order.total);
  const outstanding = Math.max(0, total - paid);
  const isFullyPaid = outstanding <= 0 && total > 0;

  return (
    <>
      <Stack.Screen options={{ title: `#${order.number}` }} />

      <ScrollView
        style={styles.container}
        contentContainerStyle={{ padding: 16, gap: 16, paddingBottom: 40 + insets.bottom }}
      >
        <View style={styles.hero}>
          <View
            style={[
              styles.statusBadge,
              { backgroundColor: orderStatusColor(order.status, colors) },
            ]}
          >
            <Text style={styles.statusBadgeText}>{orderStatusLabel[order.status]}</Text>
          </View>
          <Text style={styles.heroTotal}>{formatMoney(total)}</Text>
          <View style={styles.heroRow}>
            <View style={styles.heroCol}>
              <Text style={styles.heroLabel}>To'langan</Text>
              <Text style={[styles.heroValue, { color: colors.success }]}>
                {formatMoney(paid)}
              </Text>
            </View>
            <View
              style={[styles.heroCol, { borderLeftWidth: 1, borderLeftColor: colors.border }]}
            >
              <Text style={styles.heroLabel}>Qarz</Text>
              <Text
                style={[
                  styles.heroValue,
                  { color: outstanding > 0 ? colors.danger : colors.text },
                ]}
              >
                {formatMoney(outstanding)}
              </Text>
            </View>
          </View>
        </View>

        {customer && (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Mijoz</Text>
            <Text style={styles.customerName}>{customer.full_name}</Text>
            <Pressable
              onPress={() => {
                Haptics.selectionAsync();
                Linking.openURL(`tel:${customer.phone}`);
              }}
              style={styles.phoneBtn}
            >
              <Ionicons name="call" size={18} color="#fff" />
              <Text style={styles.phoneBtnText}>{customer.phone}</Text>
            </Pressable>
          </View>
        )}

        {address && (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Manzil · {address.label}</Text>
            <Text style={styles.addressText}>{address.address_text}</Text>
            {address.lat && address.lng ? (
              <View style={styles.mapRow}>
                <Pressable
                  onPress={() => {
                    Haptics.selectionAsync();
                    Linking.openURL(
                      `yandexmaps://maps.yandex.ru/?rtext=~${address.lat},${address.lng}&rtt=auto`,
                    ).catch(() =>
                      Linking.openURL(
                        `https://yandex.uz/maps/?rtext=~${address.lat},${address.lng}&rtt=auto`,
                      ),
                    );
                  }}
                  style={[styles.mapBtn, { backgroundColor: colors.brand }]}
                >
                  <Ionicons name="navigate" size={18} color="#fff" />
                  <Text style={[styles.mapBtnText, { color: "#fff" }]}>Marshrut</Text>
                </Pressable>
                <Pressable
                  onPress={() => {
                    Haptics.selectionAsync();
                    Linking.openURL(
                      `https://yandex.uz/maps/?pt=${address.lng},${address.lat}&z=16&l=map`,
                    );
                  }}
                  style={styles.mapBtn}
                >
                  <Ionicons name="map" size={18} color={colors.brand} />
                  <Text style={styles.mapBtnText}>Xaritada ko'rish</Text>
                </Pressable>
              </View>
            ) : (
              <View style={styles.noGpsWarning}>
                <Ionicons name="alert-circle" size={14} color={colors.warning} />
                <Text style={styles.noGpsText}>
                  GPS koordinatasi yo'q — admin'dan qo'shishni so'rang
                </Text>
              </View>
            )}
          </View>
        )}

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Mahsulotlar</Text>
          {order.items.map((it) => (
            <View key={it.id} style={styles.itemRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.itemName}>{it.product_name}</Text>
                <Text style={styles.itemMeta}>
                  {it.quantity} × {formatMoney(it.unit_price)}
                </Text>
              </View>
              <Text style={styles.itemTotal}>{formatMoney(it.total)}</Text>
            </View>
          ))}
        </View>

        {order.notes && (
          <View
            style={[
              styles.card,
              { backgroundColor: colors.warningSoft, borderColor: colors.warning + "40" },
            ]}
          >
            <Text style={[styles.noteLabel, { color: colors.warning }]}>💬 Izoh</Text>
            <Text style={styles.noteText}>{order.notes}</Text>
          </View>
        )}

        {order.status === "assigned" && (
          <Animated.View entering={FadeInDown.duration(350).springify().damping(14)} style={styles.swipeWrap}>
            <Text style={styles.swipeHint}>Yo'lga chiqish uchun suring →</Text>
            <SwipeToConfirm
              label="Yo'lga chiqaman"
              onConfirm={() => startM.mutate()}
              loading={startM.isPending}
              color={colors.brand}
              icon="navigate"
              width={swipeWidth}
            />
          </Animated.View>
        )}

        {order.status === "in_delivery" && (
          <>
            <Animated.View entering={FadeInDown.duration(350).springify().damping(14)} style={styles.swipeWrap}>
              <Text style={styles.swipeHint}>Yetkazish uchun suring →</Text>
              <SwipeToConfirm
                label="Yetkazib berdim"
                onConfirm={() => setDeliverOpen(true)}
                color={colors.success}
                icon="checkmark-done"
                width={swipeWidth}
              />
            </Animated.View>
            <Animated.View entering={FadeInDown.delay(120).duration(350).springify().damping(14)}>
              <Pressable
                onPress={() => {
                  Haptics.selectionAsync();
                  setFailOpen(true);
                }}
                style={({ pressed }) => [
                  styles.secondaryBtn,
                  pressed && { transform: [{ scale: 0.98 }], opacity: 0.92 },
                ]}
              >
                <View style={styles.secondaryIcon}>
                  <Ionicons name="alert-circle" size={22} color={colors.danger} />
                </View>
                <Text style={[styles.secondaryBtnText, { color: colors.danger }]}>
                  Yetkazib bo'lmadi
                </Text>
                <Ionicons name="chevron-forward" size={18} color={colors.danger} />
              </Pressable>
            </Animated.View>
          </>
        )}

        {order.status === "delivered" && (
          <Animated.View entering={FadeInDown.duration(400).springify()} style={styles.infoBox}>
            <Ionicons name="checkmark-circle" size={24} color={colors.success} />
            <Text style={styles.infoText}>Buyurtma yetkazildi</Text>
          </Animated.View>
        )}

        {order.status === "cancelled" && (
          <Animated.View
            entering={FadeInDown.duration(400).springify()}
            style={[styles.infoBox, { backgroundColor: colors.slate50 }]}
          >
            <Ionicons name="close-circle" size={24} color={colors.neutral} />
            <Text style={styles.infoText}>Buyurtma bekor qilingan</Text>
          </Animated.View>
        )}

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Tarix</Text>
          {order.status_logs.map((log) => {
            const label =
              !log.from_status && log.to_status === "pending"
                ? "Buyurtma yaratildi"
                : log.from_status === "pending" && log.to_status === "assigned"
                  ? "Siz biriktirildingiz"
                  : log.from_status === "assigned" && log.to_status === "in_delivery"
                    ? "Yo'lga chiqdingiz"
                    : log.from_status === "in_delivery" && log.to_status === "delivered"
                      ? "Yetkazdingiz"
                      : log.from_status === "in_delivery" && log.to_status === "failed"
                        ? "Muvaffaqiyatsiz"
                        : log.to_status === "cancelled"
                          ? "Bekor qilindi"
                          : `${log.from_status} → ${log.to_status}`;
            return (
              <View key={log.id} style={styles.logRow}>
                <View
                  style={[
                    styles.logDot,
                    { backgroundColor: orderStatusColor(log.to_status, colors) },
                  ]}
                />
                <View style={{ flex: 1 }}>
                  <Text style={styles.logText}>{label}</Text>
                  <Text style={styles.logTime}>{formatDateTime(log.created_at)}</Text>
                  {log.reason && <Text style={styles.logReason}>💬 {log.reason}</Text>}
                </View>
              </View>
            );
          })}
        </View>
      </ScrollView>

      <DeliverModal
        open={deliverOpen}
        onClose={() => setDeliverOpen(false)}
        order={order}
        outstanding={outstanding}
        colors={colors}
        styles={styles}
        onDone={() => {
          setDeliverOpen(false);
          qc.invalidateQueries({ queryKey: ["order", id] });
          qc.invalidateQueries({ queryKey: ["orders"] });
          qc.invalidateQueries({ queryKey: ["bottles"] });
          router.back();
        }}
      />

      <FailModal
        open={failOpen}
        onClose={() => setFailOpen(false)}
        orderId={id!}
        colors={colors}
        styles={styles}
        onDone={() => {
          setFailOpen(false);
          qc.invalidateQueries({ queryKey: ["order", id] });
          qc.invalidateQueries({ queryKey: ["orders"] });
          router.back();
        }}
      />
    </>
  );
}

function DeliverModal({
  open,
  onClose,
  order,
  outstanding,
  colors,
  styles,
  onDone,
}: {
  open: boolean;
  onClose: () => void;
  order: OrderDetailOut;
  outstanding: number;
  colors: ColorsScheme;
  styles: ReturnType<typeof makeStyles>;
  onDone: () => void;
}) {
  const [cash, setCash] = useState(outstanding > 0 ? String(outstanding) : "");
  const [method, setMethod] = useState<PaymentMethod>("cash");
  const [returns, setReturns] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    try {
      const amount = parseFloat(cash || "0");
      if (amount > 0) {
        await paymentsApi.record({
          order_id: order.id,
          amount: String(amount),
          method,
        });
      }
      const bottle_returns = Object.entries(returns)
        .map(([product_id, v]) => ({
          product_id,
          count: parseInt(v || "0", 10),
        }))
        .filter((r) => r.count > 0);

      await ordersApi.deliver(order.id, bottle_returns);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      onDone();
    } catch (e: any) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert("Xatolik", e?.response?.data?.detail || "Saqlab bo'lmadi");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal visible={open} animationType="slide" transparent={false} onRequestClose={onClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={{ flex: 1, backgroundColor: colors.bg }}
      >
        <View style={styles.modalHeader}>
          <Pressable onPress={onClose} style={{ padding: 8 }}>
            <Ionicons name="close" size={24} color={colors.text} />
          </Pressable>
          <Text style={styles.modalTitle}>Yetkazib berdim</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView contentContainerStyle={{ padding: 16, gap: 14 }}>
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>To'lov qabul qildingizmi?</Text>
            <Text style={styles.hint}>Qarz: {formatMoney(outstanding)}</Text>

            <View style={styles.methodRow}>
              <Pressable
                onPress={() => {
                  Haptics.selectionAsync();
                  setMethod("cash");
                }}
                style={[styles.methodChip, method === "cash" && styles.methodChipActive]}
              >
                <Ionicons
                  name="cash"
                  size={18}
                  color={method === "cash" ? "#fff" : colors.textMuted}
                />
                <Text style={[styles.methodText, method === "cash" && { color: "#fff" }]}>
                  Naqd
                </Text>
              </Pressable>
              <Pressable
                onPress={() => {
                  Haptics.selectionAsync();
                  setMethod("card_manual");
                }}
                style={[
                  styles.methodChip,
                  method === "card_manual" && styles.methodChipActive,
                ]}
              >
                <Ionicons
                  name="card"
                  size={18}
                  color={method === "card_manual" ? "#fff" : colors.textMuted}
                />
                <Text
                  style={[
                    styles.methodText,
                    method === "card_manual" && { color: "#fff" },
                  ]}
                >
                  Karta
                </Text>
              </Pressable>
            </View>

            <Text style={styles.label}>Summa (so'm)</Text>
            <TextInput
              value={cash}
              onChangeText={setCash}
              keyboardType="numeric"
              placeholder="0"
              placeholderTextColor={colors.textSubtle}
              style={styles.input}
            />
            <Text style={styles.hintSmall}>Agar to'lov bo'lmasa, 0 qoldiring</Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Bo'sh idish qaytardingizmi?</Text>
            <Text style={styles.hint}>Mahsulot bo'yicha bo'sh idish sonini kiriting</Text>
            {order.items.map((it) => (
              <View key={it.id} style={styles.returnRow}>
                <Text style={styles.returnLabel}>{it.product_name}</Text>
                <TextInput
                  value={returns[it.product_id] || ""}
                  onChangeText={(v) =>
                    setReturns({
                      ...returns,
                      [it.product_id]: v.replace(/[^0-9]/g, ""),
                    })
                  }
                  keyboardType="number-pad"
                  placeholder="0"
                  placeholderTextColor={colors.textSubtle}
                  style={[styles.input, { width: 70, textAlign: "center" }]}
                />
              </View>
            ))}
          </View>

          <Pressable
            onPress={submit}
            disabled={loading}
            style={({ pressed }) => [
              styles.primaryBtn,
              { backgroundColor: colors.success },
              (pressed || loading) && { opacity: 0.85 },
            ]}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="checkmark-done" size={20} color="#fff" />
                <Text style={styles.primaryBtnText}>Tasdiqlash</Text>
              </>
            )}
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>
    </Modal>
  );
}

function FailModal({
  open,
  onClose,
  orderId,
  colors,
  styles,
  onDone,
}: {
  open: boolean;
  onClose: () => void;
  orderId: string;
  colors: ColorsScheme;
  styles: ReturnType<typeof makeStyles>;
  onDone: () => void;
}) {
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!reason.trim()) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      Alert.alert("Diqqat", "Sabab majburiy");
      return;
    }
    setLoading(true);
    try {
      await ordersApi.fail(orderId, reason);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      onDone();
    } catch (e: any) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert("Xatolik", e?.response?.data?.detail || "Saqlab bo'lmadi");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal visible={open} animationType="slide" transparent={false} onRequestClose={onClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={{ flex: 1, backgroundColor: colors.bg }}
      >
        <View style={styles.modalHeader}>
          <Pressable onPress={onClose} style={{ padding: 8 }}>
            <Ionicons name="close" size={24} color={colors.text} />
          </Pressable>
          <Text style={styles.modalTitle}>Yetkazib bo'lmadi</Text>
          <View style={{ width: 40 }} />
        </View>

        <View style={{ padding: 16 }}>
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Sabab</Text>
            <Text style={styles.hint}>
              Nima uchun yetkazib bo'lmadi? Buyurtma tarixiga yoziladi.
            </Text>
            <TextInput
              value={reason}
              onChangeText={setReason}
              multiline
              numberOfLines={4}
              placeholder="Masalan: Mijoz uyda yo'q"
              placeholderTextColor={colors.textSubtle}
              style={[styles.input, { minHeight: 100, textAlignVertical: "top" }]}
            />
          </View>

          <Pressable
            onPress={submit}
            disabled={loading || !reason.trim()}
            style={({ pressed }) => [
              styles.primaryBtn,
              { backgroundColor: colors.danger, marginTop: 14 },
              (pressed || loading || !reason.trim()) && { opacity: 0.6 },
            ]}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="alert-circle" size={20} color="#fff" />
                <Text style={styles.primaryBtnText}>Tasdiqlash</Text>
              </>
            )}
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </Modal>
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
      backgroundColor: c.card,
      padding: 20,
      borderRadius: 16,
      borderWidth: 1,
      borderColor: c.border,
      alignItems: "center",
      gap: 10,
    },
    statusBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14 },
    statusBadgeText: { color: "#fff", fontSize: 12, fontWeight: "700" },
    heroTotal: { fontSize: 32, fontWeight: "800", color: c.text },
    heroRow: { flexDirection: "row", width: "100%", marginTop: 4 },
    heroCol: { flex: 1, alignItems: "center", padding: 8 },
    heroLabel: {
      fontSize: 11,
      color: c.textMuted,
      fontWeight: "600",
      textTransform: "uppercase",
    },
    heroValue: { fontSize: 18, fontWeight: "800", marginTop: 2 },
    card: {
      backgroundColor: c.card,
      padding: 14,
      borderRadius: 14,
      borderWidth: 1,
      borderColor: c.border,
      gap: 8,
    },
    sectionTitle: {
      fontSize: 12,
      fontWeight: "700",
      color: c.textMuted,
      textTransform: "uppercase",
    },
    customerName: { fontSize: 18, fontWeight: "700", color: c.text },
    phoneBtn: {
      marginTop: 4,
      backgroundColor: c.brand,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      padding: 12,
      borderRadius: 10,
    },
    phoneBtnText: { color: "#fff", fontSize: 15, fontWeight: "700" },
    addressText: { fontSize: 15, color: c.text, lineHeight: 22 },
    mapRow: { flexDirection: "row", gap: 8, marginTop: 4 },
    mapBtn: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 6,
      padding: 10,
      borderRadius: 10,
      borderWidth: 1,
      borderColor: c.brand,
    },
    mapBtnText: { color: c.brand, fontSize: 13, fontWeight: "700" },
    noGpsWarning: {
      marginTop: 4,
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
      backgroundColor: c.warningSoft,
      borderColor: c.warning + "40",
      borderWidth: 1,
      padding: 8,
      borderRadius: 8,
    },
    noGpsText: { fontSize: 12, color: c.text, flex: 1 },
    swipeWrap: { alignItems: "center", gap: 8, marginVertical: 4 },
    swipeHint: { fontSize: 12, color: c.textMuted, fontWeight: "600" },
    itemRow: {
      flexDirection: "row",
      alignItems: "center",
      paddingVertical: 8,
      borderBottomWidth: 1,
      borderBottomColor: c.border,
    },
    itemName: { fontSize: 15, fontWeight: "600", color: c.text },
    itemMeta: { fontSize: 12, color: c.textMuted, marginTop: 2 },
    itemTotal: { fontSize: 15, fontWeight: "700", color: c.text },
    noteLabel: { fontSize: 12, fontWeight: "700" },
    noteText: { fontSize: 14, color: c.text, marginTop: 4 },
    primaryBtn: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      backgroundColor: c.brand,
      padding: 16,
      borderRadius: 14,
      shadowColor: c.shadow,
      shadowOpacity: 0.4,
      shadowRadius: 8,
      shadowOffset: { width: 0, height: 4 },
      elevation: 3,
    },
    primaryBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
    secondaryBtn: {
      flexDirection: "row",
      alignItems: "center",
      gap: 12,
      backgroundColor: c.card,
      borderWidth: 1,
      borderColor: c.danger + "35",
      paddingHorizontal: 18,
      paddingVertical: 16,
      borderRadius: 16,
      shadowColor: c.danger,
      shadowOpacity: 0.12,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: 4 },
      elevation: 2,
    },
    secondaryIcon: {
      width: 40,
      height: 40,
      borderRadius: 12,
      backgroundColor: c.danger + "18",
      alignItems: "center",
      justifyContent: "center",
    },
    secondaryBtnText: { fontSize: 16, fontWeight: "700", flex: 1 },
    infoBox: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      backgroundColor: c.successSoft,
      padding: 14,
      borderRadius: 12,
    },
    infoText: { fontSize: 15, fontWeight: "600", color: c.text },
    logRow: { flexDirection: "row", gap: 10, paddingVertical: 6 },
    logDot: { width: 8, height: 8, borderRadius: 4, marginTop: 6 },
    logText: { fontSize: 14, fontWeight: "600", color: c.text },
    logTime: { fontSize: 11, color: c.textMuted, marginTop: 2 },
    logReason: {
      fontSize: 12,
      color: c.textMuted,
      marginTop: 4,
      fontStyle: "italic",
      backgroundColor: c.slate50,
      padding: 6,
      borderRadius: 6,
    },
    modalHeader: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingHorizontal: 8,
      paddingTop: Platform.OS === "ios" ? 54 : 16,
      paddingBottom: 12,
      backgroundColor: c.card,
      borderBottomWidth: 1,
      borderBottomColor: c.border,
    },
    modalTitle: { fontSize: 17, fontWeight: "700", color: c.text },
    label: { fontSize: 13, fontWeight: "600", color: c.text, marginTop: 8 },
    hint: { fontSize: 13, color: c.textMuted, marginTop: 2 },
    hintSmall: { fontSize: 11, color: c.textMuted, marginTop: 4 },
    input: {
      backgroundColor: c.slate50,
      borderRadius: 10,
      padding: 12,
      fontSize: 16,
      color: c.text,
      borderWidth: 1,
      borderColor: c.border,
    },
    methodRow: { flexDirection: "row", gap: 8, marginTop: 8 },
    methodChip: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 6,
      padding: 10,
      borderRadius: 10,
      backgroundColor: c.slate50,
      borderWidth: 1,
      borderColor: c.border,
    },
    methodChipActive: { backgroundColor: c.brand, borderColor: c.brand },
    methodText: { fontSize: 14, fontWeight: "700", color: c.textMuted },
    returnRow: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingVertical: 6,
    },
    returnLabel: { fontSize: 14, color: c.text, flex: 1 },
  });
