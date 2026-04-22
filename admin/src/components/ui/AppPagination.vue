<script setup lang="ts">
import { computed } from "vue";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/vue/20/solid";

const props = defineProps<{
  page: number;
  pageSize: number;
  total: number;
}>();

const emit = defineEmits<{
  (e: "update:page", value: number): void;
}>();

const pageCount = computed(() =>
  props.pageSize === 0 ? 0 : Math.max(1, Math.ceil(props.total / props.pageSize)),
);

const pages = computed(() => {
  const count = pageCount.value;
  const current = props.page;
  const arr: (number | "...")[] = [];

  if (count <= 7) {
    for (let i = 1; i <= count; i++) arr.push(i);
    return arr;
  }

  arr.push(1);
  if (current > 4) arr.push("...");

  const from = Math.max(2, current - 1);
  const to = Math.min(count - 1, current + 1);
  for (let i = from; i <= to; i++) arr.push(i);

  if (current < count - 3) arr.push("...");
  arr.push(count);
  return arr;
});

function go(p: number) {
  if (p < 1 || p > pageCount.value || p === props.page) return;
  emit("update:page", p);
}
</script>

<template>
  <div class="flex items-center justify-between py-3">
    <div class="text-xs text-slate-500 dark:text-slate-400">
      {{ total }} ta yozuv · {{ page }} / {{ pageCount }}
    </div>
    <div class="flex items-center gap-1">
      <button
        type="button"
        class="btn-secondary btn-sm"
        :disabled="page <= 1"
        @click="go(page - 1)"
      >
        <ChevronLeftIcon class="h-4 w-4" />
        Orqaga
      </button>

      <template v-for="(p, i) in pages" :key="i">
        <button
          v-if="p !== '...'"
          type="button"
          :class="[
            'h-8 min-w-[2rem] rounded-lg text-sm font-medium transition-colors',
            p === page
              ? 'bg-brand-600 text-white'
              : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800',
          ]"
          @click="go(p)"
        >
          {{ p }}
        </button>
        <span v-else class="px-1 text-slate-400">...</span>
      </template>

      <button
        type="button"
        class="btn-secondary btn-sm"
        :disabled="page >= pageCount"
        @click="go(page + 1)"
      >
        Keyingi
        <ChevronRightIcon class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
