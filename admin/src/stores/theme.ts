import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type Theme = "light" | "dark";

const STORAGE_KEY = "wdms.theme";

function systemPrefersDark(): boolean {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
}

function readInitial(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
  if (stored === "light" || stored === "dark") return stored;
  return systemPrefersDark() ? "dark" : "light";
}

function apply(theme: Theme) {
  const el = document.documentElement;
  el.classList.toggle("dark", theme === "dark");
  el.style.colorScheme = theme;
}

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<Theme>(readInitial());
  apply(theme.value);

  watch(theme, (v) => {
    localStorage.setItem(STORAGE_KEY, v);
    apply(v);
  });

  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark";
  }

  function set(next: Theme) {
    theme.value = next;
  }

  return { theme, toggle, set };
});
