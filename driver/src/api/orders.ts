import { http } from "./client";
import type {
  OrderDetailOut,
  OrderOut,
  OrderStatus,
  Page,
  UUID,
  CustomerOut,
  AddressOut,
} from "@/types/api";

export const ordersApi = {
  list: (params: { status?: OrderStatus; page?: number; page_size?: number } = {}) =>
    http.get<Page<OrderOut>>("/orders", { params }).then((r) => r.data),

  get: (id: UUID) =>
    http.get<OrderDetailOut>(`/orders/${id}`).then((r) => r.data),

  start: (id: UUID) =>
    http.post<OrderDetailOut>(`/orders/${id}/start`).then((r) => r.data),

  deliver: (
    id: UUID,
    bottle_returns: { product_id: UUID; count: number }[] = [],
  ) =>
    http
      .post<OrderDetailOut>(`/orders/${id}/deliver`, { bottle_returns })
      .then((r) => r.data),

  fail: (id: UUID, reason: string) =>
    http
      .post<OrderDetailOut>(`/orders/${id}/fail`, { reason })
      .then((r) => r.data),
};

export const customersApi = {
  get: (id: UUID) => http.get<CustomerOut>(`/customers/${id}`).then((r) => r.data),
  listAddresses: (id: UUID) =>
    http.get<AddressOut[]>(`/customers/${id}/addresses`).then((r) => r.data),
};
