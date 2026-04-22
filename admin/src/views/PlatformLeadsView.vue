<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  MagnifyingGlassIcon,
  PhoneIcon,
  TrashIcon,
  PencilSquareIcon,
  ChatBubbleLeftRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
} from "@heroicons/vue/24/outline";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import {
  leadsApi,
  LEAD_STATUS_LABELS,
  LEAD_STATUS_COLORS,
  type LeadOut,
  type LeadStatus,
} from "@/api/leads";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

const confirm = useConfirm();

const leads = ref<LeadOut[]>([]);
const loading = ref(false);
const q = ref("");
const statusFilter = ref<LeadStatus | "">("");

const statusOptions = [
  { value: "", label: "Barcha" },
  ...(Object.entries(LEAD_STATUS_LABELS) as [LeadStatus, string][]).map(([v, l]) => ({
    value: v,
    label: l,
  })),
];

async function load() {
  loading.value = true;
  try {
    leads.value = await leadsApi.list({
      q: q.value.trim() || undefined,
      status: (statusFilter.value || undefined) as LeadStatus | undefined,
    });
  } finally {
    loading.value = false;
  }
}

let t: ReturnType<typeof setTimeout> | null = null;
function onSearch() {
  if (t) clearTimeout(t);
  t = setTimeout(load, 250);
}

onMounted(load);

// Edit dialog
const editOpen = ref(false);
const editing = ref<LeadOut | null>(null);
const editForm = reactive<{
  status: LeadStatus;
  notes: string;
}>({
  status: "new",
  notes: "",
});

function openEdit(lead: LeadOut) {
  editing.value = lead;
  editForm.status = lead.status;
  editForm.notes = lead.notes || "";
  editOpen.value = true;
}

async function saveEdit() {
  if (!editing.value) return;
  try {
    const updated = await leadsApi.update(editing.value.id, {
      status: editForm.status,
      notes: editForm.notes || null,
    });
    const idx = leads.value.findIndex((l) => l.id === updated.id);
    if (idx >= 0) leads.value[idx] = updated;
    toast.success("Saqlandi");
    editOpen.value = false;
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  }
}

async function quickStatus(lead: LeadOut, s: LeadStatus) {
  try {
    const updated = await leadsApi.update(lead.id, { status: s });
    const idx = leads.value.findIndex((l) => l.id === updated.id);
    if (idx >= 0) leads.value[idx] = updated;
    toast.success(`Holat: ${LEAD_STATUS_LABELS[s]}`);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Xato");
  }
}

async function onDelete(lead: LeadOut) {
  const ok = await confirm({
    title: "Leadni o'chirish",
    description: `${lead.full_name} arizasi o'chiriladi.`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await leadsApi.remove(lead.id);
  toast.success("O'chirildi");
  load();
}

const stats = computed(() => {
  const total = leads.value.length;
  const newCount = leads.value.filter((l) => l.status === "new").length;
  const converted = leads.value.filter((l) => l.status === "converted").length;
  return { total, new: newCount, converted };
});
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Mijoz arizalari" subtitle="Landing sahifadan kelgan demo so'rovlari">
      <template #actions>
        <button class="btn-ghost !p-2" :disabled="loading" @click="load" title="Yangilash">
          <ArrowPathIcon :class="['h-5 w-5', loading && 'animate-spin']" />
        </button>
      </template>
    </PageHeader>

    <!-- Stats strip -->
    <div class="grid grid-cols-3 gap-3">
      <div class="card p-4">
        <div class="flex items-center gap-2 text-slate-500 mb-1">
          <ChatBubbleLeftRightIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Jami ariza</span>
        </div>
        <div class="text-2xl font-bold text-slate-900 dark:text-slate-100">{{ stats.total }}</div>
      </div>
      <div class="card p-4">
        <div class="flex items-center gap-2 text-sky-600 mb-1">
          <ClockIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Yangi (kutmoqda)</span>
        </div>
        <div class="text-2xl font-bold text-sky-600">{{ stats.new }}</div>
      </div>
      <div class="card p-4">
        <div class="flex items-center gap-2 text-emerald-600 mb-1">
          <CheckCircleIcon class="h-4 w-4" />
          <span class="text-[10px] font-semibold uppercase tracking-wide">Mijoz bo'lgan</span>
        </div>
        <div class="text-2xl font-bold text-emerald-600">{{ stats.converted }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4 flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <MagnifyingGlassIcon class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-slate-400" />
        <input
          v-model="q"
          type="text"
          placeholder="Ism, telefon yoki kompaniya..."
          class="input pl-9"
          @input="onSearch"
        />
      </div>
      <div class="w-full sm:w-48">
        <AppSelect v-model="statusFilter" :options="statusOptions" @update:modelValue="load" />
      </div>
    </div>

    <!-- List -->
    <EmptyState v-if="!loading && !leads.length" title="Ariza yo'q" description="Landing sahifadan demo so'rovlar shu yerda paydo bo'ladi" />

    <div v-else class="space-y-3">
      <div
        v-for="lead in leads"
        :key="lead.id"
        class="card p-5"
        :class="lead.status === 'new' && 'ring-1 ring-sky-200 dark:ring-sky-900/50'"
      >
        <div class="flex items-start gap-4">
          <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white font-bold shrink-0">
            {{ lead.full_name.slice(0, 1).toUpperCase() }}
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-3 flex-wrap">
              <div class="min-w-0">
                <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
                  {{ lead.full_name }}
                </h3>
                <div class="flex items-center gap-2 flex-wrap mt-0.5 text-sm text-slate-600 dark:text-slate-400">
                  <a :href="`tel:${lead.phone}`" class="flex items-center gap-1 hover:text-brand-600">
                    <PhoneIcon class="h-3.5 w-3.5" />
                    {{ lead.phone }}
                  </a>
                  <span v-if="lead.company_name" class="text-slate-400">·</span>
                  <span v-if="lead.company_name">{{ lead.company_name }}</span>
                </div>
              </div>

              <AppBadge :variant="LEAD_STATUS_COLORS[lead.status]">
                {{ LEAD_STATUS_LABELS[lead.status] }}
              </AppBadge>
            </div>

            <p v-if="lead.notes" class="mt-2 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 rounded-lg px-3 py-2">
              {{ lead.notes }}
            </p>

            <div class="mt-3 flex items-center justify-between gap-2 flex-wrap">
              <span class="text-xs text-slate-500">
                {{ dayjs(lead.created_at).fromNow() }} · {{ lead.source }}
              </span>

              <div class="flex items-center gap-1.5 flex-wrap">
                <button
                  v-if="lead.status === 'new'"
                  class="btn-ghost text-xs !py-1 !px-2 text-amber-600"
                  @click="quickStatus(lead, 'contacted')"
                >
                  Bog'lanildi
                </button>
                <button
                  v-if="lead.status !== 'converted' && lead.status !== 'rejected'"
                  class="btn-ghost text-xs !py-1 !px-2 text-emerald-600"
                  @click="quickStatus(lead, 'converted')"
                >
                  <CheckCircleIcon class="h-3.5 w-3.5" />
                  Mijoz bo'ldi
                </button>
                <button
                  v-if="lead.status !== 'rejected'"
                  class="btn-ghost text-xs !py-1 !px-2 text-rose-500"
                  @click="quickStatus(lead, 'rejected')"
                >
                  <XCircleIcon class="h-3.5 w-3.5" />
                  Rad
                </button>
                <button class="btn-ghost !p-1.5" @click="openEdit(lead)" title="Izoh + holat">
                  <PencilSquareIcon class="h-4 w-4" />
                </button>
                <button class="btn-ghost !p-1.5 text-rose-500" @click="onDelete(lead)" title="O'chirish">
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit dialog -->
    <AppDialog v-model:open="editOpen" :title="editing ? editing.full_name : ''" max-width="max-w-md">
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5">Holat</label>
          <AppSelect
            v-model="editForm.status"
            :options="(Object.entries(LEAD_STATUS_LABELS) as [LeadStatus, string][]).map(([v, l]) => ({ value: v, label: l }))"
          />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5">Izoh</label>
          <textarea
            v-model="editForm.notes"
            class="input"
            rows="4"
            placeholder="Bog'lanish natijasi, qo'shimcha ma'lumotlar..."
          />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="editOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="saveEdit">Saqlash</button>
      </template>
    </AppDialog>
  </div>
</template>
