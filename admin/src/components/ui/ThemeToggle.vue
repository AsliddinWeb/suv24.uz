<script setup lang="ts">
import { SunIcon, MoonIcon } from "@heroicons/vue/20/solid";
import { useThemeStore } from "@/stores/theme";

const theme = useThemeStore();
</script>

<template>
  <button
    type="button"
    class="btn-ghost !p-2"
    :title="theme.theme === 'dark' ? 'Kunduzgi rejim' : 'Tungi rejim'"
    @click="theme.toggle()"
  >
    <SunIcon v-if="theme.theme === 'dark'" class="h-5 w-5" />
    <MoonIcon v-else class="h-5 w-5" />
  </button>
</template>
