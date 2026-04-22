export const APP_TZ = "Asia/Tashkent";

export function formatMoney(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("uz-UZ", { maximumFractionDigits: 0 }).format(num) + " so'm";
}

const dateTimeFmt = new Intl.DateTimeFormat("en-GB", {
  timeZone: APP_TZ,
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

const dateFmt = new Intl.DateTimeFormat("en-GB", {
  timeZone: APP_TZ,
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

const timeFmt = new Intl.DateTimeFormat("en-GB", {
  timeZone: APP_TZ,
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

function parts(fmt: Intl.DateTimeFormat, d: Date): Record<string, string> {
  const out: Record<string, string> = {};
  for (const p of fmt.formatToParts(d)) {
    if (p.type !== "literal") out[p.type] = p.value;
  }
  return out;
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  const p = parts(dateTimeFmt, new Date(value));
  return `${p.day}.${p.month}.${p.year} ${p.hour}:${p.minute}`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const p = parts(dateFmt, new Date(value));
  return `${p.day}.${p.month}.${p.year}`;
}

export function formatTime(value: string | null | undefined): string {
  if (!value) return "—";
  const p = parts(timeFmt, new Date(value));
  return `${p.hour}:${p.minute}`;
}
