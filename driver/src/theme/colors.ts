export type ColorsScheme = typeof lightColors;

export const lightColors = {
  bg: "#f6f7fb",
  card: "#ffffff",
  cardElevated: "#ffffff",
  text: "#0f172a",
  textMuted: "#64748b",
  textSubtle: "#94a3b8",
  border: "#e2e8f0",
  borderStrong: "#cbd5e1",

  brand: "#2563eb",
  brandDark: "#1d4ed8",
  brandSoft: "#dbeafe",

  success: "#10b981",
  successSoft: "#d1fae5",
  warning: "#f59e0b",
  warningSoft: "#fef3c7",
  danger: "#f43f5e",
  dangerSoft: "#ffe4e6",
  info: "#0ea5e9",
  infoSoft: "#e0f2fe",
  neutral: "#94a3b8",
  neutralSoft: "#f1f5f9",

  slate50: "#f1f5f9",
  slate100: "#e2e8f0",
  slate200: "#cbd5e1",
  slate800: "#1e293b",

  overlay: "rgba(15, 23, 42, 0.5)",
  shadow: "rgba(0, 0, 0, 0.08)",
};

export const darkColors: ColorsScheme = {
  bg: "#0b1220",
  card: "#111827",
  cardElevated: "#1f2937",
  text: "#f1f5f9",
  textMuted: "#94a3b8",
  textSubtle: "#64748b",
  border: "#1f2937",
  borderStrong: "#334155",

  brand: "#3b82f6",
  brandDark: "#2563eb",
  brandSoft: "#1e3a8a",

  success: "#10b981",
  successSoft: "#064e3b",
  warning: "#f59e0b",
  warningSoft: "#78350f",
  danger: "#f43f5e",
  dangerSoft: "#7f1d1d",
  info: "#0ea5e9",
  infoSoft: "#0c4a6e",
  neutral: "#64748b",
  neutralSoft: "#1e293b",

  slate50: "#1e293b",
  slate100: "#1e293b",
  slate200: "#334155",
  slate800: "#e2e8f0",

  overlay: "rgba(0, 0, 0, 0.7)",
  shadow: "rgba(0, 0, 0, 0.5)",
};

export const orderStatusLabel: Record<string, string> = {
  pending: "Kutilmoqda",
  assigned: "Biriktirildi",
  in_delivery: "Yetkazilmoqda",
  delivered: "Yetkazildi",
  failed: "Muvaffaqiyatsiz",
  cancelled: "Bekor qilindi",
};

export function orderStatusColor(status: string, c: ColorsScheme): string {
  switch (status) {
    case "pending":
      return c.info;
    case "assigned":
      return c.warning;
    case "in_delivery":
      return c.brand;
    case "delivered":
      return c.success;
    case "failed":
      return c.danger;
    case "cancelled":
      return c.neutral;
    default:
      return c.textMuted;
  }
}
