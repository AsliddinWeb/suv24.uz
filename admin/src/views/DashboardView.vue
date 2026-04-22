<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from "vue";
import { useRouter } from "vue-router";
import {
  BanknotesIcon,
  ShoppingBagIcon,
  TruckIcon,
  UsersIcon,
  ArrowPathIcon,
  ArrowUpRightIcon,
} from "@heroicons/vue/24/outline";
import dayjs from "dayjs";
import { ordersApi } from "@/api/orders";
import { paymentsApi } from "@/api/payments";
import { customersApi } from "@/api/customers";
import { driversApi } from "@/api/drivers";
import { reportsApi, type DailyRevenuePoint, type StatusDistributionItem } from "@/api/reports";
import { APP_TZ, formatDateTime, formatMoney } from "@/utils/format";
import { orderStatusLabel, orderStatusType } from "@/utils/status";
import { useAuthStore } from "@/stores/auth";
import AppBadge from "@/components/ui/AppBadge.vue";
import RevenueChart from "@/components/charts/RevenueChart.vue";
import StatusDonut from "@/components/charts/StatusDonut.vue";
import type { OrderOut } from "@/types/api";

const router = useRouter();
const auth = useAuthStore();

const loading = ref(false);
const cashToday = ref("0");
const cardToday = ref("0");
const activeOrders = ref(0);
const customersTotal = ref(0);
const driversActive = ref(0);
const driversTotal = ref(0);
const recent = ref<OrderOut[]>([]);
const revenuePoints = ref<DailyRevenuePoint[]>([]);
const statusDist = ref<StatusDistributionItem[]>([]);

const tick = ref(Date.now());
let tickTimer: ReturnType<typeof setInterval> | null = null;
onMounted(() => {
  tickTimer = setInterval(() => (tick.value = Date.now()), 60_000);
});
onBeforeUnmount(() => {
  if (tickTimer) clearInterval(tickTimer);
});
const now = computed(() => {
  void tick.value;
  return dayjs().tz(APP_TZ);
});
const greeting = computed(() => {
  const h = now.value.hour();
  if (h < 6) return "Xayrli tun";
  if (h < 12) return "Xayrli tong";
  if (h < 18) return "Xayrli kun";
  return "Xayrli oqshom";
});

const todayRevenue = computed(() => {
  const today = now.value.format("YYYY-MM-DD");
  const p = revenuePoints.value.find((x) => x.date === today);
  return p ? parseFloat(p.revenue) : 0;
});

const prevRevenue = computed(() => {
  const yesterday = now.value.subtract(1, "day").format("YYYY-MM-DD");
  const p = revenuePoints.value.find((x) => x.date === yesterday);
  return p ? parseFloat(p.revenue) : 0;
});

const revenueDelta = computed(() => {
  if (prevRevenue.value === 0) return todayRevenue.value > 0 ? 100 : 0;
  return ((todayRevenue.value - prevRevenue.value) / prevRevenue.value) * 100;
});

const totalWeek = computed(() =>
  revenuePoints.value.reduce((s, p) => s + parseFloat(p.revenue), 0),
);

const ordersWeek = computed(() => revenuePoints.value.reduce((s, p) => s + p.orders, 0));

async function load() {
  loading.value = true;
  try {
    const [revenue, statuses, customersPage, drivers, summary, recentRes] = await Promise.all([
      reportsApi.dailyRevenue(7),
      reportsApi.ordersByStatus(),
      customersApi.list({ page: 1, page_size: 1 }),
      driversApi.list(),
      paymentsApi.cashSummary(),
      ordersApi.list({ page: 1, page_size: 6 }),
    ]);
    revenuePoints.value = revenue;
    statusDist.value = statuses;
    customersTotal.value = customersPage.total;
    driversTotal.value = drivers.length;
    driversActive.value = drivers.filter((d) => d.is_active).length;
    cashToday.value = summary.total_cash;
    cardToday.value = summary.total_card_manual;
    recent.value = recentRes.items;

    activeOrders.value = statuses
      .filter((s) => ["pending", "assigned", "in_delivery"].includes(s.status))
      .reduce((sum, s) => sum + s.count, 0);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

interface KpiCard {
  label: string;
  value: string;
  sub: string;
  icon: any;
  gradient: string;
  action?: () => void;
}

const kpis = computed<KpiCard[]>(() => [
  {
    label: "Bugungi tushum",
    value: formatMoney(todayRevenue.value),
    sub:
      revenueDelta.value === 0
        ? "Kecha 0 edi"
        : `${revenueDelta.value > 0 ? "+" : ""}${revenueDelta.value.toFixed(0)}% kechaga nisbatan`,
    icon: BanknotesIcon,
    gradient: "from-emerald-500 to-teal-600",
  },
  {
    label: "Faol buyurtmalar",
    value: String(activeOrders.value),
    sub: "Kutilmoqda, biriktirilgan, yo'lda",
    icon: ShoppingBagIcon,
    gradient: "from-brand-500 to-indigo-600",
    action: () => router.push("/app/orders"),
  },
  {
    label: "Faol haydovchilar",
    value: `${driversActive.value}/${driversTotal.value}`,
    sub: "Bugun ishga chiqqan",
    icon: TruckIcon,
    gradient: "from-amber-500 to-orange-600",
    action: () => router.push("/app/drivers"),
  },
  {
    label: "Mijozlar",
    value: String(customersTotal.value),
    sub: "Bazadagi jami mijoz",
    icon: UsersIcon,
    gradient: "from-rose-500 to-pink-600",
    action: () => router.push("/app/customers"),
  },
]);
</script>

<template>
  <div class="space-y-6">
    <!-- Hero -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-indigo-600 to-sky-500 p-6 sm:p-8 text-white shadow-lg">
      <div class="absolute -top-10 -right-10 h-48 w-48 rounded-full bg-white/10 blur-2xl pointer-events-none" />
      <div class="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-white/10 blur-2xl pointer-events-none" />
      <div class="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p class="text-brand-100 text-sm">{{ greeting }}, {{ auth.user?.full_name?.split(" ")[0] }} 👋</p>
          <h1 class="mt-1 text-2xl sm:text-3xl font-bold tracking-tight">Bugungi holat</h1>
          <p class="text-brand-100 text-sm mt-1">
            {{ now.format("DD MMMM YYYY, dddd") }} · {{ now.format("HH:mm") }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <div class="rounded-xl bg-white/15 backdrop-blur px-4 py-3">
            <p class="text-xs text-brand-100 uppercase tracking-wide">7 kunlik tushum</p>
            <p class="text-xl font-bold">{{ formatMoney(totalWeek) }}</p>
          </div>
          <button
            class="rounded-xl bg-white/15 hover:bg-white/25 backdrop-blur p-3 transition-colors"
            :disabled="loading"
            title="Yangilash"
            @click="load"
          >
            <ArrowPathIcon :class="['h-5 w-5', loading && 'animate-spin']" />
          </button>
        </div>
      </div>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <button
        v-for="(kpi, i) in kpis"
        :key="i"
        :class="[
          'group relative overflow-hidden rounded-2xl p-5 text-left text-white shadow-soft',
          'bg-gradient-to-br', kpi.gradient,
          'transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5',
        ]"
        :disabled="!kpi.action"
        @click="kpi.action && kpi.action()"
      >
        <div class="absolute -top-6 -right-6 h-24 w-24 rounded-full bg-white/10 blur-xl pointer-events-none" />
        <div class="relative flex items-start justify-between">
          <div class="space-y-1 min-w-0">
            <p class="text-xs font-medium uppercase tracking-wide text-white/80">{{ kpi.label }}</p>
            <p class="text-2xl font-bold truncate">{{ kpi.value }}</p>
            <p class="text-xs text-white/75 truncate">{{ kpi.sub }}</p>
          </div>
          <div class="flex h-10 w-10 items-center justify-center rounded-xl shrink-0 bg-white/20">
            <component :is="kpi.icon" class="h-5 w-5" />
          </div>
        </div>
        <ArrowUpRightIcon
          v-if="kpi.action"
          class="absolute bottom-4 right-4 h-4 w-4 text-white/60 group-hover:text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all"
        />
      </button>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="card p-6 lg:col-span-2">
        <div class="flex items-center justify-between mb-2">
          <div>
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              Tushum dinamikasi
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Oxirgi 7 kun</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-slate-500 dark:text-slate-400">Jami ({{ ordersWeek }} buyurtma)</p>
            <p class="text-lg font-semibold text-slate-900 dark:text-slate-100">{{ formatMoney(totalWeek) }}</p>
          </div>
        </div>
        <RevenueChart
          v-if="revenuePoints.length"
          :labels="revenuePoints.map((p) => p.date)"
          :revenue="revenuePoints.map((p) => parseFloat(p.revenue))"
          :orders="revenuePoints.map((p) => p.orders)"
        />
      </div>

      <div class="card p-6">
        <div>
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Buyurtmalar holati</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400">Umumiy taqsimot</p>
        </div>
        <StatusDonut :items="statusDist" class="mt-4" />
      </div>
    </div>

    <!-- Payments + Recent -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="card p-6">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-4">
          Bugungi to'lovlar
        </h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between rounded-xl bg-emerald-50 dark:bg-emerald-950/30 p-4">
            <div>
              <p class="text-xs text-emerald-700 dark:text-emerald-300 uppercase tracking-wide">Naqd</p>
              <p class="text-lg font-bold text-emerald-700 dark:text-emerald-400 mt-0.5">
                {{ formatMoney(cashToday) }}
              </p>
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-400">
              <BanknotesIcon class="h-5 w-5" />
            </div>
          </div>
          <div class="flex items-center justify-between rounded-xl bg-brand-50 dark:bg-brand-950/30 p-4">
            <div>
              <p class="text-xs text-brand-700 dark:text-brand-300 uppercase tracking-wide">Karta</p>
              <p class="text-lg font-bold text-brand-700 dark:text-brand-400 mt-0.5">
                {{ formatMoney(cardToday) }}
              </p>
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-900/50 text-brand-700 dark:text-brand-400">
              <BanknotesIcon class="h-5 w-5" />
            </div>
          </div>
        </div>
      </div>

      <div class="card lg:col-span-2">
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">So'nggi buyurtmalar</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Oxirgi 6 ta</p>
          </div>
          <button class="btn-ghost btn-sm" @click="router.push('/app/orders')">
            Hammasini ko'rish
            <ArrowUpRightIcon class="h-3.5 w-3.5" />
          </button>
        </div>
        <div class="overflow-x-auto">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Status</th>
                <th class="text-right">Summa</th>
                <th>Sana</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="o in recent"
                :key="o.id"
                class="cursor-pointer"
                @click="router.push({ name: 'order-detail', params: { id: o.id } })"
              >
                <td class="font-semibold text-brand-600 dark:text-brand-400">#{{ o.number }}</td>
                <td>
                  <AppBadge :variant="orderStatusType[o.status]">{{ orderStatusLabel[o.status] }}</AppBadge>
                </td>
                <td class="text-right font-medium">{{ formatMoney(o.total) }}</td>
                <td class="text-slate-500 dark:text-slate-400 whitespace-nowrap">{{ formatDateTime(o.created_at) }}</td>
              </tr>
              <tr v-if="!recent.length">
                <td colspan="4" class="text-center text-slate-500 dark:text-slate-400 py-12">
                  Hozircha buyurtma yo'q
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
