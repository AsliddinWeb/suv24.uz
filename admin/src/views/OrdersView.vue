<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import {
  PlusIcon,
  FunnelIcon,
  EyeIcon,
  UserPlusIcon,
  UserMinusIcon,
  TruckIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ArrowPathIcon,
  PencilSquareIcon,
  TrashIcon,
} from "@heroicons/vue/20/solid";
import { ordersApi } from "@/api/orders";
import { driversApi } from "@/api/drivers";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppPagination from "@/components/ui/AppPagination.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import {
  formatDateTime,
  formatMoney,
  toTashkentInput,
  tashkentInputToUtcIso,
} from "@/utils/format";
import { orderStatusLabel, orderStatusType } from "@/utils/status";
import type { DriverOut, OrderOut, OrderStatus } from "@/types/api";

const router = useRouter();
const confirm = useConfirm();

const loading = ref(false);
const items = ref<OrderOut[]>([]);
const total = ref(0);
const drivers = ref<DriverOut[]>([]);

const filter = reactive<{
  status: OrderStatus | null;
  page: number;
  page_size: number;
}>({
  status: null,
  page: 1,
  page_size: 20,
});

const statusOptions = [
  { value: "pending" as OrderStatus, label: "Kutilmoqda" },
  { value: "assigned" as OrderStatus, label: "Biriktirildi" },
  { value: "in_delivery" as OrderStatus, label: "Yetkazilmoqda" },
  { value: "delivered" as OrderStatus, label: "Yetkazildi" },
  { value: "failed" as OrderStatus, label: "Muvaffaqiyatsiz" },
  { value: "cancelled" as OrderStatus, label: "Bekor qilindi" },
];

type PaymentLabel = {
  label: string;
  variant: "success" | "warning" | "neutral" | "danger";
};

function paymentBadge(o: OrderOut): PaymentLabel {
  if (o.status === "cancelled") return { label: "Bekor", variant: "neutral" };
  const total = parseFloat(o.total);
  const paid = parseFloat(o.paid_amount);
  if (paid <= 0) return { label: "To'lanmagan", variant: "danger" };
  if (paid >= total) return { label: "To'langan", variant: "success" };
  return { label: "Qisman", variant: "warning" };
}

async function load() {
  loading.value = true;
  try {
    const res = await ordersApi.list({
      status: filter.status ?? undefined,
      page: filter.page,
      page_size: filter.page_size,
    });
    items.value = res.items;
    total.value = res.total;
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

function onFilterChange() {
  filter.page = 1;
  load();
}

// ---- Dialogs ----
const assignOpen = ref(false);
const assignOrder = ref<OrderOut | null>(null);
const assignDriverId = ref<string | null>(null);

const reasonOpen = ref(false);
const reasonOrder = ref<OrderOut | null>(null);
const reasonMode = ref<"cancel" | "fail">("cancel");
const reasonText = ref("");

const driverOptions = computed(() =>
  drivers.value.map((d) => ({
    value: d.id,
    label: `${d.full_name}${d.vehicle_plate ? " — " + d.vehicle_plate : ""}`,
  })),
);

// ---- Edit dialog ----
const editOpen = ref(false);
const editOrder = ref<OrderOut | null>(null);
const editForm = reactive({
  notes: "",
  delivery_window_start: "",
  delivery_window_end: "",
});

function openEdit(o: OrderOut) {
  editOrder.value = o;
  editForm.notes = o.notes || "";
  editForm.delivery_window_start = toTashkentInput(o.delivery_window_start);
  editForm.delivery_window_end = toTashkentInput(o.delivery_window_end);
  editOpen.value = true;
}

async function submitEdit() {
  if (!editOrder.value) return;
  const body: Record<string, any> = { notes: editForm.notes || null };
  if (editForm.delivery_window_start) {
    body.delivery_window_start = tashkentInputToUtcIso(editForm.delivery_window_start);
  }
  if (editForm.delivery_window_end) {
    body.delivery_window_end = tashkentInputToUtcIso(editForm.delivery_window_end);
  }
  await ordersApi.update(editOrder.value.id, body);
  editOpen.value = false;
  toast.success("Yangilandi");
  load();
}

async function onDelete(o: OrderOut) {
  const ok = await confirm({
    title: "Buyurtmani o'chirish",
    description: `#${o.number} — buyurtma ro'yxatdan butunlay olib tashlanadi. Agar faol bo'lsa, oldindan bekor qilishni tavsiya qilamiz.`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await ordersApi.remove(o.id);
  toast.success("O'chirildi");
  load();
}

// ---- Actions ----
function go(o: OrderOut) {
  router.push({ name: "order-detail", params: { id: o.id } });
}

function openAssign(o: OrderOut) {
  assignOrder.value = o;
  assignDriverId.value = null;
  assignOpen.value = true;
}

async function submitAssign() {
  if (!assignOrder.value || !assignDriverId.value) return;
  await ordersApi.assign(assignOrder.value.id, assignDriverId.value);
  assignOpen.value = false;
  toast.success("Biriktirildi");
  load();
}

async function onUnassign(o: OrderOut) {
  const ok = await confirm({
    title: "Haydovchini olib qo'yish",
    description: `#${o.number} — haydovchi biriktirilmagan holatiga qaytadi.`,
    confirmLabel: "Olib qo'yish",
    tone: "warning",
  });
  if (!ok) return;
  await ordersApi.unassign(o.id);
  toast.success("Olib qo'yildi");
  load();
}

async function onStart(o: OrderOut) {
  const ok = await confirm({
    title: "Yetkazishni boshlash",
    description: `#${o.number} — status "Yetkazilmoqda"ga o'tadi.`,
    confirmLabel: "Boshlash",
    tone: "primary",
  });
  if (!ok) return;
  await ordersApi.start(o.id);
  toast.success("Yetkazish boshlandi");
  load();
}

async function onDeliver(o: OrderOut) {
  const ok = await confirm({
    title: "Yetkazib berildi",
    description: `#${o.number} — yakuniy status.`,
    confirmLabel: "Tasdiqlash",
    tone: "primary",
  });
  if (!ok) return;
  await ordersApi.deliver(o.id, []);
  toast.success("Yetkazildi");
  load();
}

function openReason(o: OrderOut, mode: "cancel" | "fail") {
  reasonOrder.value = o;
  reasonMode.value = mode;
  reasonText.value = "";
  reasonOpen.value = true;
}

async function submitReason() {
  if (!reasonOrder.value || !reasonText.value.trim()) {
    toast.warning("Sabab majburiy");
    return;
  }
  if (reasonMode.value === "cancel") {
    await ordersApi.cancel(reasonOrder.value.id, reasonText.value);
    toast.success("Bekor qilindi");
  } else {
    await ordersApi.fail(reasonOrder.value.id, reasonText.value);
    toast.success("Muvaffaqiyatsiz deb belgilandi");
  }
  reasonOpen.value = false;
  load();
}

async function onRetry(o: OrderOut) {
  const ok = await confirm({
    title: "Qayta urinish",
    description: `#${o.number} — status "Kutilmoqda"ga qaytariladi.`,
    confirmLabel: "Qaytarish",
    tone: "primary",
  });
  if (!ok) return;
  await ordersApi.retry(o.id);
  toast.success("Qaytarildi");
  load();
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Buyurtmalar" subtitle="Barcha buyurtmalar va ularning statuslari">
      <template #actions>
        <button class="btn-primary" @click="router.push({ name: 'order-new' })">
          <PlusIcon class="h-4 w-4" />
          Yangi buyurtma
        </button>
      </template>
    </PageHeader>

    <div class="card">
      <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
          <FunnelIcon class="h-4 w-4" />
          Filter:
        </div>
        <div class="w-48">
          <AppSelect
            v-model="filter.status"
            :options="statusOptions"
            placeholder="Status (hammasi)"
            @change="onFilterChange"
          />
        </div>
        <div class="ml-auto text-sm text-slate-500 dark:text-slate-400">
          Jami: <span class="font-medium text-slate-900 dark:text-slate-100">{{ total }}</span>
        </div>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-16">
        <svg class="h-6 w-6 animate-spin text-brand-500" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
          <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
        </svg>
      </div>

      <EmptyState
        v-else-if="!items.length"
        title="Buyurtma yo'q"
        description="Yuqoridagi 'Yangi buyurtma' tugmasini bosib boshlang"
      />

      <div v-else class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Invoice</th>
              <th>Status</th>
              <th>To'lov</th>
              <th class="text-right">Summa</th>
              <th class="text-right">To'langan</th>
              <th>Sana</th>
              <th>Izoh</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in items" :key="o.id">
              <td
                class="cursor-pointer font-semibold text-brand-600 dark:text-brand-400"
                @click="go(o)"
              >
                #{{ o.number }}
              </td>
              <td class="cursor-pointer" @click="go(o)">
                <AppBadge :variant="orderStatusType[o.status]">
                  {{ orderStatusLabel[o.status] }}
                </AppBadge>
              </td>
              <td class="cursor-pointer" @click="go(o)">
                <AppBadge :variant="paymentBadge(o).variant">
                  {{ paymentBadge(o).label }}
                </AppBadge>
              </td>
              <td
                class="cursor-pointer text-right font-medium text-slate-900 dark:text-slate-100"
                @click="go(o)"
              >
                {{ formatMoney(o.total) }}
              </td>
              <td class="cursor-pointer text-right text-slate-500 dark:text-slate-400" @click="go(o)">
                {{ formatMoney(o.paid_amount) }}
              </td>
              <td class="cursor-pointer text-slate-500 dark:text-slate-400 whitespace-nowrap" @click="go(o)">
                {{ formatDateTime(o.created_at) }}
              </td>
              <td class="cursor-pointer text-slate-500 dark:text-slate-400 max-w-xs truncate" @click="go(o)">
                {{ o.notes || "—" }}
              </td>
              <td class="text-right">
                <AppMenu>
                  <AppMenuItem @click="go(o)">
                    <EyeIcon class="h-4 w-4" />
                    Ochish
                  </AppMenuItem>

                  <AppMenuItem v-if="o.status === 'pending'" @click="openAssign(o)">
                    <UserPlusIcon class="h-4 w-4" />
                    Haydovchi biriktirish
                  </AppMenuItem>

                  <template v-if="o.status === 'assigned'">
                    <AppMenuItem @click="openAssign(o)">
                      <UserPlusIcon class="h-4 w-4" />
                      Haydovchini o'zgartirish
                    </AppMenuItem>
                    <AppMenuItem @click="onUnassign(o)">
                      <UserMinusIcon class="h-4 w-4" />
                      Haydovchini olib qo'yish
                    </AppMenuItem>
                    <AppMenuItem @click="onStart(o)">
                      <TruckIcon class="h-4 w-4" />
                      Yetkazishni boshlash
                    </AppMenuItem>
                  </template>

                  <template v-if="o.status === 'in_delivery'">
                    <AppMenuItem @click="onDeliver(o)">
                      <CheckCircleIcon class="h-4 w-4" />
                      Yetkazildi
                    </AppMenuItem>
                    <AppMenuItem tone="danger" @click="openReason(o, 'fail')">
                      <ExclamationTriangleIcon class="h-4 w-4" />
                      Muvaffaqiyatsiz
                    </AppMenuItem>
                  </template>

                  <AppMenuItem
                    v-if="['pending','assigned'].includes(o.status)"
                    @click="openEdit(o)"
                  >
                    <PencilSquareIcon class="h-4 w-4" />
                    Tahrirlash
                  </AppMenuItem>

                  <AppMenuItem
                    v-if="['pending','assigned'].includes(o.status)"
                    tone="danger"
                    @click="openReason(o, 'cancel')"
                  >
                    <XCircleIcon class="h-4 w-4" />
                    Bekor qilish
                  </AppMenuItem>

                  <AppMenuItem v-if="o.status === 'failed'" @click="onRetry(o)">
                    <ArrowPathIcon class="h-4 w-4" />
                    Qayta urinish
                  </AppMenuItem>

                  <AppMenuItem tone="danger" @click="onDelete(o)">
                    <TrashIcon class="h-4 w-4" />
                    O'chirish
                  </AppMenuItem>
                </AppMenu>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="px-4 border-t border-slate-200 dark:border-slate-800" v-if="items.length">
        <AppPagination
          :page="filter.page"
          :page-size="filter.page_size"
          :total="total"
          @update:page="(p) => { filter.page = p; load(); }"
        />
      </div>
    </div>

    <!-- Assign dialog -->
    <AppDialog
      v-model:open="assignOpen"
      :title="`#${assignOrder?.number} — haydovchi biriktirish`"
    >
      <div class="space-y-3">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Buyurtmani faol haydovchiga biriktiring.
        </p>
        <AppSelect
          v-model="assignDriverId"
          :options="driverOptions"
          placeholder="Haydovchi tanlang"
        />
      </div>
      <template #footer>
        <button class="btn-secondary" @click="assignOpen = false">Bekor qilish</button>
        <button class="btn-primary" :disabled="!assignDriverId" @click="submitAssign">
          Biriktirish
        </button>
      </template>
    </AppDialog>

    <!-- Reason dialog (cancel/fail) -->
    <AppDialog
      v-model:open="reasonOpen"
      :title="reasonMode === 'cancel'
        ? `#${reasonOrder?.number} — bekor qilish`
        : `#${reasonOrder?.number} — muvaffaqiyatsiz`"
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

    <!-- Edit dialog -->
    <AppDialog
      v-model:open="editOpen"
      :title="`#${editOrder?.number} — tahrirlash`"
    >
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
              Yetkazish oynasi (boshi)
            </label>
            <input v-model="editForm.delivery_window_start" type="datetime-local" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Yetkazish oynasi (oxiri)
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
