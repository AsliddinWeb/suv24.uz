import { http } from "./client";
import type { BottleBalance, UUID } from "@/types/api";

interface DriverMe {
  id: UUID;
  user_id: UUID;
  vehicle_plate: string | null;
  is_active: boolean;
  full_name: string;
  phone: string;
}

export const driversApi = {
  me: () => http.get<DriverMe>("/drivers/me").then((r) => r.data),
  myBottles: (driverId: UUID) =>
    http.get<BottleBalance[]>(`/drivers/${driverId}/bottles`).then((r) => r.data),
  reportLocation: (lat: number, lng: number) =>
    http
      .patch("/drivers/me/location", { lat, lng })
      .then((r) => r.data),
};
