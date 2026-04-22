import { http } from "./client";

export type TariffPlan = "trial" | "start" | "biznes" | "premium";

export interface PlatformCompanyOut {
  id: string;
  name: string;
  slug: string;
  short_name: string | null;
  phone: string | null;
  support_phone: string | null;
  address: string | null;
  logo_url: string | null;
  tariff_plan: TariffPlan;
  monthly_fee: string;
  trial_ends_at: string | null;
  is_active: boolean;
  timezone: string;
  currency: string;
  created_at: string;
}

export interface PlatformCompanyStats {
  users_count: number;
  drivers_count: number;
  customers_count: number;
  orders_total: number;
  orders_this_month: number;
  revenue_this_month: string;
}

export interface PlatformCompanyDetail extends PlatformCompanyOut {
  stats: PlatformCompanyStats;
}

export interface PlatformTopCompany {
  id: string;
  name: string;
  slug: string;
  tariff_plan: TariffPlan;
  revenue_this_month: string;
  orders_this_month: number;
}

export interface PlatformOverview {
  companies_total: number;
  companies_active: number;
  companies_trial: number;
  platform_mrr: string;
  orders_this_month: number;
  revenue_this_month: string;
  tariff_breakdown: Record<TariffPlan, number>;
  top_companies_by_revenue: PlatformTopCompany[];
}

export interface PlatformCompanyCreate {
  name: string;
  slug: string;
  phone?: string | null;
  address?: string | null;
  tariff_plan?: TariffPlan;
  monthly_fee?: string | number;
  trial_ends_at?: string | null;
  admin_full_name: string;
  admin_phone: string;
  admin_password: string;
}

export interface PlatformCompanyUpdate {
  name?: string | null;
  short_name?: string | null;
  phone?: string | null;
  support_phone?: string | null;
  address?: string | null;
  logo_url?: string | null;
  tariff_plan?: TariffPlan | null;
  monthly_fee?: string | number | null;
  trial_ends_at?: string | null;
  is_active?: boolean | null;
}

export const platformApi = {
  overview: () => http.get<PlatformOverview>("/platform/overview").then((r) => r.data),
  listCompanies: (params?: { q?: string; active?: boolean }) =>
    http
      .get<PlatformCompanyOut[]>("/platform/companies", { params })
      .then((r) => r.data),
  getCompany: (id: string) =>
    http.get<PlatformCompanyDetail>(`/platform/companies/${id}`).then((r) => r.data),
  createCompany: (body: PlatformCompanyCreate) =>
    http.post<PlatformCompanyDetail>("/platform/companies", body).then((r) => r.data),
  updateCompany: (id: string, body: PlatformCompanyUpdate) =>
    http.patch<PlatformCompanyOut>(`/platform/companies/${id}`, body).then((r) => r.data),
  deleteCompany: (id: string) => http.delete(`/platform/companies/${id}`).then((r) => r.data),
};

export const TARIFF_LABELS: Record<TariffPlan, string> = {
  trial: "Sinov",
  start: "Start",
  biznes: "Biznes",
  premium: "Premium",
};

export const TARIFF_COLORS: Record<TariffPlan, string> = {
  trial: "slate",
  start: "sky",
  biznes: "amber",
  premium: "rose",
};
