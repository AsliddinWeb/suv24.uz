import { http } from "./client";

export type LeadStatus = "new" | "contacted" | "converted" | "rejected";

export interface LeadOut {
  id: string;
  full_name: string;
  phone: string;
  company_name: string | null;
  source: string;
  notes: string | null;
  status: LeadStatus;
  created_at: string;
  updated_at: string;
}

export interface LeadCreate {
  full_name: string;
  phone: string;
  company_name?: string | null;
  notes?: string | null;
  source?: string;
}

export interface LeadUpdate {
  full_name?: string | null;
  phone?: string | null;
  company_name?: string | null;
  notes?: string | null;
  status?: LeadStatus | null;
}

export const leadsApi = {
  // Public — no auth required, rate-limited
  submit: (body: LeadCreate) =>
    http.post<{ id: string; message: string }>("/leads", body).then((r) => r.data),

  // Platform owner only
  list: (params?: { status?: LeadStatus; q?: string }) =>
    http.get<LeadOut[]>("/leads", { params }).then((r) => r.data),
  update: (id: string, body: LeadUpdate) =>
    http.patch<LeadOut>(`/leads/${id}`, body).then((r) => r.data),
  remove: (id: string) => http.delete(`/leads/${id}`).then((r) => r.data),
};

export const LEAD_STATUS_LABELS: Record<LeadStatus, string> = {
  new: "Yangi",
  contacted: "Bog'lanilgan",
  converted: "Mijoz bo'lgan",
  rejected: "Rad etilgan",
};

export const LEAD_STATUS_COLORS: Record<LeadStatus, "info" | "warning" | "success" | "neutral"> = {
  new: "info",
  contacted: "warning",
  converted: "success",
  rejected: "neutral",
};
