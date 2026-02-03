<template>
  <div class="space-y-8">
    <h1 class="text-3xl font-bold text-primary-dark mb-6">Dashboard</h1>
    <AppCard>
      <div class="text-base font-semibold text-primary-dark mb-4">Vue 3D du cerveau</div>
      <Brain3D />
    </AppCard>
    <AppCard>
      <EEGChartCanvas />
    </AppCard>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <AppCard>
        <div class="text-xs text-primary-light mb-1">Sessions actives</div>
        <div class="text-3xl font-bold">3</div>
      </AppCard>
      <AppCard>
        <div class="text-xs text-primary-light mb-1">Patients</div>
        <div class="text-3xl font-bold">12</div>
      </AppCard>
      <AppCard>
        <div class="text-xs text-primary-light mb-1">Dispositifs</div>
        <div class="text-3xl font-bold">5</div>
      </AppCard>
    </div>
    <AppCard>
      <div class="text-primary-dark text-base">Graphiques et widgets à venir...</div>
    </AppCard>
  </div>
</template>

<script setup lang="ts">
import AppCard from '@/components/ui/AppCard.vue';
import Brain3D from '@/components/Brain3D.vue';
import EEGChartCanvas from '@/components/EEGChartCanvas.vue';
</script>

<style scoped>
</style>
