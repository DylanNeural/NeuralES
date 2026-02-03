<template>
  <div class="space-y-8 max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold text-primary-dark mb-6">Détail du résultat</h1>
    <AppCard>
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <div class="text-xs text-primary-light mb-1">Session</div>
          <div class="text-lg font-mono font-semibold">#1001</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Patient</div>
          <div class="text-lg font-semibold">Jean Dupont</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Date</div>
          <div class="text-lg font-semibold">2026-01-31</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Score fatigue</div>
          <div class="text-lg font-semibold">62 / 100</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Qualité</div>
          <div class="text-lg font-semibold">Bonne</div>
        </div>
      </div>
    </AppCard>
    <AppCard>
      <div class="text-primary-dark text-base">Graphique ou détails complémentaires ici...</div>
    </AppCard>
  </div>
</template>

<script setup lang="ts">
import AppCard from '@/components/ui/AppCard.vue';
</script>

<style scoped>
</style>