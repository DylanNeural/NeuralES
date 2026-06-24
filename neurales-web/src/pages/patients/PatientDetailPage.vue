<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
import AppButton from "@/components/ui/AppButton.vue";
import { usePatientsStore } from "@/stores/patients.store";
import { http as api } from "@/api/http";
import { isDesktopRuntime } from "@/utils/desktop-runtime";

const route = useRoute();
const router = useRouter();
const patientsStore = usePatientsStore();

const apiError = ref<string | null>(null);
const patient = computed(() => patientsStore.current);
const isDeleting = ref(false);

interface PatientSession {
  session_id: number;
  mode: string | null;
  started_at: string | null;
  ended_at: string | null;
  fatigue_score: number | null;
}

const patientSessions = ref<PatientSession[]>([]);
const isLoadingSessions = ref(false);

function goBack() { router.back(); }

function formatDate(value?: string | null) {
  if (!value) return "—";
  return value;
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("fr-FR");
}

function formatDateShort(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "2-digit" });
}

const fields = computed(() => [
  { label: "Identifiant interne", value: patient.value?.identifiant_interne },
  { label: "Organisation", value: patient.value?.organisation_id },
  { label: "Nom", value: patient.value?.nom },
  { label: "Prénom", value: patient.value?.prenom },
  { label: "Date de naissance", value: formatDate(patient.value?.date_naissance) },
  { label: "Sexe", value: patient.value?.sexe },
  { label: "N° sécurité sociale", value: patient.value?.numero_securite_sociale },
  { label: "Service", value: patient.value?.service },
  { label: "Médecin référent", value: patient.value?.medecin_referent },
  { label: "Remarque", value: patient.value?.remarque },
  { label: "Notes", value: patient.value?.notes },
  { label: "Créé le", value: formatDateTime(patient.value?.created_at) },
]);

function fatigueColor(score: number | null) {
  if (score === null) return '#334155';
  if (score < 30) return '#22c55e';
  if (score < 60) return '#f59e0b';
  if (score < 80) return '#f97316';
  return '#ef4444';
}

function fatigueLabel(score: number | null) {
  if (score === null) return '—';
  if (score < 30) return 'Faible';
  if (score < 60) return 'Modérée';
  if (score < 80) return 'Élevée';
  return 'Critique';
}

const chartSessions = computed(() =>
  patientSessions.value.filter(s => s.fatigue_score !== null).slice().reverse()
);

const chartMax = computed(() =>
  Math.max(100, ...chartSessions.value.map(s => s.fatigue_score ?? 0))
);

async function handleDelete() {
  if (!confirm("Supprimer ce patient ?")) return;
  try {
    isDeleting.value = true;
    await patientsStore.deletePatient(String(route.params.id));
    router.push("/patients");
  } catch {
    apiError.value = "Erreur lors de la suppression";
  } finally {
    isDeleting.value = false;
  }
}

async function fetchPatientHistory(patientId: string) {
  if (isDesktopRuntime()) return;
  isLoadingSessions.value = true;
  try {
    const res = await api.get(`/analytics/patients/${patientId}/history`);
    patientSessions.value = res.data.sessions ?? [];
  } catch {
    // silently skip if analytics not available
  } finally {
    isLoadingSessions.value = false;
  }
}

onMounted(async () => {
  const id = String(route.params.id);
  if (!id) { apiError.value = "Identifiant invalide."; return; }
  try {
    await patientsStore.fetchPatientById(id);
    await fetchPatientHistory(id);
  } catch {
    apiError.value = patientsStore.error ?? "Erreur inconnue.";
  }
});
</script>

<template>
  <div class="max-w-4xl space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <AppButton variant="ghost" size="sm" @click="goBack">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour
      </AppButton>
      <h1 class="text-2xl font-bold text-foreground">Détail du patient</h1>
    </div>

    <!-- Error -->
    <div v-if="apiError" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ apiError }}
    </div>

    <!-- Patient header card -->
    <AppCard v-if="patient">
      <div class="flex items-center gap-4 mb-6">
        <div class="h-14 w-14 rounded-2xl bg-primary/20 ring-2 ring-primary/30 flex items-center justify-center text-xl font-bold text-primary shrink-0">
          {{ (patient.prenom?.[0] || "") + (patient.nom?.[0] || "") }}
        </div>
        <div>
          <h2 class="text-xl font-bold text-foreground">{{ patient.prenom }} {{ patient.nom }}</h2>
          <p class="text-sm text-muted-foreground">{{ patient.identifiant_interne || "—" }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="field in fields" :key="field.label" class="space-y-1">
          <div class="text-xs text-muted-foreground font-medium uppercase tracking-wide">{{ field.label }}</div>
          <div class="text-sm font-medium text-foreground">{{ field.value ?? "—" }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Fatigue history chart -->
    <AppCard v-if="chartSessions.length > 0" class="!p-4">
      <h2 class="text-sm font-semibold text-foreground mb-4">Historique de fatigue cognitive</h2>
      <div class="flex items-end gap-2 h-36">
        <div
          v-for="s in chartSessions"
          :key="s.session_id"
          class="flex-1 flex flex-col items-center gap-1.5 group cursor-pointer"
          @click="router.push(`/results/${s.session_id}`)"
        >
          <!-- Bar -->
          <div class="relative w-full flex items-end" style="height: 100px;">
            <div
              class="w-full rounded-t-md transition-all duration-300 group-hover:opacity-80"
              :style="{
                height: `${((s.fatigue_score ?? 0) / chartMax) * 100}%`,
                minHeight: '4px',
                background: fatigueColor(s.fatigue_score),
                opacity: 0.85,
              }"
            />
            <!-- Score tooltip -->
            <div class="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] font-semibold"
                 :style="{ color: fatigueColor(s.fatigue_score) }">
              {{ s.fatigue_score !== null ? Math.round(s.fatigue_score) : '—' }}
            </div>
          </div>
          <!-- Date label -->
          <div class="text-[9px] text-muted-foreground text-center leading-tight">
            {{ formatDateShort(s.started_at) }}
          </div>
        </div>
      </div>
      <!-- Legend -->
      <div class="flex items-center gap-4 mt-3 text-[10px] text-muted-foreground">
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#22c55e"></span>Faible &lt;30</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#f59e0b"></span>Modérée 30–60</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#f97316"></span>Élevée 60–80</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#ef4444"></span>Critique &gt;80</span>
      </div>
    </AppCard>

    <!-- Sessions list -->
    <AppCard v-if="patientSessions.length > 0 || isLoadingSessions" class="!p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-foreground">Sessions EEG</h2>
        <span class="text-xs text-muted-foreground">{{ patientSessions.length }} session(s)</span>
      </div>
      <div v-if="isLoadingSessions" class="text-xs text-muted-foreground py-4 text-center">
        Chargement...
      </div>
      <div v-else class="space-y-2">
        <RouterLink
          v-for="s in patientSessions"
          :key="s.session_id"
          :to="`/results/${s.session_id}`"
          class="flex items-center justify-between px-3 py-2.5 rounded-lg bg-secondary/30 hover:bg-secondary/60 border border-border hover:border-primary/30 transition-all group"
        >
          <div class="flex items-center gap-3">
            <span class="text-xs font-mono text-muted-foreground">#{{ s.session_id }}</span>
            <span v-if="s.mode" class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary border border-primary/20">
              {{ s.mode }}
            </span>
            <span class="text-xs text-muted-foreground">{{ formatDateShort(s.started_at) }}</span>
          </div>
          <div class="flex items-center gap-3">
            <div v-if="s.fatigue_score !== null" class="flex items-center gap-1.5">
              <div class="h-1.5 w-1.5 rounded-full" :style="{ background: fatigueColor(s.fatigue_score) }" />
              <span class="text-xs font-semibold" :style="{ color: fatigueColor(s.fatigue_score) }">
                {{ Math.round(s.fatigue_score) }} — {{ fatigueLabel(s.fatigue_score) }}
              </span>
            </div>
            <span v-else class="text-xs text-muted-foreground">Pas de données</span>
            <svg class="h-3.5 w-3.5 text-muted-foreground group-hover:text-foreground transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </RouterLink>
      </div>
    </AppCard>

    <!-- Actions -->
    <div class="flex gap-3">
      <RouterLink :to="`/patients/${patient?.patient_id}/edit`">
        <AppButton variant="primary">Modifier</AppButton>
      </RouterLink>
      <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">
        Supprimer
      </AppButton>
    </div>
  </div>
</template>
