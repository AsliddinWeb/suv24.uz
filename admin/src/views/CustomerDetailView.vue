<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeftIcon, PlusIcon, QrCodeIcon, TrashIcon } from "@heroicons/vue/20/solid";
import { customersApi } from "@/api/customers";
import { ordersApi } from "@/api/orders";
import { formatDateTime, formatMoney } from "@/utils/format";
import { orderStatusLabel, orderStatusType, segmentLabel, segmentType } from "@/utils/status";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import type { AddressOut, CustomerOut, OrderOut } from "@/types/api";

const route = useRoute();
const router = useRouter();
const confirm = useConfirm();

const customer = ref<CustomerOut | null>(null);
const addresses = ref<AddressOut[]>([]);
const recentOrders = ref<OrderOut[]>([]);

const addAddrOpen = ref(false);
const addrForm = ref<{ label: string; address_text: string; lat: string; lng: string }>({
  label: "Uy",
  address_text: "",
  lat: "",
  lng: "",
});

async function load() {
  const id = route.params.id as string;
  const [c, a, o] = await Promise.all([
    customersApi.get(id),
    customersApi.listAddresses(id),
    ordersApi.list({ customer_id: id, page: 1, page_size: 20 }),
  ]);
  customer.value = c;
  addresses.value = a;
  recentOrders.value = o.items;
}

onMounted(load);

async function addAddress() {
  if (!customer.value || !addrForm.value.address_text.trim()) {
    toast.warning("Manzil matni majburiy");
    return;
  }
  const lat = addrForm.value.lat.trim() ? parseFloat(addrForm.value.lat) : undefined;
  const lng = addrForm.value.lng.trim() ? parseFloat(addrForm.value.lng) : undefined;
  if ((lat !== undefined && Number.isNaN(lat)) || (lng !== undefined && Number.isNaN(lng))) {
    toast.warning("Koordinatalar noto'g'ri");
    return;
  }
  await customersApi.createAddress(customer.value.id, {
    label: addrForm.value.label,
    address_text: addrForm.value.address_text,
    lat,
    lng,
  });
  addAddrOpen.value = false;
  addrForm.value = { label: "Uy", address_text: "", lat: "", lng: "" };
  await load();
  toast.success("Manzil qo'shildi");
}

function openYandexMaps() {
  window.open("https://yandex.uz/maps/", "_blank");
}

function pickCurrentLocation() {
  if (!navigator.geolocation) {
    toast.warning("Brauzer geolokatsiyani qo'llab-quvvatlamaydi");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      addrForm.value.lat = pos.coords.latitude.toFixed(7);
      addrForm.value.lng = pos.coords.longitude.toFixed(7);
      toast.success("Joriy joylashuv olindi");
    },
    () => toast.error("Joylashuvni olib bo'lmadi"),
    { enableHighAccuracy: true, timeout: 10000 },
  );
}

async function onDeleteAddress(a: AddressOut) {
  if (!customer.value) return;
  const ok = await confirm({
    title: "Manzilni o'chirish",
    description: `"${a.label}: ${a.address_text}" manzilini o'chirmoqchimisiz?`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await customersApi.removeAddress(customer.value.id, a.id);
  toast.success("Manzil o'chirildi");
  load();
}

async function onDeleteCustomer() {
  if (!customer.value) return;
  const ok = await confirm({
    title: "Mijozni o'chirish",
    description: `${customer.value.full_name} mijozini ro'yxatdan olib tashlamoqchimisiz?`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await customersApi.remove(customer.value.id);
  toast.success("O'chirildi");
  router.push("/app/customers");
}

function qrUrl(token: string) {
  return `https://order.example.uz/q/${token}`;
}
</script>

<template>
  <div v-if="customer" class="space-y-6">
    <PageHeader :title="customer.full_name" :subtitle="customer.phone">
      <template #actions>
        <button class="btn-secondary" @click="router.back()">
          <ArrowLeftIcon class="h-4 w-4" />
          Orqaga
        </button>
        <button class="btn-danger" @click="onDeleteCustomer">
          <TrashIcon class="h-4 w-4" />
          O'chirish
        </button>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card p-5">
        <p class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Segment</p>
        <div class="mt-2">
          <AppBadge :variant="segmentType[customer.segment]" class="!text-sm !px-3 !py-1.5">
            {{ segmentLabel[customer.segment] }}
          </AppBadge>
        </div>
      </div>
      <div class="card p-5">
        <p class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Qarz</p>
        <p
          class="mt-2 text-2xl font-semibold"
          :class="parseFloat(customer.balance) > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'"
        >
          {{ formatMoney(customer.balance) }}
        </p>
      </div>
      <div class="card p-5">
        <p class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Idish qarzi</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-100">
          {{ customer.bottle_debt }} <span class="text-sm font-normal text-slate-500">ta</span>
        </p>
      </div>
    </div>

    <div class="card overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Manzillar</h3>
        <button class="btn-ghost btn-sm" @click="addAddrOpen = true">
          <PlusIcon class="h-4 w-4" />
          Qo'shish
        </button>
      </div>
      <div v-if="!addresses.length" class="py-8 text-center text-sm text-slate-500">
        Manzillar yo'q
      </div>
      <ul v-else class="divide-y divide-slate-200 dark:divide-slate-800">
        <li v-for="a in addresses" :key="a.id" class="px-6 py-4 flex items-center gap-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400">
            <QrCodeIcon class="h-5 w-5" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-sm font-medium text-slate-900 dark:text-slate-100">{{ a.label }}</span>
              <AppBadge v-if="a.is_active" variant="success" class="!py-0.5 !px-2 !text-[10px]">Aktiv</AppBadge>
              <AppBadge v-if="a.lat && a.lng" variant="info" class="!py-0.5 !px-2 !text-[10px]">📍 GPS</AppBadge>
              <AppBadge v-else variant="warning" class="!py-0.5 !px-2 !text-[10px]">📍 yo'q</AppBadge>
            </div>
            <p class="text-sm text-slate-500 dark:text-slate-400 truncate">{{ a.address_text }}</p>
            <p v-if="a.lat && a.lng" class="text-[10px] text-slate-400 mt-0.5 font-mono">{{ a.lat }}, {{ a.lng }}</p>
          </div>
          <a :href="qrUrl(a.qr_token)" target="_blank" class="text-xs text-brand-600 dark:text-brand-400 hover:underline truncate max-w-[200px]">
            {{ qrUrl(a.qr_token) }}
          </a>
          <button
            class="btn-ghost !p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40"
            title="O'chirish"
            @click="onDeleteAddress(a)"
          >
            <TrashIcon class="h-4 w-4" />
          </button>
        </li>
      </ul>
    </div>

    <div class="card overflow-hidden">
      <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
        <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">So'nggi buyurtmalar</h3>
      </div>
      <div v-if="!recentOrders.length" class="py-8 text-center text-sm text-slate-500">
        Buyurtma yo'q
      </div>
      <div v-else class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Status</th>
              <th>Summa</th>
              <th>Sana</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="o in recentOrders"
              :key="o.id"
              class="cursor-pointer"
              @click="router.push({ name: 'order-detail', params: { id: o.id } })"
            >
              <td class="font-semibold text-brand-600 dark:text-brand-400">#{{ o.number }}</td>
              <td><AppBadge :variant="orderStatusType[o.status]">{{ orderStatusLabel[o.status] }}</AppBadge></td>
              <td class="font-medium">{{ formatMoney(o.total) }}</td>
              <td class="text-slate-500">{{ formatDateTime(o.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <AppDialog v-model:open="addAddrOpen" title="Manzil qo'shish" max-width="max-w-xl">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Tur (label)</label>
          <input v-model="addrForm.label" class="input" placeholder="Uy / Ofis / ..." />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Manzil matni</label>
          <textarea v-model="addrForm.address_text" rows="3" class="input resize-none" placeholder="Toshkent, Chilonzor..." />
        </div>
        <div class="rounded-lg bg-brand-50 dark:bg-brand-950/30 border border-brand-100 dark:border-brand-900/50 p-4">
          <div class="flex items-center justify-between mb-3">
            <div>
              <p class="text-sm font-semibold text-brand-900 dark:text-brand-200">📍 GPS koordinatalari</p>
              <p class="text-xs text-brand-700 dark:text-brand-400 mt-0.5">
                Haydovchi xaritada marshrut chizishi uchun
              </p>
            </div>
            <div class="flex gap-2">
              <button type="button" class="btn-secondary btn-sm" @click="pickCurrentLocation" title="Joriy joy">
                📍 Joriy
              </button>
              <button type="button" class="btn-secondary btn-sm" @click="openYandexMaps" title="Yandex Maps">
                🗺 Maps
              </button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Kenglik (lat)</label>
              <input v-model="addrForm.lat" class="input input-sm font-mono" placeholder="41.2995" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Uzunlik (lng)</label>
              <input v-model="addrForm.lng" class="input input-sm font-mono" placeholder="69.2401" />
            </div>
          </div>
          <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Yandex Maps'da nuqtaga sichqonchani bosib "Joyni ulashish" → koordinatalarni ko'chiring
          </p>
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="addAddrOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="addAddress">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
