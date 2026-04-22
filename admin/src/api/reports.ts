import { http } from "./client";
import type { OrderStatus } from "@/types/api";

export interface DailyRevenuePoint {
  date: string;
  revenue: string;
  orders: number;
}

export interface StatusDistributionItem {
  status: OrderStatus;
  count: number;
}

export const reportsApi = {
  dailyRevenue: (days = 7) =>
    http
      .get<DailyRevenuePoint[]>("/reports/revenue/daily", { params: { days } })
      .then((r) => r.data),

  ordersByStatus: () =>
    http.get<StatusDistributionItem[]>("/reports/orders/by-status").then((r) => r.data),
};
