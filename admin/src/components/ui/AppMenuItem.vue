<script setup lang="ts">
import { MenuItem } from "@headlessui/vue";

defineProps<{
  tone?: "default" | "danger";
}>();

const emit = defineEmits<{ (e: "click"): void }>();
</script>

<template>
  <MenuItem v-slot="{ active }">
    <button
      type="button"
      :class="[
        'flex w-full items-center gap-2 px-3 py-2 text-sm transition-colors text-left',
        tone === 'danger'
          ? active
            ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400'
            : 'text-rose-600 dark:text-rose-400'
          : active
            ? 'bg-slate-100 text-slate-900 dark:bg-slate-700 dark:text-slate-100'
            : 'text-slate-700 dark:text-slate-300',
      ]"
      @click="emit('click')"
    >
      <slot />
    </button>
  </MenuItem>
</template>
