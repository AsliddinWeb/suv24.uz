<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import DemoRequestDialog from "@/components/DemoRequestDialog.vue";

const router = useRouter();
const period = ref<"monthly" | "yearly">("monthly");
const demoOpen = ref(false);

function goLogin() {
  router.push("/login");
}

function openDemo() {
  demoOpen.value = true;
}

function scrollTo(selector: string, e?: Event) {
  e?.preventDefault();
  const el = document.querySelector(selector);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

onMounted(() => {
  // reset dark mode class for landing (landing is always light)
  document.documentElement.classList.remove("dark");
});
</script>

<template>
  <div class="min-h-screen bg-white text-slate-900">
    <!-- Nav -->
    <header class="fixed top-0 inset-x-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 py-4">
        <nav class="bg-white/80 backdrop-blur-md border border-white/60 shadow-sm rounded-2xl px-4 sm:px-6 py-3 flex items-center justify-between">
          <a href="#" class="flex items-center gap-2">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 text-white font-extrabold shadow-md">S</div>
            <span class="text-lg font-extrabold tracking-tight">Suv24</span>
          </a>
          <div class="hidden lg:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" @click="scrollTo('#features', $event)" class="hover:text-slate-900 transition-colors">Imkoniyatlar</a>
            <a href="#how" @click="scrollTo('#how', $event)" class="hover:text-slate-900 transition-colors">Qanday ishlaydi</a>
            <a href="#pricing" @click="scrollTo('#pricing', $event)" class="hover:text-slate-900 transition-colors">Tariflar</a>
            <a href="#faq" @click="scrollTo('#faq', $event)" class="hover:text-slate-900 transition-colors">FAQ</a>
          </div>
          <div class="flex items-center gap-2">
            <button @click="goLogin" class="hidden sm:inline-flex px-4 py-2 text-sm font-semibold text-slate-700 hover:text-slate-900">
              Kirish
            </button>
            <a href="#pricing" @click="scrollTo('#pricing', $event)" class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition-colors">
              Bepul sinash
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clip-rule="evenodd"/></svg>
            </a>
          </div>
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative pt-32 sm:pt-40 pb-20 overflow-hidden bg-gradient-to-b from-sky-50 via-indigo-50 to-white">
      <div class="absolute inset-0 -z-10 overflow-hidden">
        <div class="absolute top-20 -right-40 h-[500px] w-[500px] rounded-full bg-brand-300/40 blur-3xl animate-blob-1"></div>
        <div class="absolute top-80 -left-40 h-[500px] w-[500px] rounded-full bg-indigo-300/40 blur-3xl animate-blob-2"></div>
        <div class="absolute bottom-0 left-1/2 h-[400px] w-[400px] rounded-full bg-sky-300/30 blur-3xl -translate-x-1/2"></div>
      </div>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 text-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 text-sm font-semibold mb-6 shadow-sm">
          <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          14 kun bepul sinab ko'ring
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] max-w-4xl mx-auto">
          Suv biznesingizni
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-brand-600 via-indigo-600 to-sky-500">qog'ozdan</span><br class="hidden sm:block" />
          ekranga ko'chiring
        </h1>
        <p class="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Buyurtma, mijoz, haydovchi va to'lov — bitta ekranda.
          Operator kuniga 100+ buyurtma bemalol boshqaradi, qarz esdan chiqmaydi, idish yo'qolmaydi.
        </p>

        <div class="mt-10 flex flex-wrap items-center justify-center gap-3">
          <a href="#pricing" @click="scrollTo('#pricing', $event)" class="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-br from-brand-600 to-indigo-600 text-white font-semibold shadow-lg shadow-brand-600/25 hover:shadow-xl hover:-translate-y-0.5 transition-all text-base">
            14 kun bepul sinash
            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clip-rule="evenodd"/></svg>
          </a>
          <a href="#demo" @click="scrollTo('#demo', $event)" class="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-white border border-slate-200 text-slate-800 font-semibold hover:border-slate-300 hover:shadow-md transition-all text-base">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
            Video demo
          </a>
        </div>

        <!-- Mockup -->
        <div id="demo" class="mt-16 relative max-w-5xl mx-auto">
          <div class="absolute -inset-x-20 top-20 h-64 bg-gradient-to-r from-brand-500/20 via-indigo-500/20 to-sky-500/20 blur-3xl -z-10"></div>
          <div class="relative rounded-2xl shadow-2xl shadow-slate-900/20 ring-1 ring-slate-900/10 overflow-hidden animate-float">
            <div class="bg-slate-100 border-b border-slate-200 px-4 py-3 flex items-center gap-2">
              <div class="flex gap-1.5">
                <div class="h-3 w-3 rounded-full bg-rose-400"></div>
                <div class="h-3 w-3 rounded-full bg-amber-400"></div>
                <div class="h-3 w-3 rounded-full bg-emerald-400"></div>
              </div>
              <div class="flex-1 mx-4 bg-white rounded-md px-3 py-1 text-xs text-slate-500">app.suv24.uz/dashboard</div>
            </div>
            <div class="bg-slate-50 p-5 sm:p-6">
              <!-- Hero like real dashboard -->
              <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-indigo-600 to-sky-500 p-5 sm:p-6 text-white shadow-lg mb-5">
                <div class="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-white/10 blur-2xl pointer-events-none"></div>
                <div class="relative flex items-center justify-between gap-4">
                  <div>
                    <p class="text-brand-100 text-xs sm:text-sm">Xayrli kun, Admin 👋</p>
                    <h3 class="mt-1 text-xl sm:text-2xl font-bold tracking-tight">Bugungi holat</h3>
                    <p class="text-brand-100 text-xs mt-1">22 aprel 2026, chorshanba · 09:41</p>
                  </div>
                  <div class="rounded-xl bg-white/15 backdrop-blur px-3 py-2 text-right shrink-0">
                    <p class="text-[10px] text-brand-100 uppercase tracking-wide">7 kunlik tushum</p>
                    <p class="text-base sm:text-lg font-bold">18.4M so'm</p>
                  </div>
                </div>
              </div>

              <!-- KPI cards (match real dashboard style) -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-5">
                <div class="relative overflow-hidden rounded-2xl p-4 text-white shadow-soft bg-gradient-to-br from-emerald-500 to-teal-600">
                  <div class="absolute -top-6 -right-6 h-20 w-20 rounded-full bg-white/10 blur-xl pointer-events-none"></div>
                  <div class="relative">
                    <p class="text-[10px] font-medium uppercase tracking-wide text-white/80">Bugungi tushum</p>
                    <p class="mt-1 text-xl sm:text-2xl font-bold truncate">3.2M so'm</p>
                    <p class="text-[10px] text-white/75">+18% kechaga nisbatan</p>
                  </div>
                </div>
                <div class="relative overflow-hidden rounded-2xl p-4 text-white shadow-soft bg-gradient-to-br from-brand-500 to-indigo-600">
                  <div class="absolute -top-6 -right-6 h-20 w-20 rounded-full bg-white/10 blur-xl pointer-events-none"></div>
                  <div class="relative">
                    <p class="text-[10px] font-medium uppercase tracking-wide text-white/80">Faol buyurtmalar</p>
                    <p class="mt-1 text-xl sm:text-2xl font-bold">47</p>
                    <p class="text-[10px] text-white/75">12 yo'lda, 35 biriktirilgan</p>
                  </div>
                </div>
                <div class="relative overflow-hidden rounded-2xl p-4 text-white shadow-soft bg-gradient-to-br from-amber-500 to-orange-600">
                  <div class="absolute -top-6 -right-6 h-20 w-20 rounded-full bg-white/10 blur-xl pointer-events-none"></div>
                  <div class="relative">
                    <p class="text-[10px] font-medium uppercase tracking-wide text-white/80">Haydovchilar</p>
                    <p class="mt-1 text-xl sm:text-2xl font-bold">8/12</p>
                    <p class="text-[10px] text-white/75">smenada</p>
                  </div>
                </div>
                <div class="relative overflow-hidden rounded-2xl p-4 text-white shadow-soft bg-gradient-to-br from-rose-500 to-pink-600">
                  <div class="absolute -top-6 -right-6 h-20 w-20 rounded-full bg-white/10 blur-xl pointer-events-none"></div>
                  <div class="relative">
                    <p class="text-[10px] font-medium uppercase tracking-wide text-white/80">Mijozlar</p>
                    <p class="mt-1 text-xl sm:text-2xl font-bold">1,284</p>
                    <p class="text-[10px] text-white/75">bazadagi jami</p>
                  </div>
                </div>
              </div>

              <!-- Recent orders card -->
              <div class="rounded-2xl bg-white border border-slate-200 p-4 sm:p-5">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-semibold text-slate-900">So'nggi buyurtmalar</h4>
                  <span class="text-xs text-brand-600 font-medium">Barchasi →</span>
                </div>
                <div class="space-y-2">
                  <div class="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3 text-sm">
                    <span class="font-semibold text-brand-600">#1005</span>
                    <span class="px-2.5 py-1 rounded-full bg-emerald-500 text-white text-xs font-semibold">Yetkazildi</span>
                    <span class="text-slate-600 font-medium">96 000 so'm</span>
                  </div>
                  <div class="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3 text-sm">
                    <span class="font-semibold text-brand-600">#1004</span>
                    <span class="px-2.5 py-1 rounded-full bg-brand-500 text-white text-xs font-semibold">Yo'lda</span>
                    <span class="text-slate-600 font-medium">64 000 so'm</span>
                  </div>
                  <div class="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3 text-sm">
                    <span class="font-semibold text-brand-600">#1003</span>
                    <span class="px-2.5 py-1 rounded-full bg-amber-400 text-amber-950 text-xs font-semibold">Biriktirildi</span>
                    <span class="text-slate-600 font-medium">32 000 so'm</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Benefits bar -->
    <section class="py-12 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="flex items-start gap-3 rounded-2xl p-5 bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500 text-white">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <div>
            <p class="font-bold text-emerald-900">10 daqiqada</p>
            <p class="text-xs text-emerald-700 mt-0.5">to'liq sozlash</p>
          </div>
        </div>
        <div class="flex items-start gap-3 rounded-2xl p-5 bg-gradient-to-br from-brand-50 to-sky-50 border border-brand-100">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500 text-white">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>
          </div>
          <div>
            <p class="font-bold text-brand-900">O'zbek tilida</p>
            <p class="text-xs text-brand-700 mt-0.5">hammasi</p>
          </div>
        </div>
        <div class="flex items-start gap-3 rounded-2xl p-5 bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-100">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500 text-white">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" /></svg>
          </div>
          <div>
            <p class="font-bold text-amber-900">Naqd + karta</p>
            <p class="text-xs text-amber-700 mt-0.5">Payme yaqinda</p>
          </div>
        </div>
        <div class="flex items-start gap-3 rounded-2xl p-5 bg-gradient-to-br from-rose-50 to-pink-50 border border-rose-100">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-500 text-white">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75" /></svg>
          </div>
          <div>
            <p class="font-bold text-rose-900">Tez yordam</p>
            <p class="text-xs text-rose-700 mt-0.5">Telefon orqali</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Before / After -->
    <section class="py-24 bg-slate-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <div class="max-w-2xl mx-auto text-center">
          <p class="text-sm font-semibold uppercase tracking-wider text-brand-600">Farq bor</p>
          <h2 class="mt-3 text-3xl sm:text-5xl font-extrabold tracking-tight">
            Qog'oz daftarmi yoki
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-brand-600 via-indigo-600 to-sky-500">Suv24</span>?
          </h2>
          <p class="mt-4 text-lg text-slate-600">Xuddi shu biznes — ikki xil usul.</p>
        </div>

        <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="rounded-3xl bg-white border-2 border-rose-200 p-8 relative">
            <div class="absolute -top-3 left-8 bg-rose-100 text-rose-700 px-3 py-1 rounded-full text-xs font-bold uppercase">❌ Oldin</div>
            <h3 class="text-xl font-bold text-rose-900 mt-2">Qog'oz daftar</h3>
            <ul class="mt-6 space-y-3 text-sm text-slate-700">
              <li class="flex items-start gap-3"><span class="text-rose-500 text-lg">✗</span> Buyurtma yo'qoladi, operator unutadi</li>
              <li class="flex items-start gap-3"><span class="text-rose-500 text-lg">✗</span> Haydovchi manzilni eslab qolmaydi</li>
              <li class="flex items-start gap-3"><span class="text-rose-500 text-lg">✗</span> Mijozning qarzi — aniq emas</li>
              <li class="flex items-start gap-3"><span class="text-rose-500 text-lg">✗</span> Naqd pul yashiriladi, hisob kelmaydi</li>
              <li class="flex items-start gap-3"><span class="text-rose-500 text-lg">✗</span> Idish yo'qoladi, kim olgani bilinmaydi</li>
              <li class="flex items-start gap-3"><span class="text-rose-500 text-lg">✗</span> Oy oxirida 3 kun hisob-kitob</li>
            </ul>
          </div>
          <div class="rounded-3xl bg-gradient-to-br from-emerald-50 via-teal-50 to-sky-50 border-2 border-emerald-300 p-8 relative shadow-lg">
            <div class="absolute -top-3 left-8 bg-emerald-500 text-white px-3 py-1 rounded-full text-xs font-bold uppercase">✓ Suv24 bilan</div>
            <h3 class="text-xl font-bold text-emerald-900 mt-2">Zamonaviy tizim</h3>
            <ul class="mt-6 space-y-3 text-sm text-slate-700">
              <li class="flex items-start gap-3"><span class="text-emerald-600 text-lg">✓</span> Har buyurtma tizimda — yo'qolmaydi</li>
              <li class="flex items-start gap-3"><span class="text-emerald-600 text-lg">✓</span> Telefonda manzil + Yandex marshrut</li>
              <li class="flex items-start gap-3"><span class="text-emerald-600 text-lg">✓</span> Har mijoz qarzi real vaqtda</li>
              <li class="flex items-start gap-3"><span class="text-emerald-600 text-lg">✓</span> Naqd pul ilovaga yoziladi — audit log</li>
              <li class="flex items-start gap-3"><span class="text-emerald-600 text-lg">✓</span> Idish balansi har kuni reconcile</li>
              <li class="flex items-start gap-3"><span class="text-emerald-600 text-lg">✓</span> Hisobot bir tugma — dashboardda</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="py-24 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <div class="max-w-2xl mx-auto text-center">
          <p class="text-sm font-semibold uppercase tracking-wider text-brand-600">Imkoniyatlar</p>
          <h2 class="mt-3 text-3xl sm:text-5xl font-extrabold tracking-tight">
            Biznes uchun
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-brand-600 via-indigo-600 to-sky-500">kerakli hamma narsa</span>
          </h2>
          <p class="mt-4 text-lg text-slate-600">Qo'shimcha dastur kerakmas. Suv24'da har bir modul tayyor.</p>
        </div>

        <div class="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <div class="rounded-2xl bg-gradient-to-br from-brand-50 to-indigo-50 border border-brand-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 text-white shadow-lg shadow-brand-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007z"/></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-brand-950">Buyurtma boshqaruvi</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Kutilmoqda → Yo'lda → Yetkazildi. Har qadam audit log'da.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72M3 16.5v-2.25A2.25 2.25 0 015.25 12h13.5A2.25 2.25 0 0121 14.25v2.25" /></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-emerald-950">Mijozlar bazasi</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Tarix, qarz, segment, manzillar — bitta kartochkada.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-white shadow-lg shadow-amber-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25" /></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-amber-950">Haydovchi ilovasi</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">iOS + Android. Swipe-to-confirm, tungi/kunduzgi rejim, haptik.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-rose-50 to-pink-50 border border-rose-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-rose-500 to-pink-600 text-white shadow-lg shadow-rose-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-rose-950">Yandex marshrut</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Mijoz manzili lat/lng bilan — bitta bosishda xaritada yo'nalish.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-sky-50 to-cyan-50 border border-sky-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-cyan-600 text-white shadow-lg shadow-sky-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3" /></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-sky-950">To'lovlar va qarzlar</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Naqd + karta + qaytarish. Mijoz qarzi jonli. Payme yaqinda.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-purple-50 to-violet-50 border border-purple-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 text-white shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 12" /></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-purple-950">Idish nazorati</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Haydovchi va mijoz idish balansi har yetkazishda avtomat hisoblanadi.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-50 border border-teal-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 text-white shadow-lg shadow-teal-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18L9 11.25l4.306 4.306a11.95 11.95 0 015.814-5.518l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" /></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-teal-950">Dashboard va hisobotlar</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">7-kunlik tushum grafigi, status donut, KPI. Bir ekranda biznes holati.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white shadow-lg shadow-indigo-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-indigo-950">Audit va tarix</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Har buyurtma status tarixi: kim qachon nima qildi — hech narsa yo'qolmaydi.</p>
          </div>

          <div class="rounded-2xl bg-gradient-to-br from-fuchsia-50 to-pink-50 border border-fuchsia-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all group">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-fuchsia-500 to-pink-600 text-white shadow-lg shadow-fuchsia-500/30 group-hover:scale-110 transition-transform">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold text-fuchsia-950">Kompaniya brendi</h3>
            <p class="mt-2 text-sm text-slate-700 leading-relaxed">Logo, nom, telefon — admin panelda va haydovchi ilovada mijozga ko'rinadi.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how" class="py-24 bg-gradient-to-br from-indigo-50 via-sky-50 to-emerald-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <div class="max-w-2xl mx-auto text-center">
          <p class="text-sm font-semibold uppercase tracking-wider text-brand-600">Qanday ishlaydi</p>
          <h2 class="mt-3 text-3xl sm:text-5xl font-extrabold tracking-tight">3 qadam — siz tayyorsiz</h2>
        </div>

        <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          <div class="hidden md:block absolute top-8 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-brand-300 via-indigo-300 to-sky-300"></div>

          <div class="relative rounded-2xl bg-white border border-slate-200 p-6 text-center shadow-md">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-indigo-600 text-white text-2xl font-extrabold shadow-lg shadow-brand-500/30">1</div>
            <h3 class="mt-4 text-lg font-bold">Ro'yxatdan o'ting</h3>
            <p class="mt-2 text-sm text-slate-600">Telefon raqam bilan 30 soniyada.</p>
          </div>
          <div class="relative rounded-2xl bg-white border border-slate-200 p-6 text-center shadow-md">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white text-2xl font-extrabold shadow-lg shadow-indigo-500/30">2</div>
            <h3 class="mt-4 text-lg font-bold">Sozlamalar</h3>
            <p class="mt-2 text-sm text-slate-600">Mahsulot, haydovchi, mijoz — Excel'dan import ham bor.</p>
          </div>
          <div class="relative rounded-2xl bg-white border border-slate-200 p-6 text-center shadow-md">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-pink-600 text-white text-2xl font-extrabold shadow-lg shadow-purple-500/30">3</div>
            <h3 class="mt-4 text-lg font-bold">Ishga kirishing</h3>
            <p class="mt-2 text-sm text-slate-600">Operator va haydovchi — siz daromadni kuzatasiz.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section id="pricing" class="py-24 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <div class="max-w-2xl mx-auto text-center">
          <p class="text-sm font-semibold uppercase tracking-wider text-brand-600">Tariflar</p>
          <h2 class="mt-3 text-3xl sm:text-5xl font-extrabold tracking-tight">
            Arzon narx,
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-brand-600 via-indigo-600 to-sky-500">kuchli tizim</span>
          </h2>
          <p class="mt-4 text-lg text-slate-600">Kunlik 1-2 mijoz — oylik to'lovni qoplaydi.</p>
        </div>

        <div class="mt-10 flex justify-center">
          <div class="inline-flex items-center gap-1 rounded-full bg-slate-100 p-1 border border-slate-200">
            <button
              @click="period = 'monthly'"
              :class="[
                'px-5 py-2 rounded-full text-sm font-semibold transition-all',
                period === 'monthly' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500',
              ]"
            >Oylik</button>
            <button
              @click="period = 'yearly'"
              :class="[
                'px-5 py-2 rounded-full text-sm font-semibold transition-all',
                period === 'yearly' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500',
              ]"
            >
              Yillik
              <span class="ml-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700">-17%</span>
            </button>
          </div>
        </div>

        <div class="mt-12 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Start -->
          <div class="rounded-3xl bg-gradient-to-br from-slate-50 to-white border border-slate-200 p-8 flex flex-col hover:shadow-xl transition-shadow">
            <div class="flex items-center gap-3">
              <div class="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center">
                <svg class="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <h3 class="text-xl font-bold">Start</h3>
            </div>
            <p class="mt-3 text-sm text-slate-600">Kichik biznes — 1 operator, 3 haydovchi.</p>
            <div class="mt-6">
              <span class="text-5xl font-extrabold tracking-tight">{{ period === 'monthly' ? '99 000' : '990 000' }}</span>
              <span class="text-slate-500 ml-1 text-sm">so'm/{{ period === 'monthly' ? 'oy' : 'yil' }}</span>
              <p v-if="period === 'yearly'" class="text-xs text-emerald-600 font-semibold mt-1">2 oy tekinga · ~200k tejash</p>
            </div>
            <ul class="mt-6 space-y-3 text-sm text-slate-700 flex-1">
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg><strong>3 gacha haydovchi</strong></li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>500 mijoz · 1000 buyurtma/oy</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Haydovchi ilovasi (iOS + Android)</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Yandex xaritada marshrut</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Naqd + karta to'lov</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Idish balansi avtomat</li>
              <li class="flex items-start gap-2 text-slate-400"><svg class="h-5 w-5 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>Payme onlayn — Biznes'da</li>
            </ul>
            <button @click="openDemo" class="mt-8 inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white border border-slate-200 text-slate-800 font-semibold hover:border-slate-300 hover:shadow-md transition-all w-full">Boshlash</button>
          </div>

          <!-- Biznes -->
          <div class="relative rounded-3xl bg-gradient-to-br from-brand-600 via-indigo-600 to-sky-500 p-8 flex flex-col shadow-2xl shadow-brand-500/30 lg:scale-105 lg:-my-2">
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-amber-400 text-amber-950 px-4 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider shadow-md">⭐ Eng ko'p tanlanadi</div>
            <div class="flex items-center gap-3 text-white">
              <div class="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" /></svg>
              </div>
              <h3 class="text-xl font-bold">Biznes</h3>
            </div>
            <p class="mt-3 text-sm text-brand-50">O'rta biznes — cheksiz haydovchi va mijoz.</p>
            <div class="mt-6 text-white">
              <span class="text-5xl font-extrabold tracking-tight">{{ period === 'monthly' ? '249 000' : '2 490 000' }}</span>
              <span class="text-brand-100 ml-1 text-sm">so'm/{{ period === 'monthly' ? 'oy' : 'yil' }}</span>
              <p v-if="period === 'yearly'" class="text-xs text-amber-300 font-semibold mt-1">~500k tejash</p>
            </div>
            <ul class="mt-6 space-y-3 text-sm text-brand-50 flex-1">
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg><strong class="text-white">Cheksiz haydovchi · mijoz · buyurtma</strong></li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Start'dagi hamma narsa</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Ko'p operator</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Kompaniya brendi (logo, nom)</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Mijoz qarzlari va segmentlari</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Audit log · buyurtma tarixi</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Prioritet qo'llab-quvvatlash</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-300 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Payme onlayn to'lov (yaqinda)</li>
            </ul>
            <button @click="openDemo" class="mt-8 inline-flex items-center justify-center px-6 py-3 rounded-xl bg-white text-brand-700 font-bold hover:bg-brand-50 transition-colors shadow-md">Tanlash — ajoyib taklif</button>
          </div>

          <!-- Premium -->
          <div class="rounded-3xl bg-slate-900 text-white p-8 flex flex-col border border-slate-800 hover:shadow-xl transition-shadow">
            <div class="flex items-center gap-3">
              <div class="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center">
                <svg class="h-5 w-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M9.504 1.132a1 1 0 01.992 0l1.75 1a1 1 0 11-.992 1.736L10 3.152l-1.254.716a1 1 0 11-.992-1.736l1.75-1z" clip-rule="evenodd"/></svg>
              </div>
              <h3 class="text-xl font-bold">Premium</h3>
            </div>
            <p class="mt-3 text-sm text-slate-400">Tarmoqlar va yirik kompaniyalar.</p>
            <div class="mt-6">
              <span class="text-5xl font-extrabold tracking-tight">{{ period === 'monthly' ? '499 000' : '4 990 000' }}</span>
              <span class="text-slate-400 ml-1 text-sm">so'm/{{ period === 'monthly' ? 'oy' : 'yil' }}</span>
              <p v-if="period === 'yearly'" class="text-xs text-emerald-400 font-semibold mt-1">~1M tejash</p>
            </div>
            <ul class="mt-6 space-y-3 text-sm text-slate-300 flex-1">
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg><strong class="text-white">Biznes'dagi hammasi +</strong></li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Shaxsiy menejer</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Shaxsiy trening (offline)</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Kastom hisobot so'rov bo'yicha</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Shaxsiy domen (siz tanlang)</li>
              <li class="flex items-start gap-2"><svg class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>24/7 prioritet + SLA</li>
            </ul>
            <button @click="openDemo" class="mt-8 inline-flex items-center justify-center px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 font-semibold transition-colors border border-white/20">Bog'lanish</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Lifetime -->
    <section class="py-24 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white relative overflow-hidden">
      <div class="absolute inset-0">
        <div class="absolute top-0 left-1/4 h-96 w-96 rounded-full bg-brand-500/20 blur-3xl"></div>
        <div class="absolute bottom-0 right-1/4 h-96 w-96 rounded-full bg-amber-500/20 blur-3xl"></div>
      </div>
      <div class="relative max-w-5xl mx-auto px-4 sm:px-6 text-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-amber-400/30 bg-amber-400/10 text-amber-300 text-sm font-bold uppercase tracking-wider mb-6">
          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M9.401 2.293a.75.75 0 011.198 0l6.75 9.5a.75.75 0 01-.598 1.207H3.25a.75.75 0 01-.599-1.207l6.75-9.5z" clip-rule="evenodd"/></svg>
          2026-yil oxirigacha
        </div>
        <h2 class="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
          Bir marta to'lang —<br />
          <span class="bg-gradient-to-r from-amber-400 via-amber-300 to-amber-500 bg-clip-text text-transparent">butun umr ishlating</span>
        </h2>
        <p class="mt-6 text-lg text-slate-300 max-w-2xl mx-auto">
          Lifetime lisenziya — bir martalik to'lov. Obuna yo'q, qayta to'lovsiz. Har yili
          ming-minglab so'm tejang va biznesingizni bemalol boshqaring.
        </p>

        <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="rounded-3xl bg-white/5 backdrop-blur-sm border border-white/10 p-8 text-left hover:bg-white/10 transition-colors">
            <p class="text-xs text-slate-400 uppercase tracking-wider">Start Lifetime</p>
            <p class="mt-2 text-4xl font-extrabold">4 470 000 <span class="text-base text-slate-400 font-normal">so'm</span></p>
            <p class="mt-1 text-xs text-emerald-400 font-semibold">~15 oyda o'zini oqlaydi</p>
            <p class="mt-4 text-sm text-slate-300">3 gacha haydovchi. Kichik kiosk va kafelar uchun.</p>
            <button @click="openDemo" class="mt-6 block w-full text-center rounded-xl bg-white/10 hover:bg-white/20 font-semibold px-6 py-3 transition-colors border border-white/20">Tanlash</button>
          </div>
          <div class="relative rounded-3xl bg-gradient-to-br from-amber-400 to-orange-500 p-8 text-left text-slate-900 shadow-2xl shadow-amber-500/40 lg:scale-105">
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-900 text-amber-400 px-4 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider">🔥 Eng foydali</div>
            <p class="text-xs font-bold uppercase tracking-wider">Biznes Lifetime</p>
            <p class="mt-2 text-4xl font-extrabold">11 970 000 <span class="text-base font-semibold">so'm</span></p>
            <p class="mt-1 text-xs font-bold">~16 oyda o'zini oqlaydi</p>
            <p class="mt-4 text-sm font-medium">Cheksiz haydovchi va mijoz. O'rta biznes uchun barcha imkoniyatlar — abadiy.</p>
            <button @click="openDemo" class="mt-6 block w-full text-center rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold px-6 py-3 transition-colors shadow-md">Hoziroq sotib olish</button>
          </div>
          <div class="rounded-3xl bg-white/5 backdrop-blur-sm border border-white/10 p-8 text-left hover:bg-white/10 transition-colors">
            <p class="text-xs text-slate-400 uppercase tracking-wider">Premium Lifetime</p>
            <p class="mt-2 text-4xl font-extrabold">23 970 000 <span class="text-base text-slate-400 font-normal">so'm</span></p>
            <p class="mt-1 text-xs text-emerald-400 font-semibold">~16 oyda o'zini oqlaydi</p>
            <p class="mt-4 text-sm text-slate-300">Shaxsiy menejer, SLA, kastom integratsiya. Tarmoqlar uchun.</p>
            <button @click="openDemo" class="mt-6 block w-full text-center rounded-xl bg-white/10 hover:bg-white/20 font-semibold px-6 py-3 transition-colors border border-white/20">Tanlash</button>
          </div>
        </div>

        <div class="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-slate-400">
          <div class="flex items-center gap-2"><svg class="h-5 w-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Bepul yangilanishlar</div>
          <div class="flex items-center gap-2"><svg class="h-5 w-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>1 yil qo'llab-quvvatlash</div>
          <div class="flex items-center gap-2"><svg class="h-5 w-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>Ma'lumotlar sizga tegishli</div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="py-24 bg-slate-50">
      <div class="max-w-3xl mx-auto px-4 sm:px-6">
        <div class="text-center">
          <p class="text-sm font-semibold uppercase tracking-wider text-brand-600">FAQ</p>
          <h2 class="mt-3 text-3xl sm:text-5xl font-extrabold tracking-tight">Savollaringiz?</h2>
        </div>
        <div class="mt-12 space-y-3">
          <details class="group rounded-2xl bg-white border border-slate-200 p-5 cursor-pointer">
            <summary class="flex items-center justify-between font-semibold list-none">
              <span>Sinash davrida hamma narsa ochiqmi?</span>
              <svg class="h-5 w-5 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </summary>
            <p class="mt-3 text-sm text-slate-600">14 kun Premium ochiq. Muddat tugagach tanlov qilasiz.</p>
          </details>
          <details class="group rounded-2xl bg-white border border-slate-200 p-5 cursor-pointer">
            <summary class="flex items-center justify-between font-semibold list-none">
              <span>Ma'lumotlarim qayerda?</span>
              <svg class="h-5 w-5 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </summary>
            <p class="mt-3 text-sm text-slate-600">O'zbekistonda — ishonchli serverlar, kuniga 2 marta zaxira, TLS shifrlash.</p>
          </details>
          <details class="group rounded-2xl bg-white border border-slate-200 p-5 cursor-pointer">
            <summary class="flex items-center justify-between font-semibold list-none">
              <span>Haydovchilar o'rgana oladimi?</span>
              <svg class="h-5 w-5 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </summary>
            <p class="mt-3 text-sm text-slate-600">Ilovada 4 katta tugma. Telegram ishlatgan kishi 5 daqiqada o'rganadi.</p>
          </details>
          <details class="group rounded-2xl bg-white border border-slate-200 p-5 cursor-pointer">
            <summary class="flex items-center justify-between font-semibold list-none">
              <span>Lifetime haqiqatan butun umrmi?</span>
              <svg class="h-5 w-5 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </summary>
            <p class="mt-3 text-sm text-slate-600">Ha, bir marta to'lab cheksiz foydalanish. Yangilanish va yordam kiradi. Shartnoma tuzamiz.</p>
          </details>
          <details class="group rounded-2xl bg-white border border-slate-200 p-5 cursor-pointer">
            <summary class="flex items-center justify-between font-semibold list-none">
              <span>Excel'dan ma'lumot ko'chirish oson?</span>
              <svg class="h-5 w-5 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </summary>
            <p class="mt-3 text-sm text-slate-600">Excel yuklaysiz — biz import qilamiz. Ko'p ma'lumot bo'lsa bepul migratsiya.</p>
          </details>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-24 bg-gradient-to-br from-brand-600 via-indigo-600 to-sky-500 relative overflow-hidden">
      <div class="absolute inset-0">
        <div class="absolute -top-20 -right-20 h-96 w-96 rounded-full bg-white/10 blur-3xl"></div>
        <div class="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-white/10 blur-3xl"></div>
      </div>
      <div class="relative max-w-4xl mx-auto px-4 sm:px-6 text-center text-white">
        <h2 class="text-4xl sm:text-6xl font-extrabold tracking-tight">
          Ertaga emas — <span class="text-amber-300">bugun</span> boshlang
        </h2>
        <p class="mt-6 text-lg sm:text-xl text-brand-100 max-w-2xl mx-auto">
          14 kun bepul. Bir haftadan keyin farqni ko'rasiz.
        </p>
        <div class="mt-10 flex flex-wrap items-center justify-center gap-3">
          <button @click="openDemo" class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white text-brand-700 font-bold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all">
            Bepul sinashni boshlash
            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clip-rule="evenodd"/></svg>
          </button>
          <a href="tel:+998901234567" class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white/10 text-white font-bold border border-white/20 hover:bg-white/20 transition-colors backdrop-blur">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20"><path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/></svg>
            +998 90 123 45 67
          </a>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-slate-950 text-slate-400 py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div class="md:col-span-2">
            <div class="flex items-center gap-2">
              <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white font-extrabold">S</div>
              <span class="text-xl font-extrabold text-white">Suv24</span>
            </div>
            <p class="mt-4 text-sm max-w-sm leading-relaxed">Suv yetkazib berish bizneslari uchun boshqaruv platformasi.</p>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Mahsulot</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#features" @click="scrollTo('#features', $event)" class="hover:text-white transition-colors">Imkoniyatlar</a></li>
              <li><a href="#pricing" @click="scrollTo('#pricing', $event)" class="hover:text-white transition-colors">Tariflar</a></li>
              <li><a href="#faq" @click="scrollTo('#faq', $event)" class="hover:text-white transition-colors">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Aloqa</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="tel:+998901234567" class="hover:text-white transition-colors">+998 90 123 45 67</a></li>
              <li><a href="mailto:info@suv24.uz" class="hover:text-white transition-colors">info@suv24.uz</a></li>
              <li><a href="https://t.me/suv24_uz" class="hover:text-white transition-colors">@suv24_uz</a></li>
              <li class="text-slate-500">Toshkent, O'zbekiston</li>
            </ul>
          </div>
        </div>
        <div class="mt-12 pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-between gap-4 text-sm">
          <p>© 2026 Suv24.</p>
          <div class="flex gap-6">
            <a href="#" class="hover:text-white transition-colors">Maxfiylik</a>
            <a href="#" class="hover:text-white transition-colors">Shartlar</a>
          </div>
        </div>
      </div>
    </footer>

    <DemoRequestDialog v-model:open="demoOpen" />
  </div>
</template>

<style scoped>
:deep(html) { scroll-behavior: smooth; }
</style>
