import { http } from "./client";
import type { UserOut, UserRole, UUID } from "@/types/api";

export const usersApi = {
  list: () => http.get<UserOut[]>("/users").then((r) => r.data),

  create: (body: {
    phone: string;
    password: string;
    full_name: string;
    role: UserRole;
  }) => http.post<UserOut>("/users", body).then((r) => r.data),

  update: (
    id: UUID,
    body: {
      phone?: string;
      full_name?: string;
      role?: UserRole;
      is_active?: boolean;
    },
  ) => http.patch<UserOut>(`/users/${id}`, body).then((r) => r.data),

  resetPassword: (id: UUID, password: string) =>
    http.post(`/users/${id}/password`, { password }).then((r) => r.data),

  remove: (id: UUID) => http.delete(`/users/${id}`).then((r) => r.data),
};
