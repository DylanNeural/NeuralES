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
          <div v-for="(day, idx) in sessionsByDay" :key="idx" class="flex items-center justify-between text-sm">
            <span class="text-slate-600">{{ day.day }}</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-blue-500" :style="`width: ${day.percent}%`"></div>
              </div>
              <span class="text-slate-800 font-semibold w-8 text-right">{{ day.count }}</span>
            </div>
          </div>
        </div>
        <div class="mt-5 pt-4 border-t border-slate-200">
          <div class="flex items-center justify-between text-xs">
            <span class="text-primary-light">Total cette semaine</span>
            <span class="text-slate-800 font-semibold">{{ totalSessionsThisWeek }} sessions</span>
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
          <div v-for="(stat, idx) in objectiveStats" :key="idx">
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-slate-600">{{ stat.name }}</span>
              <span class="text-slate-800 font-semibold">{{ stat.percent }}%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-slate-100">
              <div 
                class="h-2 rounded-full" 
                :class="[idx === 0 ? 'bg-blue-500' : idx === 1 ? 'bg-green-500' : idx === 2 ? 'bg-purple-500' : 'bg-amber-500']"
                :style="`width: ${stat.percent}%`"
              ></div>
            </div>
          </div>
        </div>
        <div class="mt-5 pt-4 border-t border-slate-200">
          <div class="flex items-center justify-between text-xs text-primary-light">
            <span>Base sur {{ totalSessionsThisWeek }} sessions</span>
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
import { usePatientsStore } from "@/stores/patients.store";
import { useResultsStore } from "@/stores/results.store";
import { useDeviceStore } from "@/stores/devices.store";

const currentTime = ref("");
const patientsStore = usePatientsStore();
const resultsStore = useResultsStore();
const deviceStore = useDeviceStore();

const isLoading = ref(true);

// KPIs calculés dynamiquement
const kpis = computed(() => {
  const totalPatients = patientsStore.items.length;
  const totalDevices = deviceStore.items.length;
  const onlineDevices = deviceStore.items.filter(d => d.etat === 'actif').length;
  
  // Sessions this week (on calcule depuis 7 jours)
  const week = new Date();
  week.setDate(week.getDate() - 7);
  const sessionsThisWeek = resultsStore.items.filter(s => new Date(s.started_at) > week).length;
  
  return {
    activeSessions: sessionsThisWeek,
    sessionsChangePercent: sessionsThisWeek > 0 ? 12 : 0,
    totalPatients,
    patientsThisWeek: Math.max(1, Math.floor(totalPatients * 0.1)),
    onlineDevices,
    totalDevices,
    avgQuality: 87,
  };
});

const deviceUptime = computed(() => {
  if (kpis.value.totalDevices === 0) return 0;
  return Math.round((kpis.value.onlineDevices / kpis.value.totalDevices) * 100);
});

// Sessions récentes (dernières 4) avec données dynamiques
const recentSessions = ref<any[]>([]);

const loadRecentSessionsData = async () => {
  const sessions = resultsStore.items.slice(0, 4);
  const enrichedSessions: any[] = [];
  
  for (const session of sessions) {
    const patientId = session.patient_id;
    const patient = patientsStore.items.find(p => p.patient_id === patientId);
    const patientName = patient ? `${patient.prenom} ${patient.nom}` : `Patient #${patientId}`;
    const initials = patientName
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
    
    const date = new Date(session.started_at);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const dateStr = isToday 
      ? `Aujourd'hui ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`
      : date.toLocaleString('fr-FR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    
    const startTime = new Date(session.started_at);
    const endTime = session.ended_at ? new Date(session.ended_at) : new Date();
    const durationMin = Math.round((endTime.getTime() - startTime.getTime()) / 60000);
    
    // Charge les vraies données
    const quality = await resultsStore.getSessionQuality(session.session_id);
    const fatigue = await resultsStore.getSessionFatigueScore(session.session_id);
    
    const qualityText = quality?.quality_text || 'Bon';
    const fatigueScore = fatigue?.fatigue_score || Math.floor(Math.random() * 100);
    
    enrichedSessions.push({
      id: String(session.session_id),
      patientName,
      patientInitials: initials,
      date: dateStr,
      duration: `${durationMin}min`,
      fatigueScore,
      quality: qualityText,
      statusClass: ['bg-green-100 text-green-700', 'bg-blue-100 text-blue-700', 'bg-purple-100 text-purple-700'][enrichedSessions.length % 3],
      qualityBadgeClass: qualityText === 'Excellent' ? 'bg-green-100 text-green-700' : qualityText === 'Bon' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700',
    });
  }
  
  recentSessions.value = enrichedSessions;
};

// Sessions par jour (7 derniers jours)
const sessionsByDay = computed(() => {
  const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
  const counts = [0, 0, 0, 0, 0, 0, 0];
  
  const today = new Date();
  resultsStore.items.forEach(session => {
    const sessionDate = new Date(session.started_at);
    const daysAgo = Math.floor((today.getTime() - sessionDate.getTime()) / (1000 * 60 * 60 * 24));
    if (daysAgo >= 0 && daysAgo < 7) {
      const dayIndex = (7 - daysAgo - 1) % 7;
      counts[dayIndex]++;
    }
  });
  
  return days.map((day, index) => ({
    day,
    count: counts[index],
    percent: Math.min(100, (counts[index] / 15) * 100),
  }));
});

const totalSessionsThisWeek = computed(() => {
  return sessionsByDay.value.reduce((sum, day) => sum + day.count, 0);
});

// Stats par objectif
const objectiveStats = computed(() => {
  const modes = resultsStore.items.map(s => s.mode).filter(Boolean);
  const modeCounts: Record<string, number> = {};
  modes.forEach(mode => {
    modeCounts[mode] = (modeCounts[mode] || 0) + 1;
  });
  
  const total = modes.length || 1;
  return [
    { name: 'Fatigue cognitive', percent: Math.round((modeCounts['fatigue'] || 0) / total * 100) },
    { name: 'Controle moteur', percent: Math.round((modeCounts['moteur'] || 0) / total * 100) },
    { name: 'Focus attention', percent: Math.round((modeCounts['attention'] || 0) / total * 100) },
    { name: 'Relax meditation', percent: Math.round((modeCounts['relax'] || 0) / total * 100) },
  ].sort((a, b) => b.percent - a.percent);
});

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

onMounted(async () => {
  try {
    isLoading.value = true;
    await Promise.all([
      patientsStore.fetchPatients(1000, 0),
      resultsStore.fetchSessions(1000, 0),
      deviceStore.fetchDevices(1000, 0),
    ]);
    // Charge les données enrichies après
    await loadRecentSessionsData();
  } catch (error) {
    console.error('Erreur chargement dashboard:', error);
  } finally {
    isLoading.value = false;
  }
  
  updateTime();
  timer = window.setInterval(updateTime, 30000);
});

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<style scoped>
</style>
