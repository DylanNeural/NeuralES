<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Contrôle -->
      <section class="card p-5 lg:col-span-2">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-lg font-semibold">Contrôle acquisition</h2>
            <p class="text-sm text-slate-600 mt-1">
              Démarre/stoppe une session et récupère les métriques en temps réel.
            </p>
          </div>

          <div class="text-right">
            <div class="text-xs text-slate-500">Session</div>
            <div class="font-mono text-sm">{{ sessionId ?? "—" }}</div>
          </div>
        </div>

        <div class="mt-5 flex flex-wrap gap-2">
          <button class="btn btn-primary" :disabled="running" @click="start">Démarrer</button>
          <button class="btn btn-danger" :disabled="!running" @click="stop">Stop</button>
          <button class="btn" :disabled="!sessionId" @click="goToResults">Voir résultats</button>
        </div>
        <p v-if="liveError" class="text-sm text-red-600 mt-3">{{ liveError }}</p>

        <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="card p-4">
            <div class="text-xs text-slate-500">Qualité signal</div>
            <div class="text-2xl font-semibold mt-1">{{ live?.quality ?? 0 }}%</div>
          </div>
          <div class="card p-4">
            <div class="text-xs text-slate-500">Dernière maj</div>
            <div class="text-2xl font-semibold mt-1">{{ liveTime }}</div>
          </div>
          <div class="card p-4">
            <div class="text-xs text-slate-500">Statut</div>
            <div class="text-2xl font-semibold mt-1">
              {{ running ? "En cours" : "Arrêt" }}
            </div>
          </div>
        </div>
      </section>

      <!-- Score -->
      <aside class="card p-5">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs text-slate-500">Score fatigue</div>
            <div class="text-4xl font-semibold mt-1">
              {{ Math.round((live?.fatigue_score ?? 0) * 100) }}<span class="text-base text-slate-500">/100</span>
            </div>
          </div>
          <div class="h-12 w-12 rounded-2xl bg-slate-900 text-white grid place-items-center text-sm">
            F
          </div>
        </div>

        <div class="mt-4">
          <div class="text-xs text-slate-500 mb-2">Interprétation</div>
          <div class="text-sm font-medium">{{ fatigueLabel }}</div>
          <p class="text-sm text-slate-600 mt-1">
            (à ajuster selon ton modèle : plus haut = plus fatigué ou inverse)
          </p>
        </div>
      </aside>
    </div>

    <section class="card p-5">
      <EEGChartCanvas />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import { useRouter } from "vue-router";
import * as AcqAPI from "@/api/acquisition.api";
import EEGChartCanvas from "@/components/EEGChartCanvas.vue";

const router = useRouter();
const sessionId = ref<string | null>(null);
const running = ref(false);
const live = ref<{ fatigue_score: number; quality: number } | null>(null);
const lastTick = ref<number | null>(null);
const liveError = ref<string | null>(null);

let timer: number | null = null;

const liveTime = computed(() => {
  if (!lastTick.value) return "—";
  const d = new Date(lastTick.value);
  return d.toLocaleTimeString();
});

const fatigueLabel = computed(() => {
  const v = live.value?.fatigue_score ?? 0;
  if (v < 25) return "Faible";
  if (v < 50) return "Modéré";
  if (v < 75) return "Élevé";
  return "Très élevé";
});

async function start() {
  liveError.value = null;
  const res = await AcqAPI.startAcquisition();
  sessionId.value = res.session_id;
  running.value = true;

  timer = window.setInterval(async () => {
    if (!sessionId.value) return;
    try {
      const data = await AcqAPI.getLive(sessionId.value);
      live.value = { fatigue_score: data.fatigue_score, quality: data.quality };
      lastTick.value = Date.now();
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 404) {
        liveError.value = "Session expirée. Clique sur Démarrer pour relancer.";
        running.value = false;
        sessionId.value = null;
        if (timer) window.clearInterval(timer);
        timer = null;
      }
    }
  }, 1000);
}

async function stop() {
  if (!sessionId.value) return;
  await AcqAPI.stopAcquisition(sessionId.value);
  running.value = false;
  liveError.value = null;
  if (timer) window.clearInterval(timer);
  timer = null;
}

function goToResults() {
  router.push("/results");
}

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});
</script>
