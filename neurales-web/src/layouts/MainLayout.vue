<template>
  <div class="min-h-screen flex bg-background">
    <!-- Sidebar -->
    <aside class="sticky top-0 h-screen w-[260px] bg-primary-dark text-white flex flex-col py-8 px-6 rounded-tr-3xl rounded-br-3xl shadow-xl overflow-y-auto">
      <div class="flex items-center gap-3 mb-10">
        <img src="/logo.svg" alt="Logo" class="h-10 w-10 rounded-2xl bg-white p-1 shadow" />
        <div>
          <div class="text-xl font-bold tracking-wide font-sans">NeuralES</div>
          <div class="text-xs text-primary-light mt-1">Plateforme médicale</div>
        </div>
      </div>

      <nav class="flex flex-col gap-2">
        <RouterLink class="nav-item" to="/acquisition">Acquisition</RouterLink>
        <RouterLink class="nav-item" to="/results">Résultats</RouterLink>
        <RouterLink class="nav-item" to="/devices">Dispositifs</RouterLink>
        <RouterLink class="nav-item" to="/patients">Patients</RouterLink>
        <RouterLink class="nav-item" to="/dashboard">Dashboard</RouterLink>
      </nav>

      <div class="mt-auto bg-primary-light/10 rounded-2xl p-4 flex flex-col items-center">
        <div class="text-xs text-primary-light mb-1">Connecté :</div>
        <div class="text-base font-semibold">{{ auth.displayName || "—" }}</div>
        <button class="btn btn-primary w-full mt-4" @click="logout">Déconnexion</button>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col">
      <header class="h-20 bg-white/80 border-b border-slate-200 px-10 flex items-center justify-between shadow-sm">
        <div>
          <div class="text-xs text-primary-light uppercase tracking-widest font-semibold">NeuralES</div>
          <div class="text-2xl font-bold leading-tight font-sans">{{ pageTitle }}</div>
        </div>

        <div class="flex items-center gap-4">
          <div class="text-right">
            <div class="text-xs text-primary-light">Utilisateur</div>
            <div class="text-base font-semibold">{{ auth.displayName || "—" }}</div>
          </div>
          <div class="h-12 w-12 rounded-2xl bg-primary-light/20 border border-primary-light grid place-items-center text-lg font-bold">
            UI
          </div>
        </div>
      </header>

      <main class="p-10 bg-background flex-1">
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

const pageTitle = computed(() => {
  if (route.path.startsWith("/acquisition")) return "Acquisition";
  if (route.path.startsWith("/results")) return "Résultats";
  return "Tableau de bord";
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
  @apply rounded-xl px-4 py-2 text-base font-medium text-primary-light hover:bg-primary-light/20 hover:text-white transition-all duration-150;
}
.router-link-active {
  @apply bg-primary-light/20 text-white font-bold;
}
</style>
