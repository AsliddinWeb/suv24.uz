<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  BuildingOffice2Icon,
  PhotoIcon,
  ArrowUpTrayIcon,
  XMarkIcon,
} from "@heroicons/vue/24/outline";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";
import { companiesApi, resolveMediaUrl, type CompanyUpdate } from "@/api/companies";
import { toast } from "@/lib/toast";
import PageHeader from "@/components/ui/PageHeader.vue";

const auth = useAuthStore();
const theme = useThemeStore();

const canEditCompany = auth.hasRole("super_admin", "admin");
const loadingCompany = ref(false);
const saving = ref(false);
const uploading = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

const form = reactive({
  name: "",
  short_name: "",
  phone: "",
  support_phone: "",
  address: "",
});

const logoUrl = computed(() => resolveMediaUrl(auth.company?.logo_url));

function hydrateForm() {
  const c = auth.company;
  form.name = c?.name ?? "";
  form.short_name = c?.short_name ?? "";
  form.phone = c?.phone ?? "";
  form.support_phone = c?.support_phone ?? "";
  form.address = c?.address ?? "";
}

onMounted(async () => {
  loadingCompany.value = true;
  try {
    await auth.loadCompany();
  } catch {
    // ignore
  } finally {
    loadingCompany.value = false;
    hydrateForm();
  }
});

async function saveCompany() {
  if (!canEditCompany) return;
  saving.value = true;
  try {
    const payload: CompanyUpdate = {
      name: form.name || null,
      short_name: form.short_name || null,
      phone: form.phone || null,
      support_phone: form.support_phone || null,
      address: form.address || null,
    };
    const updated = await companiesApi.update(payload);
    auth.setCompany(updated);
    toast.success("Kompaniya saqlandi");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Saqlab bo'lmadi");
  } finally {
    saving.value = false;
  }
}

function pickLogo() {
  fileInput.value?.click();
}

async function onLogoChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) {
    toast.error("Fayl 2 MB dan katta bo'lmasligi kerak");
    target.value = "";
    return;
  }
  uploading.value = true;
  try {
    const updated = await companiesApi.uploadLogo(file);
    auth.setCompany(updated);
    toast.success("Logo yuklandi");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "Logoni yuklab bo'lmadi");
  } finally {
    uploading.value = false;
    target.value = "";
  }
}

async function removeLogo() {
  if (!canEditCompany) return;
  uploading.value = true;
  try {
    const updated = await companiesApi.update({ logo_url: null });
    auth.setCompany(updated);
    toast.success("Logo o'chirildi");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || "O'chirib bo'lmadi");
  } finally {
    uploading.value = false;
  }
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <PageHeader title="Sozlamalar" subtitle="Kompaniya, hisob va ko'rinish" />

    <!-- Company -->
    <div class="card p-6">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 dark:bg-brand-950/40 text-brand-600">
          <BuildingOffice2Icon class="h-5 w-5" />
        </div>
        <div>
          <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Kompaniya</h3>
          <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Bu ma'lumotlar admin panel va haydovchilar ilovasida ko'rinadi
          </p>
        </div>
      </div>

      <div v-if="loadingCompany" class="mt-5 text-sm text-slate-500">Yuklanmoqda...</div>

      <form v-else class="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-4" @submit.prevent="saveCompany">
        <!-- Logo upload -->
        <div class="sm:col-span-2 flex items-center gap-4">
          <div class="h-20 w-20 rounded-2xl overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center shrink-0">
            <img v-if="logoUrl" :src="logoUrl" :alt="form.name" class="h-full w-full object-cover" />
            <PhotoIcon v-else class="h-7 w-7 text-slate-400" />
          </div>
          <div class="flex-1 min-w-0">
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">
              Logo
            </label>
            <div class="flex items-center gap-2 flex-wrap">
              <input
                ref="fileInput"
                type="file"
                accept="image/png,image/jpeg,image/webp,image/svg+xml"
                class="hidden"
                @change="onLogoChange"
              />
              <button
                type="button"
                class="btn-secondary inline-flex items-center gap-1.5"
                :disabled="!canEditCompany || uploading"
                @click="pickLogo"
              >
                <ArrowUpTrayIcon class="h-4 w-4" />
                {{ uploading ? "Yuklanmoqda..." : logoUrl ? "Almashtirish" : "Rasm yuklash" }}
              </button>
              <button
                v-if="logoUrl"
                type="button"
                class="btn-ghost inline-flex items-center gap-1.5 text-rose-500"
                :disabled="!canEditCompany || uploading"
                @click="removeLogo"
              >
                <XMarkIcon class="h-4 w-4" />
                O'chirish
              </button>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-2">
              PNG, JPG, WebP yoki SVG · maks 2 MB · kvadrat (ideal 512×512px)
            </p>
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">
            Kompaniya nomi
          </label>
          <input v-model="form.name" type="text" :disabled="!canEditCompany || saving" class="input" />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">
            Qisqa nom (brand)
          </label>
          <input
            v-model="form.short_name"
            type="text"
            maxlength="32"
            placeholder="Masalan: AquaCo"
            :disabled="!canEditCompany || saving"
            class="input"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">
            Telefon
          </label>
          <input v-model="form.phone" type="tel" placeholder="+998 90 123 45 67" :disabled="!canEditCompany || saving" class="input" />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">
            Qo'llab-quvvatlash telefoni
          </label>
          <input v-model="form.support_phone" type="tel" placeholder="+998 71 123 45 67" :disabled="!canEditCompany || saving" class="input" />
        </div>

        <div class="sm:col-span-2">
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">
            Manzil
          </label>
          <input v-model="form.address" type="text" :disabled="!canEditCompany || saving" class="input" />
        </div>

        <div class="sm:col-span-2 flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-800">
          <div class="text-xs text-slate-500 dark:text-slate-400">
            <span v-if="auth.company?.slug">Slug: <code class="font-mono">{{ auth.company.slug }}</code></span>
            <span v-if="auth.company?.slug" class="mx-2">·</span>
            <span>Timezone: {{ auth.company?.timezone }}</span>
          </div>
          <button
            v-if="canEditCompany"
            type="submit"
            :disabled="saving"
            class="btn-primary"
          >
            {{ saving ? "Saqlanmoqda..." : "Saqlash" }}
          </button>
          <p v-else class="text-xs text-slate-500">Tahrirlash uchun admin huquqi kerak</p>
        </div>
      </form>
    </div>

    <!-- Account -->
    <div class="card p-6">
      <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Hisob ma'lumotlari</h3>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Joriy foydalanuvchi</p>

      <dl class="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <dt class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Ism</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">{{ auth.user?.full_name }}</dd>
        </div>
        <div>
          <dt class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Telefon</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">{{ auth.user?.phone }}</dd>
        </div>
        <div>
          <dt class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Rol</dt>
          <dd class="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100 capitalize">{{ auth.user?.role }}</dd>
        </div>
      </dl>
    </div>

    <!-- Theme -->
    <div class="card p-6">
      <h3 class="text-base font-semibold text-slate-900 dark:text-slate-100">Ko'rinish</h3>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Tungi yoki kunduzgi rejim</p>

      <div class="mt-5 grid grid-cols-2 gap-3">
        <button
          type="button"
          :class="[
            'relative flex flex-col items-center gap-2 rounded-xl border p-4 transition',
            theme.theme === 'light'
              ? 'border-brand-500 ring-2 ring-brand-100 dark:ring-brand-950/60'
              : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50',
          ]"
          @click="theme.set('light')"
        >
          <SunIcon class="h-6 w-6 text-amber-500" />
          <span class="text-sm font-medium text-slate-900 dark:text-slate-100">Kunduzgi</span>
        </button>
        <button
          type="button"
          :class="[
            'relative flex flex-col items-center gap-2 rounded-xl border p-4 transition',
            theme.theme === 'dark'
              ? 'border-brand-500 ring-2 ring-brand-100 dark:ring-brand-950/60'
              : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50',
          ]"
          @click="theme.set('dark')"
        >
          <MoonIcon class="h-6 w-6 text-indigo-500" />
          <span class="text-sm font-medium text-slate-900 dark:text-slate-100">Tungi</span>
        </button>
      </div>

      <p class="mt-3 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
        <ComputerDesktopIcon class="h-3.5 w-3.5" />
        Birinchi marta tizimning sozlamalaridan olinadi.
      </p>
    </div>
  </div>
</template>
