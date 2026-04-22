import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import "dayjs/locale/uz-latn";

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale("uz-latn");

export const APP_TZ = "Asia/Tashkent";
dayjs.tz.setDefault(APP_TZ);

export function formatMoney(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("uz-UZ", {
    maximumFractionDigits: 0,
  }).format(num) + " so'm";
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  return dayjs.utc(value).tz(APP_TZ).format("DD.MM.YYYY HH:mm");
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return dayjs.utc(value).tz(APP_TZ).format("DD.MM.YYYY");
}

export function formatTime(value: string | null | undefined): string {
  if (!value) return "—";
  return dayjs.utc(value).tz(APP_TZ).format("HH:mm");
}

// Convert backend UTC ISO string → "YYYY-MM-DDTHH:mm" for <input type="datetime-local">
// showing Asia/Tashkent wall-clock time.
export function toTashkentInput(iso: string | null | undefined): string {
  if (!iso) return "";
  return dayjs.utc(iso).tz(APP_TZ).format("YYYY-MM-DDTHH:mm");
}

// Convert <input type="datetime-local"> value (interpreted as Asia/Tashkent) → UTC ISO.
export function tashkentInputToUtcIso(local: string | null | undefined): string | null {
  if (!local) return null;
  return dayjs.tz(local, APP_TZ).utc().toISOString();
}
