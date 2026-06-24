<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { cn } from "@/lib/utils";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const collapsed = ref(false);

const navItems = [
  {
    to: "/acquisition",
    label: "Acquisition",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />`,
  },
  {
    to: "/dashboard",
    label: "Dashboard",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />`,
  },
  {
    to: "/patients",
    label: "Patients",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />`,
  },
  {
    to: "/results",
    label: "Résultats",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />`,
  },
  {
    to: "/devices",
    label: "Dispositifs",
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />`,
  },
];

const pageTitle = computed(() => {
  if (route.path.startsWith("/acquisition")) return "Acquisition EEG";
  if (route.path.startsWith("/results")) return "Résultats";
  if (route.path.startsWith("/patients/new")) return "Nouveau patient";
  if (route.path.startsWith("/patients")) return "Patients";
  if (route.path.startsWith("/devices")) return "Dispositifs";
  if (route.path.startsWith("/dashboard")) return "Dashboard";
  return "NeuralES";
});

function isActive(to: string) {
  if (to === "/patients") return route.path.startsWith("/patients");
  if (to === "/results") return route.path.startsWith("/results");
  if (to === "/devices") return route.path.startsWith("/devices");
  return route.path.startsWith(to);
}

async function logout() {
  await auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="flex h-full bg-background text-foreground">
    <!-- Sidebar -->
    <aside
      :class="cn(
        'flex flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300 shrink-0',
        collapsed ? 'w-[64px]' : 'w-[220px]'
      )"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 py-5 border-b border-sidebar-border">
        <div class="h-8 w-8 rounded-lg bg-primary/20 ring-1 ring-primary/40 flex items-center justify-center shrink-0">
          <svg class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div v-if="!collapsed" class="overflow-hidden">
          <div class="text-sm font-bold tracking-wide text-foreground">NeuralES</div>
          <div class="text-[10px] text-sidebar-foreground">Plateforme EEG</div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :class="cn(
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 group',
            isActive(item.to)
              ? 'bg-primary/15 text-primary font-medium'
              : 'text-sidebar-foreground hover:bg-white/5 hover:text-foreground'
          )"
        >
          <svg
            class="h-4 w-4 shrink-0"
            :class="isActive(item.to) ? 'text-primary' : 'text-sidebar-foreground group-hover:text-foreground'"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            v-html="item.icon"
          />
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- User + Collapse -->
      <div class="border-t border-sidebar-border p-3 space-y-2">
        <div v-if="!collapsed" class="flex items-center gap-3 px-1 py-2">
          <div class="h-7 w-7 rounded-full bg-primary/20 ring-1 ring-primary/30 flex items-center justify-center text-xs font-semibold text-primary shrink-0">
            {{ (auth.displayName || "?")[0]?.toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-xs font-medium text-foreground truncate">{{ auth.displayName || "Utilisateur" }}</div>
            <div class="text-[10px] text-sidebar-foreground truncate">Admin</div>
          </div>
        </div>

        <button
          @click="logout"
          :class="cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-sidebar-foreground hover:bg-destructive/10 hover:text-destructive transition-colors duration-150',
            collapsed && 'justify-center'
          )"
        >
          <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span v-if="!collapsed">Déconnexion</span>
        </button>

        <button
          @click="collapsed = !collapsed"
          class="w-full flex items-center justify-center h-7 rounded-lg text-sidebar-foreground hover:bg-white/5 hover:text-foreground transition-colors"
        >
          <svg
            class="h-4 w-4 transition-transform duration-300"
            :class="collapsed ? 'rotate-180' : ''"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>
    </aside>

    <!-- Main area -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <!-- Topbar -->
      <header class="h-14 shrink-0 border-b border-border bg-card/60 backdrop-blur-sm px-6 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <h1 class="text-lg font-semibold text-foreground truncate">{{ pageTitle }}</h1>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <div class="h-2 w-2 rounded-full bg-eeg-emerald animate-pulse"></div>
          <span class="text-xs text-muted-foreground hidden sm:block">Système actif</span>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
