<script setup lang="ts">
import { computed } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartOptions,
} from "chart.js";
import dayjs from "dayjs";
import { useThemeStore } from "@/stores/theme";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const props = defineProps<{
  labels: string[];
  revenue: number[];
  orders: number[];
}>();

const theme = useThemeStore();

const chartData = computed(() => {
  const dark = theme.theme === "dark";
  const gridColor = dark ? "rgba(148,163,184,0.1)" : "rgba(148,163,184,0.15)";
  return {
    labels: props.labels.map((d) => dayjs(d).format("DD MMM")),
    datasets: [
      {
        label: "Tushum (so'm)",
        data: props.revenue,
        borderColor: "#2563eb",
        backgroundColor: (ctx: any) => {
          const chart = ctx.chart;
          const { ctx: c, chartArea } = chart;
          if (!chartArea) return "rgba(37,99,235,0.1)";
          const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, "rgba(37,99,235,0.35)");
          gradient.addColorStop(1, "rgba(37,99,235,0.02)");
          return gradient;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: "#2563eb",
        pointBorderColor: dark ? "#0f172a" : "#fff",
        pointBorderWidth: 2,
        borderWidth: 2.5,
      },
    ],
    _gridColor: gridColor,
  };
});

const chartOptions = computed<ChartOptions<"line">>(() => {
  const dark = theme.theme === "dark";
  const gridColor = dark ? "rgba(148,163,184,0.1)" : "rgba(148,163,184,0.15)";
  const textColor = dark ? "#94a3b8" : "#64748b";
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: dark ? "#1e293b" : "#0f172a",
        titleColor: "#fff",
        bodyColor: "#e2e8f0",
        padding: 12,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: (ctx) => {
            const value = ctx.parsed.y ?? 0;
            const idx = ctx.dataIndex;
            const orders = props.orders[idx] ?? 0;
            const fmt = new Intl.NumberFormat("uz-UZ").format(value);
            return [`Tushum: ${fmt} so'm`, `Buyurtma: ${orders}`];
          },
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: textColor, font: { size: 11 } },
        border: { display: false },
      },
      y: {
        grid: { color: gridColor },
        ticks: {
          color: textColor,
          font: { size: 11 },
          callback: (v) => {
            const num = typeof v === "number" ? v : Number(v);
            if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
            if (num >= 1_000) return `${(num / 1_000).toFixed(0)}K`;
            return String(num);
          },
        },
        border: { display: false },
      },
    },
  };
});
</script>

<template>
  <div class="h-72">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
