<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';

const canvasRef = ref<HTMLCanvasElement | null>(null);

const jawSignal = ref(0);
const browSignal = ref(0);
const smileSignal = ref(0);
const eyeSignal = ref(0);
const expressionLabel = ref('Neutre');

let renderer: THREE.WebGLRenderer | null = null;
let animId = 0;

const expressions = [
  { label: 'Neutre', jaw: 0, brow: 0, smile: 0, eyeX: 0, dur: 2000 },
  { label: 'Bouche ouverte', jaw: 1, brow: 0, smile: 0, eyeX: 0, dur: 2500 },
  { label: 'Sourcils levés', jaw: 0, brow: 1, smile: 0, eyeX: 0, dur: 2000 },
  { label: 'Regard gauche', jaw: 0, brow: 0, smile: 0, eyeX: -1, dur: 2000 },
  { label: 'Regard droit', jaw: 0, brow: 0, smile: 0, eyeX: 1, dur: 2000 },
  { label: 'Sourire', jaw: 0, brow: 0.3, smile: 1, eyeX: 0, dur: 2500 },
  { label: 'Expression complète', jaw: 0.5, brow: 0.8, smile: 0.8, eyeX: 0, dur: 2500 },
  { label: 'Neutre', jaw: 0, brow: 0, smile: 0, eyeX: 0, dur: 1500 },
];

let exprIdx = 0;
let exprTimer = 0;
let fromExpr = expressions[0]!;
let toExpr = expressions[0]!;
let exprT = 1;

function ease(t: number) { return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t; }
function lerp(a: number, b: number, t: number) { return a + (b - a) * t; }

function buildFace(scene: THREE.Scene) {
  const skinMat = new THREE.MeshStandardMaterial({ color: 0xf2c8a0, roughness: 0.82, metalness: 0 });
  const darkSkinMat = new THREE.MeshStandardMaterial({ color: 0xd4956a, roughness: 0.82, metalness: 0 });
  const browMat = new THREE.MeshStandardMaterial({ color: 0x3d2008, roughness: 0.9 });
  const scleraMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.25, metalness: 0.05 });
  const irisMat = new THREE.MeshStandardMaterial({ color: 0x2255cc, roughness: 0.15, metalness: 0.1 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x050505 });
  const lipMat = new THREE.MeshStandardMaterial({ color: 0xc85858, roughness: 0.6 });
  const teethMat = new THREE.MeshStandardMaterial({ color: 0xf5f0e8, roughness: 0.5 });
  const mouthMat = new THREE.MeshStandardMaterial({ color: 0x2a0a0a, roughness: 0.95, side: THREE.BackSide });

  // Head
  const skull = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 40), skinMat);
  skull.scale.set(0.86, 1.14, 0.92);
  scene.add(skull);

  // Neck
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.31, 0.5, 20), skinMat);
  neck.position.set(0, -1.2, -0.06);
  scene.add(neck);

  // Jaw pivot
  const jawPivot = new THREE.Group();
  jawPivot.position.set(0, -0.7, 0);
  scene.add(jawPivot);

  const jawMesh = new THREE.Mesh(new THREE.SphereGeometry(0.7, 24, 20), skinMat);
  jawMesh.scale.set(0.80, 0.46, 0.86);
  jawMesh.position.set(0, -0.3, 0);
  jawPivot.add(jawMesh);

  const mouthInterior = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 12), mouthMat);
  mouthInterior.position.set(0, 0.02, 0.62);
  mouthInterior.scale.set(1, 0.45, 0.5);
  jawPivot.add(mouthInterior);

  const lowerTeeth = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.055, 0.04), teethMat);
  lowerTeeth.position.set(0, 0.14, 0.66);
  jawPivot.add(lowerTeeth);

  const lowerLip = new THREE.Mesh(new THREE.TorusGeometry(0.23, 0.05, 8, 20, Math.PI), lipMat);
  lowerLip.rotation.x = -Math.PI;
  lowerLip.position.set(0, -0.01, 0.64);
  jawPivot.add(lowerLip);

  // Upper lip (fixed)
  const upperLip = new THREE.Mesh(new THREE.TorusGeometry(0.23, 0.05, 8, 20, Math.PI), lipMat);
  upperLip.position.set(0, -0.6, 0.8);
  scene.add(upperLip);

  // Upper teeth (fixed)
  const upperTeeth = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.055, 0.04), teethMat);
  upperTeeth.position.set(0, -0.6, 0.84);
  scene.add(upperTeeth);

  // Eyes
  function buildEye(side: number) {
    const g = new THREE.Group();
    g.position.set(side * 0.33, 0.16, 0.83);

    const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.17, 24, 20), scleraMat);
    g.add(sclera);

    const irisGroup = new THREE.Group();

    const irisDisc = new THREE.Mesh(new THREE.CircleGeometry(0.1, 32), irisMat);
    irisDisc.position.z = 0.16;
    irisGroup.add(irisDisc);

    const limbusRing = new THREE.Mesh(
      new THREE.RingGeometry(0.09, 0.105, 32),
      new THREE.MeshStandardMaterial({ color: 0x0a2a8a, side: THREE.DoubleSide })
    );
    limbusRing.position.z = 0.161;
    irisGroup.add(limbusRing);

    const pupil = new THREE.Mesh(new THREE.CircleGeometry(0.052, 20), pupilMat);
    pupil.position.z = 0.162;
    irisGroup.add(pupil);

    const highlight = new THREE.Mesh(
      new THREE.CircleGeometry(0.018, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    highlight.position.set(0.03, 0.03, 0.163);
    irisGroup.add(highlight);

    g.add(irisGroup);

    // Eyelid shadow arc
    const arc = new THREE.Mesh(
      new THREE.TorusGeometry(0.14, 0.022, 6, 20, Math.PI),
      new THREE.MeshStandardMaterial({ color: 0x1a0e06, transparent: true, opacity: 0.7 })
    );
    arc.position.set(0, 0.03, 0.165);
    g.add(arc);

    scene.add(g);
    return { group: g, irisGroup };
  }

  const leftEye = buildEye(-1);
  const rightEye = buildEye(1);

  // Eyebrows
  function buildBrow(side: number) {
    const bg = new THREE.Group();
    bg.position.set(side * 0.33, 0.42, 0.83);
    for (let i = -1; i <= 1; i++) {
      const seg = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.11, 8), browMat);
      seg.position.x = i * 0.085;
      if (i === 0) seg.position.y = -0.018;
      if (i === -1) seg.rotation.z = side * 0.18;
      if (i === 1) seg.rotation.z = -side * 0.18;
      bg.add(seg);
    }
    scene.add(bg);
    return bg;
  }

  const leftBrow = buildBrow(-1);
  const rightBrow = buildBrow(1);

  // Nose (4 spheres)
  const noseBridge = new THREE.Mesh(new THREE.SphereGeometry(0.055, 12, 10), skinMat);
  noseBridge.position.set(0, 0.06, 0.94);
  noseBridge.scale.set(0.6, 1.5, 0.6);
  scene.add(noseBridge);

  const noseTip = new THREE.Mesh(new THREE.SphereGeometry(0.088, 16, 14), skinMat);
  noseTip.position.set(0, -0.12, 0.97);
  scene.add(noseTip);

  const nostrilL = new THREE.Mesh(new THREE.SphereGeometry(0.052, 12, 10), darkSkinMat);
  nostrilL.position.set(-0.1, -0.17, 0.92);
  nostrilL.scale.set(0.8, 0.65, 0.55);
  scene.add(nostrilL);

  const nostrilR = new THREE.Mesh(new THREE.SphereGeometry(0.052, 12, 10), darkSkinMat);
  nostrilR.position.set(0.1, -0.17, 0.92);
  nostrilR.scale.set(0.8, 0.65, 0.55);
  scene.add(nostrilR);

  // Ears
  function buildEar(side: number) {
    const earGroup = new THREE.Group();
    earGroup.position.set(side * 0.88, 0.04, -0.1);
    earGroup.rotation.y = side * 1.35;

    const outer = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 14), skinMat);
    outer.scale.set(0.38, 0.62, 0.38);
    earGroup.add(outer);

    const inner = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 10), darkSkinMat);
    inner.scale.set(0.3, 0.5, 0.28);
    inner.position.z = 0.04;
    earGroup.add(inner);

    scene.add(earGroup);
  }
  buildEar(-1);
  buildEar(1);

  // Cheeks
  const cheekMatL = new THREE.MeshStandardMaterial({ color: 0xf08888, roughness: 0.9, transparent: true, opacity: 0.0 });
  const cheekMatR = cheekMatL.clone();

  const leftCheek = new THREE.Mesh(new THREE.SphereGeometry(0.2, 12, 10), cheekMatL);
  leftCheek.position.set(-0.5, -0.22, 0.74);
  scene.add(leftCheek);

  const rightCheek = new THREE.Mesh(new THREE.SphereGeometry(0.2, 12, 10), cheekMatR);
  rightCheek.position.set(0.5, -0.22, 0.74);
  scene.add(rightCheek);

  return { jawPivot, leftBrow, rightBrow, leftEye, rightEye, leftCheek, rightCheek, cheekMatL, cheekMatR };
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (!canvas) return;

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  renderer.setClearColor(0x0a0f1a, 1);

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(42, canvas.clientWidth / canvas.clientHeight, 0.1, 50);
  camera.position.set(0, 0.05, 3.8);

  const ambient = new THREE.AmbientLight(0xfff5e8, 0.5);
  scene.add(ambient);
  const key = new THREE.DirectionalLight(0xfff0d0, 2.2);
  key.position.set(1.5, 2.5, 4);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0x8aadff, 0.7);
  fill.position.set(-3, 0, 2);
  scene.add(fill);
  const rim = new THREE.DirectionalLight(0xffffff, 0.35);
  rim.position.set(0, -2, -3);
  scene.add(rim);

  const { jawPivot, leftBrow, rightBrow, leftEye, rightEye, cheekMatL, cheekMatR } = buildFace(scene);

  exprIdx = 0;
  fromExpr = expressions[0]!;
  toExpr = expressions[1]!;
  exprT = 0;
  exprTimer = toExpr.dur;

  let lastMs = performance.now();

  function tick() {
    const now = performance.now();
    const dt = Math.min((now - lastMs) / 1000, 0.05);
    lastMs = now;

    exprTimer -= dt * 1000;
    if (exprTimer <= 0) {
      exprIdx = (exprIdx + 1) % expressions.length;
      fromExpr = toExpr;
      toExpr = expressions[(exprIdx + 1) % expressions.length]!;
      exprTimer = toExpr.dur;
      exprT = 0;
    }
    exprT = Math.min(1, exprT + dt / (toExpr.dur / 1000));
    const et = ease(exprT);

    const jaw = lerp(fromExpr.jaw, toExpr.jaw, et);
    const brow = lerp(fromExpr.brow, toExpr.brow, et);
    const smile = lerp(fromExpr.smile, toExpr.smile, et);
    const eyeX = lerp(fromExpr.eyeX, toExpr.eyeX, et);

    expressionLabel.value = exprTimer < toExpr.dur * 0.5 ? toExpr.label : fromExpr.label;

    jawSignal.value = jaw * 85 + (Math.random() - 0.5) * (jaw > 0.1 ? 18 : 4);
    browSignal.value = brow * 70 + (Math.random() - 0.5) * (brow > 0.1 ? 14 : 4);
    smileSignal.value = smile * 75 + (Math.random() - 0.5) * (smile > 0.1 ? 14 : 4);
    eyeSignal.value = eyeX * 60 + (Math.random() - 0.5) * 6;

    jawPivot.rotation.x = jaw * 0.52;
    leftBrow.position.y = 0.42 + brow * 0.22;
    rightBrow.position.y = 0.42 + brow * 0.22;
    leftBrow.rotation.z = 0.08 - brow * 0.12;
    rightBrow.rotation.z = -0.08 + brow * 0.12;

    const eyeShift = eyeX * 0.08;
    leftEye.irisGroup.position.x = eyeShift;
    rightEye.irisGroup.position.x = eyeShift;

    cheekMatL.opacity = smile * 0.55;
    cheekMatR.opacity = smile * 0.55;

    scene.rotation.y = Math.sin(now * 0.0004) * 0.25;

    renderer!.render(scene, camera);
    animId = requestAnimationFrame(tick);
  }
  tick();
});

onUnmounted(() => {
  cancelAnimationFrame(animId);
  renderer?.dispose();
});
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <div class="flex-1 space-y-4">
      <div class="text-center">
        <span class="text-2xl font-bold text-foreground">{{ expressionLabel }}</span>
        <p class="text-xs text-muted-foreground mt-1">Séquence d'expressions automatique</p>
      </div>

      <div class="rounded-xl border border-border bg-[#0a0f1a] overflow-hidden" style="height:320px;">
        <canvas ref="canvasRef" class="w-full h-full" />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-xl border border-border bg-card p-3">
          <div class="flex justify-between text-xs mb-1.5">
            <span class="text-muted-foreground">Masséter (mâchoire)</span>
            <span class="font-mono text-amber-400">{{ Math.round(Math.abs(jawSignal)) }} μV</span>
          </div>
          <div class="h-2 bg-secondary rounded-full overflow-hidden">
            <div class="h-full bg-amber-400 rounded-full transition-all duration-75"
              :style="{ width: `${Math.min(100, Math.abs(jawSignal))}%` }" />
          </div>
        </div>
        <div class="rounded-xl border border-border bg-card p-3">
          <div class="flex justify-between text-xs mb-1.5">
            <span class="text-muted-foreground">Frontal (sourcils)</span>
            <span class="font-mono text-purple-400">{{ Math.round(Math.abs(browSignal)) }} μV</span>
          </div>
          <div class="h-2 bg-secondary rounded-full overflow-hidden">
            <div class="h-full bg-purple-400 rounded-full transition-all duration-75"
              :style="{ width: `${Math.min(100, Math.abs(browSignal))}%` }" />
          </div>
        </div>
        <div class="rounded-xl border border-border bg-card p-3">
          <div class="flex justify-between text-xs mb-1.5">
            <span class="text-muted-foreground">Zygomatique (sourire)</span>
            <span class="font-mono text-pink-400">{{ Math.round(Math.abs(smileSignal)) }} μV</span>
          </div>
          <div class="h-2 bg-secondary rounded-full overflow-hidden">
            <div class="h-full bg-pink-400 rounded-full transition-all duration-75"
              :style="{ width: `${Math.min(100, Math.abs(smileSignal))}%` }" />
          </div>
        </div>
        <div class="rounded-xl border border-border bg-card p-3">
          <div class="flex justify-between text-xs mb-1.5">
            <span class="text-muted-foreground">EOG (regard)</span>
            <span class="font-mono text-cyan-400">{{ Math.round(eyeSignal) }} μV</span>
          </div>
          <div class="relative h-2 bg-secondary rounded-full overflow-hidden">
            <div class="absolute top-0 bottom-0 bg-cyan-400 rounded-full transition-all duration-75"
              :style="{ left: eyeSignal < 0 ? `${50 + eyeSignal/1.2}%` : '50%', width: `${Math.abs(eyeSignal)/1.2}%` }" />
            <div class="absolute left-1/2 top-0 bottom-0 w-px bg-white/20"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="lg:w-64 space-y-4">
      <div class="rounded-xl border border-border bg-card p-4">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Placement électrodes</h3>
        <svg viewBox="0 0 120 130" class="w-full max-w-[140px] mx-auto">
          <ellipse cx="60" cy="58" rx="42" ry="50" fill="none" stroke="#475569" stroke-width="1.5"/>
          <ellipse cx="42" cy="46" rx="10" ry="6" fill="none" stroke="#475569" stroke-width="1"/>
          <ellipse cx="78" cy="46" rx="10" ry="6" fill="none" stroke="#475569" stroke-width="1"/>
          <circle cx="42" cy="46" r="3" fill="#475569"/>
          <circle cx="78" cy="46" r="3" fill="#475569"/>
          <path d="M56 66 Q60 78 64 66" fill="none" stroke="#475569" stroke-width="1"/>
          <path d="M50 88 Q60 96 70 88" fill="none" stroke="#475569" stroke-width="1"/>
          <circle cx="60" cy="38" r="5" fill="#a78bfa" stroke="#0f172a" stroke-width="1"/>
          <text x="65" y="32" font-size="5.5" fill="#a78bfa" font-family="monospace">Frontal</text>
          <circle cx="38" cy="74" r="5" fill="#f472b6" stroke="#0f172a" stroke-width="1"/>
          <text x="1" y="82" font-size="5.5" fill="#f472b6" font-family="monospace">Zygomat.</text>
          <circle cx="82" cy="74" r="5" fill="#f472b6" stroke="#0f172a" stroke-width="1"/>
          <text x="89" y="82" font-size="5.5" fill="#f472b6" font-family="monospace">Zygomat.</text>
          <circle cx="44" cy="92" r="5" fill="#fb923c" stroke="#0f172a" stroke-width="1"/>
          <text x="1" y="106" font-size="5.5" fill="#fb923c" font-family="monospace">Masséter</text>
          <circle cx="76" cy="92" r="5" fill="#fb923c" stroke="#0f172a" stroke-width="1"/>
          <text x="83" y="106" font-size="5.5" fill="#fb923c" font-family="monospace">Masséter</text>
          <circle cx="60" cy="118" r="4" fill="#22c55e" stroke="#0f172a" stroke-width="1"/>
          <text x="60" y="128" font-size="5.5" fill="#22c55e" text-anchor="middle" font-family="monospace">REF</text>
        </svg>
        <div class="mt-3 space-y-1.5 text-xs">
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-purple-400 shrink-0"></span><span class="text-muted-foreground">Frontal — Sourcils (milieu front)</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-pink-400 shrink-0"></span><span class="text-muted-foreground">Zygomatique — Pommettes (sourire)</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-orange-400 shrink-0"></span><span class="text-muted-foreground">Masséter — Mâchoire</span></div>
          <div class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-green-500 shrink-0"></span><span class="text-muted-foreground">REF — Menton</span></div>
        </div>
      </div>
      <div class="rounded-xl border border-border bg-card/50 p-4 text-xs text-muted-foreground space-y-2">
        <p class="font-medium text-foreground">EMG facial</p>
        <p>Les muscles du visage génèrent des potentiels musculaires mesurables. Le muscle zygomatique se contracte lors d'un sourire, le masséter lors de la mastication, le frontal lors des expressions de surprise.</p>
        <p>Applications : avatars animés, interfaces BCI, études de la douleur.</p>
      </div>
    </div>
  </div>
</template>
