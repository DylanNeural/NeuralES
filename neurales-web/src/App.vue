<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import MainLayout from "@/layouts/MainLayout.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { syncWorker } from "@/services/sync.worker";

const route = useRoute();
const layout = computed(() => {
  if (route.path.startsWith("/login")) return AuthLayout;
  return MainLayout;
});

onMounted(() => {
  // Démarre la synchronisation silencieuse toutes les 30 secondes
  syncWorker.start(30000); 
});

onUnmounted(() => {
  syncWorker.stop();
});
</script>
