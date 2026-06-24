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
const showPassword = ref(false);

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

<template>
  <div class="w-full max-w-sm animate-fade-in">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-2 mb-6 lg:hidden">
        <div class="h-8 w-8 rounded-lg bg-primary/20 ring-1 ring-primary/40 flex items-center justify-center">
          <svg class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <span class="text-sm font-bold text-foreground">NeuralES</span>
      </div>
      <h1 class="text-2xl font-bold text-foreground mb-1">Connexion</h1>
      <p class="text-sm text-muted-foreground">Accède à la plateforme clinique EEG.</p>
    </div>

    <!-- Error alert -->
    <div
      v-if="error"
      class="mb-5 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <svg class="h-4 w-4 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {{ error }}
    </div>

    <!-- Form -->
    <form class="space-y-4" @submit.prevent="onSubmit">
      <!-- Email -->
      <div class="space-y-1.5">
        <label class="block text-sm font-medium text-foreground" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          autocomplete="email"
          class="flex h-9 w-full rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 focus:ring-offset-background transition-colors"
          placeholder="admin@neurales.com"
        />
      </div>

      <!-- Password -->
      <div class="space-y-1.5">
        <label class="block text-sm font-medium text-foreground" for="password">Mot de passe</label>
        <div class="relative">
          <input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            required
            autocomplete="current-password"
            class="flex h-9 w-full rounded-lg border border-border bg-secondary/30 px-3 py-2 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 focus:ring-offset-background transition-colors"
            placeholder="••••••••"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            @click="showPassword = !showPassword"
          >
            <svg v-if="!showPassword" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Submit -->
      <button
        type="submit"
        :disabled="loading"
        class="w-full h-9 flex items-center justify-center gap-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:opacity-50 disabled:pointer-events-none transition-all shadow-sm mt-2"
      >
        <svg v-if="loading" class="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        {{ loading ? "Connexion..." : "Se connecter" }}
      </button>
    </form>

    <p class="mt-8 text-center text-xs text-muted-foreground">
      Plateforme réservée au personnel médical autorisé.
    </p>
  </div>
</template>
