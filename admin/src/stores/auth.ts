import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { authApi } from "@/api/auth";
import { companiesApi, resolveMediaUrl, type CompanyOut } from "@/api/companies";
import { tokenStorage } from "@/api/client";
import type { UserOut } from "@/types/api";

const COMPANY_KEY = "wdms.company";

function loadCachedCompany(): CompanyOut | null {
  try {
    const raw = localStorage.getItem(COMPANY_KEY);
    return raw ? (JSON.parse(raw) as CompanyOut) : null;
  } catch {
    return null;
  }
}

function saveCachedCompany(company: CompanyOut | null) {
  try {
    if (company) localStorage.setItem(COMPANY_KEY, JSON.stringify(company));
    else localStorage.removeItem(COMPANY_KEY);
  } catch {
    // ignore
  }
}

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserOut | null>(tokenStorage.user());
  const company = ref<CompanyOut | null>(loadCachedCompany());

  const isAuthenticated = computed(() => !!user.value && !!tokenStorage.access());
  const role = computed(() => user.value?.role ?? null);

  const brandName = computed(() => company.value?.short_name || company.value?.name || "Suv24");
  const brandInitial = computed(() => brandName.value.slice(0, 1).toUpperCase());
  const brandLogo = computed(() => resolveMediaUrl(company.value?.logo_url));

  async function login(phone: string, password: string, company_slug?: string) {
    const res = await authApi.login(phone, password, company_slug);
    tokenStorage.set(res.access_token, res.refresh_token, res.user);
    user.value = res.user;
    if (res.user.role !== "platform_owner") {
      await loadCompany().catch(() => undefined);
    } else {
      company.value = null;
      saveCachedCompany(null);
    }
  }

  async function logout() {
    const refresh = tokenStorage.refresh();
    try {
      await authApi.logout(refresh);
    } catch {
      // ignore
    }
    tokenStorage.clear();
    saveCachedCompany(null);
    user.value = null;
    company.value = null;
  }

  async function fetchMe() {
    const me = await authApi.me();
    user.value = me;
    tokenStorage.set(tokenStorage.access()!, tokenStorage.refresh()!, me);
    return me;
  }

  async function loadCompany() {
    const c = await companiesApi.me();
    company.value = c;
    saveCachedCompany(c);
    return c;
  }

  function setCompany(c: CompanyOut) {
    company.value = c;
    saveCachedCompany(c);
  }

  function hasRole(...roles: string[]) {
    return user.value ? roles.includes(user.value.role) : false;
  }

  return {
    user,
    company,
    isAuthenticated,
    role,
    brandName,
    brandInitial,
    brandLogo,
    login,
    logout,
    fetchMe,
    loadCompany,
    setCompany,
    hasRole,
  };
});
