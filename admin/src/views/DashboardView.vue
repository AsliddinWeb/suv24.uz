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
  ArchiveBoxXMarkIcon,
  ArrowDownCircleIcon,
  ArrowUpCircleIcon,
  ChartPieIcon,
  WalletIcon,
} from "@heroicons/vue/24/outline";
import dayjs from "dayjs";
import { RouterLink } from "vue-router";
import { ordersApi } from "@/api/orders";
import { paymentsApi } from "@/api/payments";
import { customersApi } from "@/api/customers";
import { driversApi } from "@/api/drivers";
import { productsApi, type ProductStockSummary } from "@/api/products";
import {
  cashApi,
  CASH_KIND_LABELS,
  type CashSummary,
  type CashTransaction,
  type CashTxKind,
} from "@/api/warehouse";
import { reportsApi, type DailyRevenuePoint, type StatusDistributionItem } from "@/api/reports";
import { APP_TZ, formatDateTime, formatMoney } from "@/utils/format";
import { orderStatusLabel, orderStatusType } from "@/utils/status";
import { useAuthStore } from "@/stores/auth";
import AppBadge from "@/components/ui/AppBadge.vue";
import RevenueChart from "@/components/charts/RevenueChart.vue";
import StatusDonut from "@/components/charts/StatusDonut.vue";
import type { OrderOut, ProductOut } from "@/types/api";

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

// New: cash + stock signals
const cashSummary = ref<CashSummary | null>(null);
const cashRecent = ref<CashTransaction[]>([]);
const products = ref<ProductOut[]>([]);
const stocks = ref<ProductStockSummary[]>([]);

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
    const [
      revenue,
      statuses,
      customersPage,
      drivers,
      summary,
      recentRes,
      cashSum,
      cashTx,
      productList,
      stockList,
    ] = await Promise.all([
      reportsApi.dailyRevenue(7),
      reportsApi.ordersByStatus(),
      customersApi.list({ page: 1, page_size: 1 }),
      driversApi.list(),
      paymentsApi.cashSummary(),
      ordersApi.list({ page: 1, page_size: 6 }),
      cashApi.summary().catch(() => null),
      cashApi.transactions(8).catch(() => []),
      productsApi.list({ only_active: true }).catch(() => []),
      productsApi.stocks().catch(() => []),
    ]);
    revenuePoints.value = revenue;
    statusDist.value = statuses;
    customersTotal.value = customersPage.total;
    driversTotal.value = drivers.length;
    driversActive.value = drivers.filter((d) => d.is_active).length;
    cashToday.value = summary.total_cash;
    cardToday.value = summary.total_card_manual;
    recent.value = recentRes.items;
    cashSummary.value = cashSum;
    cashRecent.value = cashTx;
    products.value = productList;
    stocks.value = stockList;

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

const todayNet = computed(() => {
  const cs = cashSummary.value;
  if (!cs) return 0;
  return parseFloat(cs.today_in) - parseFloat(cs.today_out);
});

const monthNet = computed(() => {
  const cs = cashSummary.value;
  if (!cs) return 0;
  return parseFloat(cs.month_in) - parseFloat(cs.month_out);
});

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
    label: "Kassada",
    value: cashSummary.value ? formatMoney(cashSummary.value.balance) : "—",
    sub:
      cashSummary.value
        ? `Bugun: +${formatMoney(cashSummary.value.today_in)} / −${formatMoney(cashSummary.value.today_out)}`
        : "Boshlang'ich balans kerak",
    icon: WalletIcon,
    gradient: "from-brand-500 to-indigo-600",
    action: () => router.push("/app/warehouse"),
  },
  {
    label: "Faol buyurtmalar",
    value: String(activeOrders.value),
    sub: "Kutilmoqda · biriktirilgan · yo'lda",
    icon: ShoppingBagIcon,
    gradient: "from-amber-500 to-orange-600",
    action: () => router.push("/app/orders"),
  },
  {
    label: "Haydovchilar",
    value: `${driversActive.value}/${driversTotal.value}`,
    sub: "Faol / jami",
    icon: TruckIcon,
    gradient: "from-rose-500 to-pink-600",
    action: () => router.push("/app/drivers"),
  },
]);

// Stock alerts: returnable products whose available_full <= 15
interface StockAlert {
  product_id: string;
  product_name: string;
  volume_liters: number;
  available: number;
  level: "critical" | "low";
}

const stockAlerts = computed<StockAlert[]>(() => {
  const out: StockAlert[] = [];
  for (const s of stocks.value) {
    if (!s.is_returnable) continue;
    if (s.available_full > 15) continue;
    const p = products.value.find((x) => x.id === s.product_id);
    if (!p) continue;
    out.push({
      product_id: s.product_id,
      product_name: p.name,
      volume_liters: p.volume_liters,
      available: s.available_full,
      level: s.available_full < 5 ? "critical" : "low",
    });
  }
  return out.sort((a, b) => a.available - b.available);
});

function txSign(amount: string): string {
  return parseFloat(amount) >= 0 ? "+" : "";
}
function txColor(amount: string): string {
  return parseFloat(amount) >= 0
    ? "text-emerald-600 dark:text-emerald-400"
    : "text-rose-600 dark:text-rose-400";
}
function kindLabel(k: CashTxKind): string {
  return CASH_KIND_LABELS[k];
}
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

    <!-- Stock alerts + Cash flow row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Stock alerts -->
      <div class="card p-5 lg:col-span-2">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <ArchiveBoxXMarkIcon class="h-5 w-5 text-amber-500" />
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              Pasaygan zaxiralar
            </h3>
          </div>
          <RouterLink to="/app/products" class="text-xs text-brand-600 font-semibold hover:underline">
            Hammasi →
          </RouterLink>
        </div>
        <div v-if="!stockAlerts.length" class="py-6 text-center text-sm text-slate-500">
          ✅ Hamma mahsulot yetarli ({{ stocks.filter(s => s.is_returnable).length }} ta turdagi tovar)
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="a in stockAlerts"
            :key="a.product_id"
            :class="[
              'flex items-center gap-3 p-3 rounded-xl',
              a.level === 'critical'
                ? 'bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50'
                : 'bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50',
            ]"
          >
            <div
              :class="[
                'h-10 w-10 rounded-xl flex items-center justify-center text-white font-bold shrink-0',
                a.level === 'critical' ? 'bg-rose-500' : 'bg-amber-500',
              ]"
            >
              {{ a.available }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">
                {{ a.product_name }} · {{ a.volume_liters }}L
              </p>
              <p class="text-xs text-slate-600 dark:text-slate-400">
                {{ a.level === 'critical' ? 'Tugash arafasida' : 'Kam qoldi' }} —
                <strong>{{ a.available }} ta sotish uchun</strong>
              </p>
            </div>
            <RouterLink
              to="/app/products"
              class="text-xs font-bold text-brand-600 hover:underline whitespace-nowrap"
            >
              Kirim qilish →
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Cash flow this month -->
      <div class="card p-5 flex flex-col">
        <div class="flex items-center gap-2 mb-3">
          <ChartPieIcon class="h-5 w-5 text-brand-500" />
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
            Bu oy kassa
          </h3>
        </div>
        <div v-if="cashSummary" class="space-y-3 flex-1">
          <div class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-lg bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center">
              <ArrowDownCircleIcon class="h-5 w-5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[11px] text-slate-500 uppercase tracking-wide">Kirim</p>
              <p class="text-base font-bold text-emerald-600 truncate">
                +{{ formatMoney(cashSummary.month_in) }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-lg bg-rose-100 dark:bg-rose-950/40 text-rose-600 flex items-center justify-center">
              <ArrowUpCircleIcon class="h-5 w-5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[11px] text-slate-500 uppercase tracking-wide">Chiqim</p>
              <p class="text-base font-bold text-rose-600 truncate">
                −{{ formatMoney(cashSummary.month_out) }}
              </p>
            </div>
          </div>
          <div class="pt-3 border-t border-slate-200 dark:border-slate-800">
            <p class="text-[11px] text-slate-500 uppercase tracking-wide">Sof daromad</p>
            <p
              :class="[
                'text-2xl font-extrabold',
                monthNet >= 0
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : 'text-rose-600 dark:text-rose-400',
              ]"
            >
              {{ monthNet >= 0 ? '+' : '−' }}{{ formatMoney(Math.abs(monthNet)) }}
            </p>
          </div>
        </div>
        <div v-else class="flex-1 flex items-center justify-center text-sm text-slate-500 py-6">
          Boshlang'ich balans kiritilmagan
        </div>
      </div>
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
      <!-- Today's payments breakdown + recent cash transactions -->
      <div class="card p-6 flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
            Bugungi to'lovlar
          </h3>
          <RouterLink to="/app/payments" class="text-xs text-brand-600 font-semibold hover:underline">
            Hammasi →
          </RouterLink>
        </div>
        <div class="grid grid-cols-2 gap-2 mb-4">
          <div class="rounded-xl bg-emerald-50 dark:bg-emerald-950/30 p-3">
            <p class="text-[10px] text-emerald-700 dark:text-emerald-300 uppercase tracking-wide font-semibold">Naqd</p>
            <p class="text-base font-extrabold text-emerald-700 dark:text-emerald-400 mt-0.5 truncate">
              {{ formatMoney(cashToday) }}
            </p>
          </div>
          <div class="rounded-xl bg-brand-50 dark:bg-brand-950/30 p-3">
            <p class="text-[10px] text-brand-700 dark:text-brand-300 uppercase tracking-wide font-semibold">Karta</p>
            <p class="text-base font-extrabold text-brand-700 dark:text-brand-400 mt-0.5 truncate">
              {{ formatMoney(cardToday) }}
            </p>
          </div>
        </div>

        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
          So'nggi kassa harakatlari
        </h4>
        <div v-if="!cashRecent.length" class="text-sm text-slate-500 py-4 text-center flex-1">
          Hali harakat yo'q
        </div>
        <ul v-else class="divide-y divide-slate-200 dark:divide-slate-800 flex-1">
          <li
            v-for="t in cashRecent.slice(0, 6)"
            :key="t.id"
            class="py-2 flex items-start gap-2"
          >
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate">
                {{ kindLabel(t.kind) }}
              </p>
              <p class="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                {{ t.description || '—' }} · {{ dayjs(t.occurred_at).format("DD.MM HH:mm") }}
              </p>
            </div>
            <span :class="['text-sm font-bold whitespace-nowrap shrink-0', txColor(t.amount)]">
              {{ txSign(t.amount) }}{{ formatMoney(t.amount.replace('-', '')) }}
            </span>
          </li>
        </ul>
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
