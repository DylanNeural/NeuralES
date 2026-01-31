<template>
  <div ref="host" class="brain3d-host"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { ELECTRODES_16 } from "@/data/electrodes";

const host = ref<HTMLDivElement | null>(null);

THREE.ColorManagement.enabled = true;

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let controls: OrbitControls | null = null;
let raf = 0;
let brainGroup: THREE.Group | null = null;
let electrodes: THREE.Group | null = null;

function createBrainMesh() {
  const geo = new THREE.IcosahedronGeometry(1.05, 4);
  const mat = new THREE.MeshStandardMaterial({
    color: 0xf2f4f8,
    roughness: 0.85,
    metalness: 0.0,
    transparent: true,
    opacity: 0.85,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.scale.set(1.1, 1.0, 1.0);
  return mesh;
}

function createElectrodeGroup() {
  const group = new THREE.Group();
  const sphere = new THREE.SphereGeometry(0.045, 16, 16);
  ELECTRODES_16.forEach((e, i) => {
    const hue = (i / Math.max(1, ELECTRODES_16.length)) * 300;
    const mat = new THREE.MeshBasicMaterial({ color: new THREE.Color(`hsl(${hue}, 70%, 50%)`) });
    const mesh = new THREE.Mesh(sphere, mat);
    mesh.position.set(e.x, e.y, e.z);
    group.add(mesh);
  });
  return group;
}

function projectElectrodesToBrain(target: THREE.Object3D) {
  if (!electrodes) return;
  const raycaster = new THREE.Raycaster();
  const meshes: THREE.Object3D[] = [];
  target.traverse((obj) => {
    if ((obj as THREE.Mesh).isMesh) meshes.push(obj);
  });

  ELECTRODES_16.forEach((e, i) => {
    const dir = new THREE.Vector3(e.x, e.y, e.z).normalize();
    const origin = dir.clone().multiplyScalar(5);
    raycaster.set(origin, dir.clone().multiplyScalar(-1));
    const hits = raycaster.intersectObjects(meshes, true);
    const hit = hits[0];
    const node = electrodes!.children[i] as THREE.Mesh | undefined;
    if (!node) return;
    if (hit) node.position.copy(hit.point);
    else node.position.copy(dir.multiplyScalar(1.05));
  });
}

function setupScene(el: HTMLDivElement) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color("#F8F9FB");

  camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  camera.position.set(0, 0.2, 3.2);

  const ambient = new THREE.AmbientLight(0xffffff, 0.9);
  const hemi = new THREE.HemisphereLight(0xffffff, 0x9aa5b1, 0.8);
  const key = new THREE.DirectionalLight(0xffffff, 1.2);
  key.position.set(2, 3, 4);
  const rim = new THREE.DirectionalLight(0xffffff, 0.6);
  rim.position.set(-3, -2, -4);

  scene.add(ambient, hemi, key, rim);
  brainGroup = new THREE.Group();
  scene.add(brainGroup);
  electrodes = createElectrodeGroup();
  scene.add(electrodes);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.3;
  renderer.physicallyCorrectLights = false;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(el.clientWidth, el.clientHeight, false);
  el.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minDistance = 2.0;
  controls.maxDistance = 6.0;

  const onResize = () => {
    if (!renderer || !camera) return;
    const w = el.clientWidth;
    const h = el.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  };
  window.addEventListener("resize", onResize);

  const loader = new GLTFLoader();
  loader.load(
    "/brain.glb",
    (gltf) => {
      const model = gltf.scene;
      model.traverse((obj) => {
        if ((obj as THREE.Mesh).isMesh) {
          const mesh = obj as THREE.Mesh;
          const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
          mats.forEach((m) => {
            const mat = m as THREE.MeshStandardMaterial;
            if (mat.map) {
              mat.map.colorSpace = THREE.SRGBColorSpace;
              mat.needsUpdate = true;
            }
          });
          mesh.castShadow = false;
          mesh.receiveShadow = false;
        }
      });
      const box = new THREE.Box3().setFromObject(model);
      const size = new THREE.Vector3();
      box.getSize(size);
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      const scale = 2.3 / maxDim;
      model.scale.setScalar(scale);
      box.setFromObject(model);
      const center = new THREE.Vector3();
      box.getCenter(center);
      model.position.sub(center);
      model.position.y -= 0.1;
      brainGroup?.clear();
      brainGroup?.add(model);
      projectElectrodesToBrain(model);
    },
    undefined,
    () => {
      const fallback = createBrainMesh();
      brainGroup?.clear();
      brainGroup?.add(fallback);
      projectElectrodesToBrain(fallback);
    }
  );

  const animate = (t: number) => {
    raf = requestAnimationFrame(animate);
    if (brainGroup) {
      brainGroup.rotation.y = t * 0.00015;
      brainGroup.rotation.x = Math.sin(t * 0.0001) * 0.08;
    }
    if (electrodes && brainGroup) {
      electrodes.rotation.copy(brainGroup.rotation);
    }
    controls?.update();
    renderer?.render(scene!, camera!);
  };

  animate(0);

  return () => {
    window.removeEventListener("resize", onResize);
  };
}

onMounted(() => {
  if (!host.value) return;
  const cleanup = setupScene(host.value);
  onBeforeUnmount(() => {
    cancelAnimationFrame(raf);
    cleanup?.();
    if (renderer) {
      renderer.dispose();
      renderer.domElement.remove();
    }
    controls?.dispose();
    renderer = null;
    scene = null;
    camera = null;
    controls = null;
    electrodes = null;
  });
});
</script>

<style scoped>
.brain3d-host {
  width: 100%;
  height: 360px;
  border-radius: 24px;
  overflow: hidden;
  background: #f8f9fb;
  box-shadow: inset 0 0 0 1px rgba(141, 153, 174, 0.25);
}
</style>
