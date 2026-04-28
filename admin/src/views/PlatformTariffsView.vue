<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import {
  CheckCircleIcon,
  SparklesIcon,
  StarIcon,
  TrophyIcon,
  RocketLaunchIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import { platformApi, type PlatformTariffMeta, type TariffPlan } from "@/api/platform";
import { formatMoney } from "@/utils/format";

const tariffs = ref<PlatformTariffMeta[]>([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    tariffs.value = await platformApi.tariffs();
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const ICONS: Record<TariffPlan, any> = {
  trial: RocketLaunchIcon,
  start: SparklesIcon,
  biznes: StarIcon,
  premium: TrophyIcon,
};

const ACCENTS: Record<TariffPlan, string> = {
  trial: "from-slate-500 to-slate-600",
  start: "from-sky-500 to-blue-600",
  biznes: "from-brand-500 to-indigo-600",
  premium: "from-amber-500 to-orange-600",
};

function formatLimit(value: number | null): string {
  return value == null ? "Cheksiz" : value.toLocaleString("uz-UZ");
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Tariflar" subtitle="Mavjud tarif rejalari va ularning chegaralari" />

    <div v-if="loading && !tariffs.length" class="card p-12 text-center text-sm text-slate-500">
      Yuklanmoqda...
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <div
        v-for="t in tariffs"
        :key="t.plan"
        class="card p-6 flex flex-col"
      >
        <div :class="['inline-flex h-12 w-12 items-center justify-center rounded-xl text-white shadow-lg bg-gradient-to-br', ACCENTS[t.plan]]">
          <component :is="ICONS[t.plan]" class="h-6 w-6" />
        </div>
        <h3 class="mt-4 text-xl font-bold text-slate-900 dark:text-slate-100">{{ t.label }}</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ t.description }}</p>

        <div class="mt-5">
          <span class="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">
            {{ t.monthly_fee_default === 0 ? "Bepul" : formatMoney(t.monthly_fee_default) }}
          </span>
          <span v-if="t.monthly_fee_default > 0" class="text-sm text-slate-500 ml-1">/oy</span>
        </div>

        <!-- Limits -->
        <div class="mt-5 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-slate-500">Haydovchilar</span>
            <span class="font-bold text-slate-900 dark:text-slate-100">{{ formatLimit(t.max_drivers) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-slate-500">Mijozlar</span>
            <span class="font-bold text-slate-900 dark:text-slate-100">{{ formatLimit(t.max_customers) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-slate-500">Buyurtma/oy</span>
            <span class="font-bold text-slate-900 dark:text-slate-100">{{ formatLimit(t.max_orders_per_month) }}</span>
          </div>
        </div>

        <!-- Features -->
        <ul class="mt-5 space-y-2 text-sm text-slate-700 dark:text-slate-300 flex-1 pt-5 border-t border-slate-200 dark:border-slate-800">
          <li v-for="f in t.features" :key="f" class="flex items-start gap-2">
            <CheckCircleIcon class="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
            <span>{{ f }}</span>
          </li>
        </ul>
      </div>
    </div>

    <p class="text-xs text-slate-500 dark:text-slate-400 max-w-3xl">
      Chegaralar tizim tomonidan avtomatik kuzatiladi. Kompaniya yangi haydovchi/mijoz/buyurtma
      yaratganda chegaraga yetganligi tekshiriladi. Yuqori tarifga o'tish uchun kompaniyaning
      individual sahifasidan o'zgartirish mumkin.
    </p>
  </div>
</template>
