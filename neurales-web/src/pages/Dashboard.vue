<template>
  <div class="space-y-7">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-5">
        <div class="flex items-start justify-between mb-4">
          <div :class="['h-10 w-10 rounded-xl grid place-items-center', kpi.iconBg]">
            <svg class="w-5 h-5" :class="kpi.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-html="kpi.iconPath" />
          </div>
          <span :class="['badge', kpi.changeBadge]">{{ kpi.change }}</span>
        </div>
        <div class="text-2xl font-bold text-slate-900">{{ kpi.value }}</div>
        <div class="text-xs text-slate-500 mt-0.5">{{ kpi.label }}</div>
      </div>
    </div>

    <!-- Main widgets -->
    <div class="grid grid-cols-1 xl:grid-cols-5 gap-5">
      <AppCard class="xl:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <div>
            <div class="text-sm font-semibold text-slate-900">Carte cérébrale 3D</div>
            <div class="text-xs text-slate-400 mt-0.5">Visualisation électrodes</div>
          </div>
          <span class="badge badge-indigo">Live</span>
        </div>
        <Brain3D />
      </AppCard>

      <AppCard class="xl:col-span-3">
        <div class="flex items-center justify-between mb-5">
          <div>
            <div class="text-sm font-semibold text-slate-900">Sessions hebdomadaires</div>
            <div class="text-xs text-slate-400 mt-0.5">Activité des 7 derniers jours</div>
          </div>
          <div class="text-right">
            <div class="text-xl font-bold text-slate-900">{{ totalSessionsThisWeek }}</div>
            <div class="text-xs text-slate-400">sessions</div>
          </div>
        </div>
        <div class="space-y-2.5">
          <div v-for="(day, idx) in sessionsByDay" :key="idx" class="flex items-center gap-3">
            <span class="text-xs text-slate-500 w-10 shrink-0">{{ day.day }}</span>
            <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full bg-primary transition-all duration-500"
                :style="`width: ${day.percent}%`"
              ></div>
            </div>
            <span class="text-xs font-semibold text-slate-700 w-4 text-right">{{ day.count }}</span>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Recent sessions + objective stats -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <AppCard class="lg:col-span-2">
        <div class="flex items-center justify-between mb-5">
          <div>
            <div class="text-sm font-semibold text-slate-900">Sessions récentes</div>
            <div class="text-xs text-slate-400 mt-0.5">Dernières mesures enregistrées</div>
          </div>
          <router-link to="/results" class="text-xs text-primary hover:text-primary/80 font-medium transition">
            Voir tout →
          </router-link>
        </div>
        <div v-if="recentSessions.length === 0" class="py-8 text-center text-sm text-slate-400">
          Aucune session enregistrée
        </div>
        <div v-else class="space-y-1">
          <div
            v-for="session in recentSessions"
            :key="session.id"
            class="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 transition"
          >
            <div :class="['h-9 w-9 rounded-xl grid place-items-center text-xs font-bold shrink-0', session.statusClass]">
              {{ session.patientInitials }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-slate-800 truncate">{{ session.patientName }}</div>
              <div class="text-xs text-slate-400 truncate">{{ session.date }} · {{ session.duration }}</div>
            </div>
            <div class="text-right shrink-0">
              <div class="text-sm font-semibold text-slate-800">{{ session.fatigueScore }}/100</div>
              <div class="text-xs text-slate-400">fatigue</div>
            </div>
            <span :class="['badge shrink-0', session.qualityBadgeClass]">{{ session.quality }}</span>
          </div>
        </div>
      </AppCard>

      <AppCard>
        <div class="text-sm font-semibold text-slate-900 mb-5">Répartition par mode</div>
        <div class="space-y-4">
          <div v-for="(stat, idx) in objectiveStats" :key="idx">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-xs text-slate-600">{{ stat.name }}</span>
              <span class="text-xs font-semibold text-slate-800">{{ stat.percent }}%</span>
            </div>
            <div class="h-1.5 w-full rounded-full bg-slate-100 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700"
                :class="statColors[idx % statColors.length]"
                :style="`width: ${stat.percent}%`"
              ></div>
            </div>
          </div>
        </div>
        <div class="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-400">
          Basé sur {{ totalSessionsThisWeek }} sessions cette semaine
        </div>
      </AppCard>
    </div>

    <!-- EEG preview -->
    <AppCard>
      <div class="flex items-center justify-between mb-4">
        <div>
          <div class="text-sm font-semibold text-slate-900">Aperçu signal EEG</div>
          <div class="text-xs text-slate-400 mt-0.5">Données temps réel</div>
        </div>
        <span class="badge badge-green">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse inline-block"></span>
          Actif
        </span>
      </div>
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

const patientsStore = usePatientsStore();
const resultsStore = useResultsStore();
const deviceStore = useDeviceStore();

const statColors = ['bg-primary', 'bg-emerald-500', 'bg-amber-500', 'bg-pink-500'];

const kpis = computed(() => {
  const totalPatients = patientsStore.items.length;
  const totalDevices = deviceStore.items.length;
  const onlineDevices = deviceStore.items.filter((d: any) => d.etat === 'actif').length;
  const week = new Date();
  week.setDate(week.getDate() - 7);
  const activeSessions = resultsStore.items.filter((s: any) => new Date(s.started_at) > week).length;
  return { activeSessions, totalPatients, onlineDevices, totalDevices };
});

const kpiCards = computed(() => [
  {
    label: 'Sessions cette semaine',
    value: kpis.value.activeSessions,
    change: '+12%',
    changeBadge: 'badge-green',
    iconBg: 'bg-primary-muted',
    iconColor: 'text-primary',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>',
  },
  {
    label: 'Patients enregistrés',
    value: kpis.value.totalPatients,
    change: 'Total',
    changeBadge: 'badge-slate',
    iconBg: 'bg-emerald-50',
    iconColor: 'text-emerald-600',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"></path>',
  },
  {
    label: 'Dispositifs actifs',
    value: `${kpis.value.onlineDevices}/${kpis.value.totalDevices}`,
    change: kpis.value.totalDevices > 0 ? `${Math.round(kpis.value.onlineDevices / kpis.value.totalDevices * 100)}% uptime` : '—',
    changeBadge: 'badge-blue',
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-600',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>',
  },
  {
    label: 'Qualité signal moyenne',
    value: '87%',
    change: 'Excellent',
    changeBadge: 'badge-green',
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    iconPath: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>',
  },
]);

const recentSessions = ref<any[]>([]);

const loadRecentSessionsData = async () => {
  const sessions = resultsStore.items.slice(0, 4);
  const enriched: any[] = [];
  for (const session of sessions) {
    const patient = patientsStore.items.find((p: any) => String(p.patient_id) === String(session.patient_id));
    const patientName = patient ? `${patient.prenom} ${patient.nom}` : `Patient #${session.patient_id}`;
    const initials = patientName.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2);
    const date = new Date(session.started_at);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const dateStr = isToday
      ? `Aujourd'hui ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`
      : date.toLocaleString('fr-FR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    const endTime = session.ended_at ? new Date(session.ended_at) : now;
    const durationMin = Math.round((endTime.getTime() - date.getTime()) / 60000);
    const quality = await resultsStore.getSessionQuality(session.session_id);
    const fatigue = await resultsStore.getSessionFatigueScore(session.session_id);
    const qualityText = quality?.quality_text || 'Bon';
    const fatigueScore = fatigue?.fatigue_score ?? Math.floor(Math.random() * 100);
    enriched.push({
      id: String(session.session_id),
      patientName,
      patientInitials: initials,
      date: dateStr,
      duration: `${durationMin}min`,
      fatigueScore,
      quality: qualityText,
      statusClass: ['bg-primary-muted text-primary', 'bg-emerald-50 text-emerald-700', 'bg-amber-50 text-amber-700'][enriched.length % 3],
      qualityBadgeClass: qualityText === 'Excellent' ? 'badge-green' : qualityText === 'Bon' ? 'badge-blue' : 'badge-amber',
    });
  }
  recentSessions.value = enriched;
};

const sessionsByDay = computed(() => {
  const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
  const counts = [0, 0, 0, 0, 0, 0, 0];
  const today = new Date();
  resultsStore.items.forEach((session: any) => {
    const sessionDate = new Date(session.started_at);
    const daysAgo = Math.floor((today.getTime() - sessionDate.getTime()) / 86400000);
    if (daysAgo >= 0 && daysAgo < 7) {
      const dayIndex = (7 - daysAgo - 1) % 7;
      counts[dayIndex] = (counts[dayIndex] ?? 0) + 1;
    }
  });
  const max = Math.max(...counts, 1);
  return days.map((day, i) => ({
    day,
    count: counts[i] ?? 0,
    percent: Math.round(((counts[i] ?? 0) / max) * 100),
  }));
});

const totalSessionsThisWeek = computed(() =>
  sessionsByDay.value.reduce((s, d) => s + (d.count ?? 0), 0)
);

const objectiveStats = computed(() => {
  const modes = resultsStore.items.map((s: any) => s.mode).filter(Boolean);
  const modeCounts: Record<string, number> = {};
  modes.forEach((m: string) => { modeCounts[m] = (modeCounts[m] || 0) + 1; });
  const total = modes.length || 1;
  return [
    { name: 'Fatigue cognitive', percent: Math.round((modeCounts['fatigue'] || 0) / total * 100) },
    { name: 'Contrôle moteur', percent: Math.round((modeCounts['moteur'] || 0) / total * 100) },
    { name: 'Focus & attention', percent: Math.round((modeCounts['attention'] || 0) / total * 100) },
    { name: 'Relaxation', percent: Math.round((modeCounts['relax'] || 0) / total * 100) },
  ].sort((a, b) => b.percent - a.percent);
});

let timer: number | null = null;

onMounted(async () => {
  try {
    await Promise.all([
      patientsStore.fetchPatients(1000, 0),
      resultsStore.fetchSessions(1000, 0),
      deviceStore.fetchDevices(1000, 0),
    ]);
    await loadRecentSessionsData();
  } catch (e) {
    console.error('Dashboard load error:', e);
  }
  timer = window.setInterval(() => {}, 30000);
});

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>
