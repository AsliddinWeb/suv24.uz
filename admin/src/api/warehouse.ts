import { http } from "./client";
import type { UUID } from "@/types/api";

export interface WarehouseStock {
  id: UUID;
  product_id: UUID;
  product_name: string;
  volume_liters: number;
  is_returnable: boolean;
  full_count: number;
  empty_count: number;
  updated_at: string;
}

export interface WarehouseSummary {
  product_id: UUID;
  product_name: string;
  volume_liters: number;
  warehouse_full: number;
  warehouse_empty: number;
  drivers_full: number;
  drivers_empty: number;
  customer_debt: number;
  total_in_system: number;
}

export interface StockMovement {
  id: UUID;
  product_id: UUID;
  kind: string;
  full_delta: number;
  empty_delta: number;
  driver_id: UUID | null;
  reason: string | null;
  actor_user_id: UUID | null;
  occurred_at: string;
}

export const warehouseApi = {
  list: () => http.get<WarehouseStock[]>("/warehouse").then((r) => r.data),
  summary: () => http.get<WarehouseSummary[]>("/warehouse/summary").then((r) => r.data),
  movements: () => http.get<StockMovement[]>("/warehouse/movements").then((r) => r.data),
  adjust: (body: {
    product_id: UUID;
    full_delta?: number;
    empty_delta?: number;
    reason?: string | null;
  }) => http.post<WarehouseStock>("/warehouse/adjust", body).then((r) => r.data),
  transferToDriver: (body: {
    driver_id: UUID;
    product_id: UUID;
    full_count?: number;
    empty_count?: number;
    reason?: string | null;
  }) =>
    http
      .post<WarehouseStock>("/warehouse/transfer/to-driver", body)
      .then((r) => r.data),
  transferFromDriver: (body: {
    driver_id: UUID;
    product_id: UUID;
    full_count?: number;
    empty_count?: number;
    reason?: string | null;
  }) =>
    http
      .post<WarehouseStock>("/warehouse/transfer/from-driver", body)
      .then((r) => r.data),
};
