<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterView, useRoute, useRouter } from "vue-router";
import {
  HomeIcon,
  ShoppingBagIcon,
  UsersIcon,
  CubeIcon,
  TruckIcon,
  BanknotesIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
} from "@heroicons/vue/24/outline";
import { useAuthStore } from "@/stores/auth";
import ThemeToggle from "@/components/ui/ThemeToggle.vue";
import { toast } from "@/lib/toast";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const mobileOpen = ref(false);

const nav = computed(() => {
  const items: { path: string; label: string; icon: any; adminOnly?: boolean }[] = [
    { path: "/app/dashboard", label: "Dashboard", icon: HomeIcon },
    { path: "/app/orders", label: "Buyurtmalar", icon: ShoppingBagIcon },
    { path: "/app/customers", label: "Mijozlar", icon: UsersIcon },
    { path: "/app/products", label: "Mahsulotlar", icon: CubeIcon },
    { path: "/app/drivers", label: "Haydovchilar", icon: TruckIcon },
    { path: "/app/payments", label: "To'lovlar", icon: BanknotesIcon },
    { path: "/app/users", label: "Foydalanuvchilar", icon: UserGroupIcon, adminOnly: true },
    { path: "/app/settings", label: "Sozlamalar", icon: Cog6ToothIcon },
  ];
  return items.filter((i) => !i.adminOnly || auth.hasRole("super_admin", "admin"));
});

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + "/");
}

async function onLogout() {
  await auth.logout();
  toast.success("Chiqildi");
  router.push("/");
}

onMounted(() => {
  if (auth.isAuthenticated && !auth.company) {
    auth.loadCompany().catch(() => undefined);
  }
});
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
          <img
            v-if="auth.brandLogo"
            :src="auth.brandLogo"
            :alt="auth.brandName"
            class="h-8 w-8 rounded-lg object-cover bg-slate-100 dark:bg-slate-800"
          />
          <div
            v-else
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-white font-bold text-sm shrink-0"
          >
            {{ auth.brandInitial }}
          </div>
          <span class="font-semibold text-slate-900 dark:text-slate-100 tracking-tight truncate">
            {{ auth.brandName }}
          </span>
        </div>
        <button type="button" class="btn-ghost !p-1.5 lg:hidden" @click="mobileOpen = false">
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <div class="p-4">
        <div class="relative">
          <MagnifyingGlassIcon class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Qidirish..."
            class="input pl-9 input-sm bg-slate-50 dark:bg-slate-800 border-transparent dark:border-transparent"
          />
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto px-3 space-y-1">
        <router-link
          v-for="item in nav"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            isActive(item.path)
              ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/50 dark:text-brand-400'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100',
          ]"
          @click="mobileOpen = false"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="border-t border-slate-200 dark:border-slate-800 p-4">
        <div class="flex items-center gap-2">
          <router-link
            to="/app/profile"
            class="flex items-center gap-3 flex-1 min-w-0 rounded-lg px-2 py-1.5 -mx-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            @click="mobileOpen = false"
          >
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-white text-sm font-medium">
              {{ (auth.user?.full_name || "").slice(0, 1).toUpperCase() || "?" }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                {{ auth.user?.full_name }}
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400 truncate">
                {{ auth.user?.role }}
              </p>
            </div>
          </router-link>
          <button type="button" class="btn-ghost !p-1.5" title="Chiqish" @click="onLogout">
            <ArrowRightOnRectangleIcon class="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>

    <div class="lg:pl-64">
      <header
        class="sticky top-0 z-20 bg-white/80 dark:bg-slate-950/80 backdrop-blur border-b border-slate-200 dark:border-slate-800"
      >
        <div class="h-16 px-4 sm:px-6 flex items-center justify-between gap-4">
          <button type="button" class="btn-ghost !p-2 lg:hidden" @click="mobileOpen = true">
            <Bars3Icon class="h-5 w-5" />
          </button>
          <div class="flex-1" />
          <ThemeToggle />
        </div>
      </header>

      <main class="p-4 sm:p-6 lg:p-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>
