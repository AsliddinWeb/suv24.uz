import type { OrderStatus, OrderStatusLogOut } from "@/types/api";

type Tone = "success" | "warning" | "danger" | "info" | "neutral" | "primary";

export interface LogEntry {
  title: string;
  tone: Tone;
  icon: "created" | "assigned" | "reassigned" | "unassigned" | "start" | "delivered" | "failed" | "cancelled" | "retry" | "default";
  reason: string | null;
  timestamp: string;
}

const STATUS_UZ: Record<OrderStatus, string> = {
  pending: "kutilmoqda",
  assigned: "biriktirildi",
  in_delivery: "yetkazilmoqda",
  delivered: "yetkazildi",
  failed: "muvaffaqiyatsiz",
  cancelled: "bekor qilindi",
};

export function describeStatusLog(log: OrderStatusLogOut): LogEntry {
  const from = log.from_status;
  const to = log.to_status;

  if (!from && to === "pending") {
    return {
      title: "Buyurtma yaratildi",
      tone: "info",
      icon: "created",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "pending" && to === "assigned") {
    return {
      title: "Haydovchiga biriktirildi",
      tone: "warning",
      icon: "assigned",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "assigned" && to === "assigned") {
    return {
      title: "Boshqa haydovchiga qayta biriktirildi",
      tone: "warning",
      icon: "reassigned",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "assigned" && to === "pending") {
    return {
      title: "Haydovchidan olib qo'yildi",
      tone: "neutral",
      icon: "unassigned",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "assigned" && to === "in_delivery") {
    return {
      title: "Yetkazish boshlandi",
      tone: "primary",
      icon: "start",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "in_delivery" && to === "delivered") {
    return {
      title: "Yetkazib berildi",
      tone: "success",
      icon: "delivered",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "in_delivery" && to === "failed") {
    return {
      title: "Yetkazib bo'lmadi",
      tone: "danger",
      icon: "failed",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (to === "cancelled") {
    return {
      title: "Bekor qilindi",
      tone: "neutral",
      icon: "cancelled",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  if (from === "failed" && to === "pending") {
    return {
      title: "Qayta urinish",
      tone: "info",
      icon: "retry",
      reason: log.reason,
      timestamp: log.created_at,
    };
  }
  return {
    title: `${STATUS_UZ[from ?? to]} → ${STATUS_UZ[to]}`,
    tone: "neutral",
    icon: "default",
    reason: log.reason,
    timestamp: log.created_at,
  };
}
