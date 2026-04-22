<script setup lang="ts">
import { InboxIcon } from "@heroicons/vue/24/outline";

defineProps<{
  title?: string;
  description?: string;
}>();
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center">
    <div class="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
      <InboxIcon class="h-6 w-6 text-slate-400" />
    </div>
    <h3 class="mt-3 text-sm font-medium text-slate-900 dark:text-slate-100">
      {{ title || "Ma'lumot yo'q" }}
    </h3>
    <p v-if="description" class="mt-1 text-xs text-slate-500 dark:text-slate-400">
      {{ description }}
    </p>
    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>
