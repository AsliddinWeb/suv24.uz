import { http } from "./client";
import type {
  DailyCashSummary,
  Page,
  PaymentMethod,
  PaymentOut,
  PaymentStatus,
  UUID,
} from "@/types/api";

export const paymentsApi = {
  list: (params: {
    order_id?: UUID;
    customer_id?: UUID;
    method?: PaymentMethod;
    status?: PaymentStatus;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  } = {}) => http.get<Page<PaymentOut>>("/payments", { params }).then((r) => r.data),

  record: (body: {
    order_id: UUID;
    amount: string;
    method: PaymentMethod;
    notes?: string;
    provider_tx_id?: string;
  }) => http.post<PaymentOut>("/payments", body).then((r) => r.data),

  refund: (id: UUID, reason?: string) =>
    http.post<PaymentOut>(`/payments/${id}/refund`, { reason }).then((r) => r.data),

  cashSummary: (params: { day?: string; driver_id?: UUID } = {}) =>
    http.get<DailyCashSummary>("/payments/summary/cash", { params }).then((r) => r.data),
};
