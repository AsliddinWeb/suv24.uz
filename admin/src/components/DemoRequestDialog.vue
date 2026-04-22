<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { CheckCircleIcon, SparklesIcon } from "@heroicons/vue/24/outline";
import AppDialog from "@/components/ui/AppDialog.vue";
import { leadsApi } from "@/api/leads";

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{
  (e: "update:open", v: boolean): void;
}>();

const submitting = ref(false);
const done = ref(false);
const error = ref<string | null>(null);

const form = reactive({
  full_name: "",
  phone: "+998",
  company_name: "",
  notes: "",
});

watch(
  () => props.open,
  (open) => {
    if (open) {
      submitting.value = false;
      done.value = false;
      error.value = null;
      form.full_name = "";
      form.phone = "+998";
      form.company_name = "";
      form.notes = "";
    }
  },
);

function close() {
  emit("update:open", false);
}

async function onSubmit() {
  error.value = null;
  if (form.full_name.trim().length < 2) {
    error.value = "Ism familiya to'liq bo'lsin";
    return;
  }
  if (form.phone.replace(/\D/g, "").length < 9) {
    error.value = "Telefon raqamni to'liq kiriting";
    return;
  }
  submitting.value = true;
  try {
    await leadsApi.submit({
      full_name: form.full_name.trim(),
      phone: form.phone.trim(),
      company_name: form.company_name.trim() || null,
      notes: form.notes.trim() || null,
      source: "landing",
    });
    done.value = true;
  } catch (e: any) {
    error.value =
      e?.response?.status === 429
        ? "Ko'p urinish qildingiz — biroz kuting"
        : e?.response?.data?.detail || "Yuborishda xato";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <AppDialog :open="open" @update:open="emit('update:open', $event)" title="" max-width="max-w-md">
    <!-- Success state -->
    <div v-if="done" class="text-center py-6 px-2">
      <div class="mx-auto h-14 w-14 rounded-full bg-emerald-100 flex items-center justify-center mb-4">
        <CheckCircleIcon class="h-8 w-8 text-emerald-600" />
      </div>
      <h3 class="text-xl font-bold text-slate-900">Rahmat!</h3>
      <p class="mt-2 text-sm text-slate-600">
        Arizangiz qabul qilindi. Menejerimiz 1 ish kuni ichida siz bilan bog'lanadi
        va demo ko'rsatadi.
      </p>
    </div>

    <!-- Form state -->
    <div v-else>
      <div class="flex items-center gap-3 mb-4">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white">
          <SparklesIcon class="h-5 w-5" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-slate-900">Bepul demo olish</h3>
          <p class="text-xs text-slate-500">Tez orada siz bilan bog'lanamiz</p>
        </div>
      </div>

      <form class="space-y-3" @submit.prevent="onSubmit">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5">
            Ism familiya <span class="text-rose-500">*</span>
          </label>
          <input
            v-model="form.full_name"
            class="input"
            placeholder="Masalan: Asliddin Abdujabborov"
            :disabled="submitting"
            autocomplete="name"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5">
            Telefon raqami <span class="text-rose-500">*</span>
          </label>
          <input
            v-model="form.phone"
            type="tel"
            class="input"
            placeholder="+998 90 123 45 67"
            :disabled="submitting"
            autocomplete="tel"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1.5">
            Kompaniya nomi
          </label>
          <input
            v-model="form.company_name"
            class="input"
            placeholder="Ixtiyoriy"
            :disabled="submitting"
          />
        </div>

        <div v-if="error" class="text-sm text-rose-600 bg-rose-50 rounded-lg px-3 py-2">
          {{ error }}
        </div>

        <p class="text-xs text-slate-500">
          Yuborish orqali biz bilan bog'lanishga rozilik bildirasiz.
        </p>
      </form>
    </div>

    <template #footer>
      <button
        v-if="done"
        class="btn-primary w-full"
        @click="close"
      >
        Yopish
      </button>
      <template v-else>
        <button class="btn-secondary" :disabled="submitting" @click="close">Bekor qilish</button>
        <button class="btn-primary" :disabled="submitting" @click="onSubmit">
          {{ submitting ? "Yuborilmoqda..." : "Yuborish" }}
        </button>
      </template>
    </template>
  </AppDialog>
</template>
