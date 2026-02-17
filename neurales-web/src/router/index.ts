import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/acquisition" },

    { path: "/login", component: () => import("@/pages/auth/LoginPage.vue"), meta: { public: true } },
    { path: "/dev", component: () => import("@/pages/Development.vue"), meta: { public: true } },

    { path: "/acquisition", component: () => import("@/pages/acquisition/AcquisitionPage.vue") },
    { path: "/results", component: () => import("@/pages/results/ResultsPage.vue") },
    { path: "/results/:id", component: () => import("@/pages/results/ResultDetailPage.vue") },
    { path: "/dashboard", component: () => import("@/pages/Dashboard.vue") },
    { path: "/devices", component: () => import("@/pages/devices/DevicesPage.vue") },
    { path: "/patients", component: () => import("@/pages/patients/PatientsPage.vue") },

    { path: "/:pathMatch(.*)*", component: () => import("@/pages/NotFound.vue") },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  const isPublic = !!to.meta.public;

  if (!auth.isReady) {
    await auth.initialize();
  }

  if (!isPublic && !auth.isLogged) return "/login";
});

export default router;
