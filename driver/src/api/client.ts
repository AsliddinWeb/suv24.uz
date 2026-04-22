import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8017/api/v1";

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

const K_ACCESS = "wdms.access";
const K_REFRESH = "wdms.refresh";
const K_USER = "wdms.user";
const K_COMPANY = "wdms.company";

export const companyStorage = {
  async get<T = unknown>(): Promise<T | null> {
    const v = await AsyncStorage.getItem(K_COMPANY);
    return v ? (JSON.parse(v) as T) : null;
  },
  async set<T = unknown>(value: T): Promise<void> {
    await AsyncStorage.setItem(K_COMPANY, JSON.stringify(value));
  },
  async clear(): Promise<void> {
    await AsyncStorage.removeItem(K_COMPANY);
  },
};

export const tokens = {
  async get() {
    const [[, access], [, refresh], [, user]] = await AsyncStorage.multiGet([
      K_ACCESS,
      K_REFRESH,
      K_USER,
    ]);
    return {
      access,
      refresh,
      user: user ? JSON.parse(user) : null,
    };
  },
  async set(access: string, refresh: string, user?: unknown) {
    const pairs: [string, string][] = [
      [K_ACCESS, access],
      [K_REFRESH, refresh],
    ];
    if (user !== undefined) pairs.push([K_USER, JSON.stringify(user)]);
    await AsyncStorage.multiSet(pairs);
  },
  async clear() {
    await AsyncStorage.multiRemove([K_ACCESS, K_REFRESH, K_USER]);
  },
};

http.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const { access } = await tokens.get();
  if (access && config.headers) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  const { refresh } = await tokens.get();
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refresh,
    });
    await tokens.set(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    await tokens.clear();
    return null;
  }
}

http.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url?.includes("/auth/")
    ) {
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
    }
    return Promise.reject(error);
  },
);
