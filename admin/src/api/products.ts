import { http } from "./client";
import type { PriceOut, ProductOut, UUID } from "@/types/api";

export interface ProductStockSummary {
  product_id: UUID;
  warehouse_full: number;
  warehouse_empty: number;
  drivers_full: number;
  drivers_empty: number;
  available_full: number;
  is_returnable: boolean;
}

export const productsApi = {
  list: (params: { only_active?: boolean } = {}) =>
    http.get<ProductOut[]>("/products", { params }).then((r) => r.data),

  stocks: () =>
    http.get<ProductStockSummary[]>("/products/stocks").then((r) => r.data),

  get: (id: UUID) => http.get<ProductOut>(`/products/${id}`).then((r) => r.data),

  create: (body: {
    name: string;
    volume_liters: number;
    is_returnable: boolean;
    is_active?: boolean;
    initial_price: string;
  }) => http.post<ProductOut>("/products", body).then((r) => r.data),

  update: (id: UUID, body: Partial<ProductOut>) =>
    http.patch<ProductOut>(`/products/${id}`, body).then((r) => r.data),

  remove: (id: UUID) => http.delete(`/products/${id}`).then((r) => r.data),

  priceHistory: (id: UUID) =>
    http.get<PriceOut[]>(`/products/${id}/prices`).then((r) => r.data),

  setPrice: (id: UUID, price: string) =>
    http.post<PriceOut>(`/products/${id}/prices`, { price }).then((r) => r.data),
};
