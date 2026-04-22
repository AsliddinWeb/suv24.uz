import { http } from "./client";
import type { LoginResponse, TokenPair, UserOut } from "@/types/api";

export const authApi = {
  login: (phone: string, password: string, company_slug?: string) =>
    http
      .post<LoginResponse>("/auth/login", { phone, password, company_slug })
      .then((r) => r.data),

  refresh: (refresh_token: string) =>
    http.post<TokenPair>("/auth/refresh", { refresh_token }).then((r) => r.data),

  logout: (refresh_token: string | null) =>
    http.post("/auth/logout", { refresh_token }).then((r) => r.data),

  me: () => http.get<UserOut>("/auth/me").then((r) => r.data),

  updateMe: (body: { full_name?: string; phone?: string }) =>
    http.patch<UserOut>("/auth/me", body).then((r) => r.data),

  changePassword: (body: { current_password: string; new_password: string }) =>
    http.post("/auth/me/password", body).then((r) => r.data),
};
