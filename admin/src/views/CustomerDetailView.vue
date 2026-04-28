<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  PencilSquareIcon,
  MapPinIcon,
} from "@heroicons/vue/20/solid";
import { customersApi } from "@/api/customers";
import { ordersApi } from "@/api/orders";
import { formatDateTime, formatMoney } from "@/utils/format";
import { orderStatusLabel, orderStatusType, segmentLabel, segmentType } from "@/utils/status";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import type { AddressOut, CustomerOut, OrderOut } from "@/types/api";

const route = useRoute();
const router = useRouter();
const confirm = useConfirm();

const customer = ref<CustomerOut | null>(null);
const addresses = ref<AddressOut[]>([]);
const recentOrders = ref<OrderOut[]>([]);

// Single dialog used for both add and edit
const addrDialogOpen = ref(false);
const editingAddrId = ref<string | null>(null);
const addrForm = ref<{
  label: string;
  address_text: string;
  lat: string;
  lng: string;
  is_active: boolean;
}>({
  label: "Uy",
  address_text: "",
  lat: "",
  lng: "",
  is_active: true,
});
const fetchingGeo = ref(false);

const dialogTitle = computed(() =>
  editingAddrId.value ? "Manzilni tahrirlash" : "Manzil qo'shish",
);

const previewMapUrl = computed(() => {
  const lat = parseFloat(addrForm.value.lat);
  const lng = parseFloat(addrForm.value.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  // Yandex static maps embed (no API key) — shows a pin
  return `https://yandex.com/map-widget/v1/?ll=${lng},${lat}&z=16&pt=${lng},${lat},pm2rdm`;
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

function openAdd() {
  editingAddrId.value = null;
  addrForm.value = { label: "Uy", address_text: "", lat: "", lng: "", is_active: true };
  addrDialogOpen.value = true;
}

function openEdit(a: AddressOut) {
  editingAddrId.value = a.id;
  addrForm.value = {
    label: a.label || "",
    address_text: a.address_text || "",
    lat: a.lat ? String(a.lat) : "",
    lng: a.lng ? String(a.lng) : "",
    is_active: a.is_active,
  };
  addrDialogOpen.value = true;
}

async function submitAddr() {
  if (!customer.value || !addrForm.value.address_text.trim()) {
    toast.warning("Manzil matni majburiy");
    return;
  }
  const lat = addrForm.value.lat.trim() ? parseFloat(addrForm.value.lat) : null;
  const lng = addrForm.value.lng.trim() ? parseFloat(addrForm.value.lng) : null;
  if ((lat !== null && Number.isNaN(lat)) || (lng !== null && Number.isNaN(lng))) {
    toast.warning("Koordinatalar noto'g'ri");
    return;
  }

  try {
    if (editingAddrId.value) {
      await customersApi.updateAddress(customer.value.id, editingAddrId.value, {
        label: addrForm.value.label,
        address_text: addrForm.value.address_text,
        lat,
        lng,
        is_active: addrForm.value.is_active,
      });
      toast.success("Manzil yangilandi");
    } else {
      await customersApi.createAddress(customer.value.id, {
        label: addrForm.value.label,
        address_text: addrForm.value.address_text,
        lat: lat ?? undefined,
        lng: lng ?? undefined,
      });
      toast.success("Manzil qo'shildi");
    }
    addrDialogOpen.value = false;
    await load();
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

function pickCurrentLocation() {
  if (!navigator.geolocation) {
    toast.warning("Brauzer geolokatsiyani qo'llab-quvvatlamaydi");
    return;
  }
  fetchingGeo.value = true;
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      addrForm.value.lat = pos.coords.latitude.toFixed(7);
      addrForm.value.lng = pos.coords.longitude.toFixed(7);
      fetchingGeo.value = false;
      toast.success("Joriy joylashuv olindi");
    },
    () => {
      fetchingGeo.value = false;
      toast.error("Joylashuvni olib bo'lmadi (GPS / brauzer ruxsati)");
    },
    { enableHighAccuracy: true, timeout: 10000 },
  );
}

function searchOnYandex() {
  const q = encodeURIComponent(addrForm.value.address_text || "Toshkent");
  window.open(`https://yandex.uz/maps/?text=${q}`, "_blank");
}

function openOnYandexMap(a: AddressOut) {
  if (!a.lat || !a.lng) return;
  window.open(`https://yandex.uz/maps/?pt=${a.lng},${a.lat}&z=16&l=map`, "_blank");
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
        <button class="btn-ghost btn-sm" @click="openAdd">
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
            <MapPinIcon class="h-5 w-5" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-sm font-medium text-slate-900 dark:text-slate-100">{{ a.label }}</span>
              <AppBadge v-if="a.is_active" variant="success" class="!py-0.5 !px-2 !text-[10px]">Aktiv</AppBadge>
              <AppBadge v-else variant="neutral" class="!py-0.5 !px-2 !text-[10px]">Nofaol</AppBadge>
              <AppBadge v-if="a.lat && a.lng" variant="info" class="!py-0.5 !px-2 !text-[10px]">📍 GPS bor</AppBadge>
              <AppBadge v-else variant="warning" class="!py-0.5 !px-2 !text-[10px]">📍 GPS yo'q</AppBadge>
            </div>
            <p class="text-sm text-slate-500 dark:text-slate-400 truncate">{{ a.address_text }}</p>
            <p v-if="a.lat && a.lng" class="text-[10px] text-slate-400 mt-0.5 font-mono">
              {{ a.lat }}, {{ a.lng }}
            </p>
          </div>
          <AppMenu>
            <AppMenuItem @click="openEdit(a)">
              <PencilSquareIcon class="h-4 w-4" />
              Tahrirlash
            </AppMenuItem>
            <AppMenuItem v-if="a.lat && a.lng" @click="openOnYandexMap(a)">
              <MapPinIcon class="h-4 w-4" />
              Xaritada ko'rish
            </AppMenuItem>
            <AppMenuItem tone="danger" @click="onDeleteAddress(a)">
              <TrashIcon class="h-4 w-4" />
              O'chirish
            </AppMenuItem>
          </AppMenu>
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

    <!-- Add/Edit address dialog -->
    <AppDialog v-model:open="addrDialogOpen" :title="dialogTitle" max-width="max-w-2xl">
      <div class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Tur (label)</label>
            <input v-model="addrForm.label" class="input" placeholder="Uy / Ofis / Magazin..." />
          </div>
          <div class="sm:col-span-2 flex items-end">
            <label v-if="editingAddrId" class="flex items-center gap-2 cursor-pointer text-sm">
              <input v-model="addrForm.is_active" type="checkbox" class="rounded border-slate-300" />
              <span class="text-slate-700 dark:text-slate-300">Aktiv (buyurtma uchun ishlatish mumkin)</span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Manzil matni</label>
          <textarea
            v-model="addrForm.address_text"
            rows="2"
            class="input resize-none"
            placeholder="Toshkent, Chilonzor, 7-mavze, 12-uy"
          />
        </div>

        <!-- GPS picker -->
        <div class="rounded-xl border border-brand-200 dark:border-brand-900/50 bg-brand-50/40 dark:bg-brand-950/20 p-4 space-y-3">
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-brand-900 dark:text-brand-200 flex items-center gap-1.5">
                📍 Koordinatalar
              </p>
              <p class="text-xs text-brand-700 dark:text-brand-400 mt-0.5">
                Haydovchi marshrutni xaritada ochishi uchun
              </p>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button
                type="button"
                class="btn-primary !py-1.5 !px-3 text-sm inline-flex items-center gap-1.5"
                :disabled="fetchingGeo"
                @click="pickCurrentLocation"
              >
                {{ fetchingGeo ? "Olinmoqda..." : "📍 Joriy joydan olish" }}
              </button>
              <button
                type="button"
                class="btn-secondary !py-1.5 !px-3 text-sm inline-flex items-center gap-1.5"
                @click="searchOnYandex"
                title="Yandex Maps'da qidirib koordinatani ko'chirish"
              >
                🔎 Yandex'da qidirish
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Kenglik (lat)
              </label>
              <input v-model="addrForm.lat" class="input input-sm font-mono" placeholder="41.2995" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Uzunlik (lng)
              </label>
              <input v-model="addrForm.lng" class="input input-sm font-mono" placeholder="69.2401" />
            </div>
          </div>

          <!-- Map preview -->
          <div v-if="previewMapUrl" class="rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800">
            <iframe
              :src="previewMapUrl"
              class="w-full h-48 sm:h-56"
              frameborder="0"
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
            />
            <p class="text-[11px] text-slate-500 dark:text-slate-400 px-3 py-1.5 bg-slate-50 dark:bg-slate-900/50">
              Joylashuv ustida pin ko'rinadi. Koordinata noto'g'ri bo'lsa qayta kiriting.
            </p>
          </div>
          <p v-else class="text-[11px] text-slate-500 dark:text-slate-400">
            Koordinata kiritilgach, xaritada ko'rinadi. GPS shart emas — bo'sh qoldirsangiz, marshrut xaritasiz ko'rsatiladi.
          </p>
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="addrDialogOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitAddr">
          {{ editingAddrId ? "Yangilash" : "Qo'shish" }}
        </button>
      </template>
    </AppDialog>
  </div>
</template>
