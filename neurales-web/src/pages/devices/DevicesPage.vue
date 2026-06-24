<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Parc de dispositifs</h2>
        <p class="text-sm text-slate-500 mt-0.5">{{ deviceStore.items.length }} dispositif{{ deviceStore.items.length !== 1 ? 's' : '' }} enregistré{{ deviceStore.items.length !== 1 ? 's' : '' }}</p>
      </div>
      <router-link to="/devices/new">
        <AppButton variant="primary">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nouveau dispositif
        </AppButton>
      </router-link>
    </div>

    <!-- Loading -->
    <div v-if="deviceStore.isLoading" class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-12 flex flex-col items-center gap-3 text-slate-400">
      <svg class="w-7 h-7 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="text-sm">Chargement des dispositifs...</span>
    </div>

    <!-- Error -->
    <div v-else-if="deviceStore.error" class="bg-red-50 rounded-2xl border border-red-200 p-5 flex items-start gap-4">
      <svg class="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      <div>
        <p class="text-sm font-semibold text-red-800">Erreur de chargement</p>
        <p class="text-sm text-red-700 mt-0.5">{{ deviceStore.error }}</p>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="deviceStore.isEmpty" class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-16 flex flex-col items-center gap-4">
      <div class="h-16 w-16 rounded-2xl bg-slate-100 grid place-items-center">
        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="text-center">
        <p class="text-sm font-semibold text-slate-800">Aucun dispositif enregistré</p>
        <p class="text-xs text-slate-400 mt-1">Ajoutez vos équipements EEG pour commencer</p>
      </div>
      <router-link to="/devices/new">
        <AppButton variant="primary">Créer le premier dispositif</AppButton>
      </router-link>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
      <table class="min-w-full table-auto">
        <thead>
          <tr>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Marque / Modèle</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">N° de série</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Connexion</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">État</th>
            <th class="py-3 px-5 bg-slate-50/60 border-b border-slate-200 w-36"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="device in deviceStore.items"
            :key="device.device_id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/60 transition-colors"
          >
            <td class="py-3.5 px-5">
              <div class="flex items-center gap-3">
                <div class="h-8 w-8 rounded-lg bg-slate-100 grid place-items-center shrink-0">
                  <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-slate-900">{{ device.marque_modele }}</span>
              </div>
            </td>
            <td class="py-3.5 px-5 text-sm font-mono text-slate-500">{{ device.serial_number || '—' }}</td>
            <td class="py-3.5 px-5">
              <span class="badge badge-slate">{{ formatConnectionType(device.connection_type) }}</span>
            </td>
            <td class="py-3.5 px-5">
              <span :class="['badge', getStatusBadge(device.etat)]">
                {{ formatStatus(device.etat) }}
              </span>
            </td>
            <td class="py-3.5 px-5">
              <div class="flex items-center gap-2 justify-end">
                <AppButton class="!px-3 !py-1.5 !text-xs" @click="goToDetail(device.device_id)">Voir</AppButton>
                <AppButton class="!px-3 !py-1.5 !text-xs" @click="goToEdit(device.device_id)">Modifier</AppButton>
                <AppButton variant="danger" class="!px-3 !py-1.5 !text-xs" :loading="deletingId === device.device_id" @click="handleDelete(device.device_id)">✕</AppButton>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDeviceStore } from '@/stores/devices.store';
import AppButton from '@/components/ui/AppButton.vue';

const router = useRouter();
const deviceStore = useDeviceStore();
const deletingId = ref<string | null>(null);

onMounted(async () => { await deviceStore.fetchDevices(); });

const formatConnectionType = (type: string): string =>
  ({ usb: 'USB', bluetooth: 'Bluetooth', ethernet: 'Ethernet', wifi: 'Wi-Fi' }[type] || type);

const formatStatus = (status: string): string =>
  ({ actif: 'Actif', inactif: 'Inactif', defaillant: 'Défaillant', maintenance: 'Maintenance' }[status] || status);

const getStatusBadge = (status: string): string =>
  ({ actif: 'badge-green', inactif: 'badge-slate', defaillant: 'badge-red', maintenance: 'badge-amber' }[status] || 'badge-slate');

const handleDelete = async (deviceId: string) => {
  if (!confirm('Supprimer ce dispositif ?')) return;
  try {
    deletingId.value = deviceId;
    await deviceStore.deleteDevice(deviceId);
  } catch (err) {
    console.error('Erreur lors de la suppression:', err);
  } finally {
    deletingId.value = null;
  }
};

const goToDetail = (id: string) => router.push(`/devices/${id}`);
const goToEdit = (id: string) => router.push(`/devices/${id}/edit`);
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>
