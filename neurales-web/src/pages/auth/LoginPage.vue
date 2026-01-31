<template>
  <div class="min-h-screen grid place-items-center bg-slate-50 px-4">
    <div class="card w-full max-w-md p-8">
      <div class="mb-6">
        <div class="text-xs text-slate-500">Neural ES</div>
        <h1 class="text-2xl font-semibold">Connexion</h1>
        <p class="text-sm text-slate-600 mt-1">
          Accède à l’interface web pour l’acquisition et l’analyse.
        </p>
      </div>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="block text-xs text-slate-600 mb-1">Email</label>
          <input class="input" v-model="email" type="email" required />
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Mot de passe</label>
          <input class="input" v-model="password" type="password" required />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button class="btn btn-primary w-full" :disabled="loading">
          {{ loading ? "Connexion..." : "Se connecter" }}
        </button>

        <div class="text-xs text-slate-500 mt-3">
          Astuce : si tu utilises des tokens JWT, le front stocke le token en local.
        </div>
      </form>
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

async function onSubmit() {
  error.value = null;
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    router.push("/acquisition");
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? "Identifiants invalides.";
  } finally {
    loading.value = false;
  }
}
</script>
