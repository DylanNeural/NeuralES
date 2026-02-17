<template>
  <div ref="host" class="helmet-viewer" />
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

interface Props {
  modelPath?: string;
  showAxes?: boolean;
  enableAnimation?: boolean;
  animationSpeed?: number;
  helmetColor?: number;
  activeElectrodeColor?: number;
  inactiveElectrodeColor?: number;
  showLabels?: boolean;
  enableInteraction?: boolean;
  cameraPosition?: { x: number; y: number; z: number };
  modelOffset?: { x: number; y: number; z: number };
}

const props = withDefaults(defineProps<Props>(), {
  modelPath: "/casque_brain_electrodes.glb",
  showAxes: false,
  enableAnimation: true,
  animationSpeed: 0.002,
  helmetColor: 0x4b6bff,
  activeElectrodeColor: 0x00d97e,
  inactiveElectrodeColor: 0xffc857,
  showLabels: true,
  enableInteraction: true,
  cameraPosition: () => ({ x: 0, y: 0.2, z: 250 }),
  modelOffset: () => ({ x: 0, y: -50, z: 0 })
});

const emit = defineEmits<{
  electrodeClick: [name: string, active: boolean];
  modelLoaded: [];
  animationComplete: [];
}>();

const host = ref<HTMLDivElement | null>(null);

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let controls: OrbitControls | null = null;
let raf = 0;
const activeElectrodes = new Set<string>();
const electrodeMaterials = new Map<string, { active: THREE.Material | THREE.Material[]; inactive: THREE.Material | THREE.Material[] }>();
const electrodePositions = new Map<string, { start: THREE.Vector3; end: THREE.Vector3; object: THREE.Object3D; delay: number; initialRotation: { x: number; y: number; z: number }; orbitalAngle: number }>();
let assemblyProgress = 0;
let isAssembling = true;
let electrodeIndex = 0;

function setupScene(el: HTMLDivElement) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0d12);

  if (props.showAxes) {
    const axesHelper = new THREE.AxesHelper(100);
    scene.add(axesHelper);
  }

  camera = new THREE.PerspectiveCamera(50, el.clientWidth / el.clientHeight, 0.1, 1000);
  camera.position.set(props.cameraPosition.x, props.cameraPosition.y, props.cameraPosition.z);

  const ambient = new THREE.AmbientLight(0xffffff, 0.9);
  const key = new THREE.DirectionalLight(0xffffff, 1.1);
  key.position.set(3, 4, 5);
  scene.add(ambient, key);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(el.clientWidth, el.clientHeight);
  el.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.enableRotate = true;
  controls.enableZoom = true;
  controls.minDistance = 0.5;
  controls.maxDistance = 500;

  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  const loader = new GLTFLoader();
  loader.load(
    props.modelPath,
    (gltf) => {
      const root = gltf.scene;
      root.position.set(props.modelOffset.x, props.modelOffset.y, props.modelOffset.z);
      scene?.add(root);
      
      const helmetMat = new THREE.MeshStandardMaterial({ 
        color: props.helmetColor, 
        metalness: 0.4, 
        roughness: 0.35 
      });
      const electrodeMat = new THREE.MeshStandardMaterial({ 
        color: props.activeElectrodeColor, 
        metalness: 0.2, 
        roughness: 0.4 
      });

      const createLabelTexture = (text: string) => {
        const canvas = document.createElement("canvas");
        canvas.width = 256;
        canvas.height = 128;
        const ctx = canvas.getContext("2d");
        if (!ctx) return null;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 48px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        return new THREE.CanvasTexture(canvas);
      };

      const cloneMaterial = (mat: THREE.Material | THREE.Material[]) => {
        if (Array.isArray(mat)) {
          return mat.map((m) => m.clone());
        }
        return mat.clone();
      };

      root.traverse((obj) => {
        if ((obj as THREE.Mesh).isMesh) {
          const mesh = obj as THREE.Mesh;
          const name = mesh.name || "";

          if (name === "Casque") {
            mesh.material = helmetMat;
          } else if (name.startsWith("Electrode_")) {
            const inactiveMat = cloneMaterial(mesh.material as THREE.Material);
            const activeMat = cloneMaterial(electrodeMat);
            electrodeMaterials.set(name, { active: activeMat, inactive: inactiveMat });
            mesh.material = inactiveMat as any;

            if (props.enableAnimation) {
              // Store initial and final positions for assembly animation
              const endPos = mesh.position.clone();
              const direction = endPos.clone().normalize();
              const startPos = direction.multiplyScalar(-200);
              
              const orbitalAngle = Math.atan2(endPos.z, endPos.x);
              
              electrodePositions.set(name, {
                start: startPos,
                end: endPos,
                object: mesh,
                delay: electrodeIndex * 0.05,
                initialRotation: { x: mesh.rotation.x, y: mesh.rotation.y, z: mesh.rotation.z },
                orbitalAngle: orbitalAngle
              });
              
              mesh.position.copy(startPos);
              electrodeIndex++;
            }

            if (props.showLabels) {
              const label = name.replace("Electrode_", "");
              const texture = createLabelTexture(label);
              if (texture) {
                const labelBox = new THREE.Box3().setFromObject(mesh);
                const labelSize = labelBox.getSize(new THREE.Vector3());
                const maxSize = Math.max(labelSize.x, labelSize.y, labelSize.z);

                const sprite = new THREE.Sprite(
                  new THREE.SpriteMaterial({ map: texture, depthTest: false, depthWrite: false })
                );
                sprite.renderOrder = 999;
                sprite.position.set(0, maxSize * 0.6, 0);
                sprite.scale.set(maxSize * 0.8, maxSize * 0.4, 1);
                mesh.add(sprite);
              }
            }
          }
        }
      });
      
      emit('modelLoaded');
    },
    undefined,
    (error) => {
      console.error("[HelmetViewer3D] Failed to load GLB:", error);
    }
  );

  const onResize = () => {
    if (!renderer || !camera) return;
    const w = el.clientWidth;
    const h = el.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };
  window.addEventListener("resize", onResize);

  const onClick = (event: MouseEvent) => {
    if (!props.enableInteraction || !camera || !scene) return;
    const rect = el.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(scene.children, true);

    for (const hit of hits) {
      const mesh = hit.object as THREE.Mesh;
      const name = mesh.name || "";
      if (name.startsWith("Electrode_")) {
        if (activeElectrodes.has(name)) {
          activeElectrodes.delete(name);
        } else {
          activeElectrodes.add(name);
        }

        const mats = electrodeMaterials.get(name);
        if (mats) {
          mesh.material = activeElectrodes.has(name) ? (mats.active as any) : (mats.inactive as any);
        }
        
        emit('electrodeClick', name, activeElectrodes.has(name));
        break;
      }
    }
  };

  const onMouseMove = (event: MouseEvent) => {
    if (!props.enableInteraction || !camera || !scene) return;
    const rect = el.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(scene.children, true);
    const hoveringElectrode = hits.some((hit) => (hit.object as THREE.Mesh).name?.startsWith("Electrode_"));
    el.style.cursor = hoveringElectrode ? "pointer" : "default";
  };

  if (props.enableInteraction) {
    el.addEventListener("click", onClick);
    el.addEventListener("mousemove", onMouseMove);
  }

  const animate = () => {
    raf = requestAnimationFrame(animate);
    
    // Update assembly animation
    if (props.enableAnimation && isAssembling && assemblyProgress < 1) {
      assemblyProgress += props.animationSpeed;
      if (assemblyProgress >= 1) {
        assemblyProgress = 1;
        isAssembling = false;
        emit('animationComplete');
      }
      
      electrodePositions.forEach((pos) => {
        const delayedProgress = Math.max(0, assemblyProgress - pos.delay);
        if (delayedProgress <= 0) return;
        
        let electrodeProgress = delayedProgress / (1 - pos.delay);
        electrodeProgress = Math.min(1, electrodeProgress);
        
        const easedProgress = 1 - Math.pow(1 - electrodeProgress, 3);
        
        if (easedProgress >= 0.95) {
          pos.object.position.copy(pos.end);
        } else {
          const orbitalRotation = easedProgress * Math.PI * 2;
          const radius = pos.end.length();
          const spiralRadius = radius + (200 - radius) * (1 - easedProgress);
          
          const orbitalX = Math.cos(pos.orbitalAngle + orbitalRotation) * spiralRadius;
          const orbitalY = pos.end.y + (pos.start.y - pos.end.y) * (1 - easedProgress);
          const orbitalZ = Math.sin(pos.orbitalAngle + orbitalRotation) * spiralRadius;
          
          pos.object.position.set(orbitalX, orbitalY, orbitalZ);
        }
        
        const mesh = pos.object as THREE.Mesh;
        mesh.rotation.x = pos.initialRotation.x;
        mesh.rotation.y = pos.initialRotation.y;
        mesh.rotation.z = pos.initialRotation.z;
      });
    }
    
    controls?.update();
    renderer?.render(scene!, camera!);
  };
  animate();

  return () => {
    window.removeEventListener("resize", onResize);
    if (props.enableInteraction) {
      el.removeEventListener("click", onClick);
      el.removeEventListener("mousemove", onMouseMove);
    }
    cancelAnimationFrame(raf);
    controls?.dispose();
  };
}

onMounted(() => {
  if (!host.value) return;
  const cleanup = setupScene(host.value);
  onBeforeUnmount(() => {
    cleanup();
    renderer?.dispose();
  });
});

// Expose methods for parent component
defineExpose({
  resetAnimation: () => {
    assemblyProgress = 0;
    isAssembling = true;
  },
  getActiveElectrodes: () => Array.from(activeElectrodes),
  clearActiveElectrodes: () => {
    activeElectrodes.clear();
    electrodeMaterials.forEach((mats, name) => {
      const mesh = electrodePositions.get(name)?.object as THREE.Mesh;
      if (mesh) {
        mesh.material = mats.inactive as any;
      }
    });
  }
});
</script>

<style scoped>
.helmet-viewer {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  border: none;
  background: #0b0d12;
}
</style>
