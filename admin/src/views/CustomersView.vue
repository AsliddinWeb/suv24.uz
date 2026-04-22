<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { PlusIcon, MagnifyingGlassIcon, TrashIcon } from "@heroicons/vue/20/solid";
import { customersApi } from "@/api/customers";
import { formatMoney } from "@/utils/format";
import { segmentLabel, segmentType } from "@/utils/status";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppPagination from "@/components/ui/AppPagination.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { CustomerOut } from "@/types/api";

const router = useRouter();
const confirm = useConfirm();

const loading = ref(false);
const items = ref<CustomerOut[]>([]);
const total = ref(0);
const filter = reactive({ q: "", page: 1, page_size: 20 });

const newOpen = ref(false);
const form = reactive({ phone: "", full_name: "" });

async function load() {
  loading.value = true;
  try {
    const res = await customersApi.list({
      q: filter.q || undefined,
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

async function onCreate() {
  if (!form.phone || !form.full_name) {
    toast.warning("Telefon va ism majburiy");
    return;
  }
  await customersApi.create({ ...form });
  toast.success("Mijoz qo'shildi");
  newOpen.value = false;
  form.phone = "";
  form.full_name = "";
  load();
}

async function onDelete(c: CustomerOut) {
  const ok = await confirm({
    title: "Mijozni o'chirish",
    description: `${c.full_name} (${c.phone}) mijozini o'chirmoqchimisiz?`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await customersApi.remove(c.id);
  toast.success("O'chirildi");
  load();
}

function balanceBadge(balance: string) {
  const n = parseFloat(balance);
  if (n > 0) return { variant: "danger" as const, label: "Qarzdor" };
  if (n < 0) return { variant: "info" as const, label: "Depozit" };
  return { variant: "success" as const, label: "Toza" };
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Mijozlar" subtitle="Qidirish, ro'yxat, qarz va idish">
      <template #actions>
        <button class="btn-primary" @click="newOpen = true">
          <PlusIcon class="h-4 w-4" />
          Yangi mijoz
        </button>
      </template>
    </PageHeader>

    <div class="card">
      <div class="p-4 border-b border-slate-200 dark:border-slate-800">
        <div class="relative max-w-md">
          <MagnifyingGlassIcon class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-slate-400" />
          <input
            v-model="filter.q"
            class="input pl-9"
            placeholder="Ism yoki telefon bo'yicha qidirish"
            @keyup.enter="() => { filter.page = 1; load(); }"
          />
        </div>
      </div>

      <EmptyState v-if="!loading && !items.length" title="Mijoz topilmadi" />

      <div v-else class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Ism</th>
              <th>Telefon</th>
              <th>Segment</th>
              <th>Qarz holati</th>
              <th class="text-right">Qarz</th>
              <th class="text-right">Idish</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in items" :key="c.id">
              <td
                class="cursor-pointer"
                @click="router.push({ name: 'customer-detail', params: { id: c.id } })"
              >
                <div class="flex items-center gap-3">
                  <div class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-brand-400 to-brand-600 text-white text-xs font-medium">
                    {{ c.full_name.slice(0, 1).toUpperCase() }}
                  </div>
                  <span class="font-medium text-slate-900 dark:text-slate-100">{{ c.full_name }}</span>
                </div>
              </td>
              <td class="text-slate-500 dark:text-slate-400">{{ c.phone }}</td>
              <td>
                <AppBadge :variant="segmentType[c.segment]">{{ segmentLabel[c.segment] }}</AppBadge>
              </td>
              <td>
                <AppBadge :variant="balanceBadge(c.balance).variant">
                  {{ balanceBadge(c.balance).label }}
                </AppBadge>
              </td>
              <td class="text-right">
                <span
                  :class="parseFloat(c.balance) > 0 ? 'text-rose-600 dark:text-rose-400 font-medium' : 'text-slate-500 dark:text-slate-400'"
                >
                  {{ formatMoney(c.balance) }}
                </span>
              </td>
              <td class="text-right">
                <AppBadge v-if="c.bottle_debt > 0" variant="warning">{{ c.bottle_debt }} ta</AppBadge>
                <span v-else class="text-slate-400">—</span>
              </td>
              <td class="text-right">
                <AppMenu>
                  <AppMenuItem @click="router.push({ name: 'customer-detail', params: { id: c.id } })">
                    Ochish
                  </AppMenuItem>
                  <AppMenuItem tone="danger" @click="onDelete(c)">
                    <TrashIcon class="h-4 w-4" />
                    O'chirish
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

    <AppDialog v-model:open="newOpen" title="Yangi mijoz">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Telefon</label>
          <input v-model="form.phone" class="input" placeholder="+998..." />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Ism familiya</label>
          <input v-model="form.full_name" class="input" />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="newOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="onCreate">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
