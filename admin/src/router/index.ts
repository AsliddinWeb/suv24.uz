import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const BRAND = "Suv24";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "landing",
    component: () => import("@/views/LandingView.vue"),
    meta: { title: "Suv24 — Aqlli suv yetkazish tizimi" },
  },
  {
    path: "/login",
    component: () => import("@/layouts/AuthLayout.vue"),
    children: [
      {
        path: "",
        name: "login",
        component: () => import("@/views/LoginView.vue"),
        meta: { title: "Kirish" },
      },
    ],
  },
  {
    path: "/platform",
    component: () => import("@/layouts/PlatformLayout.vue"),
    meta: { requiresAuth: true, platformOnly: true },
    children: [
      {
        path: "",
        name: "platform-dashboard",
        component: () => import("@/views/PlatformDashboardView.vue"),
        meta: { title: "Platforma umumiy holat" },
      },
      {
        path: "companies",
        name: "platform-companies",
        component: () => import("@/views/PlatformCompaniesView.vue"),
        meta: { title: "Kompaniyalar" },
      },
      {
        path: "companies/new",
        name: "platform-company-new",
        component: () => import("@/views/PlatformCompanyCreateView.vue"),
        meta: { title: "Yangi kompaniya" },
      },
      {
        path: "companies/:id",
        name: "platform-company-detail",
        component: () => import("@/views/PlatformCompanyDetailView.vue"),
        meta: { title: "Kompaniya tafsiloti" },
      },
    ],
  },
  {
    path: "/app",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      { path: "", redirect: { name: "dashboard" } },
      {
        path: "dashboard",
        name: "dashboard",
        component: () => import("@/views/DashboardView.vue"),
        meta: { title: "Boshqaruv paneli" },
      },
      {
        path: "orders",
        name: "orders",
        component: () => import("@/views/OrdersView.vue"),
        meta: { title: "Buyurtmalar" },
      },
      {
        path: "orders/new",
        name: "order-new",
        component: () => import("@/views/OrderCreateView.vue"),
        meta: { title: "Yangi buyurtma" },
      },
      {
        path: "orders/:id",
        name: "order-detail",
        component: () => import("@/views/OrderDetailView.vue"),
        meta: { title: "Buyurtma tafsiloti" },
      },
      {
        path: "customers",
        name: "customers",
        component: () => import("@/views/CustomersView.vue"),
        meta: { title: "Mijozlar" },
      },
      {
        path: "customers/:id",
        name: "customer-detail",
        component: () => import("@/views/CustomerDetailView.vue"),
        meta: { title: "Mijoz tafsiloti" },
      },
      {
        path: "products",
        name: "products",
        component: () => import("@/views/ProductsView.vue"),
        meta: { title: "Mahsulotlar" },
      },
      {
        path: "drivers",
        name: "drivers",
        component: () => import("@/views/DriversView.vue"),
        meta: { title: "Haydovchilar" },
      },
      {
        path: "users",
        name: "users",
        component: () => import("@/views/UsersView.vue"),
        meta: { adminOnly: true, title: "Foydalanuvchilar" },
      },
      {
        path: "payments",
        name: "payments",
        component: () => import("@/views/PaymentsView.vue"),
        meta: { title: "To'lovlar" },
      },
      {
        path: "profile",
        name: "profile",
        component: () => import("@/views/ProfileView.vue"),
        meta: { title: "Profil" },
      },
      {
        path: "settings",
        name: "settings",
        component: () => import("@/views/SettingsView.vue"),
        meta: { title: "Sozlamalar" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { next: to.fullPath } };
  }
  const isOwner = auth.role === "platform_owner";
  if (to.name === "login" && auth.isAuthenticated) {
    return isOwner ? { name: "platform-dashboard" } : { name: "dashboard" };
  }
  if (to.meta.platformOnly && !isOwner) {
    return { name: "dashboard" };
  }
  // Platform owner can't access tenant app routes
  if (to.path.startsWith("/app") && isOwner) {
    return { name: "platform-dashboard" };
  }
  if (to.meta.adminOnly && !auth.hasRole("super_admin", "admin")) {
    return { name: "dashboard" };
  }
});

router.afterEach((to) => {
  const pageTitle = to.meta.title as string | undefined;
  if (!pageTitle) {
    document.title = BRAND;
  } else if (to.name === "landing") {
    document.title = pageTitle;
  } else {
    document.title = `${pageTitle} · ${BRAND}`;
  }
});

export default router;
