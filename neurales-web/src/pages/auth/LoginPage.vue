<template>
  <div class="min-h-screen grid lg:grid-cols-2 bg-white">
    <!-- Brand panel -->
    <div
      class="hidden lg:flex flex-col justify-between p-12 relative overflow-hidden"
      style="background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 60%, #312E81 100%);"
    >
      <!-- Glow orb -->
      <div
        class="absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-20 blur-3xl"
        style="background: radial-gradient(circle, #6366F1, transparent);"
      ></div>
      <div
        class="absolute bottom-16 right-16 w-72 h-72 rounded-full opacity-15 blur-3xl"
        style="background: radial-gradient(circle, #818CF8, transparent);"
      ></div>

      <!-- Logo -->
      <div class="relative flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-primary/80 border border-primary-ring/20 flex items-center justify-center shadow-elevated">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <span class="text-xl font-bold text-white tracking-tight">NeuralES</span>
      </div>

      <!-- Tagline -->
      <div class="relative">
        <h2 class="text-4xl font-bold text-white leading-tight mb-4">
          Analyse EEG<br />de nouvelle<br />génération.
        </h2>
        <p class="text-slate-400 text-base leading-relaxed max-w-xs">
          Acquisition, traitement et analyse des signaux électroencéphalographiques
          pour les professionnels de santé.
        </p>

        <!-- Feature bullets -->
        <div class="mt-8 space-y-3">
          <div v-for="feature in features" :key="feature" class="flex items-center gap-3">
            <div class="h-5 w-5 rounded-full bg-primary/30 border border-primary-ring/30 flex items-center justify-center shrink-0">
              <svg class="w-3 h-3 text-primary-ring" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <span class="text-slate-400 text-sm">{{ feature }}</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <p class="relative text-xs text-slate-600">
        © 2025 NeuralES — Plateforme médicale EEG
      </p>
    </div>

    <!-- Form panel -->
    <div class="flex flex-col items-center justify-center px-8 py-16 bg-background">
      <div class="w-full max-w-sm">
        <!-- Mobile logo -->
        <div class="flex items-center gap-2 mb-10 lg:hidden">
          <div class="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <span class="text-lg font-bold text-slate-900">NeuralES</span>
        </div>

        <div class="mb-8">
          <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Connexion</h1>
          <p class="text-slate-500 text-sm mt-2">
            Accède à l'interface d'acquisition et d'analyse EEG.
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="onSubmit">
          <div class="form-group">
            <label class="label" for="email">Adresse email</label>
            <input
              id="email"
              class="input"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="admin@neurales.com"
              required
            />
          </div>

          <div class="form-group">
            <label class="label" for="password">Mot de passe</label>
            <input
              id="password"
              class="input"
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              required
            />
          </div>

          <div
            v-if="error"
            class="flex items-center gap-3 rounded-xl bg-red-50 border border-red-200 px-4 py-3"
          >
            <svg class="w-4 h-4 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>

          <button
            class="btn btn-primary w-full py-2.5"
            type="submit"
            :disabled="loading"
          >
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ loading ? "Connexion..." : "Se connecter" }}
          </button>
        </form>

        <p class="mt-8 text-center text-xs text-slate-400">
          Accès réservé aux professionnels de santé autorisés.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = useRouter();
const auth = useAuthStore();

const email = ref("admin@neurales.com");
const password = ref("admin123");
const loading = ref(false);
const error = ref<string | null>(null);

const features = [
  "Streaming EEG temps réel 16 canaux",
  "Analyse de fatigue cognitive et motrice",
  "Gestion multi-patients sécurisée",
  "Compatible Tauri desktop & Web",
];

async function onSubmit() {
  error.value = null;
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    router.push("/acquisition");
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail ??
      e?.message ??
      (typeof e === "string" ? e : null) ??
      "Identifiants invalides.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
