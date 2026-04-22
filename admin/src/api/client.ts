import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { toast } from "@/lib/toast";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  withCredentials: true,
});

const STORAGE_ACCESS = "wdms.access_token";
const STORAGE_REFRESH = "wdms.refresh_token";
const STORAGE_USER = "wdms.user";

export const tokenStorage = {
  access: () => localStorage.getItem(STORAGE_ACCESS),
  refresh: () => localStorage.getItem(STORAGE_REFRESH),
  user: () => {
    const raw = localStorage.getItem(STORAGE_USER);
    return raw ? JSON.parse(raw) : null;
  },
  set(access: string, refresh: string, user?: unknown) {
    localStorage.setItem(STORAGE_ACCESS, access);
    localStorage.setItem(STORAGE_REFRESH, refresh);
    if (user !== undefined) {
      localStorage.setItem(STORAGE_USER, JSON.stringify(user));
    }
  },
  clear() {
    localStorage.removeItem(STORAGE_ACCESS);
    localStorage.removeItem(STORAGE_REFRESH);
    localStorage.removeItem(STORAGE_USER);
  },
};

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.access();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  const refresh = tokenStorage.refresh();
  if (!refresh) return null;
  try {
    const { data } = await axios.post(
      `${API_BASE_URL}/auth/refresh`,
      { refresh_token: refresh },
      { withCredentials: true },
    );
    tokenStorage.set(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    tokenStorage.clear();
    return null;
  }
}

http.interceptors.response.use(
  (r) => r,
  async (error: AxiosError<{ detail?: unknown }>) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;
    if (status === 401 && !original._retry && !original.url?.includes("/auth/")) {
      original._retry = true;
      refreshing ??= doRefresh().finally(() => {
        refreshing = null;
      });
      const token = await refreshing;
      if (token) {
        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>).Authorization = `Bearer ${token}`;
        return http(original);
      }
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    } else if (status && status >= 400 && status !== 401) {
      const detail = error.response?.data?.detail;
      const message =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? detail.map((d: any) => d.msg || JSON.stringify(d)).join("; ")
            : `Xatolik: ${status}`;
      toast.error(message);
    }
    return Promise.reject(error);
  },
);
