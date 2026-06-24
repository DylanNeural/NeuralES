<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useAcquisitionStore } from '@/stores/acquisition.store';

const store = useAcquisitionStore();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const WINDOW_SECONDS = 300;

function scoreColor(s: number) {
  if (s < 30) return '#22c55e';
  if (s < 60) return '#f59e0b';
  if (s < 80) return '#f97316';
  return '#ef4444';
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const W = canvas.width;
  const H = canvas.height;
  if (W === 0 || H === 0) return;

  const PAD = { top: 6, right: 8, bottom: 22, left: 28 };
  const cW = W - PAD.left - PAD.right;
  const cH = H - PAD.top - PAD.bottom;

  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#0d1117';
  ctx.fillRect(0, 0, W, H);

  const zones = [
    { from: 0,  to: 30,  color: 'rgba(34,197,94,0.07)'  },
    { from: 30, to: 60,  color: 'rgba(245,158,11,0.07)' },
    { from: 60, to: 80,  color: 'rgba(249,115,22,0.07)' },
    { from: 80, to: 100, color: 'rgba(239,68,68,0.07)'  },
  ];
  zones.forEach(({ from, to, color }) => {
    ctx.fillStyle = color;
    const yTop = PAD.top + cH * (1 - to / 100);
    const yBot = PAD.top + cH * (1 - from / 100);
    ctx.fillRect(PAD.left, yTop, cW, yBot - yTop);
  });

  [30, 60, 80].forEach(val => {
    const y = PAD.top + cH * (1 - val / 100);
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 4]);
    ctx.beginPath();
    ctx.moveTo(PAD.left, y);
    ctx.lineTo(PAD.left + cW, y);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#334155';
    ctx.font = '9px system-ui';
    ctx.textAlign = 'right';
    ctx.fillText(String(val), PAD.left - 3, y + 3.5);
  });

  const history = store.fatigueHistory;
  const maxT = history.length > 0
    ? Math.max(WINDOW_SECONDS, history[history.length - 1]?.t ?? 0)
    : WINDOW_SECONDS;

  const minuteStep = maxT <= 300 ? 60 : 120;
  for (let t = 0; t <= maxT; t += minuteStep) {
    const x = PAD.left + (t / maxT) * cW;
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, PAD.top);
    ctx.lineTo(x, PAD.top + cH);
    ctx.stroke();
    ctx.fillStyle = '#334155';
    ctx.font = '9px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText(`${t / 60}m`, x, H - 5);
  }

  if (history.length < 2) {
    if (history.length === 1) {
      const { t, score } = history[0]!;
      const x = PAD.left + (t / maxT) * cW;
      const y = PAD.top + cH * (1 - score / 100);
      ctx.fillStyle = scoreColor(score);
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    }
    return;
  }

  ctx.lineWidth = 2;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  for (let i = 1; i < history.length; i++) {
    const prev = history[i - 1]!;
    const curr = history[i]!;
    const x1 = PAD.left + (prev.t / maxT) * cW;
    const y1 = PAD.top + cH * (1 - prev.score / 100);
    const x2 = PAD.left + (curr.t / maxT) * cW;
    const y2 = PAD.top + cH * (1 - curr.score / 100);
    ctx.strokeStyle = scoreColor((prev.score + curr.score) / 2);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  const last = history[history.length - 1]!;
  const lx = PAD.left + (last.t / maxT) * cW;
  const ly = PAD.top + cH * (1 - last.score / 100);
  ctx.fillStyle = scoreColor(last.score);
  ctx.beginPath();
  ctx.arc(lx, ly, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#0d1117';
  ctx.lineWidth = 1.5;
  ctx.stroke();
}

watch(() => store.streamMessageSeq, draw);
watch(() => store.isRunning, () => draw());

let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  const el = canvasRef.value;
  if (!el) return;
  resizeObserver = new ResizeObserver(() => {
    const parent = el.parentElement;
    if (!parent) return;
    el.width = parent.clientWidth;
    el.height = parent.clientHeight;
    draw();
  });
  if (el.parentElement) resizeObserver.observe(el.parentElement);
});

onUnmounted(() => {
  resizeObserver?.disconnect();
});
</script>

<template>
  <div class="relative w-full h-full">
    <canvas ref="canvasRef" class="block w-full h-full" />
    <div
      v-if="store.fatigueHistory.length === 0"
      class="absolute inset-0 flex items-center justify-center pointer-events-none"
    >
      <p class="text-xs text-muted-foreground">Démarrez une session pour voir l'évolution</p>
    </div>
  </div>
</template>
