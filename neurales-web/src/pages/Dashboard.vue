<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-primary-dark">Dashboard</h1>
        <p class="text-sm text-primary-light mt-1">Vue d'ensemble de la plateforme NeuralES</p>
      </div>
      <div class="text-right">
        <div class="text-xs text-primary-light">Derniere mise a jour</div>
        <div class="text-sm font-semibold text-slate-800">{{ currentTime }}</div>
      </div>
    </div>

    <!-- KPIs principaux -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-primary-light uppercase tracking-wide">Sessions actives</div>
            <div class="text-3xl font-bold text-slate-800 mt-2">{{ kpis.activeSessions }}</div>
            <div class="text-xs text-green-600 mt-2">+{{ kpis.sessionsChangePercent }}% vs hier</div>
          </div>
          <div class="h-12 w-12 rounded-xl bg-blue-50 grid place-items-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-primary-light uppercase tracking-wide">Patients enregistres</div>
            <div class="text-3xl font-bold text-slate-800 mt-2">{{ kpis.totalPatients }}</div>
            <div class="text-xs text-green-600 mt-2">+{{ kpis.patientsThisWeek }} cette semaine</div>
          </div>
          <div class="h-12 w-12 rounded-xl bg-green-50 grid place-items-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-primary-light uppercase tracking-wide">Dispositifs en ligne</div>
            <div class="text-3xl font-bold text-slate-800 mt-2">{{ kpis.onlineDevices }}/{{ kpis.totalDevices }}</div>
            <div class="text-xs text-slate-600 mt-2">{{ deviceUptime }}% uptime</div>
          </div>
          <div class="h-12 w-12 rounded-xl bg-purple-50 grid place-items-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-primary-light uppercase tracking-wide">Qualite moyenne</div>
            <div class="text-3xl font-bold text-slate-800 mt-2">{{ kpis.avgQuality }}%</div>
            <div class="text-xs text-green-600 mt-2">Excellent signal</div>
          </div>
          <div class="h-12 w-12 rounded-xl bg-amber-50 grid place-items-center">
            <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Visualisations principales -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <AppCard>
        <div class="text-base font-semibold text-primary-dark mb-4">Cerveau 3D</div>
        <Brain3D />
      </AppCard>

      <AppCard>
        <div class="text-base font-semibold text-primary-dark mb-4">
          Sessions des 7 derniers jours
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Lundi</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 85%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">12</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Mardi</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 73%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">9</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Mercredi</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 100%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">15</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Jeudi</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 67%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">8</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Vendredi</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 93%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">14</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Samedi</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 40%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">5</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Dimanche</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" style="width: 27%"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">3</span>
            </div>
          </div>
        </div>
        <div class="mt-5 pt-4 border-t border-slate-200">
          <div class="flex items-center justify-between text-xs">
            <span class="text-primary-light">Total cette semaine</span>
            <span class="text-slate-800 font-semibold">66 sessions</span>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Activite recente et stats -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <AppCard class="lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-semibold text-primary-dark">Sessions recentes</div>
          <button class="text-xs text-blue-600 hover:underline">Voir tout</button>
        </div>
        <div class="space-y-3">
          <div
            v-for="session in recentSessions"
            :key="session.id"
            class="flex items-center justify-between p-3 rounded-lg border border-slate-200 hover:border-slate-300 transition"
          >
            <div class="flex items-center gap-3">
              <div
                class="h-10 w-10 rounded-full grid place-items-center text-sm font-semibold"
                :class="session.statusClass"
              >
                {{ session.patientInitials }}
              </div>
              <div>
                <div class="text-sm font-semibold text-slate-800">{{ session.patientName }}</div>
                <div class="text-xs text-primary-light">{{ session.date }} • {{ session.duration }}</div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <div class="text-xs text-primary-light">Score fatigue</div>
                <div class="text-sm font-semibold text-slate-800">{{ session.fatigueScore }}/100</div>
              </div>
              <div
                class="px-2 py-1 rounded-full text-xs font-medium"
                :class="session.qualityBadgeClass"
              >
                {{ session.quality }}
              </div>
            </div>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <div class="text-base font-semibold text-primary-dark mb-4">Stats par objectif</div>
        <div class="space-y-4">
          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-slate-600">Fatigue cognitive</span>
              <span class="text-slate-800 font-semibold">42%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-slate-100">
              <div class="h-2 rounded-full bg-blue-500" style="width: 42%"></div>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-slate-600">Controle moteur</span>
              <span class="text-slate-800 font-semibold">28%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-slate-100">
              <div class="h-2 rounded-full bg-green-500" style="width: 28%"></div>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-slate-600">Focus attention</span>
              <span class="text-slate-800 font-semibold">18%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-slate-100">
              <div class="h-2 rounded-full bg-purple-500" style="width: 18%"></div>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-slate-600">Relax meditation</span>
              <span class="text-slate-800 font-semibold">12%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-slate-100">
              <div class="h-2 rounded-full bg-amber-500" style="width: 12%"></div>
            </div>
          </div>
        </div>
        <div class="mt-5 pt-4 border-t border-slate-200">
          <div class="flex items-center justify-between text-xs text-primary-light">
            <span>Base sur 66 sessions</span>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Graphique EEG -->
    <AppCard>
      <div class="text-base font-semibold text-primary-dark mb-4">Apercu signal EEG</div>
      <EEGChartCanvas />
    </AppCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import AppCard from '@/components/ui/AppCard.vue';
import Brain3D from '@/components/Brain3D.vue';
import EEGChartCanvas from '@/components/EEGChartCanvas.vue';

const currentTime = ref("");

const kpis = ref({
  activeSessions: 3,
  sessionsChangePercent: 12,
  totalPatients: 47,
  patientsThisWeek: 5,
  onlineDevices: 8,
  totalDevices: 10,
  avgQuality: 87,
});

const deviceUptime = computed(() => {
  return Math.round((kpis.value.onlineDevices / kpis.value.totalDevices) * 100);
});

const recentSessions = ref([
  {
    id: "1",
    patientName: "Marie Dupont",
    patientInitials: "MD",
    date: "Aujourd'hui 14:32",
    duration: "45min",
    fatigueScore: 42,
    quality: "Excellent",
    statusClass: "bg-green-100 text-green-700",
    qualityBadgeClass: "bg-green-100 text-green-700",
  },
  {
    id: "2",
    patientName: "Jean Martin",
    patientInitials: "JM",
    date: "Aujourd'hui 11:15",
    duration: "38min",
    fatigueScore: 68,
    quality: "Bon",
    statusClass: "bg-blue-100 text-blue-700",
    qualityBadgeClass: "bg-blue-100 text-blue-700",
  },
  {
    id: "3",
    patientName: "Sophie Bernard",
    patientInitials: "SB",
    date: "Hier 16:45",
    duration: "52min",
    fatigueScore: 31,
    quality: "Excellent",
    statusClass: "bg-purple-100 text-purple-700",
    qualityBadgeClass: "bg-green-100 text-green-700",
  },
  {
    id: "4",
    patientName: "Luc Petit",
    patientInitials: "LP",
    date: "Hier 09:20",
    duration: "41min",
    fatigueScore: 55,
    quality: "Moyen",
    statusClass: "bg-amber-100 text-amber-700",
    qualityBadgeClass: "bg-amber-100 text-amber-700",
  },
]);

function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

let timer: number | null = null;

onMounted(() => {
  updateTime();
  timer = window.setInterval(updateTime, 30000);
});

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<style scoped>
</style>
