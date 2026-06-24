<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const canvasRef = ref<HTMLCanvasElement | null>(null);
const emgLevel = ref(0);
const ballY = ref(50);
const score = ref(0);
const isContracting = ref(false);
const highScore = ref(0);

let animId = 0;
let lastMs = 0;

const GRAVITY = 18;
const LIFT_FORCE = 45;
const ZONE_TOP = 35;
const ZONE_BOT = 65;

function setContracting(val: boolean) { isContracting.value = val; }

function handleKey(e: KeyboardEvent) {
  if (e.code === 'Space') { e.preventDefault(); setContracting(e.type === 'keydown'); }
}

function drawCanvas() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d')!;
  const W = canvas.width, H = canvas.height;
  const now = performance.now();
  const dt = Math.min((now - lastMs) / 1000, 0.04);
  lastMs = now;

  const force = isContracting.value ? -LIFT_FORCE : GRAVITY;
  ballY.value = Math.max(0, Math.min(100, ballY.value + force * dt));

  emgLevel.value = isContracting.value
    ? Math.min(100, 60 + Math.random() * 40)
    : Math.max(0, Math.random() * 8);

  const inZone = ballY.value >= ZONE_TOP && ballY.value <= ZONE_BOT;
  if (inZone) { score.value += dt * 10; if (score.value > highScore.value) highScore.value = score.value; }
  else if (score.value > 0) score.value = Math.max(0, score.value - dt * 3);

  ctx.clearRect(0, 0, W, H);

  const zt = (ZONE_TOP / 100) * H;
  const zb = (ZONE_BOT / 100) * H;
  ctx.fillStyle = inZone ? 'rgba(34,197,94,0.12)' : 'rgba(34,197,94,0.06)';
  ctx.fillRect(0, zt, W, zb - zt);
  ctx.strokeStyle = inZone ? 'rgba(34,197,94,0.5)' : 'rgba(34,197,94,0.2)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  ctx.beginPath(); ctx.moveTo(0, zt); ctx.lineTo(W, zt); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, zb); ctx.lineTo(W, zb); ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = 'rgba(34,197,94,0.4)';
  ctx.font = '11px system-ui';
  ctx.textAlign = 'right';
  ctx.fillText('ZONE CIBLE', W - 8, zt - 6);
  ctx.textAlign = 'left';

  const ballPx = (ballY.value / 100) * H;
  const ballR = 18;
  const ballColor = inZone ? '#22c55e' : '#f59e0b';
  ctx.beginPath();
  ctx.arc(W / 2, ballPx, ballR, 0, Math.PI * 2);
  ctx.fillStyle = ballColor;
  ctx.shadowColor = ballColor;
  ctx.shadowBlur = 20;
  ctx.fill();
  ctx.shadowBlur = 0;

  if (!isContracting.value && ballY.value > ZONE_BOT) {
    ctx.fillStyle = 'rgba(245,158,11,0.6)';
    ctx.font = 'bold 14px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText('↑ Contracte !', W / 2, ballPx - ballR - 8);
    ctx.textAlign = 'left';
  }

  animId = requestAnimationFrame(drawCanvas);
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  canvas.width = canvas.offsetWidth * devicePixelRatio;
  canvas.height = canvas.offsetHeight * devicePixelRatio;
  lastMs = performance.now();
  drawCanvas();
  window.addEventListener('keydown', handleKey);
  window.addEventListener('keyup', handleKey);
});

onUnmounted(() => {
  cancelAnimationFrame(animId);
  window.removeEventListener('keydown', handleKey);
  window.removeEventListener('keyup', handleKey);
});
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <div class="flex-1 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex gap-4">
          <div class="text-center"><div class="text-2xl font-bold text-green-400 tabular-nums">{{ Math.floor(score) }}</div><div class="text-[10px] text-muted-foreground">SCORE</div></div>
          <div class="text-center"><div class="text-2xl font-bold text-primary tabular-nums">{{ Math.floor(highScore) }}</div><div class="text-[10px] text-muted-foreground">MEILLEUR</div></div>
        </div>
        <div class="text-xs text-muted-foreground">Maintenir dans la zone verte</div>
      </div>

      <div class="relative rounded-xl border border-border bg-[#0a0f1a] overflow-hidden" style="height:320px;">
        <canvas ref="canvasRef" class="w-full h-full" />
      </div>

      <div class="rounded-xl border border-border bg-card p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-muted-foreground uppercase tracking-wider">Signal EMG</span>
          <span class="text-sm font-semibold" :class="isContracting ? 'text-amber-400' : 'text-muted-foreground'">{{ isContracting ? 'CONTRACTION' : 'Repos' }}</span>
        </div>
        <div class="h-3 bg-secondary rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-75"
            :class="isContracting ? 'bg-amber-400' : 'bg-secondary-foreground/20'"
            :style="{ width: `${emgLevel}%` }" />
        </div>
      </div>

      <button
        class="w-full py-5 rounded-xl text-lg font-bold transition-all select-none"
        :class="isContracting ? 'bg-amber-500 text-white scale-[0.98] shadow-inner' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:bg-amber-500/30'"
        @mousedown="setContracting(true)"
        @mouseup="setContracting(false)"
        @touchstart.prevent="setContracting(true)"
        @touchend.prevent="setContracting(false)"
      >
        {{ isContracting ? '⚡ En contraction !' : '💪 Maintenir appuyé pour monter' }}
      </button>
      <p class="text-center text-xs text-muted-foreground">ou touche <kbd class="px-1.5 py-0.5 bg-secondary rounded text-xs">Espace</kbd></p>
    </div>

    <div class="lg:w-64 space-y-4">
      <div class="rounded-xl border border-border bg-card p-4">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Placement électrodes</h3>
        <svg viewBox="0 0 120 100" class="w-full max-w-[140px] mx-auto">
          <rect x="15" y="20" width="90" height="32" rx="16" fill="none" stroke="#475569" stroke-width="1.5"/>
          <ellipse cx="15" cy="36" rx="10" ry="14" fill="none" stroke="#475569" stroke-width="1.5"/>
          <ellipse cx="105" cy="36" rx="14" ry="16" fill="none" stroke="#475569" stroke-width="1.5"/>
          <text x="60" y="42" font-size="7" fill="#64748b" text-anchor="middle" font-family="system-ui">Avant-bras</text>
          <circle cx="48" cy="36" r="5" fill="#ef4444" stroke="#0f172a" stroke-width="1"/>
          <text x="48" y="22" font-size="6" fill="#ef4444" text-anchor="middle" font-family="monospace">CH1</text>
          <circle cx="72" cy="36" r="5" fill="#f59e0b" stroke="#0f172a" stroke-width="1"/>
          <text x="72" y="22" font-size="6" fill="#f59e0b" text-anchor="middle" font-family="monospace">CH2</text>
          <circle cx="96" cy="36" r="5" fill="#22c55e" stroke="#0f172a" stroke-width="1"/>
          <text x="96" y="66" font-size="6" fill="#22c55e" text-anchor="middle" font-family="monospace">REF</text>
        </svg>
        <div class="mt-3 space-y-1.5 text-xs">
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-red-500 shrink-0"></span><span class="text-muted-foreground">CH1 — Ventre du muscle</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-amber-500 shrink-0"></span><span class="text-muted-foreground">CH2 — 2 cm plus distal</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-green-500 shrink-0"></span><span class="text-muted-foreground">REF — Épicondyle (coude)</span></div>
        </div>
      </div>
      <div class="rounded-xl border border-border bg-card/50 p-4 text-xs text-muted-foreground space-y-2">
        <p class="font-medium text-foreground">Principe</p>
        <p>La contraction musculaire génère des potentiels d'action dans les fibres musculaires. L'EMG mesure l'activité électrique sommée de ces fibres.</p>
      </div>
    </div>
  </div>
</template>
