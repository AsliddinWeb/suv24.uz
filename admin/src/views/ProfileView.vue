<script setup lang="ts">
import { reactive, ref } from "vue";
import {
  UserIcon,
  PhoneIcon,
  ShieldCheckIcon,
  CalendarDaysIcon,
  KeyIcon,
  PencilSquareIcon,
  ArrowLeftOnRectangleIcon,
} from "@heroicons/vue/24/outline";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";
import { toast } from "@/lib/toast";
import PageHeader from "@/components/ui/PageHeader.vue";
import AppBadge from "@/components/ui/AppBadge.vue";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const savingProfile = ref(false);
const savingPwd = ref(false);

const profileForm = reactive({
  full_name: auth.user?.full_name || "",
  phone: auth.user?.phone || "",
});

const pwdForm = reactive({
  current_password: "",
  new_password: "",
  confirm_password: "",
});

const showCurrentPwd = ref(false);
const showNewPwd = ref(false);

const roleLabel: Record<string, string> = {
  super_admin: "Super admin",
  admin: "Admin",
  operator: "Operator",
  driver: "Haydovchi",
};

async function onSaveProfile() {
  if (!profileForm.full_name.trim() || !profileForm.phone.trim()) {
    toast.warning("Ism va telefon bo'sh bo'lmasin");
    return;
  }
  savingProfile.value = true;
  try {
    const updated = await authApi.updateMe({
      full_name: profileForm.full_name,
      phone: profileForm.phone,
    });
    auth.user = updated;
    localStorage.setItem("wdms.user", JSON.stringify(updated));
    toast.success("Profil yangilandi");
  } finally {
    savingProfile.value = false;
  }
}

async function onChangePassword() {
  if (pwdForm.new_password.length < 8) {
    toast.warning("Yangi parol kamida 8 belgi");
    return;
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    toast.warning("Yangi parollar mos kelmayapti");
    return;
  }
  savingPwd.value = true;
  try {
    await authApi.changePassword({
      current_password: pwdForm.current_password,
      new_password: pwdForm.new_password,
    });
    pwdForm.current_password = "";
    pwdForm.new_password = "";
    pwdForm.confirm_password = "";
    toast.success("Parol yangilandi");
  } finally {
    savingPwd.value = false;
  }
}

async function onLogout() {
  await auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Profil" subtitle="Shaxsiy ma'lumotlar va xavfsizlik" />

    <!-- Profile Hero -->
    <div class="card overflow-hidden">
      <div class="h-28 bg-gradient-to-br from-brand-500 via-brand-600 to-sky-500" />
      <div class="px-6 pb-6 -mt-12">
        <div class="flex items-end gap-4">
          <div
            class="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl
                   bg-gradient-to-br from-brand-400 to-brand-700 text-white text-3xl font-bold
                   ring-4 ring-white dark:ring-slate-900 shadow-lg"
          >
            {{ (auth.user?.full_name || "?").slice(0, 1).toUpperCase() }}
          </div>
          <div class="flex-1 pb-2">
            <h2 class="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {{ auth.user?.full_name }}
            </h2>
            <div class="flex items-center gap-2 mt-1">
              <AppBadge variant="primary">{{ roleLabel[auth.user?.role || ""] }}</AppBadge>
              <span class="text-sm text-slate-500 dark:text-slate-400">{{ auth.user?.phone }}</span>
            </div>
          </div>
          <button class="btn-secondary" @click="onLogout">
            <ArrowLeftOnRectangleIcon class="h-4 w-4" />
            Chiqish
          </button>
        </div>
      </div>
    </div>

    <!-- Info cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-5">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/50 dark:text-brand-400">
            <UserIcon class="h-5 w-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-slate-500 dark:text-slate-400">Ism</p>
            <p class="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
              {{ auth.user?.full_name }}
            </p>
          </div>
        </div>
      </div>
      <div class="card p-5">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">
            <PhoneIcon class="h-5 w-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-slate-500 dark:text-slate-400">Telefon</p>
            <p class="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
              {{ auth.user?.phone }}
            </p>
          </div>
        </div>
      </div>
      <div class="card p-5">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400">
            <ShieldCheckIcon class="h-5 w-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-slate-500 dark:text-slate-400">Rol</p>
            <p class="text-sm font-medium text-slate-900 dark:text-slate-100">
              {{ roleLabel[auth.user?.role || ""] }}
            </p>
          </div>
        </div>
      </div>
      <div class="card p-5">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600 dark:bg-sky-950/50 dark:text-sky-400">
            <CalendarDaysIcon class="h-5 w-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-slate-500 dark:text-slate-400">Holat</p>
            <p class="text-sm font-medium text-emerald-600 dark:text-emerald-400">Faol</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Forms -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Edit profile -->
      <div class="card p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950/50 dark:text-brand-400">
            <PencilSquareIcon class="h-5 w-5" />
          </div>
          <div>
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              Profilni tahrirlash
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Ism va telefon raqamini yangilang</p>
          </div>
        </div>

        <form class="space-y-4" @submit.prevent="onSaveProfile">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Ism familiya
            </label>
            <input v-model="profileForm.full_name" class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Telefon
            </label>
            <input v-model="profileForm.phone" class="input" placeholder="+998..." />
          </div>
          <button class="btn-primary w-full" type="submit" :disabled="savingProfile">
            <svg v-if="savingProfile" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
              <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
            </svg>
            Saqlash
          </button>
        </form>
      </div>

      <!-- Change password -->
      <div class="card p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400">
            <KeyIcon class="h-5 w-5" />
          </div>
          <div>
            <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">
              Parolni o'zgartirish
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Hisobingizni xavfsiz saqlang</p>
          </div>
        </div>

        <form class="space-y-4" @submit.prevent="onChangePassword">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Joriy parol
            </label>
            <input
              v-model="pwdForm.current_password"
              :type="showCurrentPwd ? 'text' : 'password'"
              class="input"
              autocomplete="current-password"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Yangi parol
            </label>
            <input
              v-model="pwdForm.new_password"
              :type="showNewPwd ? 'text' : 'password'"
              class="input"
              autocomplete="new-password"
              placeholder="Kamida 8 belgi"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Yangi parolni takrorlang
            </label>
            <input
              v-model="pwdForm.confirm_password"
              :type="showNewPwd ? 'text' : 'password'"
              class="input"
              autocomplete="new-password"
            />
          </div>
          <button class="btn-primary w-full" type="submit" :disabled="savingPwd">
            <svg v-if="savingPwd" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
              <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
            </svg>
            Parolni yangilash
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
