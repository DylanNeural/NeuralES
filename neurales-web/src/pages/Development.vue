<template>
  <div ref="host" class="dev-viewport" />
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const host = ref<HTMLDivElement | null>(null);

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let controls: OrbitControls | null = null;
let raf = 0;
const activeElectrodes = new Set<string>();
const electrodeMaterials = new Map<string, { active: THREE.Material | THREE.Material[]; inactive: THREE.Material | THREE.Material[] }>();
let loggedElectrodeSize = false;
const electrodePositions = new Map<string, { start: THREE.Vector3; end: THREE.Vector3; object: THREE.Object3D; delay: number; initialRotation: { x: number; y: number; z: number }; orbitalAngle: number }>();
let assemblyProgress = 0;
let isAssembling = true;
let electrodeIndex = 0;

function setupScene(el: HTMLDivElement) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0d12);

  // Add axes helper for reference
  const axesHelper = new THREE.AxesHelper(100);
  scene.add(axesHelper);

  camera = new THREE.PerspectiveCamera(50, el.clientWidth / el.clientHeight, 0.1, 1000);
  camera.position.set(0, 0.2, 250);

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
    "/casque_brain_electrodes.glb",
    (gltf) => {
      const root = gltf.scene;
      root.position.y -= 50;
      scene?.add(root);
      const helmetMat = new THREE.MeshStandardMaterial({ color: 0x4b6bff, metalness: 0.4, roughness: 0.35 });
      const electrodeMat = new THREE.MeshStandardMaterial({ color: 0x00d97e, metalness: 0.2, roughness: 0.4 });

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

            // Store initial and final positions for assembly animation
            const endPos = mesh.position.clone();
            const direction = endPos.clone().normalize();
            const startPos = direction.multiplyScalar(-200); // Start far away
            
            // Calculate orbital angle for this electrode
            const orbitalAngle = Math.atan2(endPos.z, endPos.x);
            
            electrodePositions.set(name, {
              start: startPos,
              end: endPos,
              object: mesh,
              delay: electrodeIndex * 0.05, // Stagger delay
              initialRotation: { x: mesh.rotation.x, y: mesh.rotation.y, z: mesh.rotation.z },
              orbitalAngle: orbitalAngle
            });
            
            // Set initial position
            mesh.position.copy(startPos);
            
            electrodeIndex++;

            if (!loggedElectrodeSize) {
              const box = new THREE.Box3().setFromObject(mesh);
              const size = box.getSize(new THREE.Vector3());
              console.log("[Dev] Electrode size:", name, size);
              loggedElectrodeSize = true;
            }

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
      });
    },
    undefined,
    (error) => {
      console.error("[Dev] Failed to load GLB:", error);
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
    if (!camera || !scene) return;
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
        break;
      }
    }
  };

  const onMouseMove = (event: MouseEvent) => {
    if (!camera || !scene) return;
    const rect = el.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(scene.children, true);
    const hoveringElectrode = hits.some((hit) => (hit.object as THREE.Mesh).name?.startsWith("Electrode_"));
    el.style.cursor = hoveringElectrode ? "pointer" : "default";
  };

  el.addEventListener("click", onClick);
  el.addEventListener("mousemove", onMouseMove);

  const animate = () => {
    raf = requestAnimationFrame(animate);
    
    // Update assembly animation
    if (isAssembling && assemblyProgress < 1) {
      assemblyProgress += 0.002; // Adjust speed here
      if (assemblyProgress >= 1) {
        assemblyProgress = 1;
        isAssembling = false;
      }
      
      electrodePositions.forEach((pos) => {
        // Apply stagger delay
        const delayedProgress = Math.max(0, assemblyProgress - pos.delay);
        if (delayedProgress <= 0) return;
        
        // Normalize progress to 0-1 for this electrode
        let electrodeProgress = delayedProgress / (1 - pos.delay);
        electrodeProgress = Math.min(1, electrodeProgress);
        
        // Apply easing function (ease-out cubic)
        const easedProgress = 1 - Math.pow(1 - electrodeProgress, 3);
        
        if (easedProgress >= 0.95) {
          // Last 5% - snap to final position to ensure accuracy
          pos.object.position.copy(pos.end);
        } else {
          // Create orbital path - electrodes spiral around the helmet
          const orbitalRotation = easedProgress * Math.PI * 2; // One full rotation
          const radius = pos.end.length(); // Distance from origin
          const spiralRadius = radius + (200 - radius) * (1 - easedProgress); // Shrink from start to end
          
          const orbitalX = Math.cos(pos.orbitalAngle + orbitalRotation) * spiralRadius;
          const orbitalY = pos.end.y + (pos.start.y - pos.end.y) * (1 - easedProgress);
          const orbitalZ = Math.sin(pos.orbitalAngle + orbitalRotation) * spiralRadius;
          
          pos.object.position.set(orbitalX, orbitalY, orbitalZ);
        }
        
        // Rotation back to original
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
    el.removeEventListener("click", onClick);
    el.removeEventListener("mousemove", onMouseMove);
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
</script>

<style scoped>
.dev-viewport {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  border: none;
  background: #0b0d12;
}
</style>
