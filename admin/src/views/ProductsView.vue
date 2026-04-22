<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import {
  PlusIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CubeIcon,
  TrashIcon,
} from "@heroicons/vue/20/solid";
import { productsApi } from "@/api/products";
import { formatDateTime, formatMoney } from "@/utils/format";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { PriceOut, ProductOut } from "@/types/api";

const confirm = useConfirm();

const items = ref<ProductOut[]>([]);
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

async function load() {
  loading.value = true;
  try {
    items.value = await productsApi.list();
  } finally {
    loading.value = false;
  }
}

onMounted(load);

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
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Mahsulotlar" subtitle="Katalog va narx tarixi">
      <template #actions>
        <button class="btn-primary" @click="newOpen = true">
          <PlusIcon class="h-4 w-4" />
          Yangi mahsulot
        </button>
      </template>
    </PageHeader>

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

        <div class="mt-4 flex items-center gap-2">
          <AppBadge v-if="p.is_returnable" variant="success">Qaytariladigan</AppBadge>
          <AppBadge v-else variant="neutral">Bir martalik</AppBadge>
          <AppBadge v-if="!p.is_active" variant="danger">Nofaol</AppBadge>
        </div>
      </div>
    </div>

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
  </div>
</template>
