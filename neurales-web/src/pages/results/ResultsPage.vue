<template>
  <div class="space-y-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-primary-dark">Résultats</h1>
      <AppButton variant="primary">Nouveau résultat</AppButton>
    </div>

    <div class="card overflow-x-auto">
      <table class="min-w-full text-left">
        <thead>
          <tr class="text-primary-light uppercase text-xs tracking-widest border-b border-primary-light/20">
            <th class="py-3 px-4">Session</th>
            <th class="py-3 px-4">Patient</th>
            <th class="py-3 px-4">Date</th>
            <th class="py-3 px-4">Score fatigue</th>
            <th class="py-3 px-4">Qualité</th>
            <th class="py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in 5" :key="i" class="border-b last:border-0 border-primary-light/10 hover:bg-primary-light/5">
            <td class="py-3 px-4 font-mono">#{{ 1000 + i }}</td>
            <td class="py-3 px-4">Jean Dupont</td>
            <td class="py-3 px-4">2026-01-31</td>
            <td class="py-3 px-4">{{ 60 + i }} / 100</td>
            <td class="py-3 px-4">Bonne</td>
            <td class="py-3 px-4">
              <AppButton variant="primary" class="!px-3 !py-1 text-sm">Voir</AppButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppButton from '@/components/ui/AppButton.vue';
</script>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0;
}
</style>