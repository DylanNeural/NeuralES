import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/acquisition" },

    { path: "/login", component: () => import("@/pages/auth/LoginPage.vue"), meta: { public: true } },

    { path: "/acquisition", component: () => import("@/pages/acquisition/AcquisitionPage.vue") },
    { path: "/results", component: () => import("@/pages/results/ResultsPage.vue") },
    { path: "/results/new", component: () => import("@/pages/results/ResultFormPage.vue") },
    { path: "/results/:id", component: () => import("@/pages/results/ResultDetailPage.vue") },
    { path: "/results/:id/edit", component: () => import("@/pages/results/ResultFormPage.vue") },
    { path: "/dashboard", component: () => import("@/pages/Dashboard.vue") },
    { path: "/devices", component: () => import("@/pages/devices/DevicesPage.vue") },
    { path: "/devices/new", component: () => import("@/pages/devices/DeviceFormPage.vue") },
    { path: "/devices/:id", component: () => import("@/pages/devices/DeviceDetailPage.vue") },
    { path: "/devices/:id/edit", component: () => import("@/pages/devices/DeviceFormPage.vue") },
    { path: "/patients", component: () => import("@/pages/patients/PatientsPage.vue") },
    { path: "/patients/new", component: () => import("@/pages/patients/PatientCreatePage.vue") },
    { path: "/patients/:id", component: () => import("@/pages/patients/PatientDetailPage.vue") },
    { path: "/patients/:id/edit", component: () => import("@/pages/patients/PatientCreatePage.vue") },

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
