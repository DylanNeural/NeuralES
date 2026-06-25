<template>
  <div ref="host" class="waterfall-viewport" />
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { useAcquisitionStore } from "@/stores/acquisition.store";

const props = withDefaults(defineProps<{ isActive?: boolean }>(), { isActive: false });

const host = ref<HTMLDivElement | null>(null);
const acquisition = useAcquisitionStore();

const FREQ_BINS = 64;
const TIME_ROWS = 50;
const NFFT = 256;

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let controls: OrbitControls | null = null;
let raf = 0;
let posAttr: THREE.BufferAttribute | null = null;
let colorAttr: THREE.BufferAttribute | null = null;

const powerHistory: Float32Array[] = Array.from({ length: TIME_ROWS }, () => new Float32Array(FREQ_BINS));
const sampleBuffer: number[] = [];
let currentSfreq = 250;

function fft(re: Float32Array, im: Float32Array) {
  const N = re.length;
  for (let i = 1, j = 0; i < N; i++) {
    let bit = N >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) {
      let t = re[i]!; re[i] = re[j]!; re[j] = t;
      t = im[i]!; im[i] = im[j]!; im[j] = t;
    }
  }
  for (let len = 2; len <= N; len <<= 1) {
    const ang = -2 * Math.PI / len;
    const wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < N; i += len) {
      let cr = 1, ci = 0;
      for (let j = 0; j < (len >> 1); j++) {
        const ur = re[i + j]!; const ui = im[i + j]!;
        const vr = re[i + j + (len >> 1)]! * cr - im[i + j + (len >> 1)]! * ci;
        const vi = re[i + j + (len >> 1)]! * ci + im[i + j + (len >> 1)]! * cr;
        re[i + j] = ur + vr; im[i + j] = ui + vi;
        re[i + j + (len >> 1)] = ur - vr; im[i + j + (len >> 1)] = ui - vi;
        const nr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nr;
      }
    }
  }
}

function computeSpectrum(): Float32Array {
  const slice = sampleBuffer.slice(-NFFT);
  const re = new Float32Array(NFFT);
  const im = new Float32Array(NFFT);
  for (let i = 0; i < slice.length; i++) {
    const w = 0.5 * (1 - Math.cos(2 * Math.PI * i / (NFFT - 1)));
    re[i] = (slice[i] ?? 0) * w;
  }
  fft(re, im);
  const maxBin = Math.min(NFFT >> 1, Math.floor(40 * NFFT / currentSfreq));
  const out = new Float32Array(FREQ_BINS);
  for (let i = 0; i < FREQ_BINS; i++) {
    const bin = Math.round(i * maxBin / (FREQ_BINS - 1));
    out[i] = Math.sqrt(re[bin]! ** 2 + im[bin]! ** 2) / NFFT;
  }
  return out;
}

// Jet colormap: dark blue → cyan → green → yellow → red
function jetColor(t: number): [number, number, number] {
  t = Math.max(0, Math.min(1, t));
  if (t < 0.25) { const s = t / 0.25; return [0, s, 1]; }
  if (t < 0.5)  { const s = (t - 0.25) / 0.25; return [0, 1, 1 - s]; }
  if (t < 0.75) { const s = (t - 0.5) / 0.25; return [s, 1, 0]; }
  const s = (t - 0.75) / 0.25; return [1, 1 - s, 0];
}

function pushSpectrum(spec: Float32Array) {
  for (let t = TIME_ROWS - 1; t > 0; t--) powerHistory[t]!.set(powerHistory[t - 1]!);
  powerHistory[0]!.set(spec);
  updateGeometry();
}

function updateGeometry() {
  if (!posAttr || !colorAttr) return;
  const pos = posAttr.array as Float32Array;
  const col = colorAttr.array as Float32Array;

  let maxPow = 1e-12;
  for (let t = 0; t < TIME_ROWS; t++)
    for (let f = 0; f < FREQ_BINS; f++)
      if ((powerHistory[t]![f] ?? 0) > maxPow) maxPow = powerHistory[t]![f] ?? 0;

  for (let t = 0; t < TIME_ROWS; t++) {
    for (let f = 0; f < FREQ_BINS; f++) {
      const vi = t * FREQ_BINS + f;
      const norm = (powerHistory[t]![f] ?? 0) / maxPow;
      pos[vi * 3 + 1] = norm * 28;
      const [r, g, b] = jetColor(norm);
      col[vi * 3] = r; col[vi * 3 + 1] = g; col[vi * 3 + 2] = b;
    }
  }
  posAttr.needsUpdate = true;
  colorAttr.needsUpdate = true;
}

function makeLabel(text: string): THREE.Sprite {
  const canvas = document.createElement("canvas");
  canvas.width = 256; canvas.height = 64;
  const ctx = canvas.getContext("2d")!;
  ctx.fillStyle = "#64748b";
  ctx.font = "bold 28px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 128, 32);
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas), transparent: true, depthTest: false })
  );
  sprite.scale.set(14, 3.5, 1);
  return sprite;
}

function setupScene(el: HTMLDivElement) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07090f);

  camera = new THREE.PerspectiveCamera(48, el.clientWidth / el.clientHeight, 0.1, 1000);
  camera.position.set(0, 55, 100);
  camera.lookAt(0, 8, -25);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(el.clientWidth, el.clientHeight);
  el.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.target.set(0, 8, -25);
  controls.enablePan = false;
  controls.minDistance = 30;
  controls.maxDistance = 250;

  // Waterfall geometry
  const W = 100, D = 75;
  const verts = new Float32Array(TIME_ROWS * FREQ_BINS * 3);
  const cols = new Float32Array(TIME_ROWS * FREQ_BINS * 3);
  const idxs: number[] = [];

  for (let t = 0; t < TIME_ROWS; t++) {
    for (let f = 0; f < FREQ_BINS; f++) {
      const vi = t * FREQ_BINS + f;
      verts[vi * 3]     = (f / (FREQ_BINS - 1)) * W - W / 2;
      verts[vi * 3 + 1] = 0;
      verts[vi * 3 + 2] = -(t / (TIME_ROWS - 1)) * D;
      cols[vi * 3] = 0.05; cols[vi * 3 + 1] = 0.1; cols[vi * 3 + 2] = 0.25;
    }
  }
  for (let t = 0; t < TIME_ROWS - 1; t++) {
    for (let f = 0; f < FREQ_BINS - 1; f++) {
      const a = t * FREQ_BINS + f, b = a + 1, c = a + FREQ_BINS, d = c + 1;
      idxs.push(a, b, c, b, d, c);
    }
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute("position", new THREE.BufferAttribute(verts, 3));
  geom.setAttribute("color", new THREE.BufferAttribute(cols, 3));
  geom.setIndex(idxs);
  posAttr = geom.getAttribute("position") as THREE.BufferAttribute;
  colorAttr = geom.getAttribute("color") as THREE.BufferAttribute;

  scene.add(new THREE.Mesh(geom, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide })));

  // Floor grid
  const grid = new THREE.GridHelper(120, 12, 0x1a2535, 0x131d2b);
  grid.position.set(0, -0.5, -37);
  scene.add(grid);

  // Frequency band markers
  const bands = [
    { hz: 0, label: "0 Hz" },
    { hz: 4, label: "δ 4" },
    { hz: 8, label: "θ 8" },
    { hz: 13, label: "α 13" },
    { hz: 30, label: "β 30" },
    { hz: 40, label: "40 Hz" },
  ];
  bands.forEach(({ hz, label }) => {
    const x = (hz / 40) * W - W / 2;
    const lineGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(x, -0.5, 0),
      new THREE.Vector3(x, -0.5, -D),
    ]);
    scene!.add(new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ color: 0x1e2d40 })));
    const lbl = makeLabel(label);
    lbl.position.set(x, -3.5, 5);
    scene!.add(lbl);
  });

  const animate = () => {
    raf = requestAnimationFrame(animate);
    controls?.update();
    renderer?.render(scene!, camera!);
  };
  animate();

  const onResize = () => {
    if (!renderer || !camera) return;
    camera.aspect = el.clientWidth / el.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(el.clientWidth, el.clientHeight);
  };
  window.addEventListener("resize", onResize);

  return () => {
    window.removeEventListener("resize", onResize);
    cancelAnimationFrame(raf);
    controls?.dispose();
    renderer?.dispose();
  };
}

watch(() => acquisition.streamMessageSeq, () => {
  if (!props.isActive) return;
  const payload = acquisition.latestStreamChunk;
  if (!payload) return;
  currentSfreq = Number(payload.sfreq || 0) || 250;
  const samples = Array.isArray(payload.samples) ? payload.samples : [];
  const ch0 = Array.isArray(samples[0]) ? (samples[0] as number[]) : [];
  for (const s of ch0) sampleBuffer.push(Number(s) || 0);
  if (sampleBuffer.length > NFFT * 8) sampleBuffer.splice(0, sampleBuffer.length - NFFT * 4);
  if (sampleBuffer.length >= NFFT) pushSpectrum(computeSpectrum());
});

watch(() => props.isActive, (active) => {
  if (!active) {
    powerHistory.forEach((r) => r.fill(0));
    sampleBuffer.length = 0;
    updateGeometry();
  }
});

onMounted(() => {
  if (!host.value) return;
  const cleanup = setupScene(host.value);
  onBeforeUnmount(cleanup);
});
</script>

<style scoped>
.waterfall-viewport {
  width: 100%;
  height: 100%;
}
</style>
