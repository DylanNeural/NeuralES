<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';

const canvasRef = ref<HTMLCanvasElement | null>(null);
const heartRef = ref<HTMLCanvasElement | null>(null);
const bpm = ref(72);

// Three.js heart
let heartRenderer: THREE.WebGLRenderer | null = null;
let heartScene: THREE.Scene;
let heartCamera: THREE.PerspectiveCamera;
let heartGroup: THREE.Group;
let heartMesh: THREE.Mesh;
let heartAnimId = 0;
let beatPhase = 0;
let beatVel = 0;
let lastBeatMs = 0;

// ECG canvas state
const SRATE = 250;
const bufLen = SRATE * 4;
const buf = new Float32Array(bufLen);
let writeIdx = 0;
let lastMs = 0;
let t = 0;
let ecgAnimId = 0;

function gaussian(x: number, mu: number, sigma: number, amp: number) {
  return amp * Math.exp(-((x - mu) ** 2) / (2 * sigma ** 2));
}

function ecgSample(phase: number): number {
  let v = 0;
  v += gaussian(phase, 0.14, 0.022, 0.22);
  v += gaussian(phase, 0.28, 0.006, -0.13);
  v += gaussian(phase, 0.30, 0.009, 1.0);
  v += gaussian(phase, 0.325, 0.006, -0.28);
  v += gaussian(phase, 0.43, 0.042, 0.32);
  return v + (Math.random() - 0.5) * 0.018;
}

function makeHeartGeo() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.25);
  s.bezierCurveTo(0, 0.25, -0.1, 0.5, -0.3, 0.5);
  s.bezierCurveTo(-0.72, 0.5, -0.72, 0, -0.72, 0);
  s.bezierCurveTo(-0.72, -0.3, -0.45, -0.52, 0, -0.78);
  s.bezierCurveTo(0.45, -0.52, 0.72, -0.3, 0.72, 0);
  s.bezierCurveTo(0.72, 0, 0.72, 0.5, 0.3, 0.5);
  s.bezierCurveTo(0.1, 0.5, 0, 0.25, 0, 0.25);
  return new THREE.ExtrudeGeometry(s, {
    depth: 0.28,
    bevelEnabled: true,
    bevelThickness: 0.08,
    bevelSize: 0.06,
    bevelSegments: 5,
  });
}

function initHeart(canvas: HTMLCanvasElement) {
  heartScene = new THREE.Scene();
  heartScene.background = new THREE.Color(0x0a0f1a);

  const aspect = canvas.clientWidth / canvas.clientHeight;
  heartCamera = new THREE.PerspectiveCamera(38, aspect, 0.1, 50);
  heartCamera.position.set(0, 0, 3.5);

  heartRenderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  heartRenderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  heartRenderer.setSize(canvas.clientWidth, canvas.clientHeight, false);

  heartScene.add(new THREE.AmbientLight(0xffdddd, 0.4));
  const key = new THREE.DirectionalLight(0xff8888, 1.8);
  key.position.set(2, 3, 4);
  heartScene.add(key);
  const rim = new THREE.DirectionalLight(0xffffff, 0.4);
  rim.position.set(-2, -1, -2);
  heartScene.add(rim);
  const fill = new THREE.PointLight(0xff3333, 0.6, 8);
  fill.position.set(0, 0, 3);
  heartScene.add(fill);

  heartGroup = new THREE.Group();

  const heartMat = new THREE.MeshStandardMaterial({
    color: 0xcc1111,
    roughness: 0.45,
    metalness: 0.08,
    emissive: new THREE.Color(0x550000),
    emissiveIntensity: 0.25,
  });

  heartMesh = new THREE.Mesh(makeHeartGeo(), heartMat);
  heartMesh.position.set(-0.01, -0.02, -0.14);
  heartGroup.add(heartMesh);

  const vesselMat = new THREE.MeshStandardMaterial({ color: 0x991111, roughness: 0.5 });

  const aorta = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 0.45, 16), vesselMat);
  aorta.position.set(-0.15, 0.72, 0);
  aorta.rotation.z = -0.18;
  heartGroup.add(aorta);

  const pulm = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.13, 0.38, 16), vesselMat);
  pulm.position.set(0.18, 0.7, 0);
  pulm.rotation.z = 0.25;
  heartGroup.add(pulm);

  heartScene.add(heartGroup);

  function animateHeart() {
    const now = performance.now();
    const beatInterval = 60000 / bpm.value;

    if (now - lastBeatMs > beatInterval) {
      lastBeatMs = now;
      beatVel = 0.018;
    }

    beatPhase += beatVel;
    beatVel -= beatPhase * 0.10;
    beatVel *= 0.80;

    const s = 1 + beatPhase * 0.18;
    heartGroup.scale.setScalar(s);
    heartGroup.rotation.y = Math.sin(now * 0.00025) * 0.2;
    (heartMesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.25 + beatPhase * 0.5;

    heartRenderer!.render(heartScene, heartCamera);
    heartAnimId = requestAnimationFrame(animateHeart);
  }
  animateHeart();
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d')!;
  const W = canvas.width, H = canvas.height;
  const now = performance.now();
  const dt = Math.min((now - lastMs) / 1000, 0.05);
  lastMs = now;

  const period = 60 / bpm.value;
  const newSamples = Math.round(dt * SRATE);
  for (let i = 0; i < newSamples; i++) {
    t += 1 / SRATE;
    const phase = (t % period) / period;
    buf[writeIdx % bufLen] = ecgSample(phase);
    writeIdx++;
  }

  bpm.value = Math.round(72 + Math.sin(t * 0.07) * 6 + (Math.random() - 0.5) * 1.5);

  ctx.clearRect(0, 0, W, H);

  ctx.strokeStyle = 'rgba(239,68,68,0.07)';
  ctx.lineWidth = 1;
  for (let x = 0; x < W; x += 25) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += 25) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

  ctx.beginPath();
  ctx.strokeStyle = '#ef4444';
  ctx.lineWidth = 2;
  ctx.shadowColor = '#ef4444';
  ctx.shadowBlur = 6;
  for (let i = 0; i < bufLen; i++) {
    const xi = (i / bufLen) * W;
    const sampleIdx = (writeIdx - bufLen + i + bufLen) % bufLen;
    const v = buf[sampleIdx] ?? 0;
    const yi = H / 2 - v * (H / 2.8);
    if (i === 0) ctx.moveTo(xi, yi); else ctx.lineTo(xi, yi);
  }
  ctx.stroke();
  ctx.shadowBlur = 0;

  ecgAnimId = requestAnimationFrame(draw);
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (canvas) {
    canvas.width = canvas.offsetWidth * devicePixelRatio;
    canvas.height = canvas.offsetHeight * devicePixelRatio;
    lastMs = performance.now();
    draw();
  }

  const hCanvas = heartRef.value;
  if (hCanvas) {
    initHeart(hCanvas);
  }
});

onUnmounted(() => {
  cancelAnimationFrame(ecgAnimId);
  cancelAnimationFrame(heartAnimId);
  heartRenderer?.dispose();
});
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <div class="flex-1 space-y-4">
      <div class="rounded-xl border border-border bg-card p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="h-3 w-3 rounded-full bg-red-500 animate-pulse"></div>
            <span class="text-xs text-muted-foreground uppercase tracking-wider">Signal ECG</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-3xl font-bold text-red-400 tabular-nums">{{ bpm }}</span>
            <span class="text-sm text-muted-foreground">BPM</span>
          </div>
        </div>
        <div class="relative w-full h-40 bg-[#0a0f1a] rounded-lg overflow-hidden">
          <canvas ref="canvasRef" class="w-full h-full" style="image-rendering:crisp-edges" />
        </div>
        <div class="mt-3">
          <div class="flex justify-between text-[10px] text-muted-foreground mb-1">
            <span>40 BPM</span><span>Normal</span><span>160 BPM</span>
          </div>
          <div class="relative h-2 bg-secondary rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-blue-500 via-green-500 to-red-500"
              :style="{ width: `${((bpm - 40) / 120) * 100}%` }" />
            <div class="absolute top-1/2 -translate-y-1/2 h-3 w-0.5 bg-white/50 transition-all duration-500"
              :style="{ left: `${((bpm - 40) / 120) * 100}%` }" />
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-border bg-[#0a0f1a] overflow-hidden" style="height:220px;">
        <canvas ref="heartRef" class="w-full h-full" />
      </div>

      <div class="rounded-xl border border-border bg-card/50 p-4 text-sm text-muted-foreground space-y-2">
        <p class="font-medium text-foreground">Comment ça marche ?</p>
        <p>Chaque battement cardiaque génère un signal électrique mesurable à la surface de la peau. Le pic pointu (onde R) correspond à la contraction des ventricules.</p>
        <p class="text-xs">La forme <span class="text-foreground font-mono">P-QRS-T</span> est la "signature" d'un cycle cardiaque normal.</p>
      </div>
    </div>

    <div class="lg:w-64 space-y-4">
      <div class="rounded-xl border border-border bg-card p-4">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Placement électrodes</h3>
        <svg viewBox="0 0 120 160" class="w-full max-w-[140px] mx-auto">
          <ellipse cx="60" cy="22" rx="16" ry="20" fill="none" stroke="#475569" stroke-width="1.5"/>
          <rect x="38" y="42" width="44" height="55" rx="6" fill="none" stroke="#475569" stroke-width="1.5"/>
          <line x1="38" y1="48" x2="18" y2="90" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="82" y1="48" x2="102" y2="90" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="52" y1="97" x2="46" y2="150" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="68" y1="97" x2="74" y2="150" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="22" cy="72" r="5" fill="#ef4444" stroke="#0f172a" stroke-width="1"/>
          <text x="2" y="71" font-size="6" fill="#ef4444" font-family="monospace">RA</text>
          <circle cx="98" cy="72" r="5" fill="#f59e0b" stroke="#0f172a" stroke-width="1"/>
          <text x="105" y="71" font-size="6" fill="#f59e0b" font-family="monospace">LA</text>
          <circle cx="46" cy="135" r="5" fill="#22c55e" stroke="#0f172a" stroke-width="1"/>
          <text x="28" y="148" font-size="6" fill="#22c55e" font-family="monospace">REF</text>
        </svg>
        <div class="mt-3 space-y-1.5 text-xs">
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-red-500 shrink-0"></span><span class="text-muted-foreground">RA — Poignet droit</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-amber-500 shrink-0"></span><span class="text-muted-foreground">LA — Poignet gauche</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-green-500 shrink-0"></span><span class="text-muted-foreground">REF — Cheville droite</span></div>
        </div>
      </div>

      <div class="rounded-xl border border-border bg-card p-4">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Indicateurs</h3>
        <div class="space-y-3">
          <div>
            <div class="flex justify-between text-xs mb-1"><span class="text-muted-foreground">Fréquence cardiaque</span><span class="text-foreground font-semibold">{{ bpm }} BPM</span></div>
            <div class="h-1.5 bg-secondary rounded-full overflow-hidden"><div class="h-full bg-red-400 rounded-full transition-all duration-500" :style="{ width: `${((bpm-40)/120)*100}%` }" /></div>
          </div>
          <div class="flex justify-between text-xs">
            <span class="text-muted-foreground">Zone</span>
            <span :class="bpm < 60 ? 'text-blue-400' : bpm < 100 ? 'text-green-400' : 'text-red-400'" class="font-semibold text-xs">
              {{ bpm < 60 ? 'Bradycardie' : bpm < 100 ? 'Normal ✓' : 'Tachycardie' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
