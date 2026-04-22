import { http } from "./client";
import type { LoginResponse, UserOut } from "@/types/api";

export const authApi = {
  login: (phone: string, password: string) =>
    http
      .post<LoginResponse>("/auth/login", { phone, password })
      .then((r) => r.data),

  logout: (refresh_token: string | null) =>
    http.post("/auth/logout", { refresh_token }).then((r) => r.data),

  me: () => http.get<UserOut>("/auth/me").then((r) => r.data),
};
