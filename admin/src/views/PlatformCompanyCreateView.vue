<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeftIcon } from "@heroicons/vue/20/solid";
import { CheckCircleIcon } from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import {
  platformApi,
  TARIFF_LABELS,
  type PlatformCompanyCreate,
  type PlatformTariffMeta,
  type TariffPlan,
} from "@/api/platform";
import { formatMoney } from "@/utils/format";
import { toast } from "@/lib/toast";

const router = useRouter();
const saving = ref(false);
const tariffs = ref<PlatformTariffMeta[]>([]);
const monthlyFeeTouched = ref(false);

const form = reactive<PlatformCompanyCreate>({
  name: "",
  slug: "",
  phone: "",
  address: "",
  tariff_plan: "trial",
  monthly_fee: "0",
  trial_ends_at: null,
  admin_full_name: "",
  admin_phone: "",
  admin_password: "",
});

const tariffOptions = (Object.keys(TARIFF_LABELS) as TariffPlan[]).map((k) => ({
  value: k,
  label: TARIFF_LABELS[k],
}));

const selectedTariff = computed<PlatformTariffMeta | null>(() => {
  return tariffs.value.find((t) => t.plan === form.tariff_plan) ?? null;
});

onMounted(async () => {
  try {
    tariffs.value = await platformApi.tariffs();
    // Auto-fill suggested monthly fee on first load
    if (selectedTariff.value && !monthlyFeeTouched.value) {
      form.monthly_fee = String(selectedTariff.value.monthly_fee_default);
    }
  } catch {
    // ignore
  }
});

// When tariff_plan changes, auto-fill monthly_fee unless owner has manually edited it
watch(
  () => form.tariff_plan,
  () => {
    if (!monthlyFeeTouched.value && selectedTariff.value) {
      form.monthly_fee = String(selectedTariff.value.monthly_fee_default);
    }
  },
);

function formatLimit(value: number | null): string {
  return value == null ? "Cheksiz" : value.toLocaleString("uz-UZ");
}

function slugify(s: string) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

function onNameBlur() {
  if (!form.slug && form.name) form.slug = slugify(form.name);
}

async function onSubmit() {
  if (!form.name.trim() || !form.slug.trim()) {
    toast.warning("Kompaniya nomi va slug majburiy");
    return;
  }
  if (!form.admin_full_name || !form.admin_phone || !form.admin_password) {
    toast.warning("Super admin ma'lumotlari to'liq kiritilsin");
    return;
  }
  if (form.admin_password.length < 6) {
    toast.warning("Parol kamida 6 belgidan iborat bo'lsin");
    return;
  }

  saving.value = true;
  try {
    const body: PlatformCompanyCreate = {
      ...form,
      phone: form.phone || null,
      address: form.address || null,
      trial_ends_at: form.trial_ends_at || null,
      monthly_fee: form.monthly_fee || "0",
    };
    const created = await platformApi.createCompany(body);
    toast.success("Kompaniya yaratildi");
    router.push(`/platform/companies/${created.id}`);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Yaratib bo'lmadi");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <PageHeader title="Yangi kompaniya" subtitle="Platformaga yangi mijoz qo'shish">
      <template #actions>
        <button class="btn-ghost" @click="router.back()">
          <ArrowLeftIcon class="h-4 w-4" />
          Orqaga
        </button>
      </template>
    </PageHeader>

    <form class="space-y-5" @submit.prevent="onSubmit">
      <!-- Company -->
      <div class="card p-6 space-y-4">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
          Kompaniya ma'lumotlari
        </h3>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Nomi</label>
            <input v-model="form.name" class="input" placeholder="Masalan: AquaPro" @blur="onNameBlur" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Slug</label>
            <input v-model="form.slug" class="input" placeholder="aquapro" pattern="[a-z0-9][a-z0-9-]*" />
            <p class="text-xs text-slate-500 mt-1">Kichik harf, raqam va "-" bilan</p>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Telefon</label>
            <input v-model="form.phone" type="tel" class="input" placeholder="+998..." />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Manzil</label>
            <input v-model="form.address" class="input" />
          </div>
        </div>
      </div>

      <!-- Tariff -->
      <div class="card p-6 space-y-4">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Tarif</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Tarif plan</label>
            <AppSelect v-model="form.tariff_plan" :options="tariffOptions" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Oylik to'lov (so'm)</label>
            <input
              v-model="form.monthly_fee"
              type="number"
              min="0"
              class="input"
              @input="monthlyFeeTouched = true"
            />
            <p v-if="!monthlyFeeTouched && selectedTariff" class="text-xs text-slate-500 mt-1">
              Tavsiya: {{ formatMoney(selectedTariff.monthly_fee_default) }}/oy
            </p>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Sinov tugashi</label>
            <input v-model="form.trial_ends_at" type="date" class="input" />
          </div>
        </div>

        <!-- Tariff feature preview -->
        <div
          v-if="selectedTariff"
          class="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-4"
        >
          <div class="flex items-baseline justify-between gap-3 flex-wrap mb-3">
            <div>
              <h4 class="text-sm font-bold text-slate-900 dark:text-slate-100">
                {{ selectedTariff.label }}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ selectedTariff.description }}</p>
            </div>
            <div class="flex flex-wrap gap-3 text-xs">
              <span class="text-slate-500">
                Haydovchi: <strong class="text-slate-900 dark:text-slate-100">{{ formatLimit(selectedTariff.max_drivers) }}</strong>
              </span>
              <span class="text-slate-500">
                Mijoz: <strong class="text-slate-900 dark:text-slate-100">{{ formatLimit(selectedTariff.max_customers) }}</strong>
              </span>
              <span class="text-slate-500">
                Buyurtma/oy: <strong class="text-slate-900 dark:text-slate-100">{{ formatLimit(selectedTariff.max_orders_per_month) }}</strong>
              </span>
            </div>
          </div>
          <ul class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1.5 text-sm text-slate-700 dark:text-slate-300">
            <li v-for="f in selectedTariff.features" :key="f" class="flex items-start gap-1.5">
              <CheckCircleIcon class="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
              <span>{{ f }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- First admin -->
      <div class="card p-6 space-y-4">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
          Birinchi Super Admin
        </h3>
        <p class="text-sm text-slate-500 -mt-2">
          Bu foydalanuvchi kompaniya admin panelida to'liq huquqlarga ega bo'ladi
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Ism</label>
            <input v-model="form.admin_full_name" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Telefon</label>
            <input v-model="form.admin_phone" type="tel" class="input" placeholder="+998..." />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Parol</label>
            <input v-model="form.admin_password" type="text" class="input" minlength="6" />
            <p class="text-xs text-slate-500 mt-1">Mijozga uzatasiz, keyin ular o'zgartiradi</p>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3">
        <button type="button" class="btn-ghost" @click="router.back()">Bekor qilish</button>
        <button type="submit" class="btn-primary" :disabled="saving">
          {{ saving ? "Yaratilyapti..." : "Kompaniya yaratish" }}
        </button>
      </div>
    </form>
  </div>
</template>
