<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  PlusIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CubeIcon,
  TrashIcon,
  ArchiveBoxArrowDownIcon,
} from "@heroicons/vue/20/solid";
import { productsApi, type ProductStockSummary } from "@/api/products";
import { purchasesApi, cashApi, type CashSnapshot } from "@/api/warehouse";
import { formatDateTime, formatMoney } from "@/utils/format";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { PriceOut, ProductOut, UUID } from "@/types/api";

const confirm = useConfirm();

const items = ref<ProductOut[]>([]);
const stocks = ref<Record<string, ProductStockSummary>>({});
const cash = ref<CashSnapshot | null>(null);
const loading = ref(false);

const newOpen = ref(false);
const form = reactive({
  name: "",
  volume_liters: 19,
  is_returnable: true,
  initial_price: "",
});

const priceOpen = ref(false);
const pricingProduct = ref<ProductOut | null>(null);
const newPrice = ref("");

const historyOpen = ref(false);
const historyItems = ref<PriceOut[]>([]);
const historyFor = ref<ProductOut | null>(null);

// Purchase (Kirim) dialog
const purchaseOpen = ref(false);
const purchaseFor = ref<ProductOut | null>(null);
const purchaseForm = reactive({
  full_count: "0",
  empty_count: "0",
  unit_cost: "0",
  supplier: "",
  note: "",
});

const purchaseTotal = computed(() => {
  const fc = parseInt(purchaseForm.full_count || "0", 10) || 0;
  const ec = parseInt(purchaseForm.empty_count || "0", 10) || 0;
  const uc = parseFloat(purchaseForm.unit_cost || "0") || 0;
  return (fc + ec) * uc;
});

async function load() {
  loading.value = true;
  try {
    const [list, stockList, cashSnap] = await Promise.all([
      productsApi.list(),
      productsApi.stocks(),
      cashApi.snapshot().catch(() => null),
    ]);
    items.value = list;
    stocks.value = Object.fromEntries(stockList.map((s) => [s.product_id, s]));
    cash.value = cashSnap;
  } finally {
    loading.value = false;
  }
}

onMounted(load);

function stockFor(id: UUID): ProductStockSummary | undefined {
  return stocks.value[id];
}

async function onCreate() {
  if (!form.name || !form.initial_price) {
    toast.warning("Nom va narx majburiy");
    return;
  }
  await productsApi.create({ ...form });
  newOpen.value = false;
  form.name = "";
  form.initial_price = "";
  form.volume_liters = 19;
  form.is_returnable = true;
  load();
  toast.success("Yaratildi");
}

function openPrice(p: ProductOut) {
  pricingProduct.value = p;
  newPrice.value = p.current_price || "";
  priceOpen.value = true;
}

async function onSavePrice() {
  if (!pricingProduct.value || !newPrice.value) return;
  await productsApi.setPrice(pricingProduct.value.id, newPrice.value);
  priceOpen.value = false;
  load();
  toast.success("Narx yangilandi");
}

async function openHistory(p: ProductOut) {
  historyFor.value = p;
  historyItems.value = await productsApi.priceHistory(p.id);
  historyOpen.value = true;
}

async function onDelete(p: ProductOut) {
  const ok = await confirm({
    title: "Mahsulotni o'chirish",
    description: `"${p.name}" (${p.volume_liters}L) mahsulotini o'chirmoqchimisiz?`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await productsApi.remove(p.id);
  toast.success("O'chirildi");
  load();
}

function openPurchase(p: ProductOut) {
  purchaseFor.value = p;
  purchaseForm.full_count = "0";
  purchaseForm.empty_count = "0";
  purchaseForm.unit_cost = "0";
  purchaseForm.supplier = "";
  purchaseForm.note = "";
  purchaseOpen.value = true;
}

async function submitPurchase() {
  if (!purchaseFor.value) return;
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
      product_id: purchaseFor.value.id,
      full_count: fc,
      empty_count: ec,
      unit_cost: uc.toString(),
      supplier: purchaseForm.supplier || null,
      note: purchaseForm.note || null,
    });
    toast.success("Kirim yozildi");
    purchaseOpen.value = false;
    await load();
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Mahsulotlar" subtitle="Katalog, narx tarixi va ombor balansi">
      <template #actions>
        <button class="btn-primary" @click="newOpen = true">
          <PlusIcon class="h-4 w-4" />
          Yangi mahsulot
        </button>
      </template>
    </PageHeader>

    <!-- Cash hint -->
    <div
      v-if="cash"
      class="card p-4 flex items-center gap-3 bg-gradient-to-r from-brand-50 to-indigo-50 dark:from-brand-950/30 dark:to-indigo-950/30 border-brand-200 dark:border-brand-900/40"
    >
      <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500 text-white shrink-0">
        <CurrencyDollarIcon class="h-5 w-5" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-xs text-slate-500 dark:text-slate-400">Kassada</p>
        <p class="text-lg font-bold text-slate-900 dark:text-slate-100">
          {{ formatMoney(cash.account.balance) }}
        </p>
      </div>
      <RouterLink to="/app/warehouse" class="btn-ghost btn-sm">Ombor →</RouterLink>
    </div>

    <EmptyState v-if="!loading && !items.length" title="Mahsulot yo'q" />

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="p in items" :key="p.id" class="card p-5 flex flex-col">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/50 dark:text-brand-400">
              <CubeIcon class="h-5 w-5" />
            </div>
            <div>
              <h3 class="font-semibold text-slate-900 dark:text-slate-100">{{ p.name }}</h3>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ p.volume_liters }}L</p>
            </div>
          </div>
          <AppMenu>
            <AppMenuItem v-if="p.is_returnable" @click="openPurchase(p)">
              <ArchiveBoxArrowDownIcon class="h-4 w-4" />
              Yangi kirim
            </AppMenuItem>
            <AppMenuItem @click="openPrice(p)">
              <CurrencyDollarIcon class="h-4 w-4" />
              Narx o'zgartirish
            </AppMenuItem>
            <AppMenuItem @click="openHistory(p)">
              <ClockIcon class="h-4 w-4" />
              Narx tarixi
            </AppMenuItem>
            <AppMenuItem tone="danger" @click="onDelete(p)">
              <TrashIcon class="h-4 w-4" />
              O'chirish
            </AppMenuItem>
          </AppMenu>
        </div>

        <div class="mt-4">
          <p class="text-xs text-slate-500 dark:text-slate-400">Hozirgi narx</p>
          <p class="text-2xl font-semibold text-slate-900 dark:text-slate-100">
            {{ formatMoney(p.current_price) }}
          </p>
        </div>

        <!-- Stock summary -->
        <div
          v-if="p.is_returnable"
          class="mt-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-gradient-to-br from-slate-50 to-slate-100/50 dark:from-slate-800/60 dark:to-slate-800/30 p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <p class="text-[11px] font-bold uppercase tracking-wider text-slate-500">
              📦 Ombor balansi
            </p>
            <span
              :class="[
                'text-xs font-bold px-2 py-0.5 rounded-full',
                (stockFor(p.id)?.available_full ?? 0) > 10
                  ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400'
                  : (stockFor(p.id)?.available_full ?? 0) > 0
                    ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400'
                    : 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400',
              ]"
            >
              {{ stockFor(p.id)?.available_full ?? 0 }} ta sotish uchun
            </span>
          </div>

          <div class="grid grid-cols-2 gap-3 mb-3">
            <div class="rounded-xl bg-white dark:bg-slate-900/50 p-3 border border-slate-200/50 dark:border-slate-800/50">
              <p class="text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-1">Omborda</p>
              <div class="flex items-baseline gap-1">
                <span class="text-xl font-extrabold text-emerald-600">{{ stockFor(p.id)?.warehouse_full ?? 0 }}</span>
                <span class="text-[10px] text-slate-500">to'la</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">
                + <span class="font-bold text-slate-700 dark:text-slate-300">{{ stockFor(p.id)?.warehouse_empty ?? 0 }}</span> bo'sh
              </p>
            </div>
            <div class="rounded-xl bg-white dark:bg-slate-900/50 p-3 border border-slate-200/50 dark:border-slate-800/50">
              <p class="text-[10px] font-semibold uppercase tracking-wide text-slate-500 mb-1">Haydovchilarda</p>
              <div class="flex items-baseline gap-1">
                <span class="text-xl font-extrabold text-brand-600">{{ stockFor(p.id)?.drivers_full ?? 0 }}</span>
                <span class="text-[10px] text-slate-500">to'la</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">
                + <span class="font-bold text-slate-700 dark:text-slate-300">{{ stockFor(p.id)?.drivers_empty ?? 0 }}</span> bo'sh
              </p>
            </div>
          </div>

          <button
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 text-white font-bold shadow-md shadow-brand-500/25 hover:shadow-lg hover:shadow-brand-500/40 hover:-translate-y-0.5 transition-all"
            @click="openPurchase(p)"
          >
            <ArchiveBoxArrowDownIcon class="h-5 w-5" />
            Yangi kirim qo'shish
          </button>
        </div>

        <div class="mt-4 flex items-center gap-2 flex-wrap">
          <AppBadge v-if="p.is_returnable" variant="success">Qaytariladigan</AppBadge>
          <AppBadge v-else variant="neutral">Bir martalik</AppBadge>
          <AppBadge v-if="!p.is_active" variant="danger">Nofaol</AppBadge>
        </div>
      </div>
    </div>

    <!-- New product dialog -->
    <AppDialog v-model:open="newOpen" title="Yangi mahsulot">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Nom</label>
          <input v-model="form.name" class="input" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Hajm (L)</label>
            <input v-model.number="form.volume_liters" type="number" min="1" max="100" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Boshlang'ich narx</label>
            <input v-model="form.initial_price" type="number" class="input" />
          </div>
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="form.is_returnable" type="checkbox" class="rounded text-brand-600" />
          <span class="text-slate-700 dark:text-slate-300">Qaytariladigan idish</span>
        </label>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="newOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="onCreate">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Price dialog -->
    <AppDialog v-model:open="priceOpen" :title="`Narx: ${pricingProduct?.name}`">
      <div class="space-y-3">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Hozirgi: {{ formatMoney(pricingProduct?.current_price) }}
        </p>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Yangi narx (so'm)</label>
          <input v-model="newPrice" type="number" class="input" />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="priceOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="onSavePrice">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Price history -->
    <AppDialog v-model:open="historyOpen" :title="`Narx tarixi: ${historyFor?.name}`" max-width="max-w-2xl">
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Narx</th>
              <th>Dan</th>
              <th>Gacha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in historyItems" :key="h.id">
              <td class="font-medium text-slate-900 dark:text-slate-100">{{ formatMoney(h.price) }}</td>
              <td class="text-slate-500">{{ formatDateTime(h.valid_from) }}</td>
              <td>
                <span v-if="h.valid_to" class="text-slate-500">{{ formatDateTime(h.valid_to) }}</span>
                <AppBadge v-else variant="success">Hozirgi</AppBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppDialog>

    <!-- Purchase (Kirim) dialog -->
    <AppDialog v-model:open="purchaseOpen" :title="`Kirim: ${purchaseFor?.name} ${purchaseFor?.volume_liters}L`" max-width="max-w-lg">
      <div class="space-y-3">
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
          Bu summa kassadan ayiriladi va omborga
          {{ (parseInt(purchaseForm.full_count) || 0) + (parseInt(purchaseForm.empty_count) || 0) }} ta idish qo'shiladi.
        </p>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="purchaseOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitPurchase">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
