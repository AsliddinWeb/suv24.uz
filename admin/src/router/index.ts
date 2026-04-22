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
  if (to.name === "login" && auth.isAuthenticated) {
    return { name: "dashboard" };
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
