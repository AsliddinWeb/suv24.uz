import { http } from "./client";
import type {
  OrderDetailOut,
  OrderOut,
  OrderStatus,
  Page,
  UUID,
} from "@/types/api";

export const ordersApi = {
  list: (params: {
    status?: OrderStatus;
    driver_id?: UUID;
    customer_id?: UUID;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  } = {}) => http.get<Page<OrderOut>>("/orders", { params }).then((r) => r.data),

  get: (id: UUID) => http.get<OrderDetailOut>(`/orders/${id}`).then((r) => r.data),

  create: (body: {
    customer_id: UUID;
    address_id: UUID;
    items: { product_id: UUID; quantity: number }[];
    delivery_window_start?: string | null;
    delivery_window_end?: string | null;
    notes?: string;
  }) => http.post<OrderDetailOut>("/orders", body).then((r) => r.data),

  update: (id: UUID, body: { delivery_window_start?: string; delivery_window_end?: string; notes?: string }) =>
    http.patch<OrderDetailOut>(`/orders/${id}`, body).then((r) => r.data),

  assign: (id: UUID, driver_id: UUID) =>
    http.post<OrderDetailOut>(`/orders/${id}/assign`, { driver_id }).then((r) => r.data),

  unassign: (id: UUID) =>
    http.post<OrderDetailOut>(`/orders/${id}/unassign`).then((r) => r.data),

  start: (id: UUID) =>
    http.post<OrderDetailOut>(`/orders/${id}/start`).then((r) => r.data),

  deliver: (id: UUID, bottle_returns: { product_id: UUID; count: number }[] = []) =>
    http
      .post<OrderDetailOut>(`/orders/${id}/deliver`, { bottle_returns })
      .then((r) => r.data),

  fail: (id: UUID, reason: string) =>
    http.post<OrderDetailOut>(`/orders/${id}/fail`, { reason }).then((r) => r.data),

  cancel: (id: UUID, reason: string) =>
    http.post<OrderDetailOut>(`/orders/${id}/cancel`, { reason }).then((r) => r.data),

  retry: (id: UUID) =>
    http.post<OrderDetailOut>(`/orders/${id}/retry`).then((r) => r.data),

  remove: (id: UUID) => http.delete(`/orders/${id}`).then((r) => r.data),
};
