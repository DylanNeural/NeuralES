<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';

const canvasRef = ref<HTMLCanvasElement | null>(null);
const faceRef = ref<HTMLCanvasElement | null>(null);
const eyesClosed = ref(false);
const alphaPower = ref(5);

// ECG canvas state
let ecgAnimId = 0;
let t = 0;
let lastMs = 0;
const bufLen = 500;
const buf = new Float32Array(bufLen);
let writeIdx = 0;

// Three.js face
let faceRenderer: THREE.WebGLRenderer | null = null;
let faceAnimId = 0;
let eyeOpenness = 1.0;

function sample(closed: boolean): number {
  if (closed) {
    return Math.sin(2 * Math.PI * 10 * t) * 0.8 + (Math.random() - 0.5) * 0.15;
  }
  return (Math.random() - 0.5) * 0.5 + Math.sin(2 * Math.PI * 25 * t) * 0.08;
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d')!;
  const W = canvas.width, H = canvas.height;
  const now = performance.now();
  const dt = Math.min((now - lastMs) / 1000, 0.04);
  lastMs = now;

  const srate = 250;
  const newSamples = Math.round(dt * srate);
  for (let i = 0; i < newSamples; i++) {
    t += 1 / srate;
    buf[writeIdx % bufLen] = sample(eyesClosed.value);
    writeIdx++;
  }

  const target = eyesClosed.value ? 82 + (Math.random() - 0.5) * 10 : 8 + (Math.random() - 0.5) * 6;
  alphaPower.value += (target - alphaPower.value) * dt * 1.5;

  ctx.clearRect(0, 0, W, H);

  ctx.strokeStyle = 'rgba(99,102,241,0.06)';
  ctx.lineWidth = 1;
  for (let x = 0; x < W; x += 30) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += 20) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

  const color = eyesClosed.value ? '#818cf8' : '#64748b';
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.shadowColor = color;
  ctx.shadowBlur = eyesClosed.value ? 10 : 0;
  for (let i = 0; i < bufLen; i++) {
    const xi = (i / bufLen) * W;
    const si = (writeIdx - bufLen + i + bufLen * 2) % bufLen;
    const yi = H / 2 - (buf[si] ?? 0) * (H / 2.6);
    if (i === 0) ctx.moveTo(xi, yi); else ctx.lineTo(xi, yi);
  }
  ctx.stroke();
  ctx.shadowBlur = 0;

  ecgAnimId = requestAnimationFrame(draw);
}

function initFace(canvas: HTMLCanvasElement) {
  const faceScene = new THREE.Scene();
  faceScene.background = new THREE.Color(0x0a0f1a);

  const faceCamera = new THREE.PerspectiveCamera(38, canvas.clientWidth / canvas.clientHeight, 0.1, 50);
  faceCamera.position.set(0, 0, 3.8);

  faceRenderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  faceRenderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  faceRenderer.setSize(canvas.clientWidth, canvas.clientHeight, false);

  faceScene.add(new THREE.AmbientLight(0xfff5e8, 0.6));
  const key = new THREE.DirectionalLight(0xfff0d0, 2.0);
  key.position.set(1, 2, 4);
  faceScene.add(key);
  const fill = new THREE.DirectionalLight(0x88aaff, 0.5);
  fill.position.set(-3, 0, 2);
  faceScene.add(fill);

  const skinMat = new THREE.MeshStandardMaterial({ color: 0xf2c8a0, roughness: 0.82 });
  const whiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
  const irisMat = new THREE.MeshStandardMaterial({ color: 0x2255cc, roughness: 0.15 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x060606 });
  const lidMat = new THREE.MeshStandardMaterial({ color: 0xeab898, roughness: 0.85 });
  const browMat = new THREE.MeshStandardMaterial({ color: 0x3d2008, roughness: 0.9 });
  const lipMat = new THREE.MeshStandardMaterial({ color: 0xc85858, roughness: 0.6 });

  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 36), skinMat);
  head.scale.set(0.86, 1.12, 0.92);
  faceScene.add(head);

  type EyeData = { group: THREE.Group; sclera: THREE.Mesh; irisD: THREE.Mesh; pupil: THREE.Mesh; lid: THREE.Mesh };
  const eyes: EyeData[] = [];

  function buildFaceEye(side: number): EyeData {
    const g = new THREE.Group();
    g.position.set(side * 0.33, 0.14, 0.83);

    const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.17, 20, 16), whiteMat);
    g.add(sclera);

    const irisD = new THREE.Mesh(new THREE.CircleGeometry(0.1, 24), irisMat);
    irisD.position.z = 0.16;
    g.add(irisD);

    const pupil = new THREE.Mesh(new THREE.CircleGeometry(0.052, 16), pupilMat);
    pupil.position.z = 0.162;
    g.add(pupil);

    const highlight = new THREE.Mesh(
      new THREE.CircleGeometry(0.018, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    highlight.position.set(0.032, 0.032, 0.163);
    g.add(highlight);

    const lid = new THREE.Mesh(
      new THREE.CylinderGeometry(0.18, 0.18, 0.01, 24),
      lidMat
    );
    lid.rotation.x = -Math.PI / 2;
    lid.position.z = 0.17;
    lid.scale.y = 0;
    g.add(lid);

    faceScene.add(g);
    return { group: g, sclera, irisD, pupil, lid };
  }

  eyes.push(buildFaceEye(-1));
  eyes.push(buildFaceEye(1));

  // Eyebrows
  for (const side of [-1, 1]) {
    const bg = new THREE.Group();
    bg.position.set(side * 0.33, 0.40, 0.83);
    for (let i = -1; i <= 1; i++) {
      const seg = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.1, 8), browMat);
      seg.position.x = i * 0.082;
      seg.position.y = Math.abs(i) * 0.018 * side;
      seg.rotation.z = -i * 0.2 * side;
      bg.add(seg);
    }
    faceScene.add(bg);
  }

  // Nose
  const noseTip = new THREE.Mesh(new THREE.SphereGeometry(0.085, 14, 12), skinMat);
  noseTip.position.set(0, -0.14, 0.96);
  faceScene.add(noseTip);
  const noseBridge = new THREE.Mesh(new THREE.SphereGeometry(0.052, 12, 10), skinMat);
  noseBridge.position.set(0, 0.05, 0.94);
  noseBridge.scale.set(0.6, 1.4, 0.6);
  faceScene.add(noseBridge);

  // Mouth
  const mouth = new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.038, 6, 20, Math.PI), lipMat);
  mouth.position.set(0, -0.6, 0.84);
  faceScene.add(mouth);

  let faceLastMs = performance.now();

  function animateFace() {
    const now = performance.now();
    const dt = Math.min((now - faceLastMs) / 1000, 0.05);
    faceLastMs = now;

    const targetOpen = eyesClosed.value ? 0 : 1;
    eyeOpenness += (targetOpen - eyeOpenness) * dt * 4;

    const eyeScaleY = Math.max(0.05, eyeOpenness);
    const lidScale = Math.max(0, 1 - eyeOpenness);

    for (const e of eyes) {
      e.sclera.scale.y = eyeScaleY;
      e.irisD.scale.y = eyeScaleY;
      e.pupil.scale.y = eyeScaleY;
      e.lid.scale.y = lidScale * 18;
    }

    head.rotation.y = Math.sin(now * 0.0004) * 0.12;
    head.rotation.x = Math.sin(now * 0.0003) * 0.04;

    faceRenderer!.render(faceScene, faceCamera);
    faceAnimId = requestAnimationFrame(animateFace);
  }
  animateFace();
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (canvas) {
    canvas.width = canvas.offsetWidth * devicePixelRatio;
    canvas.height = canvas.offsetHeight * devicePixelRatio;
    lastMs = performance.now();
    draw();
  }

  const fc = faceRef.value;
  if (fc) initFace(fc);
});

onUnmounted(() => {
  cancelAnimationFrame(ecgAnimId);
  cancelAnimationFrame(faceAnimId);
  faceRenderer?.dispose();
});
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <div class="flex-1 space-y-4">
      <div class="flex gap-3">
        <button @click="eyesClosed = false"
          :class="['flex-1 py-4 rounded-xl text-sm font-semibold border transition-all', !eyesClosed ? 'bg-blue-500/20 border-blue-500/50 text-blue-400' : 'bg-card border-border text-muted-foreground hover:border-blue-500/30']">
          👁️ Yeux Ouverts
        </button>
        <button @click="eyesClosed = true"
          :class="['flex-1 py-4 rounded-xl text-sm font-semibold border transition-all', eyesClosed ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-400' : 'bg-card border-border text-muted-foreground hover:border-indigo-500/30']">
          😌 Yeux Fermés
        </button>
      </div>

      <div class="rounded-xl border bg-[#0a0f1a] overflow-hidden p-3"
        :class="eyesClosed ? 'border-indigo-500/30' : 'border-border'">
        <div class="text-xs text-muted-foreground mb-2 flex justify-between">
          <span>Canal O1-O2 (occipital)</span>
          <span :class="eyesClosed ? 'text-indigo-400' : 'text-muted-foreground'">
            {{ eyesClosed ? '10 Hz — Onde Alpha' : 'Signal de fond' }}
          </span>
        </div>
        <div class="relative w-full h-36">
          <canvas ref="canvasRef" class="w-full h-full" />
        </div>
      </div>

      <div class="rounded-xl border border-border bg-card p-5">
        <div class="flex items-center justify-between mb-4">
          <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Puissance Alpha (8–12 Hz)</span>
          <span class="text-2xl font-bold tabular-nums" :class="eyesClosed ? 'text-indigo-400' : 'text-muted-foreground'">
            {{ Math.round(alphaPower) }}%
          </span>
        </div>
        <div class="h-4 bg-secondary rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-300"
            :class="eyesClosed ? 'bg-indigo-500' : 'bg-slate-600'"
            :style="{ width: `${alphaPower}%` }" />
        </div>
        <div class="flex justify-between text-[10px] text-muted-foreground mt-1.5">
          <span>Faible</span><span>Élevée</span>
        </div>
        <div class="mt-3 text-center">
          <span :class="['inline-block px-3 py-1 rounded-full text-xs font-semibold border', eyesClosed ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400' : 'bg-slate-500/10 border-slate-500/30 text-slate-400']">
            {{ eyesClosed ? '✓ Alpha dominante — cerveau au repos' : 'Alpha supprimée — cerveau actif' }}
          </span>
        </div>
      </div>
    </div>

    <div class="lg:w-64 space-y-4">
      <div class="rounded-xl border border-border bg-[#0a0f1a] overflow-hidden" style="height:200px;">
        <canvas ref="faceRef" class="w-full h-full" />
      </div>

      <div class="rounded-xl border border-border bg-card p-4">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Placement électrodes</h3>
        <svg viewBox="0 0 120 120" class="w-full max-w-[140px] mx-auto">
          <ellipse cx="60" cy="60" rx="50" ry="58" fill="none" stroke="#475569" stroke-width="1.5"/>
          <path d="M 55 5 Q 60 0 65 5" fill="none" stroke="#475569" stroke-width="1"/>
          <path d="M 10 60 Q 6 52 10 44" fill="none" stroke="#475569" stroke-width="1.5"/>
          <path d="M 110 44 Q 114 52 110 60" fill="none" stroke="#475569" stroke-width="1.5"/>
          <line x1="60" y1="5" x2="60" y2="115" stroke="#334155" stroke-width="0.5" stroke-dasharray="2,3"/>
          <line x1="10" y1="60" x2="110" y2="60" stroke="#334155" stroke-width="0.5" stroke-dasharray="2,3"/>
          <circle cx="60" cy="108" r="3" fill="#334155"/>
          <text x="60" y="118" font-size="6" fill="#475569" text-anchor="middle" font-family="monospace">Oz</text>
          <circle cx="36" cy="98" r="5" fill="#818cf8" stroke="#0f172a" stroke-width="1"/>
          <text x="22" y="97" font-size="6.5" fill="#818cf8" font-family="monospace">O1</text>
          <circle cx="84" cy="98" r="5" fill="#818cf8" stroke="#0f172a" stroke-width="1"/>
          <text x="90" y="97" font-size="6.5" fill="#818cf8" font-family="monospace">O2</text>
          <circle cx="10" cy="52" r="4" fill="#22c55e" stroke="#0f172a" stroke-width="1"/>
          <text x="0" y="65" font-size="6" fill="#22c55e" font-family="monospace">A1</text>
        </svg>
        <div class="mt-3 space-y-1.5 text-xs">
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-indigo-400 shrink-0"></span><span class="text-muted-foreground">O1/O2 — Occipital (arrière tête)</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-green-500 shrink-0"></span><span class="text-muted-foreground">A1 — Lobe de l'oreille (ref)</span></div>
        </div>
      </div>
      <div class="rounded-xl border border-border bg-card/50 p-4 text-xs text-muted-foreground space-y-2">
        <p class="font-medium text-foreground">Pourquoi les yeux ?</p>
        <p>L'onde alpha (8–12 Hz) est générée par le cortex visuel au repos. L'ouverture des yeux envoie des informations visuelles au cerveau, qui "s'active" et supprime immédiatement l'alpha.</p>
        <p>C'est l'un des effets les plus reproductibles en EEG.</p>
      </div>
    </div>
  </div>
</template>
