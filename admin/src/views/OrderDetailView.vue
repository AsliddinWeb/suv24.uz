<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ArrowLeftIcon,
  XMarkIcon,
  BanknotesIcon,
  CreditCardIcon,
  CheckCircleIcon,
  UserPlusIcon,
  SparklesIcon,
  TruckIcon,
  HandRaisedIcon,
  UserMinusIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  PencilSquareIcon,
  TrashIcon,
} from "@heroicons/vue/20/solid";
import { ordersApi } from "@/api/orders";
import { driversApi } from "@/api/drivers";
import { paymentsApi } from "@/api/payments";
import {
  formatDateTime,
  formatMoney,
  toTashkentInput,
  tashkentInputToUtcIso,
} from "@/utils/format";
import { orderStatusLabel, orderStatusType, paymentMethodLabel, paymentStatusLabel, paymentStatusType } from "@/utils/status";
import { describeStatusLog } from "@/utils/orderLog";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import type {
  DriverOut,
  OrderDetailOut,
  PaymentMethod,
  PaymentOut,
} from "@/types/api";

const route = useRoute();
const router = useRouter();
const confirm = useConfirm();

const order = ref<OrderDetailOut | null>(null);
const drivers = ref<DriverOut[]>([]);
const payments = ref<PaymentOut[]>([]);
const loading = ref(false);

// Dialogs
const assignOpen = ref(false);
const selectedDriver = ref<string | null>(null);

const reasonOpen = ref(false);
const reasonMode = ref<"cancel" | "fail">("cancel");
const reasonText = ref("");

const payOpen = ref(false);
const payMethod = ref<PaymentMethod>("cash");
const payAmount = ref("");

const editOpen = ref(false);
const editForm = reactive({
  notes: "",
  delivery_window_start: "",
  delivery_window_end: "",
});

async function load() {
  loading.value = true;
  try {
    const id = route.params.id as string;
    const [o, ps] = await Promise.all([
      ordersApi.get(id),
      paymentsApi.list({ order_id: id, page_size: 50 }),
    ]);
    order.value = o;
    payments.value = ps.items;
  } finally {
    loading.value = false;
  }
}

async function loadDrivers() {
  drivers.value = (await driversApi.list()).filter((d) => d.is_active);
}

onMounted(() => {
  load();
  loadDrivers();
});

const driverOptions = computed(() =>
  drivers.value.map((d) => ({
    value: d.id,
    label: `${d.full_name}${d.vehicle_plate ? " — " + d.vehicle_plate : ""}`,
  })),
);

const assignedDriverName = computed(() => {
  if (!order.value?.driver_id) return null;
  const d = drivers.value.find((x) => x.id === order.value!.driver_id);
  return d?.full_name || order.value!.driver_id;
});

const totalNum = computed(() => (order.value ? parseFloat(order.value.total) : 0));

const paidNum = computed(() =>
  payments.value
    .filter((p) => p.status === "paid" || p.status === "partial")
    .reduce((s, p) => s + parseFloat(p.amount), 0),
);

const outstanding = computed(() => Math.max(0, totalNum.value - paidNum.value));
const isFullyPaid = computed(() => outstanding.value <= 0 && totalNum.value > 0);

const timeline = computed(() =>
  (order.value?.status_logs ?? []).map((log) => describeStatusLog(log)),
);

const timelineStyle: Record<string, { bg: string; text: string; dotBg: string; icon: any }> = {
  created: { bg: "bg-sky-100 dark:bg-sky-950/50", text: "text-sky-600 dark:text-sky-400", dotBg: "bg-sky-500", icon: SparklesIcon },
  assigned: { bg: "bg-amber-100 dark:bg-amber-950/50", text: "text-amber-600 dark:text-amber-400", dotBg: "bg-amber-500", icon: UserPlusIcon },
  reassigned: { bg: "bg-amber-100 dark:bg-amber-950/50", text: "text-amber-600 dark:text-amber-400", dotBg: "bg-amber-500", icon: UserPlusIcon },
  unassigned: { bg: "bg-slate-100 dark:bg-slate-800", text: "text-slate-500 dark:text-slate-400", dotBg: "bg-slate-400", icon: UserMinusIcon },
  start: { bg: "bg-brand-100 dark:bg-brand-950/50", text: "text-brand-600 dark:text-brand-400", dotBg: "bg-brand-500", icon: TruckIcon },
  delivered: { bg: "bg-emerald-100 dark:bg-emerald-950/50", text: "text-emerald-600 dark:text-emerald-400", dotBg: "bg-emerald-500", icon: HandRaisedIcon },
  failed: { bg: "bg-rose-100 dark:bg-rose-950/50", text: "text-rose-600 dark:text-rose-400", dotBg: "bg-rose-500", icon: ExclamationTriangleIcon },
  cancelled: { bg: "bg-slate-100 dark:bg-slate-800", text: "text-slate-500 dark:text-slate-400", dotBg: "bg-slate-400", icon: XMarkIcon },
  retry: { bg: "bg-sky-100 dark:bg-sky-950/50", text: "text-sky-600 dark:text-sky-400", dotBg: "bg-sky-500", icon: ArrowPathIcon },
  default: { bg: "bg-slate-100 dark:bg-slate-800", text: "text-slate-500 dark:text-slate-400", dotBg: "bg-slate-400", icon: ClockIcon },
};

// ---- Actions ----
async function onAssign() {
  if (!order.value || !selectedDriver.value) return;
  await ordersApi.assign(order.value.id, selectedDriver.value);
  assignOpen.value = false;
  selectedDriver.value = null;
  await load();
  toast.success("Biriktirildi");
}

async function onUnassign() {
  if (!order.value) return;
  const ok = await confirm({
    title: "Haydovchini olib qo'yish",
    description: `#${order.value.number} — kutish holatiga qaytadi.`,
    confirmLabel: "Olib qo'yish",
    tone: "warning",
  });
  if (!ok) return;
  await ordersApi.unassign(order.value.id);
  await load();
  toast.success("Olib qo'yildi");
}

async function onStart() {
  if (!order.value) return;
  const ok = await confirm({
    title: "Yetkazishni boshlash",
    description: `#${order.value.number} — status "Yetkazilmoqda"ga o'tadi.`,
    confirmLabel: "Boshlash",
    tone: "primary",
  });
  if (!ok) return;
  await ordersApi.start(order.value.id);
  await load();
  toast.success("Yetkazish boshlandi");
}

async function onDeliver() {
  if (!order.value) return;
  const ok = await confirm({
    title: "Yetkazib berildi",
    description: `#${order.value.number} — yakuniy status bo'ladi.`,
    confirmLabel: "Tasdiqlash",
    tone: "primary",
  });
  if (!ok) return;
  await ordersApi.deliver(order.value.id, []);
  await load();
  toast.success("Yetkazildi");
}

async function onRetry() {
  if (!order.value) return;
  const ok = await confirm({
    title: "Qayta urinish",
    description: `#${order.value.number} — "Kutilmoqda"ga qaytariladi.`,
    confirmLabel: "Qaytarish",
    tone: "primary",
  });
  if (!ok) return;
  await ordersApi.retry(order.value.id);
  await load();
  toast.success("Qaytarildi");
}

function openReason(mode: "cancel" | "fail") {
  reasonMode.value = mode;
  reasonText.value = "";
  reasonOpen.value = true;
}

async function submitReason() {
  if (!order.value || !reasonText.value.trim()) {
    toast.warning("Sabab majburiy");
    return;
  }
  if (reasonMode.value === "cancel") {
    await ordersApi.cancel(order.value.id, reasonText.value);
    toast.success("Bekor qilindi");
  } else {
    await ordersApi.fail(order.value.id, reasonText.value);
    toast.success("Muvaffaqiyatsiz deb belgilandi");
  }
  reasonOpen.value = false;
  await load();
}

function openPayment(method: PaymentMethod) {
  payMethod.value = method;
  payAmount.value = outstanding.value.toString();
  payOpen.value = true;
}

async function onSubmitPayment() {
  if (!order.value || !payAmount.value) return;
  if (Number(payAmount.value) <= 0) {
    toast.warning("Musbat son kiriting");
    return;
  }
  await paymentsApi.record({
    order_id: order.value.id,
    amount: payAmount.value,
    method: payMethod.value,
  });
  payOpen.value = false;
  await load();
  toast.success("To'lov yozildi");
}

function openEdit() {
  if (!order.value) return;
  editForm.notes = order.value.notes || "";
  editForm.delivery_window_start = toTashkentInput(order.value.delivery_window_start);
  editForm.delivery_window_end = toTashkentInput(order.value.delivery_window_end);
  editOpen.value = true;
}

async function submitEdit() {
  if (!order.value) return;
  const body: Record<string, any> = { notes: editForm.notes || null };
  if (editForm.delivery_window_start) {
    body.delivery_window_start = tashkentInputToUtcIso(editForm.delivery_window_start);
  }
  if (editForm.delivery_window_end) {
    body.delivery_window_end = tashkentInputToUtcIso(editForm.delivery_window_end);
  }
  await ordersApi.update(order.value.id, body);
  editOpen.value = false;
  await load();
  toast.success("Yangilandi");
}

async function onDelete() {
  if (!order.value) return;
  const ok = await confirm({
    title: "Buyurtmani o'chirish",
    description: `#${order.value.number} — ro'yxatdan butunlay olib tashlanadi.`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await ordersApi.remove(order.value.id);
  toast.success("O'chirildi");
  router.push("/app/orders");
}

// ---- Conditions ----
const canAssign = computed(() => order.value?.status === "pending");
const canReassign = computed(() => order.value?.status === "assigned");
const canUnassign = computed(() => order.value?.status === "assigned");
const canStart = computed(() => order.value?.status === "assigned");
const canDeliver = computed(() => order.value?.status === "in_delivery");
const canFail = computed(() => order.value?.status === "in_delivery");
const canCancel = computed(
  () => order.value && ["pending", "assigned"].includes(order.value.status),
);
const canRetry = computed(() => order.value?.status === "failed");
const canEdit = computed(
  () => order.value && ["pending", "assigned"].includes(order.value.status),
);
const canPay = computed(
  () => order.value && order.value.status !== "cancelled" && !isFullyPaid.value,
);
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      :title="order ? `Buyurtma #${order.number}` : 'Buyurtma'"
      :subtitle="order ? `Yaratilgan: ${formatDateTime(order.created_at)}` : ''"
    >
      <template #actions>
        <button class="btn-secondary" @click="router.back()">
          <ArrowLeftIcon class="h-4 w-4" />
          Orqaga
        </button>
        <button class="btn-danger" @click="onDelete">
          <TrashIcon class="h-4 w-4" />
          O'chirish
        </button>
      </template>
    </PageHeader>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <svg class="h-6 w-6 animate-spin text-brand-500" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
        <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
      </svg>
    </div>

    <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main column -->
      <div class="lg:col-span-2 space-y-6">
        <div class="card p-6">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div class="flex items-center gap-3">
              <AppBadge :variant="orderStatusType[order.status]">
                {{ orderStatusLabel[order.status] }}
              </AppBadge>
              <span class="text-xs text-slate-500 dark:text-slate-400 capitalize">
                Manba: {{ order.source }}
              </span>
            </div>
          </div>

          <div class="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="rounded-xl bg-slate-50 dark:bg-slate-800/50 p-4">
              <p class="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide">Jami</p>
              <p class="mt-1 text-xl font-semibold text-slate-900 dark:text-slate-100">
                {{ formatMoney(totalNum) }}
              </p>
            </div>
            <div class="rounded-xl bg-emerald-50 dark:bg-emerald-950/30 p-4">
              <p class="text-xs text-emerald-700 dark:text-emerald-300 uppercase tracking-wide">To'langan</p>
              <p class="mt-1 text-xl font-semibold text-emerald-700 dark:text-emerald-400">
                {{ formatMoney(paidNum) }}
              </p>
            </div>
            <div
              :class="[
                'rounded-xl p-4',
                outstanding > 0
                  ? 'bg-rose-50 dark:bg-rose-950/30'
                  : 'bg-slate-50 dark:bg-slate-800/50',
              ]"
            >
              <p
                :class="[
                  'text-xs uppercase tracking-wide',
                  outstanding > 0
                    ? 'text-rose-700 dark:text-rose-300'
                    : 'text-slate-500 dark:text-slate-400',
                ]"
              >
                Qarz
              </p>
              <p
                :class="[
                  'mt-1 text-xl font-semibold',
                  outstanding > 0
                    ? 'text-rose-700 dark:text-rose-400'
                    : 'text-slate-900 dark:text-slate-100',
                ]"
              >
                {{ formatMoney(outstanding) }}
              </p>
            </div>
          </div>

          <dl class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4 text-sm">
            <div>
              <dt class="text-slate-500 dark:text-slate-400">Haydovchi</dt>
              <dd class="mt-0.5 text-slate-900 dark:text-slate-100">
                <span v-if="assignedDriverName">{{ assignedDriverName }}</span>
                <span v-else class="text-slate-400">— biriktirilmagan —</span>
              </dd>
            </div>
            <div>
              <dt class="text-slate-500 dark:text-slate-400">Yangilangan</dt>
              <dd class="mt-0.5 text-slate-900 dark:text-slate-100">
                {{ formatDateTime(order.updated_at) }}
              </dd>
            </div>
            <div v-if="order.notes" class="md:col-span-2">
              <dt class="text-slate-500 dark:text-slate-400">Izoh</dt>
              <dd class="mt-0.5 text-slate-900 dark:text-slate-100">{{ order.notes }}</dd>
            </div>
            <div v-if="order.cancel_reason" class="md:col-span-2">
              <dt class="text-slate-500 dark:text-slate-400">Bekor sababi</dt>
              <dd class="mt-0.5 text-rose-600 dark:text-rose-400">{{ order.cancel_reason }}</dd>
            </div>
          </dl>
        </div>

        <div class="card">
          <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Mahsulotlar</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Mahsulot</th>
                  <th class="text-right">Miqdor</th>
                  <th class="text-right">Birlik narxi</th>
                  <th class="text-right">Jami</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="it in order.items" :key="it.id">
                  <td class="font-medium text-slate-900 dark:text-slate-100">{{ it.product_name }}</td>
                  <td class="text-right">{{ it.quantity }}</td>
                  <td class="text-right text-slate-500 dark:text-slate-400">{{ formatMoney(it.unit_price) }}</td>
                  <td class="text-right font-medium text-slate-900 dark:text-slate-100">{{ formatMoney(it.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card" v-if="payments.length">
          <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              To'lovlar ({{ payments.length }})
            </h3>
          </div>
          <div class="overflow-x-auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Sana</th>
                  <th>Usul</th>
                  <th>Holati</th>
                  <th class="text-right">Summa</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in payments" :key="p.id">
                  <td class="text-slate-500 whitespace-nowrap">{{ formatDateTime(p.created_at) }}</td>
                  <td>{{ paymentMethodLabel[p.method] }}</td>
                  <td><AppBadge :variant="paymentStatusType[p.status]">{{ paymentStatusLabel[p.status] }}</AppBadge></td>
                  <td
                    class="text-right font-medium"
                    :class="p.status === 'refunded' ? 'text-slate-400 line-through' : 'text-slate-900 dark:text-slate-100'"
                  >
                    {{ formatMoney(p.amount) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card p-6">
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-5">
            Buyurtma tarixi
          </h3>
          <ol class="relative space-y-6">
            <div class="absolute left-4 top-3 bottom-3 w-px bg-slate-200 dark:bg-slate-700" />
            <li v-for="(entry, idx) in timeline" :key="idx" class="relative pl-12">
              <div
                :class="[
                  'absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full ring-4 ring-white dark:ring-slate-900',
                  timelineStyle[entry.icon].bg,
                ]"
              >
                <component
                  :is="timelineStyle[entry.icon].icon"
                  :class="['h-4 w-4', timelineStyle[entry.icon].text]"
                />
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {{ entry.title }}
                </p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {{ formatDateTime(entry.timestamp) }}
                </p>
                <p
                  v-if="entry.reason"
                  class="mt-2 text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/50 rounded-lg px-3 py-2"
                >
                  {{ entry.reason }}
                </p>
              </div>
            </li>
          </ol>
        </div>
      </div>

      <!-- Side column -->
      <div class="space-y-6">
        <!-- Delivery actions -->
        <div class="card p-6">
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-3">
            Yetkazish
          </h3>
          <div class="space-y-2">
            <button v-if="canAssign" class="btn-primary w-full" @click="assignOpen = true">
              <UserPlusIcon class="h-4 w-4" />
              Haydovchi biriktirish
            </button>

            <template v-if="canReassign">
              <button class="btn-secondary w-full" @click="assignOpen = true">
                <UserPlusIcon class="h-4 w-4" />
                Haydovchini o'zgartirish
              </button>
              <button class="btn-secondary w-full" @click="onUnassign">
                <UserMinusIcon class="h-4 w-4" />
                Haydovchini olib qo'yish
              </button>
            </template>

            <button v-if="canStart" class="btn-primary w-full" @click="onStart">
              <TruckIcon class="h-4 w-4" />
              Yetkazishni boshlash
            </button>

            <template v-if="canDeliver || canFail">
              <button v-if="canDeliver" class="btn-success w-full" @click="onDeliver">
                <CheckCircleIcon class="h-4 w-4" />
                Yetkazildi
              </button>
              <button v-if="canFail" class="btn-secondary w-full" @click="openReason('fail')">
                <ExclamationTriangleIcon class="h-4 w-4" />
                Muvaffaqiyatsiz
              </button>
            </template>

            <button v-if="canRetry" class="btn-primary w-full" @click="onRetry">
              <ArrowPathIcon class="h-4 w-4" />
              Qayta urinish
            </button>

            <div
              v-if="order.status === 'delivered'"
              class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 rounded-lg p-3 text-sm"
            >
              <CheckCircleIcon class="h-5 w-5 shrink-0" />
              <span>Buyurtma yetkazildi</span>
            </div>

            <div
              v-if="order.status === 'cancelled'"
              class="flex items-center gap-2 text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 rounded-lg p-3 text-sm"
            >
              <XMarkIcon class="h-5 w-5 shrink-0" />
              <span>Buyurtma bekor qilingan</span>
            </div>
          </div>
        </div>

        <!-- Payment -->
        <div v-if="canPay" class="card p-6">
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-1">
            To'lov yozish
          </h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-3">
            Qolgan qarz: <strong class="text-slate-900 dark:text-slate-100">{{ formatMoney(outstanding) }}</strong>
          </p>
          <div class="space-y-2">
            <button class="btn-success w-full" @click="openPayment('cash')">
              <BanknotesIcon class="h-4 w-4" />
              Naqd to'lov
            </button>
            <button class="btn-secondary w-full" @click="openPayment('card_manual')">
              <CreditCardIcon class="h-4 w-4" />
              Karta (manual)
            </button>
          </div>
        </div>

        <div
          v-else-if="isFullyPaid"
          class="card p-4 flex items-center gap-2 text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 text-sm"
        >
          <CheckCircleIcon class="h-5 w-5 shrink-0" />
          <span>To'liq to'langan</span>
        </div>

        <!-- Management -->
        <div v-if="canEdit || canCancel" class="card p-6">
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100 mb-3">
            Boshqaruv
          </h3>
          <div class="space-y-2">
            <button v-if="canEdit" class="btn-secondary w-full" @click="openEdit">
              <PencilSquareIcon class="h-4 w-4" />
              Tahrirlash
            </button>
            <button v-if="canCancel" class="btn-danger w-full" @click="openReason('cancel')">
              <XMarkIcon class="h-4 w-4" />
              Bekor qilish
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign dialog -->
    <AppDialog v-model:open="assignOpen" title="Haydovchi biriktirish">
      <div class="space-y-3">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Buyurtmani faol haydovchiga biriktiring.
        </p>
        <AppSelect v-model="selectedDriver" :options="driverOptions" placeholder="Haydovchi tanlang" />
      </div>
      <template #footer>
        <button class="btn-secondary" @click="assignOpen = false">Bekor qilish</button>
        <button class="btn-primary" :disabled="!selectedDriver" @click="onAssign">Biriktirish</button>
      </template>
    </AppDialog>

    <!-- Reason dialog (cancel/fail) -->
    <AppDialog
      v-model:open="reasonOpen"
      :title="reasonMode === 'cancel' ? 'Bekor qilish' : 'Muvaffaqiyatsiz'"
    >
      <div class="space-y-3">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Sabab majburiy. Status tarixiga yoziladi.
        </p>
        <textarea
          v-model="reasonText"
          rows="3"
          class="input resize-none"
          placeholder="Sababni kiriting..."
        />
      </div>
      <template #footer>
        <button class="btn-secondary" @click="reasonOpen = false">Yopish</button>
        <button class="btn-danger" :disabled="!reasonText.trim()" @click="submitReason">
          {{ reasonMode === "cancel" ? "Bekor qilish" : "Tasdiqlash" }}
        </button>
      </template>
    </AppDialog>

    <!-- Payment dialog -->
    <AppDialog
      v-model:open="payOpen"
      :title="payMethod === 'cash' ? 'Naqd to\'lov' : 'Karta (manual) to\'lov'"
    >
      <div class="space-y-3">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Summa (so'm)
        </label>
        <input v-model="payAmount" type="number" min="1" class="input" />
        <p class="text-xs text-slate-500 dark:text-slate-400">
          Qarz: <strong class="text-slate-900 dark:text-slate-100">{{ formatMoney(outstanding) }}</strong>
        </p>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="payOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="onSubmitPayment">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Edit dialog -->
    <AppDialog v-model:open="editOpen" title="Buyurtmani tahrirlash">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Izoh
          </label>
          <textarea
            v-model="editForm.notes"
            rows="3"
            class="input resize-none"
            placeholder="Masalan: 14:00-18:00 ga yetkazish"
          />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Oyna boshi
            </label>
            <input v-model="editForm.delivery_window_start" type="datetime-local" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Oyna oxiri
            </label>
            <input v-model="editForm.delivery_window_end" type="datetime-local" class="input" />
          </div>
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="editOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="submitEdit">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
