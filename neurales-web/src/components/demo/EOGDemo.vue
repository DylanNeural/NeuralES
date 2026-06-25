<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';

const gazeX = ref(0);
const gazeY = ref(0);
const signalH = ref(0);
const signalV = ref(0);
const faceRef = ref<HTMLCanvasElement | null>(null);

const sequence = [
  { x: 0, y: 0, label: 'Centre', dur: 1500 },
  { x: -1, y: 0, label: '← Gauche', dur: 2000 },
  { x: 0, y: 0, label: 'Centre', dur: 1200 },
  { x: 1, y: 0, label: '→ Droite', dur: 2000 },
  { x: 0, y: 0, label: 'Centre', dur: 1200 },
  { x: 0, y: -1, label: '↑ Haut', dur: 2000 },
  { x: 0, y: 0, label: 'Centre', dur: 1200 },
  { x: 0, y: 1, label: '↓ Bas', dur: 2000 },
  { x: 0, y: 0, label: 'Centre', dur: 1000 },
  { x: -0.7, y: -0.7, label: '↖ Diagonale', dur: 1800 },
  { x: 0.7, y: 0.7, label: '↘ Diagonale', dur: 1800 },
  { x: 0, y: 0, label: 'Centre', dur: 1000 },
];

const currentLabel = ref('Centre');
let seqIdx = 0;
let targetX = 0;
let targetY = 0;
let animId = 0;
let lastMs = 0;
let stepTimer = 0;

// Three.js face
let faceRenderer: THREE.WebGLRenderer | null = null;
let faceAnimId = 0;

function nextStep() {
  const step = sequence[seqIdx % sequence.length]!;
  targetX = step.x;
  targetY = step.y;
  currentLabel.value = step.label;
  stepTimer = step.dur;
  seqIdx++;
}

function animate() {
  const now = performance.now();
  const dt = Math.min((now - lastMs) / 1000, 0.04);
  lastMs = now;
  stepTimer -= dt * 1000;
  if (stepTimer <= 0) nextStep();

  const speed = 5;
  gazeX.value += (targetX - gazeX.value) * speed * dt;
  gazeY.value += (targetY - gazeY.value) * speed * dt;

  signalH.value = gazeX.value * 100 + (Math.random() - 0.5) * 8;
  signalV.value = gazeY.value * 100 + (Math.random() - 0.5) * 8;

  animId = requestAnimationFrame(animate);
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
  const browMat = new THREE.MeshStandardMaterial({ color: 0x3d2008, roughness: 0.9 });
  const lipMat = new THREE.MeshStandardMaterial({ color: 0xc85858, roughness: 0.6 });

  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 36), skinMat);
  head.scale.set(0.86, 1.12, 0.92);
  faceScene.add(head);

  const eyeIrisGroups: THREE.Group[] = [];

  function buildTrackEye(side: number) {
    const g = new THREE.Group();
    g.position.set(side * 0.33, 0.14, 0.83);

    const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.17, 20, 16), whiteMat);
    g.add(sclera);

    const irisGroup = new THREE.Group();

    const irisD = new THREE.Mesh(new THREE.CircleGeometry(0.1, 24), irisMat);
    irisD.position.z = 0.16;
    irisGroup.add(irisD);

    const pupil = new THREE.Mesh(new THREE.CircleGeometry(0.052, 16), pupilMat);
    pupil.position.z = 0.162;
    irisGroup.add(pupil);

    const highlight = new THREE.Mesh(
      new THREE.CircleGeometry(0.018, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    highlight.position.set(0.032, 0.032, 0.163);
    irisGroup.add(highlight);

    g.add(irisGroup);
    eyeIrisGroups.push(irisGroup);

    const arc = new THREE.Mesh(
      new THREE.TorusGeometry(0.14, 0.022, 6, 20, Math.PI),
      new THREE.MeshStandardMaterial({ color: 0x1a0e06, transparent: true, opacity: 0.7 })
    );
    arc.position.set(0, 0.03, 0.165);
    g.add(arc);

    faceScene.add(g);
    return g;
  }

  buildTrackEye(-1);
  buildTrackEye(1);

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

    const gx = gazeX.value * 0.065;
    const gy = -gazeY.value * 0.065;
    for (const ig of eyeIrisGroups) {
      ig.position.x += (gx - ig.position.x) * dt * 8;
      ig.position.y += (gy - ig.position.y) * dt * 8;
    }

    head.rotation.y = Math.sin(now * 0.0003) * 0.08;

    faceRenderer!.render(faceScene, faceCamera);
    faceAnimId = requestAnimationFrame(animateFace);
  }
  animateFace();
}

onMounted(() => {
  nextStep();
  lastMs = performance.now();
  animate();

  const fc = faceRef.value;
  if (fc) initFace(fc);
});

onUnmounted(() => {
  cancelAnimationFrame(animId);
  cancelAnimationFrame(faceAnimId);
  faceRenderer?.dispose();
});
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <div class="flex-1 space-y-4">
      <div class="text-center">
        <span class="text-3xl font-bold text-foreground">{{ currentLabel }}</span>
        <p class="text-xs text-muted-foreground mt-1">Séquence automatique — direction du regard simulée</p>
      </div>

      <div class="rounded-xl border border-border bg-[#0a0f1a] p-6 flex items-center justify-center" style="height:320px;">
        <div class="relative w-full h-full max-w-[320px] max-h-[280px] mx-auto">
          <div class="absolute inset-0 border border-slate-700/50 rounded-lg">
            <div class="absolute left-1/2 top-0 bottom-0 w-px bg-slate-700/40 -translate-x-1/2"></div>
            <div class="absolute top-1/2 left-0 right-0 h-px bg-slate-700/40 -translate-y-1/2"></div>
            <span class="absolute top-2 left-2 text-[10px] text-slate-600">↖</span>
            <span class="absolute top-2 right-2 text-[10px] text-slate-600">↗</span>
            <span class="absolute bottom-2 left-2 text-[10px] text-slate-600">↙</span>
            <span class="absolute bottom-2 right-2 text-[10px] text-slate-600">↘</span>
          </div>
          <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full border border-slate-700/40"></div>
          <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 rounded-full border border-slate-700/20"></div>
          <div class="absolute h-5 w-5 rounded-full bg-cyan-400 shadow-[0_0_16px_4px_rgba(34,211,238,0.5)] pointer-events-none"
            :style="{ left: `calc(50% + ${gazeX * 44}% - 10px)`, top: `calc(50% + ${gazeY * 44}% - 10px)` }" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-xl border border-border bg-card p-3">
          <div class="flex justify-between text-xs mb-2">
            <span class="text-muted-foreground">EOG Horizontal</span>
            <span class="font-mono" :class="signalH > 20 ? 'text-cyan-400' : signalH < -20 ? 'text-purple-400' : 'text-muted-foreground'">{{ Math.round(signalH) }} μV</span>
          </div>
          <div class="relative h-2 bg-secondary rounded-full overflow-hidden">
            <div class="absolute top-0 bottom-0 bg-cyan-400 rounded-full transition-all duration-75"
              :style="{ left: signalH < 0 ? `${50 + signalH/2}%` : '50%', width: `${Math.abs(signalH)/2}%` }" />
            <div class="absolute left-1/2 top-0 bottom-0 w-px bg-white/20"></div>
          </div>
          <div class="flex justify-between text-[9px] text-slate-600 mt-1"><span>G</span><span>D</span></div>
        </div>
        <div class="rounded-xl border border-border bg-card p-3">
          <div class="flex justify-between text-xs mb-2">
            <span class="text-muted-foreground">EOG Vertical</span>
            <span class="font-mono" :class="signalV < -20 ? 'text-cyan-400' : signalV > 20 ? 'text-purple-400' : 'text-muted-foreground'">{{ Math.round(signalV) }} μV</span>
          </div>
          <div class="relative h-2 bg-secondary rounded-full overflow-hidden">
            <div class="absolute top-0 bottom-0 bg-purple-400 rounded-full transition-all duration-75"
              :style="{ left: signalV > 0 ? '50%' : `${50 + signalV/2}%`, width: `${Math.abs(signalV)/2}%` }" />
            <div class="absolute left-1/2 top-0 bottom-0 w-px bg-white/20"></div>
          </div>
          <div class="flex justify-between text-[9px] text-slate-600 mt-1"><span>H</span><span>B</span></div>
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
          <ellipse cx="60" cy="58" rx="42" ry="50" fill="none" stroke="#475569" stroke-width="1.5"/>
          <ellipse cx="42" cy="46" rx="10" ry="6" fill="none" stroke="#475569" stroke-width="1"/>
          <ellipse cx="78" cy="46" rx="10" ry="6" fill="none" stroke="#475569" stroke-width="1"/>
          <circle cx="42" cy="46" r="3" fill="#475569"/>
          <circle cx="78" cy="46" r="3" fill="#475569"/>
          <path d="M56 62 Q60 72 64 62" fill="none" stroke="#475569" stroke-width="1"/>
          <path d="M48 82 Q60 90 72 82" fill="none" stroke="#475569" stroke-width="1"/>
          <circle cx="18" cy="46" r="5" fill="#22d3ee" stroke="#0f172a" stroke-width="1"/>
          <text x="3" y="38" font-size="5.5" fill="#22d3ee" font-family="monospace">H-L</text>
          <circle cx="102" cy="46" r="5" fill="#22d3ee" stroke="#0f172a" stroke-width="1"/>
          <text x="104" y="38" font-size="5.5" fill="#22d3ee" font-family="monospace">H-R</text>
          <circle cx="78" cy="34" r="5" fill="#a78bfa" stroke="#0f172a" stroke-width="1"/>
          <text x="84" y="28" font-size="5.5" fill="#a78bfa" font-family="monospace">V-H</text>
          <circle cx="78" cy="58" r="5" fill="#a78bfa" stroke="#0f172a" stroke-width="1"/>
          <text x="84" y="70" font-size="5.5" fill="#a78bfa" font-family="monospace">V-B</text>
          <circle cx="60" cy="108" r="4" fill="#22c55e" stroke="#0f172a" stroke-width="1"/>
          <text x="60" y="118" font-size="5.5" fill="#22c55e" text-anchor="middle" font-family="monospace">REF</text>
        </svg>
        <div class="mt-3 space-y-1.5 text-xs">
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-cyan-400 shrink-0"></span><span class="text-muted-foreground">H-L / H-R — Coins des yeux (horizontal)</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-purple-400 shrink-0"></span><span class="text-muted-foreground">V-H / V-B — Au-dessus/dessous œil (vertical)</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-green-500 shrink-0"></span><span class="text-muted-foreground">REF — Menton ou oreille</span></div>
        </div>
      </div>
      <div class="rounded-xl border border-border bg-card/50 p-4 text-xs text-muted-foreground space-y-2">
        <p class="font-medium text-foreground">Principe</p>
        <p>L'œil est une pile électrique : la cornée est positive, la rétine négative. Quand l'œil bouge, ce dipôle se déplace et change le potentiel mesuré aux électrodes.</p>
        <p>Applications : BCI, détection somnolence, accessibilité (contrôle par les yeux).</p>
      </div>
    </div>
  </div>
</template>
