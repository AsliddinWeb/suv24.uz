<script setup lang="ts">
import { computed } from "vue";
import { Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartOptions,
} from "chart.js";
import { useThemeStore } from "@/stores/theme";
import { orderStatusLabel } from "@/utils/status";
import type { OrderStatus } from "@/types/api";

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  items: { status: OrderStatus; count: number }[];
}>();

const theme = useThemeStore();

const COLORS: Record<OrderStatus, string> = {
  pending: "#0ea5e9",
  assigned: "#f59e0b",
  in_delivery: "#2563eb",
  delivered: "#10b981",
  failed: "#f43f5e",
  cancelled: "#94a3b8",
};

const total = computed(() => props.items.reduce((s, i) => s + i.count, 0));

const chartData = computed(() => {
  const dark = theme.theme === "dark";
  return {
    labels: props.items.map((i) => orderStatusLabel[i.status]),
    datasets: [
      {
        data: props.items.map((i) => i.count),
        backgroundColor: props.items.map((i) => COLORS[i.status]),
        borderColor: dark ? "#0f172a" : "#fff",
        borderWidth: 3,
        hoverOffset: 6,
      },
    ],
  };
});

const chartOptions = computed<ChartOptions<"doughnut">>(() => {
  const dark = theme.theme === "dark";
  return {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "72%",
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: dark ? "#1e293b" : "#0f172a",
        titleColor: "#fff",
        bodyColor: "#e2e8f0",
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (ctx) => {
            const value = ctx.parsed;
            const pct = total.value ? ((value / total.value) * 100).toFixed(0) : "0";
            return ` ${ctx.label}: ${value} (${pct}%)`;
          },
        },
      },
    },
  };
});
</script>

<template>
  <div>
    <div class="relative h-64 flex items-center justify-center">
      <Doughnut v-if="items.length" :data="chartData" :options="chartOptions" />
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide">Jami</p>
        <p class="text-3xl font-bold text-slate-900 dark:text-slate-100">{{ total }}</p>
      </div>
    </div>

    <div class="mt-5 grid grid-cols-2 gap-x-4 gap-y-2">
      <div
        v-for="item in items"
        :key="item.status"
        class="flex items-center justify-between text-sm"
      >
        <div class="flex items-center gap-2 min-w-0">
          <span class="h-2.5 w-2.5 rounded-full shrink-0" :style="{ backgroundColor: COLORS[item.status] }" />
          <span class="text-slate-600 dark:text-slate-400 truncate">{{ orderStatusLabel[item.status] }}</span>
        </div>
        <span class="font-medium text-slate-900 dark:text-slate-100">{{ item.count }}</span>
      </div>
    </div>
  </div>
</template>
