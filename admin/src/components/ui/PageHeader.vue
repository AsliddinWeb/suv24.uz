<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
}>();
</script>

<template>
  <div class="flex items-start justify-between gap-4 flex-wrap">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">
        {{ title }}
      </h1>
      <p v-if="subtitle" class="mt-1 text-sm text-slate-500 dark:text-slate-400">
        {{ subtitle }}
      </p>
    </div>
    <div class="flex items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>
