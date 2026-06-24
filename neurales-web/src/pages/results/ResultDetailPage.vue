<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
import AppButton from "@/components/ui/AppButton.vue";
import FatigueGauge from "@/components/FatigueGauge.vue";
import { useResultsStore } from "@/stores/results.store";
import { http as api } from "@/api/http";
import { isDesktopRuntime } from "@/utils/desktop-runtime";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();

const apiError = ref<string | null>(null);
const session = computed(() => resultsStore.current);
const isDeleting = ref(false);

interface AlertItem {
  type: string;
  message: string;
  severity: string;
  triggered_at: string | null;
}

const fatigueScore = ref<number | null>(null);
const qualityScore = ref<number | null>(null);
const qualityText = ref<string>('');
const sessionAlerts = ref<AlertItem[]>([]);
const isLoadingMetrics = ref(false);

function goBack() { router.back(); }

function formatDate(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("fr-FR");
}

function fatigueColor(score: number | null) {
  if (score === null) return '#94a3b8';
  if (score < 30) return '#22c55e';
  if (score < 60) return '#f59e0b';
  if (score < 80) return '#f97316';
  return '#ef4444';
}

function severityClass(severity: string) {
  if (severity === 'critical') return 'border-red-500/20 bg-red-500/10 text-red-400';
  if (severity === 'warning') return 'border-amber-500/20 bg-amber-500/10 text-amber-400';
  return 'border-blue-500/20 bg-blue-500/10 text-blue-400';
}

async function handleDelete() {
  if (!confirm("Supprimer cette session ?")) return;
  try {
    isDeleting.value = true;
    await resultsStore.deleteSession(String(route.params.id));
    router.push("/results");
  } catch {
    apiError.value = "Erreur lors de la suppression";
  } finally {
    isDeleting.value = false;
  }
}

function exportPDF() {
  window.print();
}

async function fetchMetrics(sessionId: string) {
  if (isDesktopRuntime()) {
    fatigueScore.value = 23;
    qualityScore.value = 82;
    qualityText.value = 'Bon';
    return;
  }
  isLoadingMetrics.value = true;
  try {
    const [fatigueRes, qualityRes, alertsRes] = await Promise.allSettled([
      api.get(`/analytics/sessions/${sessionId}/fatigue-score`),
      api.get(`/analytics/sessions/${sessionId}/quality`),
      api.get(`/analytics/sessions/${sessionId}/alerts`),
    ]);
    if (fatigueRes.status === 'fulfilled') fatigueScore.value = fatigueRes.value.data.fatigue_score ?? null;
    if (qualityRes.status === 'fulfilled') {
      qualityScore.value = qualityRes.value.data.quality_score ?? null;
      qualityText.value = qualityRes.value.data.quality_text ?? '';
    }
    if (alertsRes.status === 'fulfilled') sessionAlerts.value = alertsRes.value.data.alerts ?? [];
  } finally {
    isLoadingMetrics.value = false;
  }
}

onMounted(async () => {
  const id = String(route.params.id);
  if (!id) { apiError.value = "Identifiant invalide."; return; }
  try {
    await resultsStore.fetchSessionById(id);
    await fetchMetrics(id);
  } catch {
    apiError.value = resultsStore.error ?? "Erreur inconnue.";
  }
});
</script>

<template>
  <div class="max-w-3xl space-y-6 animate-fade-in print:max-w-none print:space-y-4">
    <!-- Header (hidden on print) -->
    <div class="flex items-center justify-between print:hidden">
      <div class="flex items-center gap-3">
        <AppButton variant="ghost" size="sm" @click="goBack">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Retour
        </AppButton>
        <h1 class="text-2xl font-bold text-foreground">Détail de la session</h1>
      </div>
      <AppButton v-if="session" variant="ghost" size="sm" @click="exportPDF">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Exporter PDF
      </AppButton>
    </div>

    <!-- Print header (only on print) -->
    <div class="hidden print:block mb-6">
      <h1 class="text-2xl font-bold">Rapport de session EEG — NeuralES</h1>
      <p class="text-sm text-gray-500 mt-1">Session #{{ session?.session_id }} · Généré le {{ new Date().toLocaleString('fr-FR') }}</p>
    </div>

    <!-- Error -->
    <div v-if="apiError" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive print:hidden">
      {{ apiError }}
    </div>

    <!-- KPI cards: fatigue + quality -->
    <div v-if="session" class="grid grid-cols-2 gap-4">
      <!-- Fatigue gauge -->
      <AppCard class="!p-4 flex flex-col items-center gap-3">
        <h2 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider self-start">Score de fatigue</h2>
        <div v-if="isLoadingMetrics" class="py-8 text-xs text-muted-foreground">Chargement…</div>
        <FatigueGauge v-else-if="fatigueScore !== null" :score="fatigueScore" :size="140" />
        <div v-else class="py-8 text-xs text-muted-foreground">Non disponible</div>
      </AppCard>

      <!-- Quality card -->
      <AppCard class="!p-4 flex flex-col gap-3">
        <h2 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Qualité du signal</h2>
        <div v-if="isLoadingMetrics" class="py-8 text-xs text-muted-foreground">Chargement…</div>
        <div v-else-if="qualityScore !== null" class="flex-1 flex flex-col items-center justify-center gap-3">
          <div class="text-5xl font-bold" :style="{ color: fatigueColor(100 - qualityScore) }">
            {{ qualityScore }}
          </div>
          <div class="text-sm text-muted-foreground">/ 100</div>
          <div class="px-3 py-1 rounded-full text-xs font-semibold border"
               :class="qualityScore >= 85 ? 'border-green-500/30 bg-green-500/10 text-green-400'
                      : qualityScore >= 70 ? 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                      : 'border-red-500/30 bg-red-500/10 text-red-400'">
            {{ qualityText }}
          </div>
        </div>
        <div v-else class="py-8 text-xs text-muted-foreground">Non disponible</div>
      </AppCard>
    </div>

    <!-- Session metadata -->
    <AppCard v-if="session">
      <div class="flex items-center gap-4 mb-6">
        <div class="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
          <svg class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-foreground font-mono">Session #{{ session.session_id }}</h2>
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20 mt-1">
            {{ session.mode || "—" }}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 rounded-xl bg-secondary/20 border border-border">
        <div>
          <div class="text-xs text-muted-foreground mb-1">Patient</div>
          <div class="text-sm font-semibold text-foreground">{{ session.patient_id ? `#${session.patient_id}` : "—" }}</div>
        </div>
        <div>
          <div class="text-xs text-muted-foreground mb-1">Début</div>
          <div class="text-sm font-semibold text-foreground">{{ formatDate(session.started_at) }}</div>
        </div>
        <div>
          <div class="text-xs text-muted-foreground mb-1">Fin</div>
          <div class="text-sm font-semibold text-foreground">{{ formatDate(session.ended_at) }}</div>
        </div>
        <div>
          <div class="text-xs text-muted-foreground mb-1">Dispositif</div>
          <div class="text-sm font-semibold text-foreground">{{ session.device_id ?? "—" }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="[label, value] in [
          ['Organisation', session.organisation_id],
          ['Utilisateur créateur', session.created_by_user_id],
          ['Consentement', session.consent_id],
          ['Version app', session.app_version],
          ['Notes', session.notes],
        ]" :key="label" class="space-y-1">
          <div class="text-xs text-muted-foreground font-medium uppercase tracking-wide">{{ label }}</div>
          <div class="text-sm font-medium text-foreground">{{ value ?? "—" }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Alerts -->
    <AppCard v-if="sessionAlerts.length > 0" class="!p-4">
      <h2 class="text-sm font-semibold text-foreground mb-3">Alertes déclenchées</h2>
      <div class="space-y-2">
        <div
          v-for="(alert, i) in sessionAlerts"
          :key="i"
          class="flex items-start gap-3 px-3 py-2.5 rounded-lg border text-xs"
          :class="severityClass(alert.severity)"
        >
          <svg class="h-3.5 w-3.5 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div class="flex-1">
            <span class="font-semibold">{{ alert.type }}</span>
            <span class="ml-2 opacity-80">{{ alert.message }}</span>
          </div>
          <span v-if="alert.triggered_at" class="opacity-60 shrink-0">
            {{ new Date(alert.triggered_at).toLocaleTimeString('fr-FR') }}
          </span>
        </div>
      </div>
    </AppCard>

    <!-- Actions (hidden on print) -->
    <div class="flex gap-3 print:hidden">
      <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">
        Supprimer
      </AppButton>
    </div>
  </div>
</template>

<style>
@media print {
  nav, aside, header, .print\:hidden { display: none !important; }
  body { background: white !important; color: black !important; }
  .animate-fade-in { animation: none !important; }
}
</style>
