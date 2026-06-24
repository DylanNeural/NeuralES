<script setup lang="ts">
import { useRouter } from "vue-router";
const router = useRouter();
</script>

<template>
  <div class="min-h-screen bg-background flex items-center justify-center p-6">
    <div class="text-center animate-fade-in max-w-sm">
      <div class="text-8xl font-bold gradient-text mb-4">404</div>
      <h1 class="text-xl font-semibold text-foreground mb-2">Page introuvable</h1>
      <p class="text-sm text-muted-foreground mb-8">
        La page que vous cherchez n'existe pas ou a été déplacée.
      </p>
      <button
        class="inline-flex items-center gap-2 h-9 px-5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors shadow-sm"
        @click="router.push('/acquisition')"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour à l'accueil
      </button>
    </div>
  </div>
</template>
