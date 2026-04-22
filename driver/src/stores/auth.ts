import { create } from "zustand";
import { authApi } from "@/api/auth";
import { companiesApi, type CompanyOut } from "@/api/companies";
import { companyStorage, tokens } from "@/api/client";
import type { UserOut } from "@/types/api";

interface AuthState {
  user: UserOut | null;
  company: CompanyOut | null;
  ready: boolean;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  bootstrap: () => Promise<void>;
  refreshCompany: () => Promise<void>;
}

async function fetchCompany(): Promise<CompanyOut | null> {
  try {
    const c = await companiesApi.me();
    await companyStorage.set(c);
    return c;
  } catch {
    return null;
  }
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  company: null,
  ready: false,

  async bootstrap() {
    const { access, user } = await tokens.get();
    if (access && user) {
      const cached = await companyStorage.get<CompanyOut>();
      set({ user, company: cached });
      fetchCompany().then((c) => {
        if (c) set({ company: c });
      });
    }
    set({ ready: true });
  },

  async login(phone, password) {
    const res = await authApi.login(phone, password);
    await tokens.set(res.access_token, res.refresh_token, res.user);
    set({ user: res.user });
    const c = await fetchCompany();
    if (c) set({ company: c });
  },

  async logout() {
    const { refresh } = await tokens.get();
    try {
      await authApi.logout(refresh);
    } catch {
      // ignore
    }
    await tokens.clear();
    await companyStorage.clear();
    set({ user: null, company: null });
  },

  async refreshCompany() {
    const c = await fetchCompany();
    if (c) set({ company: c });
  },
}));
