import { http } from "./client";
import type { AddressOut, CustomerOut, Page, UUID } from "@/types/api";

export const customersApi = {
  list: (params: { q?: string; page?: number; page_size?: number } = {}) =>
    http.get<Page<CustomerOut>>("/customers", { params }).then((r) => r.data),

  get: (id: UUID) => http.get<CustomerOut>(`/customers/${id}`).then((r) => r.data),

  create: (body: {
    phone: string;
    full_name: string;
    segment?: string;
    notes?: string;
  }) => http.post<CustomerOut>("/customers", body).then((r) => r.data),

  update: (id: UUID, body: Partial<CustomerOut>) =>
    http.patch<CustomerOut>(`/customers/${id}`, body).then((r) => r.data),

  remove: (id: UUID) => http.delete(`/customers/${id}`).then((r) => r.data),

  listAddresses: (id: UUID) =>
    http.get<AddressOut[]>(`/customers/${id}/addresses`).then((r) => r.data),

  createAddress: (
    id: UUID,
    body: {
      label?: string;
      address_text: string;
      lat?: number | null;
      lng?: number | null;
      notes?: string;
    },
  ) => http.post<AddressOut>(`/customers/${id}/addresses`, body).then((r) => r.data),

  removeAddress: (customerId: UUID, addressId: UUID) =>
    http.delete(`/customers/${customerId}/addresses/${addressId}`).then((r) => r.data),
};
