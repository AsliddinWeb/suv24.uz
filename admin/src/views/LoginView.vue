<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { toast } from "@/lib/toast";
import { EyeIcon, EyeSlashIcon } from "@heroicons/vue/20/solid";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const form = reactive({
  phone: "+998",
  password: "",
});
const loading = ref(false);
const showPassword = ref(false);

async function onSubmit() {
  if (!form.phone || !form.password) {
    toast.warning("Telefon va parolni kiriting");
    return;
  }
  loading.value = true;
  try {
    await auth.login(form.phone, form.password);
    toast.success("Xush kelibsiz");
    const nextParam = route.query.next as string | undefined;
    const defaultHome = auth.role === "platform_owner" ? "/platform" : "/app/dashboard";
    router.push(nextParam || defaultHome);
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Kirish xato");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="card p-8">
    <h2 class="text-xl font-semibold text-slate-900 dark:text-slate-100">
      Kirish
    </h2>
    <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
      Hisobingiz bilan tizimga kiring
    </p>

    <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
      <div>
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
          Telefon raqami
        </label>
        <input
          v-model="form.phone"
          type="tel"
          placeholder="+998..."
          autocomplete="username"
          class="input"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
          Parol
        </label>
        <div class="relative">
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            class="input pr-10"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            tabindex="-1"
            @click="showPassword = !showPassword"
          >
            <EyeSlashIcon v-if="showPassword" class="h-5 w-5" />
            <EyeIcon v-else class="h-5 w-5" />
          </button>
        </div>
      </div>

      <button type="submit" class="btn-primary w-full py-2.5" :disabled="loading">
        <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
          <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
        </svg>
        <span>Kirish</span>
      </button>
    </form>

  </div>
</template>
