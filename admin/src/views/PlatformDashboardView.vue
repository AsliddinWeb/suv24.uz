<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  BuildingOffice2Icon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  SparklesIcon,
  ArrowPathIcon,
  ArrowUpRightIcon,
  PlusIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import {
  platformApi,
  TARIFF_LABELS,
  type PlatformOverview,
  type TariffPlan,
} from "@/api/platform";
import { formatMoney } from "@/utils/format";

const loading = ref(false);
const data = ref<PlatformOverview | null>(null);

async function load() {
  loading.value = true;
  try {
    data.value = await platformApi.overview();
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const kpis = computed(() => {
  const d = data.value;
  if (!d) return [];
  return [
    {
      label: "Kompaniyalar",
      value: String(d.companies_total),
      sub: `${d.companies_active} aktiv · ${d.companies_trial} sinov`,
      icon: BuildingOffice2Icon,
      gradient: "from-brand-500 to-indigo-600",
    },
    {
      label: "Oylik daromad (MRR)",
      value: formatMoney(d.platform_mrr),
      sub: "Sizning to'lovingiz",
      icon: CurrencyDollarIcon,
      gradient: "from-emerald-500 to-teal-600",
    },
    {
      label: "Buyurtmalar (bu oy)",
      value: String(d.orders_this_month),
      sub: "Hamma kompaniyalarda",
      icon: ShoppingBagIcon,
      gradient: "from-amber-500 to-orange-600",
    },
    {
      label: "Tushum (bu oy)",
      value: formatMoney(d.revenue_this_month),
      sub: "Hamma kompaniyalarda",
      icon: SparklesIcon,
      gradient: "from-rose-500 to-pink-600",
    },
  ];
});

const tariffRows = computed(() => {
  if (!data.value) return [];
  return (Object.keys(TARIFF_LABELS) as TariffPlan[]).map((k) => ({
    key: k,
    label: TARIFF_LABELS[k],
    count: data.value!.tariff_breakdown[k] || 0,
  }));
});
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Umumiy holat" subtitle="Suv24 platformasining joriy ko'rsatkichlari">
      <template #actions>
        <RouterLink to="/platform/companies/new" class="btn-primary">
          <PlusIcon class="h-4 w-4" />
          Yangi kompaniya
        </RouterLink>
        <button class="btn-ghost !p-2" :disabled="loading" @click="load" title="Yangilash">
          <ArrowPathIcon :class="['h-5 w-5', loading && 'animate-spin']" />
        </button>
      </template>
    </PageHeader>

    <!-- KPI -->
    <div v-if="data" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="(kpi, i) in kpis"
        :key="i"
        :class="[
          'relative overflow-hidden rounded-2xl p-5 text-white shadow-soft',
          'bg-gradient-to-br', kpi.gradient,
        ]"
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
      </div>
    </div>

    <div v-if="data" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Top companies -->
      <div class="card p-6 lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              Top kompaniyalar (tushum bo'yicha)
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Bu oy</p>
          </div>
          <RouterLink to="/platform/companies" class="text-sm text-brand-600 font-medium">
            Barchasi →
          </RouterLink>
        </div>

        <div v-if="data.top_companies_by_revenue.length" class="space-y-2">
          <RouterLink
            v-for="c in data.top_companies_by_revenue"
            :key="c.id"
            :to="`/platform/companies/${c.id}`"
            class="group flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
          >
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white font-bold shrink-0">
              {{ c.name.slice(0, 1).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">{{ c.name }}</div>
              <div class="text-xs text-slate-500 dark:text-slate-400">
                {{ TARIFF_LABELS[c.tariff_plan] }} · {{ c.orders_this_month }} buyurtma
              </div>
            </div>
            <div class="text-right shrink-0">
              <div class="text-sm font-bold text-slate-900 dark:text-slate-100">{{ formatMoney(c.revenue_this_month) }}</div>
              <ArrowUpRightIcon class="inline h-3 w-3 text-slate-400 group-hover:text-brand-600" />
            </div>
          </RouterLink>
        </div>
        <div v-else class="py-8 text-center text-sm text-slate-500">
          Hali buyurtma yo'q
        </div>
      </div>

      <!-- Tariff breakdown -->
      <div class="card p-6">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-4">
          Tariflar bo'yicha
        </h3>
        <div class="space-y-3">
          <div
            v-for="row in tariffRows"
            :key="row.key"
            class="flex items-center justify-between"
          >
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ row.label }}</span>
            <div class="flex items-center gap-2">
              <div class="h-2 w-24 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-brand-500 to-indigo-600"
                  :style="{ width: (data.companies_total ? (row.count / data.companies_total) * 100 : 0) + '%' }"
                />
              </div>
              <span class="text-sm font-bold text-slate-900 dark:text-slate-100 w-6 text-right">
                {{ row.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card p-12 text-center text-sm text-slate-500">
      Yuklanmoqda...
    </div>
  </div>
</template>
