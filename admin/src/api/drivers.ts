import { http } from "./client";
import type { BottleBalanceWithProduct, DriverOut, UUID } from "@/types/api";

export const driversApi = {
  list: () => http.get<DriverOut[]>("/drivers").then((r) => r.data),

  get: (id: UUID) => http.get<DriverOut>(`/drivers/${id}`).then((r) => r.data),

  create: (body: {
    full_name: string;
    phone: string;
    password: string;
    vehicle_plate?: string | null;
  }) => http.post<DriverOut>("/drivers", body).then((r) => r.data),

  update: (
    id: UUID,
    body: {
      full_name?: string | null;
      phone?: string | null;
      password?: string | null;
      vehicle_plate?: string | null;
      is_active?: boolean | null;
    },
  ) => http.patch<DriverOut>(`/drivers/${id}`, body).then((r) => r.data),

  remove: (id: UUID) => http.delete(`/drivers/${id}`).then((r) => r.data),

  bottles: (id: UUID) =>
    http.get<BottleBalanceWithProduct[]>(`/drivers/${id}/bottles`).then((r) => r.data),

  adjustBottles: (
    id: UUID,
    body: {
      product_id: UUID;
      full_delta?: number;
      empty_delta?: number;
      reason?: string;
    },
  ) =>
    http
      .post<BottleBalanceWithProduct>(`/drivers/${id}/bottles/adjust`, body)
      .then((r) => r.data),
};
