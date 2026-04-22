<script setup lang="ts">
import { computed } from "vue";
import { ExclamationTriangleIcon } from "@heroicons/vue/24/outline";
import AppDialog from "@/components/ui/AppDialog.vue";
import { confirmState, resolveConfirm } from "@/lib/confirm";

const open = computed({
  get: () => confirmState.open,
  set: (v) => {
    if (!v) resolveConfirm(false);
  },
});

const toneStyles = computed(() => {
  switch (confirmState.options.tone) {
    case "primary":
      return {
        iconBg: "bg-brand-50 dark:bg-brand-950/50",
        iconColor: "text-brand-600 dark:text-brand-400",
        button: "btn-primary",
      };
    case "warning":
      return {
        iconBg: "bg-amber-50 dark:bg-amber-950/50",
        iconColor: "text-amber-600 dark:text-amber-400",
        button: "btn-primary",
      };
    case "danger":
    default:
      return {
        iconBg: "bg-rose-50 dark:bg-rose-950/50",
        iconColor: "text-rose-600 dark:text-rose-400",
        button: "btn-danger",
      };
  }
});

function onCancel() {
  resolveConfirm(false);
}

function onConfirm() {
  resolveConfirm(true);
}
</script>

<template>
  <AppDialog v-model:open="open" :title="undefined" max-width="max-w-md">
    <div class="flex gap-4">
      <div
        :class="[
          'flex h-10 w-10 shrink-0 items-center justify-center rounded-full',
          toneStyles.iconBg,
        ]"
      >
        <ExclamationTriangleIcon :class="['h-5 w-5', toneStyles.iconColor]" />
      </div>
      <div class="flex-1 pt-1">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
          {{ confirmState.options.title }}
        </h3>
        <p
          v-if="confirmState.options.description"
          class="mt-1.5 text-sm text-slate-600 dark:text-slate-400"
        >
          {{ confirmState.options.description }}
        </p>
      </div>
    </div>
    <template #footer>
      <button class="btn-secondary" :disabled="confirmState.loading" @click="onCancel">
        {{ confirmState.options.cancelLabel }}
      </button>
      <button :class="toneStyles.button" :disabled="confirmState.loading" @click="onConfirm">
        <svg v-if="confirmState.loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
          <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
        </svg>
        {{ confirmState.options.confirmLabel }}
      </button>
    </template>
  </AppDialog>
</template>
