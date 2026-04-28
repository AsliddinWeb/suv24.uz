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

// ----- Cash + Purchases -----

export type CashTxKind =
  | "opening_balance"
  | "purchase"
  | "expense"
  | "customer_payment"
  | "refund"
  | "manual_in"
  | "manual_out";

export interface CashAccount {
  id: UUID;
  balance: string;
  currency: string;
  opening_set_at: string | null;
}

export interface CashTransaction {
  id: UUID;
  kind: CashTxKind;
  amount: string;
  description: string | null;
  occurred_at: string;
  actor_user_id: UUID | null;
  related_purchase_id: UUID | null;
  related_payment_id: UUID | null;
  created_at: string;
}

export interface CashSnapshot {
  account: CashAccount;
  recent: CashTransaction[];
  needs_opening_balance: boolean;
}

export interface InventoryPurchase {
  id: UUID;
  product_id: UUID;
  product_name: string | null;
  volume_liters: number | null;
  full_count: number;
  empty_count: number;
  unit_cost: string;
  total_cost: string;
  supplier: string | null;
  note: string | null;
  occurred_at: string;
  created_at: string;
}

export interface CashSummary {
  balance: string;
  today_in: string;
  today_out: string;
  month_in: string;
  month_out: string;
}

export const cashApi = {
  snapshot: () => http.get<CashSnapshot>("/warehouse/cash").then((r) => r.data),
  summary: () => http.get<CashSummary>("/warehouse/cash/summary").then((r) => r.data),
  transactions: (limit = 100) =>
    http
      .get<CashTransaction[]>("/warehouse/cash/transactions", { params: { limit } })
      .then((r) => r.data),
  setOpeningBalance: (body: { amount: string | number; note?: string | null }) =>
    http.post<CashAccount>("/warehouse/cash/opening-balance", body).then((r) => r.data),
  expense: (body: { amount: string | number; description: string; occurred_at?: string | null }) =>
    http.post<CashTransaction>("/warehouse/cash/expense", body).then((r) => r.data),
  manual: (body: {
    direction: "in" | "out";
    amount: string | number;
    description: string;
    occurred_at?: string | null;
  }) => http.post<CashTransaction>("/warehouse/cash/manual", body).then((r) => r.data),
};

export const purchasesApi = {
  list: (limit = 100) =>
    http.get<InventoryPurchase[]>("/warehouse/purchases", { params: { limit } }).then((r) => r.data),
  create: (body: {
    product_id: UUID;
    full_count?: number;
    empty_count?: number;
    unit_cost: string | number;
    supplier?: string | null;
    note?: string | null;
    occurred_at?: string | null;
  }) =>
    http.post<InventoryPurchase>("/warehouse/purchases", body).then((r) => r.data),
};

export const CASH_KIND_LABELS: Record<CashTxKind, string> = {
  opening_balance: "Boshlang'ich balans",
  purchase: "Mahsulot kirimi",
  expense: "Xarajat",
  customer_payment: "Mijoz to'lovi",
  refund: "Qaytarish",
  manual_in: "Qo'lda kirim",
  manual_out: "Qo'lda chiqim",
};

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
