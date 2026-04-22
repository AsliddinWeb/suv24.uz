<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { FunnelIcon } from "@heroicons/vue/20/solid";
import { paymentsApi } from "@/api/payments";
import { formatDateTime, formatMoney } from "@/utils/format";
import { paymentMethodLabel, paymentStatusLabel, paymentStatusType } from "@/utils/status";
import { toast } from "@/lib/toast";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppPagination from "@/components/ui/AppPagination.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { PaymentMethod, PaymentOut, PaymentStatus } from "@/types/api";

const router = useRouter();
const items = ref<PaymentOut[]>([]);
const total = ref(0);
const loading = ref(false);
const filter = reactive<{
  method: PaymentMethod | null;
  status: PaymentStatus | null;
  page: number;
  page_size: number;
}>({ method: null, status: null, page: 1, page_size: 20 });

const methodOptions = [
  { value: "cash" as PaymentMethod, label: "Naqd" },
  { value: "card_manual" as PaymentMethod, label: "Karta (manual)" },
  { value: "payme" as PaymentMethod, label: "Payme" },
  { value: "click" as PaymentMethod, label: "Click" },
];

const statusOptions = [
  { value: "paid" as PaymentStatus, label: "To'langan" },
  { value: "partial" as PaymentStatus, label: "Qisman" },
  { value: "refunded" as PaymentStatus, label: "Qaytarilgan" },
  { value: "cancelled" as PaymentStatus, label: "Bekor qilindi" },
];

const refundOpen = ref(false);
const refundingPayment = ref<PaymentOut | null>(null);
const refundReason = ref("");

async function load() {
  loading.value = true;
  try {
    const res = await paymentsApi.list({
      method: filter.method ?? undefined,
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

onMounted(load);

function openRefund(p: PaymentOut) {
  refundingPayment.value = p;
  refundReason.value = "";
  refundOpen.value = true;
}

async function submitRefund() {
  if (!refundingPayment.value) return;
  await paymentsApi.refund(refundingPayment.value.id, refundReason.value || undefined);
  refundOpen.value = false;
  load();
  toast.success("Pul qaytarildi");
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="To'lovlar" subtitle="Barcha to'lovlar va refundlar" />

    <div class="card overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
          <FunnelIcon class="h-4 w-4" />
          Filter:
        </div>
        <div class="w-48">
          <AppSelect
            v-model="filter.method"
            :options="methodOptions"
            placeholder="Usul (hammasi)"
            @change="() => { filter.page = 1; load(); }"
          />
        </div>
        <div class="w-48">
          <AppSelect
            v-model="filter.status"
            :options="statusOptions"
            placeholder="Status (hammasi)"
            @change="() => { filter.page = 1; load(); }"
          />
        </div>
        <div class="ml-auto text-sm text-slate-500 dark:text-slate-400">
          Jami: <span class="font-medium text-slate-900 dark:text-slate-100">{{ total }}</span>
        </div>
      </div>

      <EmptyState v-if="!loading && !items.length" title="To'lov yo'q" />

      <div v-else class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Sana</th>
              <th class="text-right">Summa</th>
              <th>Usul</th>
              <th>Status</th>
              <th>Buyurtma</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in items" :key="p.id">
              <td class="text-slate-500 dark:text-slate-400 whitespace-nowrap">{{ formatDateTime(p.created_at) }}</td>
              <td class="text-right font-medium text-slate-900 dark:text-slate-100">{{ formatMoney(p.amount) }}</td>
              <td>{{ paymentMethodLabel[p.method] }}</td>
              <td>
                <AppBadge :variant="paymentStatusType[p.status]">{{ paymentStatusLabel[p.status] }}</AppBadge>
              </td>
              <td>
                <button
                  class="text-brand-600 dark:text-brand-400 hover:underline text-sm"
                  @click="router.push({ name: 'order-detail', params: { id: p.order_id } })"
                >
                  Ko'rish
                </button>
              </td>
              <td class="text-right">
                <AppMenu v-if="p.status === 'paid' || p.status === 'partial'">
                  <AppMenuItem tone="danger" @click="openRefund(p)">
                    Qaytarish
                  </AppMenuItem>
                </AppMenu>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="items.length" class="px-4 border-t border-slate-200 dark:border-slate-800">
        <AppPagination
          :page="filter.page"
          :page-size="filter.page_size"
          :total="total"
          @update:page="(p) => { filter.page = p; load(); }"
        />
      </div>
    </div>

    <AppDialog v-model:open="refundOpen" title="To'lovni qaytarish">
      <div class="space-y-3">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          <span class="font-medium text-slate-900 dark:text-slate-100">{{ formatMoney(refundingPayment?.amount) }}</span>
          miqdorda qaytariladi. Mijoz balansi yangilanadi.
        </p>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Sabab (ixtiyoriy)</label>
          <textarea v-model="refundReason" rows="3" class="input resize-none" />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="refundOpen = false">Yopish</button>
        <button class="btn-danger" @click="submitRefund">Qaytarish</button>
      </template>
    </AppDialog>
  </div>
</template>
