<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  ShoppingBagIcon,
  UsersIcon,
  TruckIcon,
  CurrencyDollarIcon,
  TrashIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import {
  platformApi,
  TARIFF_LABELS,
  type CompanyAdminOut,
  type PlatformCompanyDetail,
  type TariffPlan,
} from "@/api/platform";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import { formatMoney } from "@/utils/format";
import dayjs from "dayjs";

const route = useRoute();
const router = useRouter();
const confirm = useConfirm();
const company = ref<PlatformCompanyDetail | null>(null);
const loading = ref(false);
const savingInfo = ref(false);
const savingTariff = ref(false);
const deleting = ref(false);

const info = reactive({
  name: "",
  short_name: "",
  phone: "",
  support_phone: "",
  address: "",
});

const tariff = reactive<{
  tariff_plan: TariffPlan;
  monthly_fee: string;
  trial_ends_at: string;
  is_active: boolean;
}>({
  tariff_plan: "trial",
  monthly_fee: "0",
  trial_ends_at: "",
  is_active: true,
});

const tariffOptions = (Object.keys(TARIFF_LABELS) as TariffPlan[]).map((k) => ({
  value: k,
  label: TARIFF_LABELS[k],
}));

// Super admin section
const admins = ref<CompanyAdminOut[]>([]);
const editingAdminId = ref<string | null>(null);
const adminForm = reactive({
  full_name: "",
  phone: "",
  password: "",
  is_active: true,
});
const savingAdmin = ref(false);

async function loadAdmins(companyId: string) {
  try {
    admins.value = await platformApi.listCompanyAdmins(companyId);
  } catch {
    // ignore
  }
}

function startEditAdmin(a: CompanyAdminOut) {
  editingAdminId.value = a.id;
  adminForm.full_name = a.full_name;
  adminForm.phone = a.phone;
  adminForm.password = "";
  adminForm.is_active = a.is_active;
}

function cancelEditAdmin() {
  editingAdminId.value = null;
  adminForm.password = "";
}

async function saveAdmin() {
  if (!company.value || !editingAdminId.value) return;
  savingAdmin.value = true;
  try {
    const body: any = {
      full_name: adminForm.full_name,
      phone: adminForm.phone,
      is_active: adminForm.is_active,
    };
    if (adminForm.password.trim()) body.password = adminForm.password;
    const updated = await platformApi.updateCompanyAdmin(
      company.value.id,
      editingAdminId.value,
      body,
    );
    const idx = admins.value.findIndex((a) => a.id === updated.id);
    if (idx >= 0) admins.value[idx] = updated;
    toast.success("Super admin yangilandi");
    cancelEditAdmin();
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  } finally {
    savingAdmin.value = false;
  }
}

async function load() {
  loading.value = true;
  try {
    const id = route.params.id as string;
    const c = await platformApi.getCompany(id);
    company.value = c;
    info.name = c.name;
    info.short_name = c.short_name ?? "";
    info.phone = c.phone ?? "";
    info.support_phone = c.support_phone ?? "";
    info.address = c.address ?? "";
    tariff.tariff_plan = c.tariff_plan;
    tariff.monthly_fee = String(c.monthly_fee);
    tariff.trial_ends_at = c.trial_ends_at ? c.trial_ends_at.slice(0, 10) : "";
    tariff.is_active = c.is_active;
    loadAdmins(c.id);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

async function saveInfo() {
  if (!company.value) return;
  savingInfo.value = true;
  try {
    const updated = await platformApi.updateCompany(company.value.id, {
      name: info.name,
      short_name: info.short_name || null,
      phone: info.phone || null,
      support_phone: info.support_phone || null,
      address: info.address || null,
    });
    company.value = { ...company.value, ...updated };
    toast.success("Ma'lumotlar saqlandi");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  } finally {
    savingInfo.value = false;
  }
}

async function saveTariff() {
  if (!company.value) return;
  savingTariff.value = true;
  try {
    const updated = await platformApi.updateCompany(company.value.id, {
      tariff_plan: tariff.tariff_plan,
      monthly_fee: tariff.monthly_fee,
      trial_ends_at: tariff.trial_ends_at ? new Date(tariff.trial_ends_at).toISOString() : null,
      is_active: tariff.is_active,
    });
    company.value = { ...company.value, ...updated };
    toast.success("Tarif saqlandi");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  } finally {
    savingTariff.value = false;
  }
}

async function onDelete() {
  if (!company.value) return;
  const ok = await confirm({
    title: "Kompaniyani o'chirish",
    description: `"${company.value.name}" kompaniyasi va uning barcha foydalanuvchilari o'chiriladi. Ma'lumotlar DB'da qoladi (soft delete), lekin kirish imkoni yo'qoladi.`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  deleting.value = true;
  try {
    await platformApi.deleteCompany(company.value.id);
    toast.success("Kompaniya o'chirildi");
    router.push("/platform/companies");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "O'chirib bo'lmadi");
  } finally {
    deleting.value = false;
  }
}

const stats = computed(() => {
  const s = company.value?.stats;
  if (!s) return [];
  return [
    { label: "Buyurtmalar (bu oy)", value: String(s.orders_this_month), icon: ShoppingBagIcon },
    { label: "Jami buyurtma", value: String(s.orders_total), icon: ShoppingBagIcon },
    { label: "Foydalanuvchilar", value: String(s.users_count), icon: UsersIcon },
    { label: "Haydovchilar", value: String(s.drivers_count), icon: TruckIcon },
    { label: "Mijozlar", value: String(s.customers_count), icon: UsersIcon },
    { label: "Tushum (bu oy)", value: formatMoney(s.revenue_this_month), icon: CurrencyDollarIcon },
  ];
});
</script>

<template>
  <div v-if="loading && !company" class="card p-12 text-center text-sm text-slate-500">
    Yuklanmoqda...
  </div>

  <div v-else-if="company" class="space-y-6">
    <PageHeader :title="company.name" :subtitle="`/${company.slug} · ${TARIFF_LABELS[company.tariff_plan]}`">
      <template #actions>
        <button class="btn-ghost" @click="router.push('/platform/companies')">
          <ArrowLeftIcon class="h-4 w-4" />
          Ro'yxat
        </button>
        <button
          class="btn-ghost text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40"
          :disabled="deleting"
          @click="onDelete"
        >
          <TrashIcon class="h-4 w-4" />
          O'chirish
        </button>
      </template>
    </PageHeader>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div v-for="(s, i) in stats" :key="i" class="card p-4">
        <div class="flex items-center gap-2 text-slate-500 mb-1">
          <component :is="s.icon" class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide truncate">{{ s.label }}</span>
        </div>
        <div class="text-lg font-bold text-slate-900 dark:text-slate-100 truncate">{{ s.value }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Info (editable) -->
      <form class="card p-6 space-y-4" @submit.prevent="saveInfo">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Ma'lumotlar</h3>

        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Nomi</label>
            <input v-model="info.name" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Qisqa nom</label>
            <input v-model="info.short_name" class="input" maxlength="32" />
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Telefon</label>
              <input v-model="info.phone" type="tel" class="input" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Qo'llab-quvvatlash</label>
              <input v-model="info.support_phone" type="tel" class="input" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Manzil</label>
            <input v-model="info.address" class="input" />
          </div>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500">
          <span>Slug: <code class="font-mono">{{ company.slug }}</code> · {{ dayjs(company.created_at).format("DD.MM.YYYY") }}</span>
          <button type="submit" class="btn-primary !py-1.5 !px-3 text-sm" :disabled="savingInfo">
            {{ savingInfo ? "Saqlanmoqda..." : "Saqlash" }}
          </button>
        </div>
      </form>

      <!-- Tariff & status -->
      <form class="card p-6 space-y-4" @submit.prevent="saveTariff">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Tarif va holat</h3>

        <div>
          <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Tarif plan</label>
          <AppSelect v-model="tariff.tariff_plan" :options="tariffOptions" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Oylik to'lov (so'm)</label>
            <input v-model="tariff.monthly_fee" type="number" min="0" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Sinov tugashi</label>
            <input v-model="tariff.trial_ends_at" type="date" class="input" />
          </div>
        </div>

        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="tariff.is_active" type="checkbox" class="rounded border-slate-300" />
          <span class="text-sm text-slate-700 dark:text-slate-300">Aktiv (kirishga ruxsat)</span>
        </label>

        <div class="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-800">
          <span class="text-xs">
            <AppBadge v-if="company.is_active" type="success">
              <CheckCircleIcon class="h-3 w-3" /> Aktiv
            </AppBadge>
            <AppBadge v-else type="danger">
              <XCircleIcon class="h-3 w-3" /> O'chirilgan
            </AppBadge>
          </span>
          <button type="submit" class="btn-primary !py-1.5 !px-3 text-sm" :disabled="savingTariff">
            {{ savingTariff ? "Saqlanmoqda..." : "Saqlash" }}
          </button>
        </div>
      </form>
    </div>

    <!-- Super admin(s) -->
    <div class="card p-6 space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Super admin(lar)</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Kompaniya admin paneliga to'liq huquq bilan kira oladigan foydalanuvchilar
          </p>
        </div>
      </div>

      <div v-if="!admins.length" class="text-sm text-slate-500 py-4 text-center">
        Super admin yo'q
      </div>

      <div v-else class="divide-y divide-slate-200 dark:divide-slate-800">
        <div v-for="a in admins" :key="a.id" class="py-3 first:pt-0 last:pb-0">
          <!-- View mode -->
          <div v-if="editingAdminId !== a.id" class="flex items-center gap-3 flex-wrap">
            <div class="h-10 w-10 rounded-full bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white font-bold shrink-0">
              {{ a.full_name.slice(0, 1).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                {{ a.full_name }}
              </div>
              <div class="text-xs text-slate-500 dark:text-slate-400">{{ a.phone }}</div>
            </div>
            <AppBadge :type="a.is_active ? 'success' : 'neutral'" class="shrink-0">
              {{ a.is_active ? 'Aktiv' : 'O\'chirilgan' }}
            </AppBadge>
            <button class="btn-ghost text-sm !py-1 !px-2.5" @click="startEditAdmin(a)">
              Tahrirlash
            </button>
          </div>

          <!-- Edit mode -->
          <div v-else class="space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Ism</label>
                <input v-model="adminForm.full_name" class="input" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">Telefon</label>
                <input v-model="adminForm.phone" type="tel" class="input" />
              </div>
              <div class="sm:col-span-2">
                <label class="block text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">
                  Yangi parol <span class="text-slate-400 font-normal">(ixtiyoriy)</span>
                </label>
                <input
                  v-model="adminForm.password"
                  type="text"
                  class="input"
                  placeholder="O'zgartirmaslik uchun bo'sh qoldiring"
                  minlength="6"
                />
              </div>
            </div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="adminForm.is_active" type="checkbox" class="rounded border-slate-300" />
              <span class="text-sm text-slate-700 dark:text-slate-300">Aktiv (kira oladi)</span>
            </label>
            <div class="flex justify-end gap-2 pt-1">
              <button class="btn-ghost !py-1.5 !px-3 text-sm" @click="cancelEditAdmin">Bekor</button>
              <button
                class="btn-primary !py-1.5 !px-3 text-sm"
                :disabled="savingAdmin"
                @click="saveAdmin"
              >
                {{ savingAdmin ? "Saqlanmoqda..." : "Saqlash" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
