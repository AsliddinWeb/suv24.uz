import type {
  CustomerSegment,
  OrderStatus,
  PaymentMethod,
  PaymentStatus,
} from "@/types/api";

type BadgeVariant = "success" | "warning" | "danger" | "info" | "neutral" | "primary";

export const orderStatusLabel: Record<OrderStatus, string> = {
  pending: "Kutilmoqda",
  assigned: "Biriktirildi",
  in_delivery: "Yetkazilmoqda",
  delivered: "Yetkazildi",
  failed: "Muvaffaqiyatsiz",
  cancelled: "Bekor qilindi",
};

export const orderStatusType: Record<OrderStatus, BadgeVariant> = {
  pending: "info",
  assigned: "warning",
  in_delivery: "primary",
  delivered: "success",
  failed: "danger",
  cancelled: "neutral",
};

export const paymentStatusLabel: Record<PaymentStatus, string> = {
  pending: "Kutilmoqda",
  processing: "Jarayonda",
  paid: "To'langan",
  partial: "Qisman",
  failed: "Xato",
  refunded: "Qaytarilgan",
  cancelled: "Bekor qilindi",
};

export const paymentStatusType: Record<PaymentStatus, BadgeVariant> = {
  pending: "info",
  processing: "warning",
  paid: "success",
  partial: "warning",
  failed: "danger",
  refunded: "neutral",
  cancelled: "neutral",
};

export const paymentMethodLabel: Record<PaymentMethod, string> = {
  cash: "Naqd",
  card_manual: "Karta (manual)",
  payme: "Payme",
  click: "Click",
};

export const segmentLabel: Record<CustomerSegment, string> = {
  new: "Yangi",
  active: "Faol",
  vip: "VIP",
  sleeping: "Uxlayotgan",
};

export const segmentType: Record<CustomerSegment, BadgeVariant> = {
  new: "info",
  active: "success",
  vip: "warning",
  sleeping: "neutral",
};
