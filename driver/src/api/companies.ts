import { http } from "./client";

export interface CompanyOut {
  id: string;
  name: string;
  slug: string;
  short_name: string | null;
  phone: string | null;
  support_phone: string | null;
  address: string | null;
  logo_url: string | null;
  timezone: string;
  currency: string;
}

export const companiesApi = {
  me: () => http.get<CompanyOut>("/companies/me").then((r) => r.data),
};

// Resolve relative /media URLs against the API origin (strip /api/v1 suffix).
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  const base = http.defaults.baseURL || "";
  const origin = base.replace(/\/api\/v\d+\/?$/, "");
  return `${origin}${url.startsWith("/") ? "" : "/"}${url}`;
}
