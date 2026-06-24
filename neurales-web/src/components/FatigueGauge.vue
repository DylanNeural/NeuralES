<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  score: number;
  baseline?: number | null;
  size?: number;
}>();

const CX = 100, CY = 100, R = 72, SW = 12;
const START_DEG = 225;
const SWEEP_DEG = 270;

function pt(deg: number) {
  const rad = (deg * Math.PI) / 180;
  return { x: CX + R * Math.sin(rad), y: CY - R * Math.cos(rad) };
}

const startPt = pt(START_DEG);
const endPt = pt(START_DEG + SWEEP_DEG);

const bgArc = `M ${startPt.x.toFixed(2)} ${startPt.y.toFixed(2)} A ${R} ${R} 0 1 1 ${endPt.x.toFixed(2)} ${endPt.y.toFixed(2)}`;

const progressArc = computed(() => {
  const s = Math.max(0, Math.min(100, props.score));
  if (s < 0.5) return '';
  const sweep = (s / 100) * SWEEP_DEG;
  const end = pt(START_DEG + sweep);
  const large = sweep > 180 ? 1 : 0;
  return `M ${startPt.x.toFixed(2)} ${startPt.y.toFixed(2)} A ${R} ${R} 0 ${large} 1 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
});

const gaugeColor = computed(() => {
  const s = props.score;
  if (s < 30) return '#22c55e';
  if (s < 60) return '#f59e0b';
  if (s < 80) return '#f97316';
  return '#ef4444';
});

const levelLabel = computed(() => {
  const s = props.score;
  if (s < 30) return 'Faible';
  if (s < 60) return 'Modérée';
  if (s < 80) return 'Élevée';
  return 'Critique';
});

const levelClass = computed(() => {
  const s = props.score;
  if (s < 30) return 'border-green-500/30 bg-green-500/10 text-green-400';
  if (s < 60) return 'border-amber-500/30 bg-amber-500/10 text-amber-400';
  if (s < 80) return 'border-orange-500/30 bg-orange-500/10 text-orange-400';
  return 'border-red-500/30 bg-red-500/10 text-red-400';
});

const delta = computed(() => {
  if (props.baseline == null) return null;
  return props.score - props.baseline;
});
</script>

<template>
  <div class="flex flex-col items-center gap-2">
    <svg :width="size ?? 180" :height="size ?? 180" viewBox="0 0 200 200" class="overflow-visible">
      <!-- Glow under progress -->
      <path v-if="progressArc" :d="progressArc" fill="none" :stroke="gaugeColor"
        :stroke-width="SW + 8" stroke-linecap="round" :opacity="0.12" />
      <!-- Background track -->
      <path :d="bgArc" fill="none" stroke="#1e293b" :stroke-width="SW" stroke-linecap="round" />
      <!-- Progress arc -->
      <path v-if="progressArc" :d="progressArc" fill="none" :stroke="gaugeColor"
        :stroke-width="SW" stroke-linecap="round" />
      <!-- Score number -->
      <text x="100" y="97" text-anchor="middle" :fill="gaugeColor"
        font-size="42" font-weight="700" font-family="system-ui,sans-serif">
        {{ Math.round(score) }}
      </text>
      <!-- /100 -->
      <text x="100" y="118" text-anchor="middle" fill="#475569"
        font-size="13" font-family="system-ui,sans-serif">/ 100</text>
      <!-- Delta from baseline -->
      <text v-if="delta !== null" x="100" y="140" text-anchor="middle"
        font-size="12" font-family="system-ui,sans-serif"
        :fill="delta > 0 ? '#ef4444' : delta < 0 ? '#22c55e' : '#94a3b8'">
        {{ delta > 0 ? '▲' : delta < 0 ? '▼' : '–' }} {{ Math.abs(delta).toFixed(1) }} pts
      </text>
    </svg>
    <span :class="['px-3 py-1 rounded-full text-xs font-semibold border', levelClass]">
      {{ levelLabel }}
    </span>
  </div>
</template>
