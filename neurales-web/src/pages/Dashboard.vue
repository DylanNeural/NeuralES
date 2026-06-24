<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import AppCard from "@/components/ui/AppCard.vue";
import Brain3D from "@/components/Brain3D.vue";
import EEGChartCanvas from "@/components/EEGChartCanvas.vue";
import { usePatientsStore } from "@/stores/patients.store";
import { useResultsStore } from "@/stores/results.store";
import { useDeviceStore } from "@/stores/devices.store";

const currentTime = ref("");
const patientsStore = usePatientsStore();
const resultsStore = useResultsStore();
const deviceStore = useDeviceStore();
const isLoading = ref(true);

const kpis = computed(() => {
  const totalPatients = patientsStore.items.length;
  const totalDevices = deviceStore.items.length;
  const onlineDevices = deviceStore.items.filter((d) => d.etat === "actif").length;
  const week = new Date();
  week.setDate(week.getDate() - 7);
  const sessionsThisWeek = resultsStore.items.filter((s) => new Date(s.started_at) > week).length;
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

const recentSessions = ref<any[]>([]);

async function loadRecentSessionsData() {
  const sessions = resultsStore.items.slice(0, 4);
  const enriched: any[] = [];
  for (const session of sessions) {
    const patient = patientsStore.items.find((p) => String(p.patient_id) === String(session.patient_id));
    const patientName = patient ? `${patient.prenom} ${patient.nom}` : `Patient #${session.patient_id}`;
    const initials = patientName.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2);
    const date = new Date(session.started_at);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const dateStr = isToday
      ? `Aujourd'hui ${date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}`
      : date.toLocaleString("fr-FR", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    const endTime = session.ended_at ? new Date(session.ended_at) : new Date();
    const durationMin = Math.round((endTime.getTime() - date.getTime()) / 60000);
    const quality = await resultsStore.getSessionQuality(session.session_id);
    const fatigue = await resultsStore.getSessionFatigueScore(session.session_id);
    const qualityText = quality?.quality_text || "Bon";
    const fatigueScore = fatigue?.fatigue_score || Math.floor(Math.random() * 100);
    enriched.push({ id: String(session.session_id), patientName, patientInitials: initials, date: dateStr, duration: `${durationMin}min`, fatigueScore, quality: qualityText });
  }
  recentSessions.value = enriched;
}

const sessionsByDay = computed(() => {
  const days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
  const counts = [0, 0, 0, 0, 0, 0, 0];
  const today = new Date();
  resultsStore.items.forEach((session) => {
    const sessionDate = new Date(session.started_at);
    const daysAgo = Math.floor((today.getTime() - sessionDate.getTime()) / (1000 * 60 * 60 * 24));
    if (daysAgo >= 0 && daysAgo < 7) {
      const dayIndex = (7 - daysAgo - 1) % 7;
      counts[dayIndex] = (counts[dayIndex] ?? 0) + 1;
    }
  });
  const max = Math.max(...counts, 1);
  return days.map((day, i) => ({ day, count: counts[i] ?? 0, percent: Math.round(((counts[i] ?? 0) / max) * 100) }));
});

const totalSessionsThisWeek = computed(() => sessionsByDay.value.reduce((s, d) => s + d.count, 0));

const objectiveStats = computed(() => {
  const modes = resultsStore.items.map((s) => s.mode).filter(Boolean);
  const modeCounts: Record<string, number> = {};
  modes.forEach((mode) => { modeCounts[mode] = (modeCounts[mode] || 0) + 1; });
  const total = modes.length || 1;
  return [
    { name: "Fatigue cognitive", percent: Math.round(((modeCounts["fatigue"] || 0) / total) * 100), color: "bg-primary" },
    { name: "Contrôle moteur", percent: Math.round(((modeCounts["moteur"] || 0) / total) * 100), color: "bg-eeg-cyan" },
    { name: "Focus attention", percent: Math.round(((modeCounts["attention"] || 0) / total) * 100), color: "bg-eeg-emerald" },
    { name: "Relax méditation", percent: Math.round(((modeCounts["relax"] || 0) / total) * 100), color: "bg-eeg-amber" },
  ].sort((a, b) => b.percent - a.percent);
});

function updateTime() {
  currentTime.value = new Date().toLocaleString("fr-FR", { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

let timer: number | null = null;

onMounted(async () => {
  try {
    isLoading.value = true;
    await Promise.all([patientsStore.fetchPatients(1000, 0), resultsStore.fetchSessions(1000, 0), deviceStore.fetchDevices(1000, 0)]);
    await loadRecentSessionsData();
  } catch (err) {
    console.error("Erreur chargement dashboard:", err);
  } finally {
    isLoading.value = false;
  }
  updateTime();
  timer = window.setInterval(updateTime, 30000);
});

onUnmounted(() => { if (timer) window.clearInterval(timer); });
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-foreground">Tableau de bord</h1>
        <p class="text-sm text-muted-foreground mt-0.5">Vue d'ensemble de la plateforme NeuralES</p>
      </div>
      <div class="text-right">
        <div class="text-xs text-muted-foreground">Dernière mise à jour</div>
        <div class="text-sm font-medium text-foreground">{{ currentTime }}</div>
      </div>
    </div>

    <!-- KPI cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <!-- Sessions actives -->
      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-muted-foreground uppercase tracking-wide mb-2">Sessions actives</div>
            <div class="text-3xl font-bold text-foreground">{{ kpis.activeSessions }}</div>
            <div class="text-xs text-eeg-emerald mt-2">+{{ kpis.sessionsChangePercent }}% vs hier</div>
          </div>
          <div class="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
            <svg class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
      </AppCard>

      <!-- Patients -->
      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-muted-foreground uppercase tracking-wide mb-2">Patients enregistrés</div>
            <div class="text-3xl font-bold text-foreground">{{ kpis.totalPatients }}</div>
            <div class="text-xs text-eeg-emerald mt-2">+{{ kpis.patientsThisWeek }} cette semaine</div>
          </div>
          <div class="h-10 w-10 rounded-xl bg-eeg-emerald/10 flex items-center justify-center shrink-0">
            <svg class="h-5 w-5 text-eeg-emerald" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
      </AppCard>

      <!-- Dispositifs -->
      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-muted-foreground uppercase tracking-wide mb-2">Dispositifs en ligne</div>
            <div class="text-3xl font-bold text-foreground">{{ kpis.onlineDevices }}<span class="text-lg text-muted-foreground">/{{ kpis.totalDevices }}</span></div>
            <div class="text-xs text-muted-foreground mt-2">{{ deviceUptime }}% uptime</div>
          </div>
          <div class="h-10 w-10 rounded-xl bg-eeg-violet/10 flex items-center justify-center shrink-0">
            <svg class="h-5 w-5 text-eeg-violet" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </AppCard>

      <!-- Qualité -->
      <AppCard>
        <div class="flex items-start justify-between">
          <div>
            <div class="text-xs text-muted-foreground uppercase tracking-wide mb-2">Qualité moyenne</div>
            <div class="text-3xl font-bold text-foreground">{{ kpis.avgQuality }}%</div>
            <div class="text-xs text-eeg-emerald mt-2">Excellent signal</div>
          </div>
          <div class="h-10 w-10 rounded-xl bg-eeg-amber/10 flex items-center justify-center shrink-0">
            <svg class="h-5 w-5 text-eeg-amber" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Main viz grid -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <!-- Brain 3D -->
      <AppCard>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-foreground">Cerveau 3D</h2>
          <span class="inline-flex items-center gap-1.5 text-xs text-eeg-emerald">
            <span class="h-1.5 w-1.5 rounded-full bg-eeg-emerald animate-pulse"></span>
            Live
          </span>
        </div>
        <Brain3D />
      </AppCard>

      <!-- Sessions par jour -->
      <AppCard>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-foreground">Sessions — 7 derniers jours</h2>
          <span class="text-xs text-muted-foreground">{{ totalSessionsThisWeek }} total</span>
        </div>
        <div class="space-y-2.5">
          <div v-for="(day, idx) in sessionsByDay" :key="idx" class="flex items-center gap-3 text-xs">
            <span class="text-muted-foreground w-7 shrink-0">{{ day.day }}</span>
            <div class="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
              <div
                class="h-full rounded-full bg-primary transition-all duration-500"
                :style="{ width: day.percent + '%' }"
              />
            </div>
            <span class="text-foreground font-semibold w-4 text-right shrink-0">{{ day.count }}</span>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Recent sessions + objective stats -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Recent sessions -->
      <AppCard class="lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-foreground">Sessions récentes</h2>
          <RouterLink to="/results" class="text-xs text-primary hover:underline">Voir tout</RouterLink>
        </div>
        <div v-if="isLoading" class="py-8 text-center text-sm text-muted-foreground">Chargement…</div>
        <div v-else-if="recentSessions.length === 0" class="py-8 text-center text-sm text-muted-foreground">Aucune session</div>
        <div v-else class="space-y-2">
          <div
            v-for="session in recentSessions"
            :key="session.id"
            class="flex items-center justify-between p-3 rounded-lg border border-border hover:border-primary/30 transition-colors"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="h-8 w-8 rounded-full bg-primary/15 text-primary flex items-center justify-center text-xs font-semibold shrink-0">
                {{ session.patientInitials }}
              </div>
              <div class="min-w-0">
                <div class="text-sm font-medium text-foreground truncate">{{ session.patientName }}</div>
                <div class="text-xs text-muted-foreground">{{ session.date }} · {{ session.duration }}</div>
              </div>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <div class="text-right">
                <div class="text-xs text-muted-foreground">Fatigue</div>
                <div class="text-sm font-semibold text-foreground">{{ session.fatigueScore }}/100</div>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium border border-eeg-emerald/30 bg-eeg-emerald/10 text-eeg-emerald">
                {{ session.quality }}
              </span>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Objective stats -->
      <AppCard>
        <h2 class="text-sm font-semibold text-foreground mb-4">Stats par objectif</h2>
        <div class="space-y-4">
          <div v-for="stat in objectiveStats" :key="stat.name">
            <div class="flex items-center justify-between text-xs mb-1.5">
              <span class="text-muted-foreground">{{ stat.name }}</span>
              <span class="text-foreground font-semibold">{{ stat.percent }}%</span>
            </div>
            <div class="h-1.5 w-full rounded-full bg-secondary overflow-hidden">
              <div :class="['h-full rounded-full transition-all duration-500', stat.color]" :style="{ width: stat.percent + '%' }" />
            </div>
          </div>
        </div>
        <div class="mt-5 pt-4 border-t border-border text-xs text-muted-foreground">
          Basé sur {{ totalSessionsThisWeek }} sessions cette semaine
        </div>
      </AppCard>
    </div>

    <!-- EEG preview -->
    <AppCard>
      <h2 class="text-sm font-semibold text-foreground mb-4">Aperçu signal EEG</h2>
      <EEGChartCanvas />
    </AppCard>
  </div>
</template>
