<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { PlusIcon, TrashIcon, ArrowLeftIcon } from "@heroicons/vue/20/solid";
import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
  ComboboxButton,
} from "@headlessui/vue";
import { ChevronUpDownIcon, CheckIcon } from "@heroicons/vue/20/solid";
import { customersApi } from "@/api/customers";
import { productsApi, type ProductStockSummary } from "@/api/products";
import { ordersApi } from "@/api/orders";
import { formatMoney } from "@/utils/format";
import { toast } from "@/lib/toast";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import type { AddressOut, CustomerOut, ProductOut, UUID } from "@/types/api";

const router = useRouter();
const saving = ref(false);

const customers = ref<CustomerOut[]>([]);
const customerQuery = ref("");
const selectedCustomer = ref<CustomerOut | null>(null);
const addresses = ref<AddressOut[]>([]);
const products = ref<ProductOut[]>([]);
const stocks = ref<Record<string, ProductStockSummary>>({});

const form = reactive<{
  address_id: UUID | null;
  items: { product_id: UUID; quantity: number }[];
  notes: string;
}>({
  address_id: null,
  items: [],
  notes: "",
});

async function searchCustomers(q: string) {
  const res = await customersApi.list({ q, page: 1, page_size: 20 });
  customers.value = res.items;
}

async function loadProducts() {
  const [list, stockList] = await Promise.all([
    productsApi.list({ only_active: true }),
    productsApi.stocks().catch(() => []),
  ]);
  products.value = list;
  stocks.value = Object.fromEntries(stockList.map((s) => [s.product_id, s]));
}

watch(selectedCustomer, async (c) => {
  form.address_id = null;
  addresses.value = [];
  if (c) {
    addresses.value = await customersApi.listAddresses(c.id);
    if (addresses.value.length === 1) {
      form.address_id = addresses.value[0].id;
    }
  }
});

onMounted(async () => {
  await Promise.all([searchCustomers(""), loadProducts()]);
});

function addLine() {
  if (!products.value.length) return;
  form.items.push({ product_id: products.value[0].id, quantity: 1 });
}

function removeLine(i: number) {
  form.items.splice(i, 1);
}

function incQty(i: number) {
  form.items[i].quantity = Math.min(100, form.items[i].quantity + 1);
}

function decQty(i: number) {
  form.items[i].quantity = Math.max(1, form.items[i].quantity - 1);
}

const total = computed(() => {
  let sum = 0;
  for (const it of form.items) {
    const p = products.value.find((x) => x.id === it.product_id);
    if (p?.current_price) sum += parseFloat(p.current_price) * it.quantity;
  }
  return sum;
});

const productOptions = computed(() =>
  products.value.map((p) => {
    const stock = stocks.value[p.id];
    const stockHint = p.is_returnable && stock
      ? ` · ombor: ${stock.available_full}`
      : "";
    return {
      value: p.id,
      label: `${p.name} — ${formatMoney(p.current_price)}${stockHint}`,
    };
  }),
);

interface StockShort {
  product_name: string;
  required: number;
  available: number;
}

const stockShortfalls = computed<StockShort[]>(() => {
  const required: Record<string, number> = {};
  for (const it of form.items) {
    required[it.product_id] = (required[it.product_id] || 0) + it.quantity;
  }
  const out: StockShort[] = [];
  for (const [pid, need] of Object.entries(required)) {
    const product = products.value.find((p) => p.id === pid);
    if (!product?.is_returnable) continue;
    const s = stocks.value[pid];
    if (!s) continue;
    if (s.available_full < need) {
      out.push({
        product_name: `${product.name} ${product.volume_liters}L`,
        required: need,
        available: s.available_full,
      });
    }
  }
  return out;
});

const addressOptions = computed(() =>
  addresses.value.map((a) => ({
    value: a.id,
    label: `${a.label} · ${a.address_text}`,
  })),
);

async function onSubmit() {
  if (!selectedCustomer.value || !form.address_id || form.items.length === 0) {
    toast.warning("Mijoz, manzil va kamida 1 ta mahsulot tanlang");
    return;
  }
  saving.value = true;
  try {
    const order = await ordersApi.create({
      customer_id: selectedCustomer.value.id,
      address_id: form.address_id,
      items: form.items,
      notes: form.notes || undefined,
    });
    toast.success(`Buyurtma #${order.number} yaratildi`);
    router.push({ name: "order-detail", params: { id: order.id } });
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="space-y-6 max-w-4xl mx-auto">
    <PageHeader title="Yangi buyurtma" subtitle="Mijoz, manzil va mahsulotlarni tanlang">
      <template #actions>
        <button class="btn-secondary" @click="router.back()">
          <ArrowLeftIcon class="h-4 w-4" />
          Orqaga
        </button>
      </template>
    </PageHeader>

    <div class="card p-6 space-y-5">
      <!-- Customer combobox -->
      <div>
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
          Mijoz
        </label>
        <Combobox v-model="selectedCustomer" @update:model-value="customerQuery = $event?.full_name || ''">
          <div class="relative">
            <ComboboxInput
              class="input pr-10"
              placeholder="Ism yoki telefon bo'yicha qidirish..."
              :display-value="(c: any) => c ? `${c.full_name} — ${c.phone}` : ''"
              @change="searchCustomers($event.target.value)"
            />
            <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-3">
              <ChevronUpDownIcon class="h-5 w-5 text-slate-400" />
            </ComboboxButton>
            <ComboboxOptions
              class="absolute z-[60] mt-1 max-h-60 w-full overflow-auto rounded-lg bg-white dark:bg-slate-800 py-1 text-sm shadow-lg ring-1 ring-slate-200 dark:ring-slate-700"
            >
              <ComboboxOption
                v-for="c in customers"
                :key="c.id"
                :value="c"
                v-slot="{ active, selected }"
                as="template"
              >
                <li
                  :class="[
                    'relative cursor-pointer select-none px-4 py-2 flex items-center justify-between',
                    active ? 'bg-brand-50 text-brand-900 dark:bg-brand-950/60 dark:text-brand-200' : 'text-slate-700 dark:text-slate-200',
                  ]"
                >
                  <div>
                    <div class="font-medium">{{ c.full_name }}</div>
                    <div class="text-xs opacity-60">{{ c.phone }}</div>
                  </div>
                  <CheckIcon v-if="selected" class="h-4 w-4 text-brand-600" />
                </li>
              </ComboboxOption>
              <div v-if="customers.length === 0" class="px-4 py-2 text-slate-500 text-sm">
                Topilmadi
              </div>
            </ComboboxOptions>
          </div>
        </Combobox>
      </div>

      <!-- Address -->
      <div v-if="selectedCustomer">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
          Manzil
        </label>
        <AppSelect
          v-if="addresses.length"
          v-model="form.address_id"
          :options="addressOptions"
          placeholder="Manzil tanlash"
        />
        <div
          v-else
          class="rounded-lg bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 px-4 py-3 text-sm"
        >
          Mijozda manzil yo'q. Avval mijoz sahifasida manzil qo'shing.
        </div>
      </div>

      <!-- Items -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
            Mahsulotlar
          </label>
          <button class="btn-ghost btn-sm" @click="addLine">
            <PlusIcon class="h-4 w-4" />
            Qator qo'shish
          </button>
        </div>

        <div v-if="!form.items.length" class="rounded-lg border-2 border-dashed border-slate-200 dark:border-slate-800 py-8 text-center">
          <p class="text-sm text-slate-500">Mahsulot qatorini qo'shing</p>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="(it, i) in form.items"
            :key="i"
            class="flex items-center gap-2 rounded-lg bg-slate-50 dark:bg-slate-800/50 p-2"
          >
            <div class="flex-1">
              <AppSelect v-model="it.product_id" :options="productOptions" />
            </div>
            <div class="flex items-center gap-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-1">
              <button type="button" class="btn-ghost !p-1 text-slate-700 dark:text-slate-200" @click="decQty(i)">−</button>
              <span class="min-w-[2.5rem] text-center font-medium text-slate-900 dark:text-slate-100">{{ it.quantity }}</span>
              <button type="button" class="btn-ghost !p-1 text-slate-700 dark:text-slate-200" @click="incQty(i)">+</button>
            </div>
            <button type="button" class="btn-ghost !p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40" @click="removeLine(i)">
              <TrashIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div>
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
          Izoh
        </label>
        <textarea v-model="form.notes" rows="2" class="input resize-none" placeholder="Masalan: 14:00-18:00 ga yetkazish" />
      </div>

      <!-- Stock shortfall warning -->
      <div
        v-if="stockShortfalls.length"
        class="rounded-xl border border-rose-200 dark:border-rose-900/50 bg-rose-50 dark:bg-rose-950/30 p-4 space-y-1.5"
      >
        <p class="text-sm font-bold text-rose-900 dark:text-rose-200">
          ⚠️ Omborda yetarli idish yo'q
        </p>
        <ul class="text-sm text-rose-800 dark:text-rose-300 space-y-0.5">
          <li v-for="s in stockShortfalls" :key="s.product_name">
            {{ s.product_name }}: kerak <strong>{{ s.required }}</strong>,
            mavjud <strong>{{ s.available }}</strong>
            <span class="text-rose-600">(
              <RouterLink to="/app/products" class="underline font-semibold">Mahsulotlar</RouterLink>
              sahifasidan kirim qiling)
            </span>
          </li>
        </ul>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between border-t border-slate-200 dark:border-slate-800 pt-5">
        <div>
          <p class="text-sm text-slate-500 dark:text-slate-400">Jami</p>
          <p class="text-2xl font-semibold text-slate-900 dark:text-slate-100">{{ formatMoney(total) }}</p>
        </div>
        <button class="btn-primary" :disabled="saving || stockShortfalls.length > 0" @click="onSubmit">
          <svg v-if="saving" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
            <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
          </svg>
          Yaratish
        </button>
      </div>
    </div>
  </div>
</template>
