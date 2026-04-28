<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  CubeIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  PencilSquareIcon,
  ArrowPathIcon,
  ScaleIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import {
  warehouseApi,
  type WarehouseStock,
  type WarehouseSummary,
} from "@/api/warehouse";
import { driversApi } from "@/api/drivers";
import { toast } from "@/lib/toast";
import dayjs from "dayjs";
import type { DriverOut } from "@/types/api";

const stocks = ref<WarehouseStock[]>([]);
const summary = ref<WarehouseSummary[]>([]);
const drivers = ref<DriverOut[]>([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const [s, sum, d] = await Promise.all([
      warehouseApi.list(),
      warehouseApi.summary(),
      driversApi.list(),
    ]);
    stocks.value = s;
    summary.value = sum;
    drivers.value = d.filter((x) => x.is_active);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

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
    <PageHeader title="Ombor" subtitle="To'la va bo'sh idishlar balansi">
      <template #actions>
        <button class="btn-ghost !p-2" :disabled="loading" @click="load" title="Yangilash">
          <ArrowPathIcon :class="['h-5 w-5', loading && 'animate-spin']" />
        </button>
      </template>
    </PageHeader>

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
  </div>
</template>
