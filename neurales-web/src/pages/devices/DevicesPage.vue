<template>
  <div class="space-y-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-primary-dark">Dispositifs</h1>
      <router-link to="/devices/new">
        <AppButton variant="primary">Nouveau dispositif</AppButton>
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="deviceStore.isLoading" class="card">
      <div class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p class="text-primary-light">Chargement des dispositifs...</p>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="deviceStore.error" class="card bg-red-50 border border-red-200">
      <div class="flex items-center gap-4">
        <div class="text-red-600 text-2xl">⚠️</div>
        <div>
          <p class="font-semibold text-red-800">Erreur</p>
          <p class="text-red-700">{{ deviceStore.error }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!deviceStore.isLoading && deviceStore.isEmpty" class="card">
      <div class="flex flex-col items-center justify-center py-12 text-center">
        <div class="text-6xl mb-4">📦</div>
        <h3 class="text-xl font-semibold text-primary-dark mb-2">Aucun dispositif</h3>
        <p class="text-primary-light mb-6">Aucun dispositif n'a été enregistré pour le moment.</p>
        <router-link to="/devices/new">
          <AppButton variant="primary">Créer le premier dispositif</AppButton>
        </router-link>
      </div>
    </div>

    <!-- Devices Table -->
    <div v-if="!deviceStore.isLoading && !deviceStore.isEmpty" class="card overflow-x-auto">
      <table class="min-w-full text-left">
        <thead>
          <tr class="text-primary-light uppercase text-xs tracking-widest border-b border-primary-light/20">
            <th class="py-3 px-4">Marque / Modèle</th>
            <th class="py-3 px-4">Numéro de série</th>
            <th class="py-3 px-4">Type de connexion</th>
            <th class="py-3 px-4">État</th>
            <th class="py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="device in deviceStore.items" :key="device.device_id" class="border-b last:border-0 border-primary-light/10 hover:bg-primary-light/5">
            <td class="py-3 px-4 font-medium">{{ device.marque_modele }}</td>
            <td class="py-3 px-4 text-sm text-primary-light">{{ device.serial_number || '-' }}</td>
            <td class="py-3 px-4 text-sm">{{ formatConnectionType(device.connection_type) }}</td>
            <td class="py-3 px-4">
              <span :class="getStatusClass(device.etat)" class="px-2 py-1 rounded text-xs font-semibold">
                {{ formatStatus(device.etat) }}
              </span>
            </td>
            <td class="py-3 px-4">
              <div class="flex gap-2">
                <router-link :to="`/devices/${device.device_id}`">
                  <AppButton variant="primary" class="!px-3 !py-1 text-sm">Voir</AppButton>
                </router-link>
                <router-link :to="`/devices/${device.device_id}/edit`">
                  <AppButton variant="secondary" class="!px-3 !py-1 text-sm">Modifier</AppButton>
                </router-link>
                <AppButton 
                  variant="danger" 
                  class="!px-3 !py-1 text-sm"
                  @click="handleDelete(device.device_id)"
                  :loading="deletingId === device.device_id"
                >
                  Supprimer
                </AppButton>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useDeviceStore } from '@/stores/devices.store'
import AppButton from '@/components/ui/AppButton.vue'

const deviceStore = useDeviceStore()
const deletingId = ref<number | null>(null)

onMounted(async () => {
  await deviceStore.fetchDevices()
})

const formatConnectionType = (type: string): string => {
  const map: Record<string, string> = {
    'usb': 'USB',
    'bluetooth': 'Bluetooth',
    'ethernet': 'Ethernet',
    'wifi': 'Wi-Fi'
  }
  return map[type] || type
}

const formatStatus = (status: string): string => {
  const map: Record<string, string> = {
    'actif': 'Actif',
    'inactif': 'Inactif',
    'defaillant': 'Défaillant',
    'maintenance': 'Maintenance'
  }
  return map[status] || status
}

const getStatusClass = (status: string): string => {
  const classes: Record<string, string> = {
    'actif': 'bg-green-100 text-green-800',
    'inactif': 'bg-gray-100 text-gray-800',
    'defaillant': 'bg-red-100 text-red-800',
    'maintenance': 'bg-yellow-100 text-yellow-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const handleDelete = async (deviceId: number) => {
  if (!confirm('Êtes-vous sûr(e) de vouloir supprimer ce dispositif ?')) {
    return
  }
  
  try {
    deletingId.value = deviceId
    await deviceStore.deleteDevice(deviceId)
  } catch (error) {
    console.error('Erreur lors de la suppression:', error)
  } finally {
    deletingId.value = null
  }
}
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
