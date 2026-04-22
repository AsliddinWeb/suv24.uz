<script setup lang="ts">
import { RouterView } from "vue-router";
import ThemeToggle from "@/components/ui/ThemeToggle.vue";
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4 relative">
    <div class="absolute top-4 right-4">
      <ThemeToggle />
    </div>

    <div class="pointer-events-none fixed inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-brand-400/20 dark:bg-brand-600/20 blur-3xl" />
      <div class="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-sky-400/20 dark:bg-sky-600/20 blur-3xl" />
    </div>

    <div class="relative w-full max-w-md">
      <div class="mb-8 text-center">
        <div class="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white font-bold text-lg shadow-lg">
          S
        </div>
        <h1 class="mt-4 text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">
          Suv24
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Suv yetkazish boshqaruv tizimi
        </p>
      </div>

      <RouterView />
    </div>
  </div>
</template>
