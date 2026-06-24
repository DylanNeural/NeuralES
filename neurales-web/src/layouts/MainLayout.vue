<template>
  <div class="min-h-screen flex bg-background">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-30 flex flex-col w-64 bg-primary-dark border-r border-white/5"
      style="background: linear-gradient(180deg, #111827 0%, #0F172A 100%);"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-5 pt-7 pb-6">
        <div class="h-9 w-9 rounded-xl bg-primary flex items-center justify-center shadow-elevated">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <div class="text-base font-bold text-white tracking-tight">NeuralES</div>
          <div class="text-xs text-slate-500 mt-0.5">Plateforme médicale</div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 space-y-0.5 overflow-y-auto">
        <div class="text-[10px] font-semibold uppercase tracking-widest text-slate-600 px-3 mb-2 mt-1">Navigation</div>

        <RouterLink class="nav-item" to="/acquisition">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>Acquisition</span>
        </RouterLink>

        <RouterLink class="nav-item" to="/results">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>Résultats</span>
        </RouterLink>

        <RouterLink class="nav-item" to="/patients">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>Patients</span>
        </RouterLink>

        <RouterLink class="nav-item" to="/devices">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <span>Dispositifs</span>
        </RouterLink>

        <RouterLink class="nav-item" to="/dashboard">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          <span>Dashboard</span>
        </RouterLink>
      </nav>

      <!-- User profile -->
      <div class="px-3 pb-5 pt-3 border-t border-white/5">
        <div class="flex items-center gap-3 rounded-xl px-3 py-3 bg-white/5">
          <div class="h-8 w-8 rounded-lg bg-primary/30 flex items-center justify-center text-xs font-bold text-primary-ring shrink-0">
            {{ initials }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-white truncate">{{ auth.displayName || "Utilisateur" }}</div>
            <div class="text-xs text-slate-500 truncate">Admin</div>
          </div>
          <button
            @click="logout"
            class="shrink-0 p-1.5 text-slate-500 hover:text-white hover:bg-white/10 rounded-lg transition"
            title="Déconnexion"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0 pl-64">
      <!-- Top bar -->
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur border-b border-slate-200/80 px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div>
            <h1 class="text-lg font-semibold text-slate-900 leading-tight">{{ pageTitle }}</h1>
            <p class="text-xs text-slate-500 leading-tight">{{ pageSubtitle }}</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Status indicator -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span class="text-xs font-medium text-emerald-700">Système actif</span>
          </div>
          <div class="h-8 w-8 rounded-lg bg-slate-100 border border-slate-200 grid place-items-center text-xs font-bold text-slate-600">
            {{ initials }}
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-8 bg-background min-h-0">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const auth = useAuthStore();
const route = useRoute();

const initials = computed(() => {
  const name = auth.displayName || "";
  return name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2) || "?";
});

const pageTitle = computed(() => {
  if (route.path.startsWith("/acquisition")) return "Acquisition EEG";
  if (route.path.match(/^\/results\/\d+\/edit/)) return "Modifier la session";
  if (route.path.match(/^\/results\/new/)) return "Nouvelle session";
  if (route.path.match(/^\/results\/\d+/)) return "Détail de la session";
  if (route.path.startsWith("/results")) return "Sessions & Résultats";
  if (route.path.match(/^\/patients\/new/)) return "Nouveau patient";
  if (route.path.match(/^\/patients\/\d+\/edit/)) return "Modifier le patient";
  if (route.path.match(/^\/patients\/\d+/)) return "Détail du patient";
  if (route.path.startsWith("/patients")) return "Patients";
  if (route.path.match(/^\/devices\/new/)) return "Nouveau dispositif";
  if (route.path.match(/^\/devices\/\d+\/edit/)) return "Modifier le dispositif";
  if (route.path.match(/^\/devices\/\d+/)) return "Détail du dispositif";
  if (route.path.startsWith("/devices")) return "Dispositifs";
  if (route.path.startsWith("/dashboard")) return "Tableau de bord";
  return "NeuralES";
});

const pageSubtitle = computed(() => {
  if (route.path.startsWith("/acquisition")) return "Streaming EEG temps réel";
  if (route.path.startsWith("/results")) return "Historique des sessions de mesure";
  if (route.path.startsWith("/patients")) return "Gestion du registre patients";
  if (route.path.startsWith("/devices")) return "Parc d'équipements EEG";
  if (route.path.startsWith("/dashboard")) return "Vue d'ensemble de la plateforme";
  return "Plateforme médicale EEG";
});

function logout() {
  auth.logout();
  window.location.href = "/login";
}
</script>

<style scoped>
@config "../../tailwind.config.ts";
@reference "tailwindcss";

.nav-item {
  @apply flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-400
         hover:text-white transition-all duration-150 cursor-pointer;
}
.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
}
.nav-item.router-link-active {
  color: white;
  background-color: rgba(255, 255, 255, 0.10);
}
</style>
