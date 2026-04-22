import { http } from "./client";
import type { PaymentMethod, UUID } from "@/types/api";

export const paymentsApi = {
  record: (body: {
    order_id: UUID;
    amount: string;
    method: PaymentMethod;
    notes?: string;
  }) => http.post("/payments", body).then((r) => r.data),
};
