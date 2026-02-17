<template>
  <div class="eeg-chart">
    <div class="eeg-chart__header">
      <div class="eeg-chart__title">Lecture EEG ({{ channelsCountLabel }})</div>
      <div class="eeg-chart__meta">
        <span class="eeg-chart__dot" :class="statusClass"></span>
        {{ statusText }} • fenêtre 10 s
      </div>
    </div>
    <div class="eeg-chart__plot">
      <canvas ref="canvas" class="eeg-chart__canvas"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch, withDefaults, defineProps } from "vue";

interface Props {
  isActive?: boolean;
  selectedElectrodes?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
  selectedElectrodes: () => [],
});

const canvas = ref<HTMLCanvasElement | null>(null);

const seconds = 10;
const status = ref<"idle" | "connecting" | "live" | "error">("idle");
const channelsCount = ref(0);
const channelNames = ref<string[]>([]);
const filteredChannelIndices = ref<number[]>([]);

let ws: WebSocket | null = null;
let ctx: CanvasRenderingContext2D | null = null;
let raf = 0;
let xs: Float32Array | null = null;
let ys: Float32Array[] = [];
let points = 0;
let sfreq = 0;
let maxAbsRaw = 0;
let lastDraw = 0;

const channelsCountLabel = computed(() => {
  return channelsCount.value > 0 ? `${channelsCount.value} canaux` : "en attente";
});
const statusText = computed(() => {
  if (status.value === "live") return "stream live";
  if (status.value === "connecting") return "connexion...";
  if (status.value === "error") return "erreur stream";
  return "attente";
});
const statusClass = computed(() => {
  return {
    "eeg-chart__dot--live": status.value === "live",
    "eeg-chart__dot--connecting": status.value === "connecting",
    "eeg-chart__dot--error": status.value === "error",
  };
});

// Update filtered channels when selection changes
watch(
  () => props.selectedElectrodes,
  (selected) => {
    if (selected.length === 0) {
      // Show all channels if none selected
      filteredChannelIndices.value = Array.from({ length: channelNames.value.length }, (_, i) => i);
    } else {
      // Show only selected channels
      filteredChannelIndices.value = channelNames.value
        .map((name, idx) => (selected.includes(name) ? idx : -1))
        .filter(idx => idx !== -1);
    }
  },
  { deep: true }
);

function initBuffers(newSfreq: number, names: string[]) {
  sfreq = newSfreq;
  channelsCount.value = names.length;
  channelNames.value = names;
  points = Math.max(1, Math.round(sfreq * seconds));
  xs = new Float32Array(points);
  ys = [];
  for (let c = 0; c < channelsCount.value; c += 1) {
    ys.push(new Float32Array(points));
  }
  for (let i = 0; i < points; i += 1) {
    xs[i] = i / sfreq;
  }
  maxAbsRaw = 0;
}

function appendSamples(samples: number[][]) {
  if (!xs || ys.length === 0) return;
  const normalized = Array.isArray(samples[0]) ? samples : [samples as unknown as number[]];
  const nCh = Math.min(normalized.length, ys.length);
  const nSamples = normalized[0]?.length ?? 0;
  if (nSamples === 0) return;

  for (let i = 0; i < nSamples; i += 1) {
    xs?.copyWithin(0, 1);
    if (xs && xs.length > 0) {
      xs[xs.length - 1] = (xs[xs.length - 2] ?? 0) + 1 / sfreq;
    }

    for (let c = 0; c < nCh; c += 1) {
      const row = ys[c];
      if (row) {
        row.copyWithin(0, 1);
        const v = Number(normalized[c]?.[i] ?? 0) || 0;
        row[row.length - 1] = v;
        const av = Math.abs(v);
        if (av > maxAbsRaw) maxAbsRaw = av;
      }
    }
  }
}

function draw() {
  if (!canvas.value || !ctx) return;
  const now = performance.now();
  if (now - lastDraw < 16) {
    raf = requestAnimationFrame(draw);
    return;
  }
  lastDraw = now;

  const w = canvas.value.clientWidth;
  const h = canvas.value.clientHeight;
  if (canvas.value.width !== w || canvas.value.height !== h) {
    canvas.value.width = w;
    canvas.value.height = h;
  }

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, w, h);

  if (!xs || ys.length === 0) {
    raf = requestAnimationFrame(draw);
    return;
  }

  const padL = 60;
  const padR = 16;
  const padT = 16;
  const padB = 24;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;
  
  // Use filtered channels for display
  const displayChannels = filteredChannelIndices.value.length > 0 ? filteredChannelIndices.value : Array.from({ length: ys.length }, (_, i) => i);
  const ch = displayChannels.length;
  const rowH = plotH / Math.max(1, ch);
  const ampPx = rowH * 0.35;
  const gain = maxAbsRaw > 0 ? ampPx / maxAbsRaw : 1;

  ctx.strokeStyle = "rgba(141,153,174,0.25)";
  ctx.lineWidth = 1;
  for (let displayIdx = 0; displayIdx < ch; displayIdx += 1) {
    const y = padT + displayIdx * rowH + rowH / 2;
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(padL + plotW, y);
    ctx.stroke();
  }

  // Light background band per channel.
  for (let displayIdx = 0; displayIdx < ch; displayIdx += 1) {
    const yTop = padT + displayIdx * rowH;
    ctx.fillStyle = "rgba(141,153,174,0.06)";
    ctx.fillRect(padL, yTop, plotW, rowH);
  }

  ctx.font = "12px sans-serif";
  ctx.fillStyle = "#64748b";
  for (let displayIdx = 0; displayIdx < ch; displayIdx += 1) {
    const c = displayChannels[displayIdx];
    const y = padT + displayIdx * rowH + rowH / 2 + 4;
    ctx.fillText(channelNames.value[c] ?? `Ch ${c + 1}`, 8, y);
  }

  for (let displayIdx = 0; displayIdx < ch; displayIdx += 1) {
    const c = displayChannels[displayIdx];
    const row = ys[c];
    if (!row || row.length === 0) continue;
    const y0 = padT + displayIdx * rowH + rowH / 2;
    ctx.strokeStyle = `hsl(${Math.round((displayIdx / Math.max(1, ch)) * 300)}, 70%, 45%)`;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    for (let i = 0; i < row.length; i += 1) {
      const x = padL + (i / (row.length - 1)) * plotW;
      const y = y0 - (row[i] ?? 0) * gain;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  raf = requestAnimationFrame(draw);
}

function connectWebSocket() {
  const base = (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";
  const wsBase = String(base).replace(/^http/i, "ws");
  const token = localStorage.getItem("access_token");
  const wsUrl = token ? `${wsBase}/eeg/stream?token=${token}` : `${wsBase}/eeg/stream`;

  status.value = "connecting";
  ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    if (payload.error) {
      status.value = "error";
      return;
    }
    const samples = Array.isArray(payload.samples) ? payload.samples : [];
    const inferredChannels =
      Array.isArray(payload.channels) && payload.channels.length > 0
        ? payload.channels
        : Array.isArray(samples) && Array.isArray(samples[0])
        ? samples.map((_, i) => `Ch ${i + 1}`)
        : [];
    const f = Number(payload.sfreq || 0) || 100;
    if (channelsCount.value === 0 && inferredChannels.length > 0) {
      initBuffers(f, inferredChannels);
    }
    if (samples.length > 0) {
      appendSamples(samples);
      status.value = "live";
    }
  };

  ws.onerror = () => {
    status.value = "error";
  };
  
  ws.onclose = () => {
    if (status.value !== "live") status.value = "error";
  };
}

function disconnectWebSocket() {
  ws?.close();
  ws = null;
  status.value = "idle";
  channelsCount.value = 0;
  channelNames.value = [];
  xs = null;
  ys = [];
  points = 0;
  sfreq = 0;
  maxAbsRaw = 0;
}

onMounted(() => {
  if (!canvas.value) return;
  ctx = canvas.value.getContext("2d");
  if (!ctx) return;
  
  raf = requestAnimationFrame(draw);
  
  // Connect only if isActive is true
  if (props.isActive) {
    connectWebSocket();
  }
});

// Watch isActive prop to connect/disconnect
watch(() => props.isActive, (newValue) => {
  if (newValue) {
    if (!ws || ws.readyState === WebSocket.CLOSED) {
      connectWebSocket();
    }
  } else {
    disconnectWebSocket();
  }
});

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf);
  ws?.close();
  ws = null;
});
</script>

<style scoped>
.eeg-chart {
  display: grid;
  gap: 12px;
}
.eeg-chart__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.eeg-chart__title {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1b26;
}
.eeg-chart__meta {
  font-size: 0.75rem;
  color: #8d99ae;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.eeg-chart__dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #cbd5e1;
}
.eeg-chart__dot--connecting {
  background: #f59e0b;
}
.eeg-chart__dot--live {
  background: #22c55e;
}
.eeg-chart__dot--error {
  background: #ef4444;
}
.eeg-chart__plot {
  height: 440px;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: inset 0 0 0 1px rgba(141, 153, 174, 0.25);
  overflow: hidden;
}
.eeg-chart__canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
