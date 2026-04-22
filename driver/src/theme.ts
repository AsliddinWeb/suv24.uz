export const colors = {
  bg: "#f8fafc",
  card: "#ffffff",
  text: "#0f172a",
  textMuted: "#64748b",
  border: "#e2e8f0",
  brand: "#2563eb",
  brandDark: "#1d4ed8",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#f43f5e",
  info: "#0ea5e9",
  neutral: "#94a3b8",
  slate50: "#f1f5f9",
  slate100: "#e2e8f0",
  slate200: "#cbd5e1",
  slate800: "#1e293b",
};

export const orderStatusLabel: Record<string, string> = {
  pending: "Kutilmoqda",
  assigned: "Biriktirildi",
  in_delivery: "Yetkazilmoqda",
  delivered: "Yetkazildi",
  failed: "Muvaffaqiyatsiz",
  cancelled: "Bekor qilindi",
};

export const orderStatusColor: Record<string, string> = {
  pending: colors.info,
  assigned: colors.warning,
  in_delivery: colors.brand,
  delivered: colors.success,
  failed: colors.danger,
  cancelled: colors.neutral,
};
