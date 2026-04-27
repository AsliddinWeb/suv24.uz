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

export interface CompanyUpdate {
  name?: string | null;
  short_name?: string | null;
  phone?: string | null;
  support_phone?: string | null;
  address?: string | null;
  logo_url?: string | null;
}

export interface TariffUsage {
  tariff_plan: "trial" | "start" | "biznes" | "premium";
  tariff_label: string;
  drivers: { used: number; limit: number | null };
  customers: { used: number; limit: number | null };
  orders_this_month: { used: number; limit: number | null };
  trial_ends_at: string | null;
}

export const companiesApi = {
  me: () => http.get<CompanyOut>("/companies/me").then((r) => r.data),
  usage: () => http.get<TariffUsage>("/companies/me/usage").then((r) => r.data),
  update: (body: CompanyUpdate) =>
    http.patch<CompanyOut>("/companies/me", body).then((r) => r.data),
  uploadLogo: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return http
      .post<CompanyOut>("/companies/me/logo", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};

// Resolve a possibly-relative media URL (e.g. "/media/logos/x.png") to
// something the browser can load. Vite proxies /media to the backend in dev,
// so a relative URL works as-is.
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return url;
}
