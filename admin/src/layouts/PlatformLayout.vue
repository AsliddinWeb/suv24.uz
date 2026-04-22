<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterView, useRoute, useRouter } from "vue-router";
import {
  HomeIcon,
  BuildingOffice2Icon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/vue/24/outline";
import { useAuthStore } from "@/stores/auth";
import ThemeToggle from "@/components/ui/ThemeToggle.vue";
import { toast } from "@/lib/toast";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const mobileOpen = ref(false);

const nav = computed(() => [
  { path: "/platform", label: "Umumiy holat", icon: HomeIcon, exact: true },
  { path: "/platform/companies", label: "Kompaniyalar", icon: BuildingOffice2Icon },
  { path: "/platform/leads", label: "Mijoz arizalari", icon: ChatBubbleLeftRightIcon },
]);

function isActive(path: string, exact?: boolean) {
  if (exact) return route.path === path;
  return route.path === path || route.path.startsWith(path + "/");
}

async function onLogout() {
  await auth.logout();
  toast.success("Chiqildi");
  router.push("/");
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950">
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-30 bg-slate-900/50 backdrop-blur-sm lg:hidden"
      @click="mobileOpen = false"
    />

    <aside
      :class="[
        'fixed inset-y-0 left-0 z-40 w-64 border-r border-slate-200 dark:border-slate-800',
        'bg-white dark:bg-slate-900 flex flex-col transition-transform duration-200',
        mobileOpen ? 'translate-x-0' : '-translate-x-full',
        'lg:translate-x-0',
      ]"
    >
      <div class="h-16 px-6 flex items-center justify-between border-b border-slate-200 dark:border-slate-800">
        <div class="flex items-center gap-2 min-w-0">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-indigo-600 text-white font-bold text-sm shrink-0"
          >
            S
          </div>
          <div class="min-w-0">
            <div class="font-semibold text-slate-900 dark:text-slate-100 tracking-tight truncate">
              Suv24
            </div>
            <div class="text-[10px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
              Platforma
            </div>
          </div>
        </div>
        <button type="button" class="btn-ghost !p-1.5 lg:hidden" @click="mobileOpen = false">
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <nav class="flex-1 p-4 space-y-1">
        <RouterLink
          v-for="item in nav"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition',
            isActive(item.path, item.exact)
              ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/40 dark:text-brand-300'
              : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/70',
          ]"
          @click="mobileOpen = false"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="border-t border-slate-200 dark:border-slate-800 p-4 space-y-3">
        <div class="flex items-center gap-3">
          <div class="h-9 w-9 rounded-full bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white text-sm font-semibold shrink-0">
            {{ (auth.user?.full_name || "?").slice(0, 1) }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
              {{ auth.user?.full_name }}
            </div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">Owner</div>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <ThemeToggle class="flex-1 !justify-start" />
          <button
            type="button"
            class="btn-ghost !p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40"
            @click="onLogout"
          >
            <ArrowRightOnRectangleIcon class="h-5 w-5" />
          </button>
        </div>
      </div>
    </aside>

    <header class="lg:hidden sticky top-0 z-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur border-b border-slate-200 dark:border-slate-800 px-4 h-14 flex items-center gap-3">
      <button type="button" class="btn-ghost !p-2" @click="mobileOpen = true">
        <Bars3Icon class="h-5 w-5" />
      </button>
      <span class="font-semibold">Suv24 Platforma</span>
    </header>

    <main class="lg:pl-64">
      <div class="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        <RouterView />
      </div>
    </main>
  </div>
</template>
