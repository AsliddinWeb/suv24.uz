import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Pressable,
  RefreshControl,
  ActivityIndicator,
  Linking,
} from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useFocusEffect } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import * as Haptics from "expo-haptics";
import Animated, { FadeInDown } from "react-native-reanimated";
import { ordersApi } from "@/api/orders";
import { useAuth } from "@/stores/auth";
import { useTheme } from "@/stores/theme";
import { orderStatusColor, orderStatusLabel, type ColorsScheme } from "@/theme/colors";
import { formatMoney, formatTime } from "@/utils/format";
import { useDriverLocation, haversineKm } from "@/hooks/useDriverLocation";
import type { OrderOut, OrderStatus } from "@/types/api";

const FILTERS: { label: string; value: OrderStatus | null }[] = [
  { label: "Bugungi", value: null },
  { label: "Biriktirilgan", value: "assigned" },
  { label: "Yo'lda", value: "in_delivery" },
  { label: "Yetkazildi", value: "delivered" },
];

function formatDistance(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)} m`;
  return `${km.toFixed(km < 10 ? 1 : 0)} km`;
}

export default function OrdersListScreen() {
  const { colors } = useTheme();
  const styles = useMemo(() => makeStyles(colors), [colors]);

  const [filter, setFilter] = useState<OrderStatus | null>(null);
  const [pulling, setPulling] = useState(false);
  const seenIdsRef = useRef<Set<string>>(new Set());
  const firstLoadRef = useRef(true);

  const { user } = useAuth();
  const isDriver = user?.role === "driver";
  // Track GPS in foreground; pings backend every 30s while driver is logged in
  const { coords: driverCoords } = useDriverLocation({ enabled: isDriver });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["orders", filter],
    queryFn: () => ordersApi.list({ status: filter ?? undefined, page_size: 50 }),
    staleTime: 15_000,
  });

  useFocusEffect(
    useCallback(() => {
      refetch();
    }, [refetch]),
  );

  const rawItems = data?.items ?? [];

  // Compute distance for each order from driver's current position; sort active
  // (assigned/in_delivery) orders nearest-first so the driver knows where to go next.
  const items = useMemo(() => {
    if (!driverCoords) return rawItems;
    const ACTIVE = new Set<OrderStatus>(["assigned", "in_delivery", "pending"]);

    type Decorated = OrderOut & { _km?: number };
    const decorated: Decorated[] = rawItems.map((o) => {
      const lat = o.address?.lat ? Number(o.address.lat) : null;
      const lng = o.address?.lng ? Number(o.address.lng) : null;
      const km =
        lat != null && lng != null
          ? haversineKm(driverCoords, { lat, lng })
          : undefined;
      return { ...o, _km: km };
    });

    return decorated.sort((a, b) => {
      const aActive = ACTIVE.has(a.status);
      const bActive = ACTIVE.has(b.status);
      if (aActive !== bActive) return aActive ? -1 : 1;
      // Within active: nearest first (orders without coords go to bottom)
      if (aActive && bActive) {
        if (a._km == null && b._km == null) return 0;
        if (a._km == null) return 1;
        if (b._km == null) return -1;
        return a._km - b._km;
      }
      return 0;
    });
  }, [rawItems, driverCoords]);

  const activeWithCoords = useMemo(
    () =>
      items.filter(
        (o) =>
          (o.status === "assigned" || o.status === "in_delivery" || o.status === "pending") &&
          o.address?.lat &&
          o.address?.lng,
      ),
    [items],
  );

  function openMultiStopRoute() {
    if (!activeWithCoords.length || !driverCoords) return;
    Haptics.selectionAsync();
    // Yandex multi-stop: rtext=lat,lng~lat,lng~... Start with driver's current location.
    const points = [
      `${driverCoords.lat},${driverCoords.lng}`,
      ...activeWithCoords.map((o) => `${o.address!.lat},${o.address!.lng}`),
    ].join("~");
    const yandexApp = `yandexmaps://maps.yandex.ru/?rtext=${points}&rtt=auto`;
    const yandexWeb = `https://yandex.uz/maps/?rtext=${points}&rtt=auto`;
    Linking.openURL(yandexApp).catch(() => Linking.openURL(yandexWeb));
  }

  const { assignedCount, inDeliveryCount, deliveredCount } = useMemo(() => {
    return {
      assignedCount: items.filter((o) => o.status === "assigned").length,
      inDeliveryCount: items.filter((o) => o.status === "in_delivery").length,
      deliveredCount: items.filter((o) => o.status === "delivered").length,
    };
  }, [items]);

  const newIds = useMemo(() => {
    const current = new Set(items.map((o) => o.id));
    const previous = seenIdsRef.current;
    const fresh = new Set<string>();
    current.forEach((id) => {
      if (!previous.has(id)) fresh.add(id);
    });
    seenIdsRef.current = current;
    return fresh;
  }, [items]);

  useEffect(() => {
    if (firstLoadRef.current) {
      if (items.length > 0) firstLoadRef.current = false;
      return;
    }
    if (newIds.size > 0) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  }, [newIds, items.length]);

  function onFilterChange(next: OrderStatus | null) {
    Haptics.selectionAsync();
    setFilter(next);
  }

  async function onRefresh() {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setPulling(true);
    try {
      await refetch();
    } finally {
      setPulling(false);
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.summaryRow}>
        <SummaryPill
          icon="hourglass"
          label="Kutilmoqda"
          value={assignedCount}
          color={colors.warning}
          colors={colors}
          styles={styles}
        />
        <SummaryPill
          icon="navigate"
          label="Yo'lda"
          value={inDeliveryCount}
          color={colors.brand}
          colors={colors}
          styles={styles}
        />
        <SummaryPill
          icon="checkmark-done"
          label="Yetkazildi"
          value={deliveredCount}
          color={colors.success}
          colors={colors}
          styles={styles}
        />
      </View>

      <View style={styles.filters}>
        <FlatList
          data={FILTERS}
          horizontal
          showsHorizontalScrollIndicator={false}
          keyExtractor={(f) => f.label}
          contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
          renderItem={({ item }) => {
            const active = filter === item.value;
            return (
              <Pressable
                onPress={() => onFilterChange(item.value)}
                style={[styles.chip, active && styles.chipActive]}
              >
                <Text style={[styles.chipText, active && styles.chipTextActive]}>
                  {item.label}
                </Text>
              </Pressable>
            );
          }}
        />
      </View>

      {activeWithCoords.length >= 2 && driverCoords && (
        <Pressable onPress={openMultiStopRoute} style={styles.routeBtn}>
          <Ionicons name="navigate" size={18} color="#fff" />
          <View style={{ flex: 1 }}>
            <Text style={styles.routeBtnText}>Marshrutni xaritada ko'rish</Text>
            <Text style={styles.routeBtnSub}>
              {activeWithCoords.length} ta nuqta · eng yaqindan boshlab
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={18} color="#fff" />
        </Pressable>
      )}

      {isLoading && items.length === 0 ? (
        <View style={styles.loading}>
          <ActivityIndicator size="large" color={colors.brand} />
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(o) => o.id}
          contentContainerStyle={{ padding: 16, gap: 12, paddingBottom: 28 }}
          refreshControl={
            <RefreshControl
              refreshing={pulling}
              onRefresh={onRefresh}
              tintColor={colors.brand}
            />
          }
          ListEmptyComponent={
            <View style={styles.empty}>
              <View style={styles.emptyIcon}>
                <Ionicons name="cafe-outline" size={40} color={colors.brand} />
              </View>
              <Text style={styles.emptyText}>Hozircha buyurtma yo'q</Text>
              <Text style={styles.emptySub}>Yangi buyurtma kelganda bu yerda ko'rinadi</Text>
            </View>
          }
          renderItem={({ item, index }) => (
            <OrderCard
              order={item}
              isNew={newIds.has(item.id)}
              index={index}
              distanceKm={(item as OrderOut & { _km?: number })._km}
              orderIndex={
                activeWithCoords.findIndex((o) => o.id === item.id) >= 0
                  ? activeWithCoords.findIndex((o) => o.id === item.id) + 1
                  : null
              }
              colors={colors}
              styles={styles}
            />
          )}
        />
      )}
    </View>
  );
}

function SummaryPill({
  icon,
  label,
  value,
  color,
  styles,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: number;
  color: string;
  colors: ColorsScheme;
  styles: ReturnType<typeof makeStyles>;
}) {
  return (
    <View
      style={[styles.summaryPill, { backgroundColor: color + "18", borderColor: color + "40" }]}
    >
      <Ionicons name={icon} size={16} color={color} />
      <View>
        <Text style={[styles.summaryValue, { color }]}>{value}</Text>
        <Text style={styles.summaryLabel}>{label}</Text>
      </View>
    </View>
  );
}

function OrderCard({
  order,
  isNew,
  index,
  distanceKm,
  orderIndex,
  colors,
  styles,
}: {
  order: OrderOut;
  isNew: boolean;
  index: number;
  distanceKm?: number;
  orderIndex: number | null;
  colors: ColorsScheme;
  styles: ReturnType<typeof makeStyles>;
}) {
  const statusColor = orderStatusColor(order.status, colors);
  const total = parseFloat(order.total);
  const paid = parseFloat(order.paid_amount || "0");
  const isFullyPaid = paid >= total;

  return (
    <Animated.View entering={FadeInDown.delay(Math.min(index, 6) * 40).duration(300)}>
    <Pressable
      onPress={() => {
        Haptics.selectionAsync();
        router.push(`/orders/${order.id}`);
      }}
      style={({ pressed }) => [
        styles.card,
        pressed && { transform: [{ scale: 0.98 }], opacity: 0.92 },
        isNew && styles.cardNew,
      ]}
    >
      {isNew && (
        <View style={styles.newBadge}>
          <Text style={styles.newBadgeText}>YANGI</Text>
        </View>
      )}

      <View style={styles.cardTop}>
        <View style={styles.cardLeft}>
          {orderIndex != null && (
            <View style={styles.stopBadge}>
              <Text style={styles.stopBadgeText}>{orderIndex}</Text>
            </View>
          )}
          <Text style={styles.orderNumber}>#{order.number}</Text>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusBadgeText}>{orderStatusLabel[order.status]}</Text>
          </View>
        </View>
        <Text style={styles.cardTotal}>{formatMoney(order.total)}</Text>
      </View>

      {order.customer && (
        <View style={styles.cardCustomer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {order.customer.full_name.slice(0, 1).toUpperCase()}
            </Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.customerName} numberOfLines={1}>
              {order.customer.full_name}
            </Text>
            <Text style={styles.customerPhone}>{order.customer.phone}</Text>
          </View>
        </View>
      )}

      {order.address && (
        <View style={styles.cardRow}>
          <Ionicons name="location" size={15} color={colors.textMuted} />
          <Text style={styles.addressText} numberOfLines={1}>
            {order.address.address_text}
          </Text>
          {distanceKm != null && (
            <View style={styles.distancePill}>
              <Text style={styles.distanceText}>{formatDistance(distanceKm)}</Text>
            </View>
          )}
          {order.address.lat && order.address.lng && (
            <Ionicons name="navigate-circle" size={16} color={colors.brand} />
          )}
        </View>
      )}

      <View style={styles.cardFooter}>
        {order.delivery_window_start && (
          <View style={styles.metaPill}>
            <Ionicons name="time" size={13} color={colors.textMuted} />
            <Text style={styles.metaText}>
              {formatTime(order.delivery_window_start)}
              {order.delivery_window_end ? `–${formatTime(order.delivery_window_end)}` : ""}
            </Text>
          </View>
        )}
        <View style={{ flex: 1 }} />
        {!isFullyPaid && order.status !== "cancelled" && (
          <View style={[styles.payPill, { backgroundColor: colors.danger }]}>
            <Text style={styles.payPillText}>To'lanmagan</Text>
          </View>
        )}
        {isFullyPaid && (
          <View style={[styles.payPill, { backgroundColor: colors.success }]}>
            <Text style={styles.payPillText}>✓ To'langan</Text>
          </View>
        )}
      </View>

      {order.notes && (
        <View style={styles.noteBox}>
          <Ionicons name="chatbubble-ellipses" size={13} color={colors.warning} />
          <Text style={styles.noteText} numberOfLines={2}>
            {order.notes}
          </Text>
        </View>
      )}
    </Pressable>
    </Animated.View>
  );
}

const makeStyles = (c: ColorsScheme) =>
  StyleSheet.create({
    container: { flex: 1, backgroundColor: c.bg },
    summaryRow: {
      flexDirection: "row",
      paddingHorizontal: 16,
      paddingTop: 12,
      gap: 8,
      backgroundColor: c.card,
      borderBottomWidth: 1,
      borderBottomColor: c.border,
      paddingBottom: 12,
    },
    summaryPill: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      gap: 8,
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 12,
      borderWidth: 1,
    },
    summaryValue: { fontSize: 18, fontWeight: "800" },
    summaryLabel: { fontSize: 10, color: c.textMuted, fontWeight: "600" },
    filters: {
      backgroundColor: c.card,
      paddingVertical: 10,
      borderBottomWidth: 1,
      borderBottomColor: c.border,
    },
    chip: {
      paddingHorizontal: 14,
      paddingVertical: 8,
      borderRadius: 20,
      backgroundColor: c.slate50,
      borderWidth: 1,
      borderColor: "transparent",
    },
    chipActive: { backgroundColor: c.brand, borderColor: c.brand },
    chipText: { fontSize: 13, fontWeight: "600", color: c.textMuted },
    chipTextActive: { color: "#fff" },
    routeBtn: {
      marginHorizontal: 16,
      marginTop: 12,
      backgroundColor: c.brand,
      flexDirection: "row",
      alignItems: "center",
      gap: 12,
      paddingHorizontal: 16,
      paddingVertical: 12,
      borderRadius: 14,
      shadowColor: c.brand,
      shadowOpacity: 0.3,
      shadowRadius: 10,
      shadowOffset: { width: 0, height: 4 },
      elevation: 4,
    },
    routeBtnText: { color: "#fff", fontSize: 14, fontWeight: "700" },
    routeBtnSub: { color: "rgba(255,255,255,0.85)", fontSize: 11, marginTop: 2 },
    stopBadge: {
      width: 22,
      height: 22,
      borderRadius: 11,
      backgroundColor: c.brand,
      alignItems: "center",
      justifyContent: "center",
    },
    stopBadgeText: { color: "#fff", fontSize: 11, fontWeight: "800" },
    distancePill: {
      paddingHorizontal: 8,
      paddingVertical: 2,
      borderRadius: 8,
      backgroundColor: c.brandSoft,
    },
    distanceText: {
      fontSize: 11,
      fontWeight: "700",
      color: c.brand,
    },
    loading: { flex: 1, alignItems: "center", justifyContent: "center" },
    card: {
      backgroundColor: c.card,
      borderRadius: 16,
      padding: 14,
      gap: 10,
      borderWidth: 1,
      borderColor: c.border,
      shadowColor: c.shadow,
      shadowOpacity: 0.6,
      shadowRadius: 6,
      shadowOffset: { width: 0, height: 2 },
      elevation: 1,
    },
    cardNew: {
      borderColor: c.brand,
      shadowColor: c.brand,
      shadowOpacity: 0.3,
      shadowRadius: 12,
      elevation: 4,
    },
    newBadge: {
      position: "absolute",
      top: -1,
      right: 12,
      backgroundColor: c.brand,
      paddingHorizontal: 10,
      paddingVertical: 4,
      borderBottomLeftRadius: 8,
      borderBottomRightRadius: 8,
      zIndex: 1,
    },
    newBadgeText: { color: "#fff", fontSize: 10, fontWeight: "800", letterSpacing: 0.5 },
    cardTop: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
    cardLeft: { flexDirection: "row", alignItems: "center", gap: 10 },
    orderNumber: { fontSize: 17, fontWeight: "800", color: c.brand },
    statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
    statusBadgeText: { color: "#fff", fontSize: 10, fontWeight: "700" },
    cardTotal: { fontSize: 17, fontWeight: "800", color: c.text },
    cardCustomer: {
      flexDirection: "row",
      alignItems: "center",
      gap: 10,
      paddingVertical: 6,
      borderTopWidth: 1,
      borderTopColor: c.border,
    },
    avatar: {
      width: 34,
      height: 34,
      borderRadius: 17,
      backgroundColor: c.brand,
      alignItems: "center",
      justifyContent: "center",
    },
    avatarText: { color: "#fff", fontSize: 13, fontWeight: "800" },
    customerName: { fontSize: 14, fontWeight: "700", color: c.text },
    customerPhone: { fontSize: 12, color: c.textMuted, marginTop: 1 },
    cardRow: { flexDirection: "row", alignItems: "center", gap: 6 },
    addressText: { flex: 1, fontSize: 13, color: c.textMuted },
    cardFooter: { flexDirection: "row", alignItems: "center", gap: 8 },
    metaPill: {
      flexDirection: "row",
      alignItems: "center",
      gap: 4,
      backgroundColor: c.slate50,
      paddingHorizontal: 10,
      paddingVertical: 5,
      borderRadius: 10,
    },
    metaText: { fontSize: 11, color: c.textMuted, fontWeight: "600" },
    payPill: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 10 },
    payPillText: { color: "#fff", fontSize: 10, fontWeight: "800" },
    noteBox: {
      flexDirection: "row",
      alignItems: "flex-start",
      gap: 6,
      backgroundColor: c.warningSoft,
      padding: 8,
      borderRadius: 10,
      borderWidth: 1,
      borderColor: c.warning + "40",
    },
    noteText: { flex: 1, fontSize: 12, color: c.text, lineHeight: 16 },
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
    emptyText: { fontSize: 16, fontWeight: "700", color: c.text },
    emptySub: { fontSize: 13, color: c.textMuted, textAlign: "center" },
  });
