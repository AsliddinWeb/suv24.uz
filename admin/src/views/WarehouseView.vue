<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  CubeIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  PencilSquareIcon,
  ArrowPathIcon,
  ScaleIcon,
  BanknotesIcon,
  PlusCircleIcon,
  MinusCircleIcon,
  ArrowDownCircleIcon,
  ClockIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import {
  warehouseApi,
  cashApi,
  purchasesApi,
  CASH_KIND_LABELS,
  type WarehouseStock,
  type WarehouseSummary,
  type CashSnapshot,
  type CashTransaction,
  type InventoryPurchase,
  type CashTxKind,
} from "@/api/warehouse";
import { driversApi } from "@/api/drivers";
import { formatMoney } from "@/utils/format";
import { toast } from "@/lib/toast";
import dayjs from "dayjs";
import type { DriverOut } from "@/types/api";

const stocks = ref<WarehouseStock[]>([]);
const summary = ref<WarehouseSummary[]>([]);
const drivers = ref<DriverOut[]>([]);
const cash = ref<CashSnapshot | null>(null);
const transactions = ref<CashTransaction[]>([]);
const purchases = ref<InventoryPurchase[]>([]);
const loading = ref(false);
const tab = ref<"stock" | "cash" | "purchases">("stock");

async function loadCash() {
  cash.value = await cashApi.snapshot();
}
async function loadTransactions() {
  transactions.value = await cashApi.transactions(100);
}
async function loadPurchases() {
  purchases.value = await purchasesApi.list(100);
}

async function load() {
  loading.value = true;
  try {
    const [s, sum, d, c] = await Promise.all([
      warehouseApi.list(),
      warehouseApi.summary(),
      driversApi.list(),
      cashApi.snapshot(),
    ]);
    stocks.value = s;
    summary.value = sum;
    drivers.value = d.filter((x) => x.is_active);
    cash.value = c;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await load();
  // Lazy-load secondary tabs in background so switching tabs is instant
  loadTransactions().catch(() => undefined);
  loadPurchases().catch(() => undefined);
});

// ----- Cash dialogs -----
const openingOpen = ref(false);
const openingForm = reactive({ amount: "0", note: "" });
function openOpeningBalance() {
  openingForm.amount = "0";
  openingForm.note = "";
  openingOpen.value = true;
}
async function submitOpening() {
  const amount = parseFloat(openingForm.amount || "0") || 0;
  if (amount < 0) {
    toast.warning("Manfiy son bermang");
    return;
  }
  try {
    await cashApi.setOpeningBalance({ amount: amount.toString(), note: openingForm.note || null });
    toast.success("Boshlang'ich balans saqlandi");
    openingOpen.value = false;
    await loadCash();
    loadTransactions().catch(() => undefined);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

const expenseOpen = ref(false);
const expenseForm = reactive({ amount: "0", description: "" });
function openExpense() {
  expenseForm.amount = "0";
  expenseForm.description = "";
  expenseOpen.value = true;
}
async function submitExpense() {
  const amount = parseFloat(expenseForm.amount || "0") || 0;
  if (amount <= 0) {
    toast.warning("Summa 0 dan katta bo'lsin");
    return;
  }
  if (!expenseForm.description.trim()) {
    toast.warning("Sabab majburiy");
    return;
  }
  try {
    await cashApi.expense({ amount: amount.toString(), description: expenseForm.description });
    toast.success("Xarajat yozildi");
    expenseOpen.value = false;
    await loadCash();
    loadTransactions().catch(() => undefined);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

const manualOpen = ref(false);
const manualForm = reactive<{ direction: "in" | "out"; amount: string; description: string }>({
  direction: "in",
  amount: "0",
  description: "",
});
function openManual(dir: "in" | "out") {
  manualForm.direction = dir;
  manualForm.amount = "0";
  manualForm.description = "";
  manualOpen.value = true;
}
async function submitManual() {
  const amount = parseFloat(manualForm.amount || "0") || 0;
  if (amount <= 0) {
    toast.warning("Summa 0 dan katta bo'lsin");
    return;
  }
  if (!manualForm.description.trim()) {
    toast.warning("Sabab majburiy");
    return;
  }
  try {
    await cashApi.manual({
      direction: manualForm.direction,
      amount: amount.toString(),
      description: manualForm.description,
    });
    toast.success(manualForm.direction === "in" ? "Kirim yozildi" : "Chiqim yozildi");
    manualOpen.value = false;
    await loadCash();
    loadTransactions().catch(() => undefined);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

// ----- Purchase dialog -----
const purchaseOpen = ref(false);
const purchaseForm = reactive<{
  product_id: string | null;
  product_name: string;
  full_count: string;
  empty_count: string;
  unit_cost: string;
  supplier: string;
  note: string;
}>({
  product_id: null,
  product_name: "",
  full_count: "0",
  empty_count: "0",
  unit_cost: "0",
  supplier: "",
  note: "",
});

const productOptions = computed(() =>
  stocks.value.map((s) => ({
    value: s.product_id,
    label: `${s.product_name} · ${s.volume_liters}L`,
  })),
);

const purchaseTotal = computed(() => {
  const fc = parseInt(purchaseForm.full_count || "0", 10) || 0;
  const ec = parseInt(purchaseForm.empty_count || "0", 10) || 0;
  const uc = parseFloat(purchaseForm.unit_cost || "0") || 0;
  return (fc + ec) * uc;
});

function openPurchase(s?: WarehouseStock) {
  purchaseForm.product_id = s?.product_id || stocks.value[0]?.product_id || null;
  purchaseForm.product_name = s ? `${s.product_name} · ${s.volume_liters}L` : "";
  purchaseForm.full_count = "0";
  purchaseForm.empty_count = "0";
  purchaseForm.unit_cost = "0";
  purchaseForm.supplier = "";
  purchaseForm.note = "";
  purchaseOpen.value = true;
}

async function submitPurchase() {
  if (!purchaseForm.product_id) {
    toast.warning("Mahsulot tanlang");
    return;
  }
  const fc = parseInt(purchaseForm.full_count || "0", 10) || 0;
  const ec = parseInt(purchaseForm.empty_count || "0", 10) || 0;
  if (fc < 0 || ec < 0) {
    toast.warning("Manfiy son bermang");
    return;
  }
  if (fc + ec === 0) {
    toast.warning("Soni 0 bo'lmasin");
    return;
  }
  const uc = parseFloat(purchaseForm.unit_cost || "0") || 0;
  if (uc < 0) {
    toast.warning("Birlik narxi manfiy bo'lmasin");
    return;
  }
  try {
    await purchasesApi.create({
      product_id: purchaseForm.product_id,
      full_count: fc,
      empty_count: ec,
      unit_cost: uc.toString(),
      supplier: purchaseForm.supplier || null,
      note: purchaseForm.note || null,
    });
    toast.success("Mahsulot kirimi yozildi");
    purchaseOpen.value = false;
    await load();
    loadTransactions().catch(() => undefined);
    loadPurchases().catch(() => undefined);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

// ----- Helpers for tx display -----
function txSign(amount: string): string {
  const n = parseFloat(amount);
  return n >= 0 ? "+" : "";
}
function txColor(amount: string): string {
  const n = parseFloat(amount);
  return n >= 0
    ? "text-emerald-600 dark:text-emerald-400"
    : "text-rose-600 dark:text-rose-400";
}
function kindLabel(k: CashTxKind): string {
  return CASH_KIND_LABELS[k];
}

// Adjust dialog
const adjOpen = ref(false);
const adjForm = reactive<{
  product_id: string | null;
  product_name: string;
  full_delta: string;
  empty_delta: string;
  reason: string;
}>({
  product_id: null,
  product_name: "",
  full_delta: "0",
  empty_delta: "0",
  reason: "",
});

function openAdjust(s: WarehouseStock) {
  adjForm.product_id = s.product_id;
  adjForm.product_name = `${s.product_name} · ${s.volume_liters}L`;
  adjForm.full_delta = "0";
  adjForm.empty_delta = "0";
  adjForm.reason = "";
  adjOpen.value = true;
}

async function submitAdjust() {
  if (!adjForm.product_id) return;
  const fd = parseInt(adjForm.full_delta || "0", 10) || 0;
  const ed = parseInt(adjForm.empty_delta || "0", 10) || 0;
  if (fd === 0 && ed === 0) {
    toast.warning("Hech narsa kiritilmagan");
    return;
  }
  try {
    await warehouseApi.adjust({
      product_id: adjForm.product_id,
      full_delta: fd,
      empty_delta: ed,
      reason: adjForm.reason || null,
    });
    toast.success("Ombor yangilandi");
    adjOpen.value = false;
    await load();
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

// Transfer dialog
type TransferDir = "to" | "from";
const trOpen = ref(false);
const trDir = ref<TransferDir>("to");
const trForm = reactive<{
  product_id: string | null;
  product_name: string;
  driver_id: string | null;
  full_count: string;
  empty_count: string;
  reason: string;
}>({
  product_id: null,
  product_name: "",
  driver_id: null,
  full_count: "0",
  empty_count: "0",
  reason: "",
});

const driverOptions = computed(() =>
  drivers.value.map((d) => ({
    value: d.id,
    label: `${d.full_name}${d.vehicle_plate ? ` · ${d.vehicle_plate}` : ""}`,
  })),
);

const trTitle = computed(() =>
  trDir.value === "to" ? "Haydovchiga yuklash" : "Haydovchidan qaytarish",
);

function openTransfer(s: WarehouseStock, dir: TransferDir) {
  trDir.value = dir;
  trForm.product_id = s.product_id;
  trForm.product_name = `${s.product_name} · ${s.volume_liters}L`;
  trForm.driver_id = drivers.value[0]?.id ?? null;
  trForm.full_count = "0";
  trForm.empty_count = "0";
  trForm.reason = "";
  trOpen.value = true;
}

async function submitTransfer() {
  if (!trForm.product_id || !trForm.driver_id) {
    toast.warning("Mahsulot va haydovchi tanlang");
    return;
  }
  const fc = parseInt(trForm.full_count || "0", 10) || 0;
  const ec = parseInt(trForm.empty_count || "0", 10) || 0;
  if (fc < 0 || ec < 0) {
    toast.warning("Manfiy son bermang");
    return;
  }
  if (fc === 0 && ec === 0) {
    toast.warning("Hech narsa kiritilmagan");
    return;
  }
  try {
    const fn =
      trDir.value === "to"
        ? warehouseApi.transferToDriver
        : warehouseApi.transferFromDriver;
    await fn({
      driver_id: trForm.driver_id,
      product_id: trForm.product_id,
      full_count: fc,
      empty_count: ec,
      reason: trForm.reason || null,
    });
    toast.success("Bajarildi");
    trOpen.value = false;
    await load();
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Bajarib bo'lmadi");
  }
}

// Quick "initial stock" entry — preset for blank rows
function openInitial(s: WarehouseStock) {
  openAdjust(s);
  adjForm.reason = "Boshlang'ich balans";
}

const totalFull = computed(() => summary.value.reduce((sum, s) => sum + s.warehouse_full, 0));
const totalEmpty = computed(() => summary.value.reduce((sum, s) => sum + s.warehouse_empty, 0));
const totalDriversFull = computed(() => summary.value.reduce((sum, s) => sum + s.drivers_full, 0));
const totalDriversEmpty = computed(() => summary.value.reduce((sum, s) => sum + s.drivers_empty, 0));
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Ombor" subtitle="Idish balansi va kassa">
      <template #actions>
        <button class="btn-primary" @click="openPurchase()" :disabled="!stocks.length">
          <PlusCircleIcon class="h-4 w-4" />
          Yangi kirim
        </button>
        <button class="btn-ghost !p-2" :disabled="loading" @click="load" title="Yangilash">
          <ArrowPathIcon :class="['h-5 w-5', loading && 'animate-spin']" />
        </button>
      </template>
    </PageHeader>

    <!-- Cash balance card -->
    <div v-if="cash" class="card p-6 bg-gradient-to-br from-brand-600 via-indigo-600 to-sky-500 text-white shadow-lg shadow-brand-600/25 relative overflow-hidden">
      <div class="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-white/10 blur-2xl pointer-events-none" />
      <div class="relative flex items-start justify-between gap-4 flex-wrap">
        <div class="flex items-center gap-3">
          <div class="h-12 w-12 rounded-xl bg-white/20 flex items-center justify-center">
            <BanknotesIcon class="h-6 w-6" />
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-brand-100">Kassa balansi</p>
            <p class="text-3xl sm:text-4xl font-extrabold tracking-tight mt-1">
              {{ formatMoney(cash.account.balance) }}
            </p>
            <p v-if="cash.account.opening_set_at" class="text-xs text-brand-100 mt-1">
              Boshlangan: {{ dayjs(cash.account.opening_set_at).format("DD.MM.YYYY") }}
            </p>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-if="cash.needs_opening_balance"
            class="rounded-lg bg-white text-brand-700 font-bold px-4 py-2 text-sm hover:bg-brand-50 transition"
            @click="openOpeningBalance"
          >
            🏁 Boshlang'ich balans
          </button>
          <button
            class="rounded-lg bg-white/15 hover:bg-white/25 backdrop-blur px-3 py-2 text-sm font-medium transition inline-flex items-center gap-1.5"
            @click="openManual('in')"
          >
            <PlusCircleIcon class="h-4 w-4" />
            Qo'lda kirim
          </button>
          <button
            class="rounded-lg bg-white/15 hover:bg-white/25 backdrop-blur px-3 py-2 text-sm font-medium transition inline-flex items-center gap-1.5"
            @click="openExpense"
          >
            <MinusCircleIcon class="h-4 w-4" />
            Xarajat
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 border-b border-slate-200 dark:border-slate-800">
      <button
        :class="['px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition', tab === 'stock' ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200']"
        @click="tab = 'stock'"
      >
        Idish balansi
      </button>
      <button
        :class="['px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition', tab === 'cash' ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200']"
        @click="tab = 'cash'; loadTransactions()"
      >
        Kassa harakatlari
      </button>
      <button
        :class="['px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition', tab === 'purchases' ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200']"
        @click="tab = 'purchases'; loadPurchases()"
      >
        Kirimlar tarixi
      </button>
    </div>

    <!-- TAB: Stock -->
    <div v-if="tab === 'stock'" class="space-y-6">
    <!-- Reconciliation strip -->
    <div v-if="summary.length" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="card p-4">
        <div class="flex items-center gap-2 text-emerald-600 mb-1">
          <CubeIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Omborda to'la</span>
        </div>
        <div class="text-2xl font-bold text-emerald-600">{{ totalFull }}</div>
      </div>
      <div class="card p-4">
        <div class="flex items-center gap-2 text-slate-500 mb-1">
          <CubeIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Omborda bo'sh</span>
        </div>
        <div class="text-2xl font-bold text-slate-700 dark:text-slate-200">{{ totalEmpty }}</div>
      </div>
      <div class="card p-4">
        <div class="flex items-center gap-2 text-brand-600 mb-1">
          <ScaleIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Haydovchilarda to'la</span>
        </div>
        <div class="text-2xl font-bold text-brand-600">{{ totalDriversFull }}</div>
      </div>
      <div class="card p-4">
        <div class="flex items-center gap-2 text-slate-500 mb-1">
          <ScaleIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Haydovchilarda bo'sh</span>
        </div>
        <div class="text-2xl font-bold text-slate-700 dark:text-slate-200">{{ totalDriversEmpty }}</div>
      </div>
    </div>

    <EmptyState
      v-if="!loading && !stocks.length"
      title="Qaytariladigan mahsulot yo'q"
      description="Avval Mahsulotlar bo'limidan idishli suvlar (19L, 10L) ni qo'shing"
    />

    <div v-else class="card overflow-hidden">
      <table class="data-table">
        <thead>
          <tr>
            <th>Mahsulot</th>
            <th class="text-center">Omborda to'la</th>
            <th class="text-center">Omborda bo'sh</th>
            <th>Yangilangan</th>
            <th class="text-right">Amal</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in stocks" :key="s.id">
            <td>
              <div class="font-semibold text-slate-900 dark:text-slate-100">{{ s.product_name }}</div>
              <div class="text-xs text-slate-500">{{ s.volume_liters }} litr</div>
            </td>
            <td class="text-center">
              <span class="text-lg font-bold text-emerald-600 dark:text-emerald-400">{{ s.full_count }}</span>
            </td>
            <td class="text-center">
              <span class="text-lg font-bold text-slate-700 dark:text-slate-200">{{ s.empty_count }}</span>
            </td>
            <td class="text-xs text-slate-500">{{ dayjs(s.updated_at).format("DD.MM HH:mm") }}</td>
            <td class="text-right">
              <div class="flex justify-end gap-1.5 flex-wrap">
                <button
                  v-if="s.full_count === 0 && s.empty_count === 0"
                  class="btn-primary btn-sm"
                  @click="openInitial(s)"
                  title="Boshlang'ich balans"
                >
                  <PencilSquareIcon class="h-4 w-4" />
                  Boshlang'ich
                </button>
                <template v-else>
                  <button
                    class="btn-secondary btn-sm"
                    @click="openTransfer(s, 'to')"
                    :disabled="!drivers.length"
                    title="Haydovchiga yuklash"
                  >
                    <ArrowUpTrayIcon class="h-4 w-4" />
                    Yuklash
                  </button>
                  <button
                    class="btn-secondary btn-sm"
                    @click="openTransfer(s, 'from')"
                    :disabled="!drivers.length"
                    title="Haydovchidan qaytarish"
                  >
                    <ArrowDownTrayIcon class="h-4 w-4" />
                    Qaytarish
                  </button>
                  <button
                    class="btn-ghost !p-2"
                    @click="openAdjust(s)"
                    title="Tuzatish"
                  >
                    <PencilSquareIcon class="h-4 w-4" />
                  </button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    </div>
    <!-- /TAB stock -->

    <!-- TAB: Cash -->
    <div v-if="tab === 'cash'" class="card overflow-hidden">
      <div v-if="!transactions.length" class="py-12 text-center text-sm text-slate-500">
        Hali harakat yo'q
      </div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Sana</th>
            <th>Turi</th>
            <th>Tavsif</th>
            <th class="text-right">Summa</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in transactions" :key="t.id">
            <td class="text-xs text-slate-500 whitespace-nowrap">
              {{ dayjs(t.occurred_at).format("DD.MM.YYYY HH:mm") }}
            </td>
            <td>
              <AppBadge
                :variant="t.kind === 'opening_balance' ? 'info' : (parseFloat(t.amount) >= 0 ? 'success' : 'danger')"
                class="!text-[10px]"
              >
                {{ kindLabel(t.kind) }}
              </AppBadge>
            </td>
            <td class="text-sm text-slate-700 dark:text-slate-300">{{ t.description || '—' }}</td>
            <td :class="['text-right font-bold whitespace-nowrap', txColor(t.amount)]">
              {{ txSign(t.amount) }}{{ formatMoney(t.amount.replace('-', '')) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- /TAB cash -->

    <!-- TAB: Purchases -->
    <div v-if="tab === 'purchases'" class="card overflow-hidden">
      <div v-if="!purchases.length" class="py-12 text-center text-sm text-slate-500">
        Hali kirim yo'q. <button class="text-brand-600 hover:underline" @click="openPurchase()">Birinchi kirim qo'shing</button>
      </div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Sana</th>
            <th>Mahsulot</th>
            <th class="text-center">To'la</th>
            <th class="text-center">Bo'sh</th>
            <th class="text-right">Birlik narx</th>
            <th class="text-right">Jami</th>
            <th>Yetkazib beruvchi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in purchases" :key="p.id">
            <td class="text-xs text-slate-500 whitespace-nowrap">
              {{ dayjs(p.occurred_at).format("DD.MM.YYYY") }}
            </td>
            <td class="font-medium">{{ p.product_name }} <span class="text-xs text-slate-500">· {{ p.volume_liters }}L</span></td>
            <td class="text-center text-emerald-600 font-bold">{{ p.full_count || '—' }}</td>
            <td class="text-center text-slate-700 dark:text-slate-200">{{ p.empty_count || '—' }}</td>
            <td class="text-right text-sm">{{ formatMoney(p.unit_cost) }}</td>
            <td class="text-right font-bold text-rose-600">−{{ formatMoney(p.total_cost) }}</td>
            <td class="text-sm text-slate-600 dark:text-slate-400">{{ p.supplier || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- /TAB purchases -->

    <!-- Adjust dialog -->
    <AppDialog v-model:open="adjOpen" title="Ombor balansini tuzatish" max-width="max-w-md">
      <div class="space-y-3">
        <div class="text-sm text-slate-600 dark:text-slate-400">
          <span class="font-semibold text-slate-900 dark:text-slate-100">{{ adjForm.product_name }}</span>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              To'la (delta)
            </label>
            <input v-model="adjForm.full_delta" type="number" class="input" placeholder="+10, -2" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Bo'sh (delta)
            </label>
            <input v-model="adjForm.empty_delta" type="number" class="input" placeholder="+5" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Sabab (ixtiyoriy)
          </label>
          <input v-model="adjForm.reason" class="input" placeholder="Boshlang'ich balans / Yo'qotish / Refill..." />
        </div>
        <p class="text-xs text-slate-500 dark:text-slate-400">
          Musbat son qo'shadi, manfiy son ayiradi. <span class="kbd">+50</span> = 50 ta to'la
          qo'shish, <span class="kbd">-3</span> = 3 ta yo'qotish.
        </p>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="adjOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitAdjust">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Transfer dialog -->
    <AppDialog v-model:open="trOpen" :title="trTitle" max-width="max-w-md">
      <div class="space-y-3">
        <div class="text-sm text-slate-600 dark:text-slate-400">
          <span class="font-semibold text-slate-900 dark:text-slate-100">{{ trForm.product_name }}</span>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Haydovchi</label>
          <AppSelect v-model="trForm.driver_id" :options="driverOptions" placeholder="Tanlang" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">To'la</label>
            <input v-model="trForm.full_count" type="number" min="0" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Bo'sh</label>
            <input v-model="trForm.empty_count" type="number" min="0" class="input" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Izoh</label>
          <input v-model="trForm.reason" class="input" />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="trOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitTransfer">
          {{ trDir === "to" ? "Yuklash" : "Qaytarish" }}
        </button>
      </template>
    </AppDialog>

    <!-- Opening balance dialog -->
    <AppDialog v-model:open="openingOpen" title="Boshlang'ich balans" max-width="max-w-md">
      <div class="space-y-3">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Tizimga o'tish vaqtidagi joriy kassa balansini bir martalik kiritasiz.
          Keyin har bir kirim/chiqim avtomat hisoblanadi.
        </p>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Joriy summa (so'm)
          </label>
          <input v-model="openingForm.amount" type="number" min="0" class="input" placeholder="5000000" />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Izoh (ixtiyoriy)
          </label>
          <input v-model="openingForm.note" class="input" placeholder="Boshlang'ich kassa" />
        </div>
        <p class="text-[11px] text-slate-500">Diqqat: bu amal faqat 1 marta bajariladi.</p>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="openingOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitOpening">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Expense dialog -->
    <AppDialog v-model:open="expenseOpen" title="Xarajat qo'shish" max-width="max-w-md">
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Summa (so'm)
          </label>
          <input v-model="expenseForm.amount" type="number" min="0" class="input" placeholder="100000" />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Tavsif
          </label>
          <input v-model="expenseForm.description" class="input" placeholder="Yoqilg'i / Ish haqi / Reklama..." />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="expenseOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitExpense">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Manual cash dialog -->
    <AppDialog
      v-model:open="manualOpen"
      :title="manualForm.direction === 'in' ? 'Qo\'lda kirim' : 'Qo\'lda chiqim'"
      max-width="max-w-md"
    >
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Summa (so'm)
          </label>
          <input v-model="manualForm.amount" type="number" min="0" class="input" />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Tavsif
          </label>
          <input v-model="manualForm.description" class="input" placeholder="Sabab..." />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="manualOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitManual">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Purchase dialog -->
    <AppDialog v-model:open="purchaseOpen" title="Yangi mahsulot kirimi" max-width="max-w-lg">
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Mahsulot
          </label>
          <AppSelect v-model="purchaseForm.product_id" :options="productOptions" placeholder="Tanlang" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              To'la idishlar
            </label>
            <input v-model="purchaseForm.full_count" type="number" min="0" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Bo'sh idishlar
            </label>
            <input v-model="purchaseForm.empty_count" type="number" min="0" class="input" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
            Bir dona narxi (so'm)
          </label>
          <input v-model="purchaseForm.unit_cost" type="number" min="0" class="input" placeholder="15000" />
        </div>
        <div class="rounded-lg bg-slate-50 dark:bg-slate-800/50 p-3 flex items-baseline justify-between">
          <span class="text-xs text-slate-500 uppercase tracking-wide font-semibold">Jami xarajat</span>
          <span class="text-xl font-extrabold text-rose-600">−{{ formatMoney(purchaseTotal) }}</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Yetkazib beruvchi
            </label>
            <input v-model="purchaseForm.supplier" class="input" placeholder="Hayot Suv MChJ" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
              Izoh
            </label>
            <input v-model="purchaseForm.note" class="input" />
          </div>
        </div>
        <p class="text-[11px] text-slate-500">
          Bu summa kassadan ayiriladi va omborga {{ (parseInt(purchaseForm.full_count) || 0) + (parseInt(purchaseForm.empty_count) || 0) }} ta idish qo'shiladi.
        </p>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="purchaseOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitPurchase">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
