<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center justify-between">
      <AppButton @click="() => router.push('/devices')">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </AppButton>
      <div class="flex gap-2">
        <AppButton variant="primary" @click="goToEdit">Modifier</AppButton>
        <AppButton variant="danger" @click="handleDelete" :loading="isDeleting">Supprimer</AppButton>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="deviceStore.isLoading" class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-12 flex flex-col items-center gap-3 text-slate-400">
      <svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="text-sm">Chargement...</span>
    </div>

    <!-- Error -->
    <div v-else-if="deviceStore.error && !deviceStore.isLoading" class="bg-red-50 rounded-2xl border border-red-200 p-5">
      <p class="text-sm font-semibold text-red-800">Erreur</p>
      <p class="text-sm text-red-700 mt-1">{{ deviceStore.error }}</p>
    </div>

    <!-- Content -->
    <template v-else-if="deviceStore.current">
      <!-- Header card -->
      <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
        <div class="flex items-center gap-4">
          <div class="h-12 w-12 rounded-xl bg-slate-100 grid place-items-center shrink-0">
            <svg class="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold text-slate-900">{{ deviceStore.current.marque_modele }}</h2>
            <p class="text-sm text-slate-400 mt-0.5 font-mono">{{ deviceStore.current.serial_number || 'Pas de numéro de série' }}</p>
          </div>
          <span :class="['badge', getStatusBadge(deviceStore.current.etat)]">
            {{ formatStatus(deviceStore.current.etat) }}
          </span>
        </div>
      </div>

      <!-- Details -->
      <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
        <div class="text-sm font-semibold text-slate-900 mb-5">Caractéristiques</div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
          <div>
            <div class="text-xs text-slate-400 mb-1">Type de connexion</div>
            <div class="flex items-center gap-2">
              <span class="badge badge-slate">{{ formatConnectionType(deviceStore.current.connection_type) }}</span>
            </div>
          </div>
          <div>
            <div class="text-xs text-slate-400 mb-1">État</div>
            <span :class="['badge', getStatusBadge(deviceStore.current.etat)]">{{ formatStatus(deviceStore.current.etat) }}</span>
          </div>
          <div>
            <div class="text-xs text-slate-400 mb-1">Numéro de série</div>
            <div class="text-sm font-medium text-slate-800 font-mono">{{ deviceStore.current.serial_number || '—' }}</div>
          </div>
          <div>
            <div class="text-xs text-slate-400 mb-1">Organisation</div>
            <div class="text-sm font-medium text-slate-800">#{{ deviceStore.current.organisation_id }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useDeviceStore } from '@/stores/devices.store';
import AppButton from '@/components/ui/AppButton.vue';

const router = useRouter();
const route = useRoute();
const deviceStore = useDeviceStore();
const isDeleting = ref(false);

onMounted(async () => {
  try {
    await deviceStore.fetchDeviceById(String(route.params.id));
  } catch (err) {
    console.error('Erreur lors du chargement:', err);
  }
});

const formatConnectionType = (type: string): string =>
  ({ usb: 'USB', bluetooth: 'Bluetooth', ethernet: 'Ethernet', wifi: 'Wi-Fi' }[type] || type);

const formatStatus = (status: string): string =>
  ({ actif: 'Actif', inactif: 'Inactif', defaillant: 'Défaillant', maintenance: 'Maintenance' }[status] || status);

const getStatusBadge = (status: string): string =>
  ({ actif: 'badge-green', inactif: 'badge-slate', defaillant: 'badge-red', maintenance: 'badge-amber' }[status] || 'badge-slate');

const handleDelete = async () => {
  if (!confirm('Supprimer ce dispositif ?')) return;
  try {
    isDeleting.value = true;
    await deviceStore.deleteDevice(String(route.params.id));
    await router.push('/devices');
  } catch {
    console.error('Erreur lors de la suppression');
  } finally {
    isDeleting.value = false;
  }
};

const goToEdit = () => router.push(`/devices/${route.params.id}/edit`);
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>
