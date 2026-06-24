<script setup lang="ts">
import { ref } from 'vue';
import HeartDemo from '@/components/demo/HeartDemo.vue';
import EMGGameDemo from '@/components/demo/EMGGameDemo.vue';
import AlphaDemo from '@/components/demo/AlphaDemo.vue';
import EOGDemo from '@/components/demo/EOGDemo.vue';
import FaceEMGDemo from '@/components/demo/FaceEMGDemo.vue';

const tabs = [
  { id: 'heart', label: 'ECG Cardiaque', icon: '❤️' },
  { id: 'emg', label: 'Jeu Musculaire', icon: '💪' },
  { id: 'alpha', label: 'Yeux Fermés', icon: '👁️' },
  { id: 'eog', label: 'Mouvement Yeux', icon: '👀' },
  { id: 'face', label: 'Visage 3D', icon: '😊' },
];
const active = ref('heart');
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h1 class="text-2xl font-bold text-foreground">Démos Biosignaux</h1>
      <p class="text-sm text-muted-foreground mt-1">Mode simulation — données générées, prêt pour OpenBCI</p>
    </div>

    <!-- Tab bar -->
    <div class="flex gap-2 p-1 bg-secondary/30 rounded-xl border border-border w-fit flex-wrap">
      <button v-for="t in tabs" :key="t.id"
        @click="active = t.id"
        :class="['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
          active === t.id ? 'bg-primary text-white shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-white/5']">
        <span>{{ t.icon }}</span>
        <span class="hidden sm:inline">{{ t.label }}</span>
      </button>
    </div>

    <!-- Demo panels -->
    <HeartDemo v-if="active === 'heart'" />
    <EMGGameDemo v-if="active === 'emg'" />
    <AlphaDemo v-if="active === 'alpha'" />
    <EOGDemo v-if="active === 'eog'" />
    <FaceEMGDemo v-if="active === 'face'" />
  </div>
</template>
