<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import {
  PlusIcon,
  TrashIcon,
  PencilSquareIcon,
  KeyIcon,
  PauseCircleIcon,
  PlayCircleIcon,
} from "@heroicons/vue/20/solid";
import { usersApi } from "@/api/users";
import { toast } from "@/lib/toast";
import { useConfirm } from "@/lib/confirm";
import { useAuthStore } from "@/stores/auth";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import AppDialog from "@/components/ui/AppDialog.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import AppMenu from "@/components/ui/AppMenu.vue";
import AppMenuItem from "@/components/ui/AppMenuItem.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { UserOut, UserRole } from "@/types/api";

const auth = useAuthStore();
const confirm = useConfirm();

const items = ref<UserOut[]>([]);
const loading = ref(false);

// Create dialog
const newOpen = ref(false);
const createForm = reactive<{
  phone: string;
  password: string;
  full_name: string;
  role: UserRole;
}>({
  phone: "",
  password: "",
  full_name: "",
  role: "operator",
});

// Edit dialog
const editOpen = ref(false);
const editing = ref<UserOut | null>(null);
const editForm = reactive<{
  full_name: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
}>({ full_name: "", phone: "", role: "operator", is_active: true });

// Password dialog
const pwdOpen = ref(false);
const pwdTarget = ref<UserOut | null>(null);
const newPassword = ref("");

const roleOptions = [
  { value: "admin" as UserRole, label: "Admin" },
  { value: "operator" as UserRole, label: "Operator" },
  { value: "driver" as UserRole, label: "Haydovchi" },
];

const roleLabel: Record<UserRole, string> = {
  super_admin: "Super admin",
  admin: "Admin",
  operator: "Operator",
  driver: "Haydovchi",
};

const roleVariant: Record<UserRole, "success" | "warning" | "info" | "neutral" | "primary"> = {
  super_admin: "primary",
  admin: "warning",
  operator: "info",
  driver: "success",
};

async function load() {
  loading.value = true;
  try {
    items.value = await usersApi.list();
  } finally {
    loading.value = false;
  }
}

onMounted(load);

async function onCreate() {
  if (!createForm.phone || !createForm.password || !createForm.full_name) {
    toast.warning("Barcha maydonlar majburiy");
    return;
  }
  await usersApi.create({ ...createForm });
  newOpen.value = false;
  createForm.phone = "";
  createForm.password = "";
  createForm.full_name = "";
  createForm.role = "operator";
  load();
  toast.success("Yaratildi");
}

function openEdit(u: UserOut) {
  editing.value = u;
  editForm.full_name = u.full_name;
  editForm.phone = u.phone;
  editForm.role = u.role;
  editForm.is_active = u.is_active;
  editOpen.value = true;
}

async function onEdit() {
  if (!editing.value) return;
  if (!editForm.full_name || !editForm.phone) {
    toast.warning("Ism va telefon majburiy");
    return;
  }
  const body: Record<string, any> = {
    full_name: editForm.full_name,
    phone: editForm.phone,
    is_active: editForm.is_active,
  };
  if (editing.value.role !== "super_admin") body.role = editForm.role;
  await usersApi.update(editing.value.id, body);
  editOpen.value = false;
  load();
  toast.success("Yangilandi");
}

function openPasswordReset(u: UserOut) {
  pwdTarget.value = u;
  newPassword.value = "";
  pwdOpen.value = true;
}

async function onResetPassword() {
  if (!pwdTarget.value) return;
  if (newPassword.value.length < 8) {
    toast.warning("Parol kamida 8 belgidan iborat bo'lsin");
    return;
  }
  await usersApi.resetPassword(pwdTarget.value.id, newPassword.value);
  pwdOpen.value = false;
  toast.success("Parol yangilandi");
}

async function onToggleActive(u: UserOut) {
  if (u.id === auth.user?.id) {
    toast.warning("O'zingizni nofaol qila olmaysiz");
    return;
  }
  const nextActive = !u.is_active;
  const ok = await confirm({
    title: nextActive ? "Faollashtirish" : "Nofaol qilish",
    description: `${u.full_name} — ${nextActive ? "faollashtirishni" : "nofaol qilishni"} tasdiqlaysizmi?`,
    confirmLabel: nextActive ? "Faollashtirish" : "Nofaol qilish",
    tone: nextActive ? "primary" : "warning",
  });
  if (!ok) return;
  await usersApi.update(u.id, { is_active: nextActive });
  load();
  toast.success(nextActive ? "Faollashtirildi" : "Nofaol qilindi");
}

async function onDelete(u: UserOut) {
  if (u.id === auth.user?.id) {
    toast.warning("O'zingizni o'chira olmaysiz");
    return;
  }
  const ok = await confirm({
    title: "Foydalanuvchini o'chirish",
    description: `${u.full_name} (${u.phone}) o'chiriladi.`,
    confirmLabel: "O'chirish",
    tone: "danger",
  });
  if (!ok) return;
  await usersApi.remove(u.id);
  toast.success("O'chirildi");
  load();
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Foydalanuvchilar" subtitle="Xodimlar va haydovchilar">
      <template #actions>
        <button class="btn-primary" @click="newOpen = true">
          <PlusIcon class="h-4 w-4" />
          Yangi foydalanuvchi
        </button>
      </template>
    </PageHeader>

    <div class="card">
      <EmptyState v-if="!loading && !items.length" title="Foydalanuvchi yo'q" />

      <div v-else class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Ism</th>
              <th>Telefon</th>
              <th>Rol</th>
              <th>Holat</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in items" :key="u.id">
              <td>
                <div class="flex items-center gap-3">
                  <div class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-brand-400 to-brand-600 text-white text-xs font-medium">
                    {{ u.full_name.slice(0, 1).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-medium text-slate-900 dark:text-slate-100">{{ u.full_name }}</div>
                    <div v-if="u.id === auth.user?.id" class="text-[10px] font-medium text-brand-600 dark:text-brand-400 mt-0.5">
                      Siz
                    </div>
                  </div>
                </div>
              </td>
              <td class="text-slate-500 dark:text-slate-400">{{ u.phone }}</td>
              <td>
                <AppBadge :variant="roleVariant[u.role]">{{ roleLabel[u.role] }}</AppBadge>
              </td>
              <td>
                <AppBadge :variant="u.is_active ? 'success' : 'neutral'">
                  {{ u.is_active ? "Faol" : "Nofaol" }}
                </AppBadge>
              </td>
              <td class="text-right">
                <AppMenu>
                  <AppMenuItem @click="openEdit(u)">
                    <PencilSquareIcon class="h-4 w-4" />
                    Tahrirlash
                  </AppMenuItem>
                  <AppMenuItem @click="openPasswordReset(u)">
                    <KeyIcon class="h-4 w-4" />
                    Parolni tiklash
                  </AppMenuItem>
                  <AppMenuItem
                    v-if="u.id !== auth.user?.id"
                    @click="onToggleActive(u)"
                  >
                    <component :is="u.is_active ? PauseCircleIcon : PlayCircleIcon" class="h-4 w-4" />
                    {{ u.is_active ? "Nofaol qilish" : "Faollashtirish" }}
                  </AppMenuItem>
                  <AppMenuItem
                    v-if="u.id !== auth.user?.id"
                    tone="danger"
                    @click="onDelete(u)"
                  >
                    <TrashIcon class="h-4 w-4" />
                    O'chirish
                  </AppMenuItem>
                </AppMenu>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create dialog -->
    <AppDialog v-model:open="newOpen" title="Yangi foydalanuvchi">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Ism familiya</label>
          <input v-model="createForm.full_name" class="input" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Telefon</label>
          <input v-model="createForm.phone" class="input" placeholder="+998..." />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Parol</label>
          <input v-model="createForm.password" type="password" class="input" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Rol</label>
          <AppSelect v-model="createForm.role" :options="roleOptions" />
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="newOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="onCreate">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Edit dialog -->
    <AppDialog v-model:open="editOpen" :title="`Tahrirlash: ${editing?.full_name}`">
      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Ism familiya</label>
          <input v-model="editForm.full_name" class="input" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Telefon</label>
          <input v-model="editForm.phone" class="input" />
        </div>
        <div v-if="editing?.role !== 'super_admin'">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Rol</label>
          <AppSelect v-model="editForm.role" :options="roleOptions" />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input
            v-model="editForm.is_active"
            type="checkbox"
            class="rounded text-brand-600"
            :disabled="editing?.id === auth.user?.id"
          />
          <span class="text-slate-700 dark:text-slate-300">Faol</span>
        </label>
      </div>
      <template #footer>
        <button class="btn-secondary" @click="editOpen = false">Bekor qilish</button>
        <button class="btn-primary" @click="onEdit">Saqlash</button>
      </template>
    </AppDialog>

    <!-- Password reset dialog -->
    <AppDialog v-model:open="pwdOpen" :title="`Parolni tiklash: ${pwdTarget?.full_name}`">
      <div class="space-y-3">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Yangi parolni kiriting. Kamida 8 belgi.
        </p>
        <input v-model="newPassword" type="password" class="input" placeholder="••••••••" />
      </div>
      <template #footer>
        <button class="btn-secondary" @click="pwdOpen = false">Bekor qilish</button>
        <button class="btn-primary" :disabled="newPassword.length < 8" @click="onResetPassword">
          Yangilash
        </button>
      </template>
    </AppDialog>
  </div>
</template>
