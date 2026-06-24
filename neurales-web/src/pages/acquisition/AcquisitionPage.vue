<script setup lang="ts">
import { computed } from "vue";
import AppCard from "@/components/ui/AppCard.vue";
import Brain3D from "@/components/Brain3D.vue";
import EEGChartCanvas from "@/components/EEGChartCanvas.vue";
import { useAcquisitionStore } from "@/stores/acquisition.store";

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

      <div class="flex items-center gap-3">
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
          <Brain3D :selected-electrodes="selectedElectrodes" @electrode-click="toggleElectrode" />
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

    <!-- EEG Chart -->
    <AppCard class="!p-4">
      <h2 class="text-sm font-semibold text-foreground mb-4">Signaux EEG en temps réel</h2>
      <EEGChartCanvas :is-active="isRunning" :selected-electrodes="selectedElectrodes" />
    </AppCard>
  </div>
</template>
