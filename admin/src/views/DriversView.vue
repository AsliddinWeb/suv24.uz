<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import {
  PlusIcon,
  TruckIcon,
  CubeIcon,
  TrashIcon,
  EllipsisHorizontalIcon,
} from "@heroicons/vue/20/solid";
import { driversApi } from "@/api/drivers";
import { productsApi } from "@/api/products";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { BottleBalanceWithProduct, DriverOut, ProductOut, UUID } from "@/types/api";

const confirm = useConfirm();

const drivers = ref<DriverOut[]>([]);
const products = ref<ProductOut[]>([]);
const loading = ref(false);

const bottlesOpen = ref(false);
const bottlesFor = ref<DriverOut | null>(null);
const balances = ref<BottleBalanceWithProduct[]>([]);

const adjustOpen = ref(false);
const adjForm = reactive<{
  product_id: UUID | null;
  full_delta: number;
  empty_delta: number;
}>({ product_id: null, full_delta: 0, empty_delta: 0 });

async function load() {
  loading.value = true;
  try {
    const [d, p] = await Promise.all([
      driversApi.list(),
      productsApi.list({ only_active: true }),
    ]);
    drivers.value = d;
    products.value = p.filter((x) => x.is_returnable);
  } finally {
    loading.value = false;
  }
}

onMounted(load);

async function showBottles(d: DriverOut) {
  bottlesFor.value = d;
  balances.value = await driversApi.bottles(d.id);
  bottlesOpen.value = true;
}

function openAdjust() {
  adjForm.product_id = products.value[0]?.id || null;
  adjForm.full_delta = 0;
  adjForm.empty_delta = 0;
  adjustOpen.value = true;
}

async function submitAdjust() {
  if (!bottlesFor.value || !adjForm.product_id) return;
  if (adjForm.full_delta === 0 && adjForm.empty_delta === 0) {
    toast.warning("Delta 0 bo'lmasligi kerak");
    return;
  }
  await driversApi.adjustBottles(bottlesFor.value.id, {
    product_id: adjForm.product_id,
    full_delta: adjForm.full_delta,
    empty_delta: adjForm.empty_delta,
  });
  adjustOpen.value = false;
  balances.value = await driversApi.bottles(bottlesFor.value.id);
  toast.success("Yangilandi");
}

async function onDelete(d: DriverOut) {
  const ok = await confirm({
    title: "Haydovchini o'chirish",
    description: `${d.full_name}${d.vehicle_plate ? " (" + d.vehicle_plate + ")" : ""} haydovchisini o'chirmoqchimisiz?`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await driversApi.remove(d.id);
  toast.success("O'chirildi");
  load();
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Haydovchilar" subtitle="Haydovchilar va ularning idish balansi" />

    <EmptyState v-if="!loading && !drivers.length" title="Haydovchi yo'q" />

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="d in drivers" :key="d.id" class="card p-5">
        <div class="flex items-start gap-3">
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white font-semibold">
            {{ d.full_name.slice(0, 1).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-slate-900 dark:text-slate-100 truncate">{{ d.full_name }}</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ d.phone }}</p>
          </div>
          <AppBadge :variant="d.is_active ? 'success' : 'neutral'">
            {{ d.is_active ? "Faol" : "Nofaol" }}
          </AppBadge>
          <AppMenu>
            <AppMenuItem @click="showBottles(d)">
              <CubeIcon class="h-4 w-4" />
              Idish balansi
            </AppMenuItem>
            <AppMenuItem tone="danger" @click="onDelete(d)">
              <TrashIcon class="h-4 w-4" />
              O'chirish
            </AppMenuItem>
          </AppMenu>
        </div>

        <div v-if="d.vehicle_plate" class="mt-3 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
          <TruckIcon class="h-4 w-4" />
          <span class="font-medium">{{ d.vehicle_plate }}</span>
        </div>

        <button class="btn-secondary btn-sm w-full mt-4" @click="showBottles(d)">
          <CubeIcon class="h-4 w-4" />
          Idish balansi
        </button>
      </div>
    </div>

    <AppDialog v-model:open="bottlesOpen" :title="`${bottlesFor?.full_name} — idish balansi`" max-width="max-w-xl">
      <EmptyState v-if="!balances.length" title="Balans bo'sh" description="Ombor kursidan birinchi marta yuklang" />

      <div v-else class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Mahsulot</th>
              <th class="text-center">To'la</th>
              <th class="text-center">Bo'sh</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in balances" :key="b.id">
              <td class="font-medium text-slate-900 dark:text-slate-100">
                {{ b.product_name }} <span class="text-slate-400">· {{ b.volume_liters }}L</span>
              </td>
              <td class="text-center font-semibold text-emerald-600 dark:text-emerald-400">{{ b.full_count }}</td>
              <td class="text-center text-slate-500">{{ b.empty_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <template #footer>
        <button class="btn-secondary" @click="bottlesOpen = false">Yopish</button>
        <button class="btn-primary" @click="openAdjust">
          <PlusIcon class="h-4 w-4" />
          Balansni tuzatish
        </button>
      </template>
    </AppDialog>

    <AppDialog v-model:open="adjustOpen" title="Balansni tuzatish">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Mahsulot</label>
          <AppSelect
            v-model="adjForm.product_id"
            :options="products.map((p) => ({ value: p.id, label: `${p.name} · ${p.volume_liters}L` }))"
            placeholder="Tanlang"
          />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">To'la (delta)</label>
            <input v-model.number="adjForm.full_delta" type="number" class="input" placeholder="+10, -2" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Bo'sh (delta)</label>
            <input v-model.number="adjForm.empty_delta" type="number" class="input" placeholder="+3" />
          </div>
        </div>
        <p class="text-xs text-slate-500">
          Musbat = qo'shish, manfiy = olib tashlash. Masalan ombordan 10 to'la olish — <span class="kbd">+10</span> to'la.
        </p>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="adjustOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitAdjust">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
