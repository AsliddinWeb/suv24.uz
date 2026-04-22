export type UUID = string;

export type UserRole = "super_admin" | "admin" | "operator" | "driver";

export interface UserOut {
  id: UUID;
  company_id: UUID;
  phone: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_ttl_seconds: number;
  refresh_ttl_seconds: number;
  user: UserOut;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_ttl_seconds: number;
  refresh_ttl_seconds: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type CustomerSegment = "new" | "active" | "vip" | "sleeping";

export interface CustomerOut {
  id: UUID;
  company_id: UUID;
  phone: string;
  full_name: string;
  segment: CustomerSegment;
  notes: string | null;
  balance: string;
  bottle_debt: number;
}

export interface AddressOut {
  id: UUID;
  customer_id: UUID;
  label: string;
  address_text: string;
  lat: string | null;
  lng: string | null;
  qr_token: string;
  is_active: boolean;
  notes: string | null;
}

export interface ProductOut {
  id: UUID;
  company_id: UUID;
  name: string;
  volume_liters: number;
  is_returnable: boolean;
  is_active: boolean;
  current_price: string | null;
}

export interface PriceOut {
  id: UUID;
  product_id: UUID;
  price: string;
  valid_from: string;
  valid_to: string | null;
}

export interface DriverOut {
  id: UUID;
  company_id: UUID;
  user_id: UUID;
  vehicle_plate: string | null;
  is_active: boolean;
  current_lat: string | null;
  current_lng: string | null;
  last_seen_at: string | null;
  full_name: string;
  phone: string;
}

export type OrderStatus =
  | "pending"
  | "assigned"
  | "in_delivery"
  | "delivered"
  | "failed"
  | "cancelled";

export type OrderSource = "operator" | "qr" | "subscription" | "admin";

export interface OrderItemOut {
  id: UUID;
  product_id: UUID;
  product_name: string;
  quantity: number;
  unit_price: string;
  total: string;
}

export interface OrderStatusLogOut {
  id: UUID;
  from_status: OrderStatus | null;
  to_status: OrderStatus;
  actor_user_id: UUID | null;
  reason: string | null;
  created_at: string;
}

export interface OrderOut {
  id: UUID;
  number: number;
  company_id: UUID;
  customer_id: UUID;
  address_id: UUID;
  driver_id: UUID | null;
  created_by_user_id: UUID | null;
  status: OrderStatus;
  source: OrderSource;
  total: string;
  paid_amount: string;
  delivery_window_start: string | null;
  delivery_window_end: string | null;
  notes: string | null;
  cancel_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrderDetailOut extends OrderOut {
  items: OrderItemOut[];
  status_logs: OrderStatusLogOut[];
}

export type PaymentMethod = "cash" | "card_manual" | "payme" | "click";
export type PaymentStatus =
  | "pending"
  | "processing"
  | "paid"
  | "partial"
  | "failed"
  | "refunded"
  | "cancelled";

export interface PaymentOut {
  id: UUID;
  company_id: UUID;
  order_id: UUID;
  customer_id: UUID;
  amount: string;
  method: PaymentMethod;
  status: PaymentStatus;
  provider_tx_id: string | null;
  recorded_by_user_id: UUID | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DailyCashSummary {
  date: string;
  driver_id: UUID | null;
  total_cash: string;
  total_card_manual: string;
  count: number;
}

export interface BottleBalanceWithProduct {
  id: UUID;
  driver_id: UUID;
  product_id: UUID;
  full_count: number;
  empty_count: number;
  product_name: string;
  volume_liters: number;
}
