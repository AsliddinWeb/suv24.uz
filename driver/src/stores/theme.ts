import { useEffect, useState } from "react";
import { Appearance, type ColorSchemeName } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { darkColors, lightColors, type ColorsScheme } from "@/theme/colors";

export type ThemeMode = "system" | "light" | "dark";
const STORAGE_KEY = "wdms.theme";

interface ThemeState {
  mode: ThemeMode;
  _hydrated: boolean;
  setMode: (mode: ThemeMode) => Promise<void>;
  bootstrap: () => Promise<void>;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  mode: "system",
  _hydrated: false,

  async bootstrap() {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY);
      if (stored === "light" || stored === "dark" || stored === "system") {
        set({ mode: stored, _hydrated: true });
        return;
      }
    } catch {
      // ignore
    }
    set({ _hydrated: true });
  },

  async setMode(mode) {
    set({ mode });
    try {
      await AsyncStorage.setItem(STORAGE_KEY, mode);
    } catch {
      // ignore
    }
  },
}));

export function useTheme(): { colors: ColorsScheme; isDark: boolean; mode: ThemeMode } {
  const mode = useThemeStore((s) => s.mode);
  const [systemScheme, setSystemScheme] = useState<ColorSchemeName>(
    Appearance.getColorScheme(),
  );

  useEffect(() => {
    const sub = Appearance.addChangeListener(({ colorScheme }) => {
      setSystemScheme(colorScheme);
    });
    return () => sub.remove();
  }, []);

  const isDark =
    mode === "dark" || (mode === "system" && systemScheme === "dark");

  return {
    colors: isDark ? darkColors : lightColors,
    isDark,
    mode,
  };
}
