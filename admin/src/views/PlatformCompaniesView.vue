<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  PlusIcon,
  MagnifyingGlassIcon,
  CheckBadgeIcon,
  XCircleIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import {
  platformApi,
  TARIFF_LABELS,
  type PlatformCompanyOut,
} from "@/api/platform";
import { formatMoney } from "@/utils/format";
import dayjs from "dayjs";

const companies = ref<PlatformCompanyOut[]>([]);
const loading = ref(false);
const q = ref("");

async function load() {
  loading.value = true;
  try {
    companies.value = await platformApi.listCompanies({
      q: q.value.trim() || undefined,
    });
  } finally {
    loading.value = false;
  }
}

let t: ReturnType<typeof setTimeout> | null = null;
function onSearch() {
  if (t) clearTimeout(t);
  t = setTimeout(load, 250);
}

onMounted(load);
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Kompaniyalar" subtitle="Platformaga ulangan mijozlar">
      <template #actions>
        <RouterLink to="/platform/companies/new" class="btn-primary">
          <PlusIcon class="h-4 w-4" />
          Qo'shish
        </RouterLink>
      </template>
    </PageHeader>

    <div class="card p-0 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-800">
        <div class="relative max-w-sm">
          <MagnifyingGlassIcon class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-slate-400" />
          <input
            v-model="q"
            type="text"
            placeholder="Nom yoki slug..."
            class="input pl-9"
            @input="onSearch"
          />
        </div>
      </div>

      <div v-if="loading && !companies.length" class="p-8 text-center text-sm text-slate-500">
        Yuklanmoqda...
      </div>
      <div v-else-if="!companies.length" class="p-8 text-center text-sm text-slate-500">
        Kompaniyalar yo'q
      </div>
      <div v-else class="divide-y divide-slate-200 dark:divide-slate-800">
        <RouterLink
          v-for="c in companies"
          :key="c.id"
          :to="`/platform/companies/${c.id}`"
          class="flex items-center gap-4 px-4 py-4 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
        >
          <div class="h-12 w-12 rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
            <img v-if="c.logo_url" :src="c.logo_url" :alt="c.name" class="h-full w-full object-cover" />
            <div
              v-else
              class="h-full w-full bg-gradient-to-br from-brand-500 to-indigo-600 text-white font-bold flex items-center justify-center"
            >
              {{ c.name.slice(0, 1).toUpperCase() }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                {{ c.name }}
              </span>
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                {{ TARIFF_LABELS[c.tariff_plan] }}
              </span>
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400 truncate">
              {{ c.slug }} · {{ c.phone || "telefon yo'q" }} · {{ dayjs(c.created_at).format("DD.MM.YYYY") }}
            </div>
          </div>
          <div class="text-right shrink-0 hidden sm:block">
            <div class="text-sm font-bold text-slate-900 dark:text-slate-100">
              {{ formatMoney(c.monthly_fee) }}<span class="text-xs text-slate-500">/oy</span>
            </div>
            <div class="mt-0.5">
              <CheckBadgeIcon v-if="c.is_active" class="inline h-4 w-4 text-emerald-500" />
              <XCircleIcon v-else class="inline h-4 w-4 text-rose-500" />
              <span class="ml-1 text-xs text-slate-500">
                {{ c.is_active ? "Aktiv" : "O'chirilgan" }}
              </span>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
