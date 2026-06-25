<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AppCard from "@/components/ui/AppCard.vue";
import Brain3D from "@/components/Brain3D.vue";
import EEGChartCanvas from "@/components/EEGChartCanvas.vue";
import EEGWaterfall3D from "@/components/EEGWaterfall3D.vue";
import FatigueGauge from "@/components/FatigueGauge.vue";
import FatigueTimeline from "@/components/FatigueTimeline.vue";
import { useAcquisitionStore } from "@/stores/acquisition.store";
import { http as api } from "@/api/http";
import { isDesktopRuntime } from "@/utils/desktop-runtime";

const acquisition = useAcquisitionStore();

const electrodes = [
  { id: "P4" }, { id: "O2" }, { id: "P8" }, { id: "O1" }, { id: "P7" },
  { id: "T7" }, { id: "F7" }, { id: "Fp1" }, { id: "Fp2" }, { id: "F4" },
  { id: "F8" }, { id: "T8" }, { id: "C4" }, { id: "F3" }, { id: "P3" }, { id: "C3" },
];

const selectedElectrodes = computed(() => acquisition.selectedElectrodes);
const selectedSet = computed(() => new Set(acquisition.selectedElectrodes));
const isRunning = computed(() => acquisition.isRunning);
const sessionId = computed(() => acquisition.sessionId);
const qualityByElectrode = computed(() => acquisition.qualityByElectrode);
const streamStatus = computed(() => acquisition.streamStatus);
const error = computed(() => acquisition.error);

// Heatmap: quality normalized to 0-1, only active when session is running
const heatmapData = computed<Record<string, number>>(() => {
  if (!isRunning.value) return {};
  const result: Record<string, number> = {};
  for (const [el, q] of Object.entries(qualityByElectrode.value)) {
    result[el] = Math.max(0, Math.min(1, (q ?? 0) / 100));
  }
  return result;
});

const presetMap: Record<string, string[]> = {
  frontal: ["Fp1", "Fp2", "F3", "F4", "F7", "F8"],
  motor: ["C3", "C4", "T7", "T8"],
  parietal: ["P3", "P4", "P7", "P8"],
  occipital: ["O1", "O2"],
};

function toggleElectrode(id: string) { acquisition.toggleElectrode(id); }
function applyPreset(key: string) { acquisition.setSelectedElectrodes(presetMap[key] || []); }
function clearAll() { acquisition.clearSelectedElectrodes(); }
function selectAll() { acquisition.setSelectedElectrodes(electrodes.map((e) => e.id)); }
async function toggleSession() {
  if (acquisition.isRunning) await acquisition.stopSession();
  else await acquisition.startSession();
}
function clearError() { acquisition.error = null; }

function formatQuality(value?: number) {
  if (value === undefined) return "—";
  return `${Math.round(value)}%`;
}

function qualityColorClass(value?: number) {
  if (value === undefined) return "bg-secondary";
  if (value >= 75) return "bg-eeg-emerald";
  if (value >= 50) return "bg-eeg-amber";
  return "bg-eeg-rose";
}

const streamStatusLabel = computed(() => {
  if (streamStatus.value === "connecting") return "Connexion...";
  if (streamStatus.value === "open") return "Connecté";
  if (streamStatus.value === "closed") return "Fermé";
  if (streamStatus.value === "error") return "Erreur";
  return "Inactif";
});

const streamDotClass = computed(() => {
  if (streamStatus.value === "open") return "bg-eeg-emerald";
  if (streamStatus.value === "connecting") return "bg-eeg-amber";
  if (streamStatus.value === "error") return "bg-eeg-rose";
  return "bg-muted-foreground";
});

const fatigueScore = computed(() => acquisition.liveMetrics?.fatigue_score ?? 0);
const activeAlerts = computed(() => acquisition.activeAlerts);
const baselineFatigue = computed(() => acquisition.baselineFatigue);
const datasetLabel = computed(() => acquisition.datasetLabel);

function setBaseline() { acquisition.setBaseline(); }
function clearBaseline() { acquisition.clearBaseline(); }

interface EEGmatEntry {
  subject: string;
  condition: "rest" | "task";
  label: string;
  filename: string;
}

const eegmatFiles = ref<EEGmatEntry[]>([]);

onMounted(async () => {
  if (isDesktopRuntime()) return;
  try {
    const res = await api.get("/eeg/datasets");
    eegmatFiles.value = res.data.eegmat ?? [];
  } catch {
    // silently ignore if backend unavailable
  }
});

function selectSource(dataset: "sleep" | "eegmat", subject: string, condition: "rest" | "task") {
  acquisition.setEegSource(dataset, subject, condition);
}
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page header + session controls -->
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-foreground">Acquisition EEG</h1>
        <p class="text-sm text-muted-foreground mt-0.5">
          Sélectionne les électrodes et démarre une session d'enregistrement
        </p>
      </div>

      <div class="flex items-center gap-3 flex-wrap">
        <!-- Source EEG selector -->
        <div v-if="!isRunning" class="relative">
          <select
            class="h-9 pl-3 pr-8 rounded-lg bg-card border border-border text-xs text-foreground appearance-none cursor-pointer hover:border-primary/50 transition-colors focus:outline-none focus:ring-1 focus:ring-primary/50"
            :value="acquisition.eegDataset === 'sleep' ? 'sleep' : `${acquisition.eegSubject}_${acquisition.eegCondition}`"
            @change="(e) => {
              const v = (e.target as HTMLSelectElement).value;
              if (v === 'sleep') selectSource('sleep', '00', 'rest');
              else {
                const [sub, cond] = v.split('_');
                selectSource('eegmat', sub ?? '00', (cond ?? 'rest') as 'rest' | 'task');
              }
            }"
          >
            <option value="sleep">Sleep-EDF (base)</option>
            <optgroup v-if="eegmatFiles.length > 0" label="EEGmat — Charge cognitive">
              <option v-for="f in eegmatFiles" :key="f.filename" :value="`${f.subject}_${f.condition}`">
                {{ f.label }}
              </option>
            </optgroup>
          </select>
          <svg class="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        <!-- Source badge during session -->
        <div v-else class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-secondary/50 border border-border text-xs text-muted-foreground">
          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
          {{ datasetLabel }}
        </div>

        <!-- Status indicator -->
        <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-card border border-border text-sm">
          <span :class="['h-2 w-2 rounded-full', streamDotClass, streamStatus === 'open' && 'animate-pulse']" />
          <span class="text-muted-foreground text-xs">{{ streamStatusLabel }}</span>
        </div>

        <!-- Start / Stop -->
        <button
          :class="[
            'inline-flex items-center gap-2 h-9 px-4 rounded-lg font-medium text-sm transition-all duration-150 shadow-sm',
            isRunning
              ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90'
              : 'bg-eeg-emerald text-white hover:bg-eeg-emerald/90',
          ]"
          @click="toggleSession"
        >
          <svg v-if="!isRunning" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          {{ isRunning ? "Arrêter" : "Démarrer" }}
        </button>
      </div>
    </div>

    <!-- Error banner -->
    <div
      v-if="error"
      class="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <svg class="h-4 w-4 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div class="flex-1">
        <p class="font-medium">Erreur d'acquisition</p>
        <p class="text-xs opacity-80 mt-0.5 font-mono">{{ error }}</p>
      </div>
      <button @click="clearError" class="opacity-70 hover:opacity-100 transition-opacity shrink-0">✕</button>
    </div>

    <!-- Main grid: 3D viewer + controls -->
    <div class="grid grid-cols-1 xl:grid-cols-[1.5fr_1fr] gap-4">
      <!-- 3D Viewer -->
      <AppCard class="h-[580px] flex flex-col !p-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-foreground">Visualisation 3D</h2>
          <div class="flex items-center gap-4 text-xs text-muted-foreground">
            <span class="flex items-center gap-1.5">
              <span class="h-2 w-2 rounded-full bg-eeg-emerald"></span>
              Active
            </span>
            <span class="flex items-center gap-1.5">
              <span class="h-2 w-2 rounded-full bg-secondary"></span>
              Inactive
            </span>
          </div>
        </div>
        <div class="flex-1 rounded-lg overflow-hidden bg-[#070a10]">
          <Brain3D :selected-electrodes="selectedElectrodes" :heatmap-data="heatmapData" @electrode-click="toggleElectrode" />
        </div>
      </AppCard>

      <!-- Controls panel -->
      <div class="flex flex-col gap-4">
        <!-- Presets -->
        <AppCard class="!p-4">
          <h2 class="text-sm font-semibold text-foreground mb-3">Configuration rapide</h2>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="preset in [
                { key: 'frontal', label: 'Frontal', count: '6' },
                { key: 'motor', label: 'Moteur', count: '4' },
                { key: 'parietal', label: 'Pariétal', count: '4' },
                { key: 'occipital', label: 'Occipital', count: '2' },
              ]"
              :key="preset.key"
              class="flex flex-col items-center gap-0.5 px-3 py-2.5 rounded-lg border border-border bg-secondary/30 hover:border-primary/40 hover:bg-primary/5 text-sm font-medium text-foreground transition-all duration-150"
              @click="applyPreset(preset.key)"
            >
              {{ preset.label }}
              <span class="text-[10px] text-muted-foreground">{{ preset.count }} électrodes</span>
            </button>
            <button
              class="flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border border-eeg-emerald/30 bg-eeg-emerald/5 hover:bg-eeg-emerald/10 text-xs font-medium text-eeg-emerald transition-all"
              @click="selectAll"
            >
              Tout sélectionner
            </button>
            <button
              class="flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border border-destructive/30 bg-destructive/5 hover:bg-destructive/10 text-xs font-medium text-destructive transition-all"
              @click="clearAll"
            >
              Effacer
            </button>
          </div>
        </AppCard>

        <!-- Electrode grid -->
        <AppCard class="!p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-foreground">Électrodes</h2>
            <span class="text-xs font-semibold text-eeg-emerald">{{ selectedElectrodes.length }}/{{ electrodes.length }}</span>
          </div>
          <div class="grid grid-cols-5 gap-1.5">
            <button
              v-for="electrode in electrodes"
              :key="electrode.id"
              :class="[
                'py-2 rounded-lg text-xs font-medium transition-all duration-150',
                selectedSet.has(electrode.id)
                  ? 'bg-eeg-emerald text-white shadow-sm'
                  : 'bg-secondary/40 border border-border text-muted-foreground hover:border-primary/30 hover:text-foreground',
              ]"
              @click="toggleElectrode(electrode.id)"
            >
              {{ electrode.id }}
            </button>
          </div>
        </AppCard>

        <!-- Session info -->
        <AppCard class="!p-4">
          <h2 class="text-sm font-semibold text-foreground mb-3">Session en cours</h2>
          <div class="space-y-2 mb-3">
            <div class="flex items-center justify-between py-2 px-3 rounded-lg bg-secondary/30 text-xs">
              <span class="text-muted-foreground">ID de session</span>
              <span class="font-mono text-foreground">{{ sessionId || "—" }}</span>
            </div>
            <div class="flex items-center justify-between py-2 px-3 rounded-lg bg-secondary/30 text-xs">
              <span class="text-muted-foreground">Électrodes actives</span>
              <span class="font-semibold text-foreground">{{ selectedElectrodes.length }}</span>
            </div>
            <div class="flex items-center justify-between py-2 px-3 rounded-lg bg-secondary/30 text-xs">
              <span class="text-muted-foreground">Streaming</span>
              <span class="flex items-center gap-1.5 font-semibold text-foreground">
                <span :class="['h-1.5 w-1.5 rounded-full', streamDotClass]" />
                {{ streamStatusLabel }}
              </span>
            </div>
          </div>
          <div v-if="selectedElectrodes.length > 0" class="flex flex-wrap gap-1">
            <span
              v-for="el in selectedElectrodes"
              :key="el"
              class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary border border-primary/20"
            >
              {{ el }}
            </span>
          </div>
          <div v-else class="text-xs text-muted-foreground text-center py-3">Aucune électrode sélectionnée</div>
        </AppCard>
      </div>
    </div>

    <!-- Fatigue section: gauge + timeline -->
    <div class="grid grid-cols-1 xl:grid-cols-[220px_1fr] gap-4">
      <!-- Gauge card -->
      <AppCard class="!p-4 flex flex-col items-center justify-center gap-3">
        <h2 class="text-sm font-semibold text-foreground self-start">Score de fatigue</h2>
        <FatigueGauge :score="fatigueScore" :baseline="baselineFatigue" :size="160" />
        <div class="flex gap-2 w-full">
          <button
            class="flex-1 px-3 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:border-primary/40 transition-colors"
            @click="setBaseline"
          >
            Définir référence
          </button>
          <button
            v-if="baselineFatigue !== null"
            class="px-2.5 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-destructive hover:border-destructive/30 transition-colors"
            @click="clearBaseline"
            title="Effacer la référence"
          >
            ✕
          </button>
        </div>
        <div v-if="baselineFatigue !== null" class="text-[10px] text-muted-foreground text-center">
          Référence : {{ baselineFatigue.toFixed(0) }} pts
        </div>
      </AppCard>

      <!-- Timeline card -->
      <AppCard class="!p-4 flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-foreground">Évolution de la fatigue cognitive</h2>
          <div class="flex items-center gap-3 text-[10px] text-muted-foreground">
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#22c55e"></span>Faible</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#f59e0b"></span>Modérée</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#f97316"></span>Élevée</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-1.5 rounded" style="background:#ef4444"></span>Critique</span>
          </div>
        </div>
        <div class="flex-1 min-h-[140px]">
          <FatigueTimeline />
        </div>
      </AppCard>
    </div>

    <!-- Active alerts -->
    <div v-if="activeAlerts.length > 0" class="flex flex-wrap gap-2">
      <div
        v-for="alert in activeAlerts"
        :key="alert"
        class="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400"
      >
        <svg class="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        {{ alert }}
      </div>
    </div>

    <!-- Signal quality bars -->
    <AppCard v-if="selectedElectrodes.length > 0" class="!p-4">
      <h2 class="text-sm font-semibold text-foreground mb-4">Qualité du signal</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        <div v-for="electrode in selectedElectrodes" :key="electrode" class="space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <span class="font-semibold text-foreground">{{ electrode }}</span>
            <span class="text-muted-foreground">{{ formatQuality(qualityByElectrode[electrode]) }}</span>
          </div>
          <div class="h-1.5 rounded-full bg-secondary overflow-hidden">
            <div
              :class="['h-full rounded-full transition-all duration-300', qualityColorClass(qualityByElectrode[electrode])]"
              :style="{ width: `${qualityByElectrode[electrode] ?? 0}%` }"
            />
          </div>
        </div>
      </div>
    </AppCard>

    <!-- EEG waveform + Waterfall side by side -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <!-- Waveform -->
      <AppCard class="!p-4">
        <h2 class="text-sm font-semibold text-foreground mb-4">Signaux EEG en temps réel</h2>
        <EEGChartCanvas :is-active="isRunning" />
      </AppCard>

      <!-- Spectral waterfall 3D -->
      <AppCard class="!p-4 flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-foreground">Spectre fréquentiel 3D</h2>
          <div class="flex items-center gap-3 text-[10px] text-muted-foreground">
            <span class="flex items-center gap-1"><span class="inline-block w-3 h-1.5 rounded" style="background:#0080ff"></span>Bas</span>
            <span class="flex items-center gap-1"><span class="inline-block w-3 h-1.5 rounded" style="background:#00ff80"></span>Moyen</span>
            <span class="flex items-center gap-1"><span class="inline-block w-3 h-1.5 rounded" style="background:#ff4400"></span>Élevé</span>
          </div>
        </div>
        <div class="flex-1 rounded-lg overflow-hidden" style="height: 400px;">
          <EEGWaterfall3D :is-active="isRunning" />
        </div>
      </AppCard>
    </div>
  </div>
</template>
