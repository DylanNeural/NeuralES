<template>
  <div class="space-y-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-primary-dark">Patients</h1>
      <AppButton variant="primary" @click="goToCreate">Nouveau patient</AppButton>
    </div>
    <div class="card overflow-x-auto">
      <table class="min-w-full text-left">
        <thead>
          <tr class="text-primary-light uppercase text-xs tracking-widest border-b border-primary-light/20">
            <th class="py-3 px-4">Nom</th>
            <th class="py-3 px-4">Prénom</th>
            <th class="py-3 px-4">Date de naissance</th>
            <th class="py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in 4" :key="i" class="border-b last:border-0 border-primary-light/10 hover:bg-primary-light/5">
            <td class="py-3 px-4">Dupont</td>
            <td class="py-3 px-4">Jean {{ i }}</td>
            <td class="py-3 px-4">1990-01-0{{ i }}</td>
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
import { useRouter } from 'vue-router';
import AppButton from '@/components/ui/AppButton.vue';

const router = useRouter();

function goToCreate() {
  router.push('/patients/new');
}
</script>

<style scoped>
</style>
