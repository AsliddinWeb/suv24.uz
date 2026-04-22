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
  access_ttl_seconds: number;
  refresh_ttl_seconds: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type OrderStatus =
  | "pending"
  | "assigned"
  | "in_delivery"
  | "delivered"
  | "failed"
  | "cancelled";

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

export interface CustomerShort {
  id: UUID;
  full_name: string;
  phone: string;
}

export interface AddressShort {
  id: UUID;
  label: string;
  address_text: string;
  lat: string | null;
  lng: string | null;
}

export interface OrderOut {
  id: UUID;
  number: number;
  customer_id: UUID;
  address_id: UUID;
  driver_id: UUID | null;
  status: OrderStatus;
  total: string;
  paid_amount: string;
  notes: string | null;
  cancel_reason: string | null;
  created_at: string;
  updated_at: string;
  delivery_window_start: string | null;
  delivery_window_end: string | null;
  customer: CustomerShort | null;
  address: AddressShort | null;
}

export interface OrderDetailOut extends OrderOut {
  items: OrderItemOut[];
  status_logs: OrderStatusLogOut[];
}

export interface CustomerOut {
  id: UUID;
  phone: string;
  full_name: string;
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
}

export interface BottleBalance {
  id: UUID;
  driver_id: UUID;
  product_id: UUID;
  full_count: number;
  empty_count: number;
  product_name: string;
  volume_liters: number;
}

export type PaymentMethod = "cash" | "card_manual" | "payme" | "click";
