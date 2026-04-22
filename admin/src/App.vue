<script setup lang="ts">
import { computed } from "vue";
import { RouterView } from "vue-router";
import { Toaster } from "vue-sonner";
import { useThemeStore } from "@/stores/theme";
import ConfirmHost from "@/components/ConfirmHost.vue";

const themeStore = useThemeStore();
const toasterTheme = computed<"light" | "dark">(() => themeStore.theme);
</script>

<template>
  <RouterView />
  <Toaster :theme="toasterTheme" position="top-right" rich-colors close-button />
  <ConfirmHost />
</template>
