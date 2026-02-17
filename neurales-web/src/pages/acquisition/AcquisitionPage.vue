<template>
  <div class="acquisition-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Acquisition EEG en temps réel</h1>
        <p class="page-subtitle">
          Sélectionne les électrodes à activer et démarre une session d'enregistrement
        </p>
      </div>
      <div class="session-controls">
        <button
          class="btn-session"
          :class="isRunning ? 'btn-stop' : 'btn-start'"
          @click="toggleSession"
        >
          <svg v-if="!isRunning" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          {{ isRunning ? 'Arrêter' : 'Démarrer' }}
        </button>
        <div class="session-info">
          <div class="status-indicator" :class="`status-${streamStatus}`"></div>
          <span class="status-text">{{ streamStatusLabel }}</span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="main-grid">
      <!-- 3D Viewer -->
      <AppCard class="viewer-card">
        <div class="card-header">
          <h2 class="card-title">Visualisation 3D</h2>
          <div class="electrode-legend">
            <span class="legend-item">
              <span class="legend-dot active"></span>
              Active
            </span>
            <span class="legend-item">
              <span class="legend-dot inactive"></span>
              Inactive
            </span>
          </div>
        </div>
        <div class="viewer-container">
          <Brain3D
            :selected-electrodes="selectedElectrodes"
            @electrode-click="toggleElectrode"
          />
        </div>
      </AppCard>

      <!-- Controls Panel -->
      <div class="controls-panel">
        <!-- Presets -->
        <AppCard>
          <div class="card-header">
            <h2 class="card-title">Configuration rapide</h2>
          </div>
          <div class="presets-grid">
            <button class="preset-btn" @click="applyPreset('frontal')">
              <svg class="preset-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Frontal</span>
              <span class="preset-count">6 électrodes</span>
            </button>
            <button class="preset-btn" @click="applyPreset('motor')">
              <svg class="preset-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Moteur</span>
              <span class="preset-count">4 électrodes</span>
            </button>
            <button class="preset-btn" @click="applyPreset('parietal')">
              <svg class="preset-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Pariétal</span>
              <span class="preset-count">4 électrodes</span>
            </button>
            <button class="preset-btn" @click="applyPreset('occipital')">
              <svg class="preset-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>Occipital</span>
              <span class="preset-count">2 électrodes</span>
            </button>
            <button class="preset-btn preset-all" @click="selectAll">
              <svg class="preset-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Tout sélectionner</span>
            </button>
            <button class="preset-btn preset-clear" @click="clearAll">
              <svg class="preset-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Effacer</span>
            </button>
          </div>
        </AppCard>

        <!-- Electrode Selection -->
        <AppCard>
          <div class="card-header">
            <h2 class="card-title">Électrodes</h2>
            <span class="electrode-counter">{{ selectedElectrodes.length }} / {{ electrodes.length }}</span>
          </div>
          <div class="electrodes-grid">
            <button
              v-for="electrode in electrodes"
              :key="electrode.id"
              class="electrode-btn"
              :class="{ active: selectedSet.has(electrode.id) }"
              @click="toggleElectrode(electrode.id)"
            >
              {{ electrode.id }}
            </button>
          </div>
        </AppCard>

        <!-- Session Info -->
        <AppCard>
          <div class="card-header">
            <h2 class="card-title">Session en cours</h2>
          </div>
          <div class="session-details">
            <div class="detail-row">
              <span class="detail-label">ID de session</span>
              <span class="detail-value">{{ sessionId || '—' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Électrodes actives</span>
              <span class="detail-value">{{ selectedElectrodes.length }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Status streaming</span>
              <span class="detail-value" :class="`status-${streamStatus}`">{{ streamStatusLabel }}</span>
            </div>
          </div>
          <div class="selected-list">
            <div v-if="selectedElectrodes.length > 0" class="selected-chips">
              <span
                v-for="electrode in selectedElectrodes"
                :key="electrode"
                class="electrode-chip"
              >
                {{ electrode }}
              </span>
            </div>
            <div v-else class="empty-state">
              Aucune électrode sélectionnée
            </div>
          </div>
        </AppCard>
      </div>
    </div>

    <!-- Signal Quality -->
    <AppCard v-if="selectedElectrodes.length > 0">
      <div class="card-header">
        <h2 class="card-title">Qualité du signal</h2>
      </div>
      <div class="quality-grid">
        <div
          v-for="electrode in selectedElectrodes"
          :key="electrode"
          class="quality-item"
        >
          <div class="quality-header">
            <span class="quality-label">{{ electrode }}</span>
            <span class="quality-value">{{ formatQuality(qualityByElectrode[electrode]) }}</span>
          </div>
          <div class="quality-bar-bg">
            <div
              class="quality-bar"
              :class="qualityClass(qualityByElectrode[electrode])"
              :style="{ width: `${qualityByElectrode[electrode] ?? 0}%` }"
            ></div>
          </div>
        </div>
      </div>
    </AppCard>

    <!-- EEG Chart -->
    <AppCard>
      <div class="card-header">
        <h2 class="card-title">Signaux EEG en temps réel</h2>
      </div>
      <EEGChartCanvas :is-active="isRunning" />
    </AppCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import AppCard from '@/components/ui/AppCard.vue';
import Brain3D from '@/components/Brain3D.vue';
import EEGChartCanvas from '@/components/EEGChartCanvas.vue';
import { useAcquisitionStore } from "@/stores/acquisition.store";

const acquisition = useAcquisitionStore();

// 16 electrodes from casque_brain_electrodes.glb model
const electrodes = [
  { id: "P4" },
  { id: "O2" },
  { id: "P8" },
  { id: "O1" },
  { id: "P7" },
  { id: "T7" },
  { id: "F7" },
  { id: "Fp1" },
  { id: "Fp2" },
  { id: "F4" },
  { id: "F8" },
  { id: "T8" },
  { id: "C4" },
  { id: "F3" },
  { id: "P3" },
  { id: "C3" },
];
const selectedElectrodes = computed(() => acquisition.selectedElectrodes);
const selectedSet = computed(() => new Set(acquisition.selectedElectrodes));
const isRunning = computed(() => acquisition.isRunning);
const sessionId = computed(() => acquisition.sessionId);
const qualityByElectrode = computed(() => acquisition.qualityByElectrode);
const streamStatus = computed(() => acquisition.streamStatus);

const presetMap: Record<string, string[]> = {
  frontal: ["Fp1", "Fp2", "F3", "F4", "F7", "F8"],
  motor: ["C3", "C4", "T7", "T8"],
  parietal: ["P3", "P4", "P7", "P8"],
  occipital: ["O1", "O2"],
};

function toggleElectrode(id: string) {
  acquisition.toggleElectrode(id);
}

function applyPreset(key: string) {
  acquisition.setSelectedElectrodes(presetMap[key] || []);
}

function clearAll() {
  acquisition.clearSelectedElectrodes();
}

function selectAll() {
  acquisition.setSelectedElectrodes(electrodes.map((e) => e.id));
}

async function toggleSession() {
  if (acquisition.isRunning) await acquisition.stopSession();
  else await acquisition.startSession();
}

function formatQuality(value?: number) {
  if (value === undefined) return "—";
  return `${Math.round(value)}%`;
}

function qualityClass(value?: number) {
  if (value === undefined) return "quality-unknown";
  if (value >= 75) return "quality-good";
  if (value >= 50) return "quality-medium";
  return "quality-poor";
}

const streamStatusLabel = computed(() => {
  if (streamStatus.value === "connecting") return "Connexion...";
  if (streamStatus.value === "open") return "Connecté";
  if (streamStatus.value === "closed") return "Fermé";
  if (streamStatus.value === "error") return "Erreur";
  return "Inactif";
});
</script>

<style scoped>
.acquisition-page {
  padding: 2rem;
  max-width: 1920px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.page-subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin-top: 0.5rem;
}

.session-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-session {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-start {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.btn-start:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-stop {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.btn-stop:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.session-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
}

.status-indicator {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-connecting {
  background: #f59e0b;
}

.status-open {
  background: #10b981;
}

.status-closed {
  background: #94a3b8;
}

.status-error {
  background: #ef4444;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 1280px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

.viewer-card {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.controls-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Card */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.electrode-legend {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #64748b;
}

.legend-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.legend-dot.active {
  background: #00d97e;
}

.legend-dot.inactive {
  background: #cbd5e1;
}

/* Viewer */
.viewer-container {
  flex: 1;
  min-height: 0;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #0b0d12;
}

/* Presets */
.presets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.preset-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  padding: 1rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
}

.preset-btn:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.preset-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #64748b;
}

.preset-count {
  font-size: 0.75rem;
  color: #94a3b8;
}

.preset-all {
  grid-column: span 2;
  flex-direction: row;
  justify-content: center;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-color: #86efac;
}

.preset-all:hover {
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  border-color: #4ade80;
}

.preset-clear {
  grid-column: span 2;
  flex-direction: row;
  justify-content: center;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border-color: #fca5a5;
}

.preset-clear:hover {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  border-color: #f87171;
}

/* Electrodes Grid */
.electrode-counter {
  font-size: 0.875rem;
  font-weight: 600;
  color: #10b981;
}

.electrodes-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.25rem;
}

.electrode-btn {
  padding: 0.625rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.electrode-btn:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.electrode-btn.active {
  background: linear-gradient(135deg, #00d97e, #00b569);
  border-color: #00d97e;
  color: white;
}

/* Session Details */
.session-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem;
  background: #f8fafc;
  border-radius: 0.375rem;
}

.detail-label {
  font-size: 0.875rem;
  color: #64748b;
}

.detail-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.selected-list {
  min-height: 80px;
}

.selected-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.electrode-chip {
  padding: 0.25rem 0.625rem;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Quality Grid */
.quality-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.quality-item {
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
}

.quality-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.quality-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
}

.quality-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.quality-bar-bg {
  height: 0.5rem;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.quality-bar {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 9999px;
}

.quality-good {
  background: linear-gradient(90deg, #10b981, #059669);
}

.quality-medium {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.quality-poor {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.quality-unknown {
  background: #cbd5e1;
}
</style>
