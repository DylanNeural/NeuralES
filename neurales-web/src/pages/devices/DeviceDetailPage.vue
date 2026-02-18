<template>
  <div class="space-y-8">
    <div class="flex items-center gap-4 mb-6">
      <router-link to="/devices">
        <AppButton variant="secondary" class="!px-3">← Retour</AppButton>
      </router-link>
      <h1 class="text-3xl font-bold text-primary-dark">Détails du dispositif</h1>
    </div>

    <!-- Loading State -->
    <div v-if="deviceStore.isLoading" class="card">
      <div class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p class="text-primary-light">Chargement...</p>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="deviceStore.error && !deviceStore.isLoading" class="card bg-red-50 border border-red-200">
      <div class="flex items-center gap-4">
        <div class="text-red-600 text-2xl">⚠️</div>
        <div>
          <p class="font-semibold text-red-800">Erreur</p>
          <p class="text-red-700">{{ deviceStore.error }}</p>
        </div>
      </div>
    </div>

    <!-- Device Details -->
    <div v-if="!deviceStore.isLoading && deviceStore.current" class="space-y-6">
      <div class="card">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Marque / Modèle -->
          <div>
            <p class="text-sm text-primary-light mb-2">Marque / Modèle</p>
            <p class="text-lg font-semibold text-primary-dark">{{ deviceStore.current.marque_modele }}</p>
          </div>

          <!-- Numéro de série -->
          <div>
            <p class="text-sm text-primary-light mb-2">Numéro de série</p>
            <p class="text-lg font-semibold text-primary-dark">{{ deviceStore.current.serial_number || '-' }}</p>
          </div>

          <!-- Type de connexion -->
          <div>
            <p class="text-sm text-primary-light mb-2">Type de connexion</p>
            <p class="text-lg font-semibold text-primary-dark">{{ formatConnectionType(deviceStore.current.connection_type) }}</p>
          </div>

          <!-- État -->
          <div>
            <p class="text-sm text-primary-light mb-2">État</p>
            <span :class="getStatusClass(deviceStore.current.etat)" class="inline-block px-3 py-1 rounded-lg text-sm font-semibold">
              {{ formatStatus(deviceStore.current.etat) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-4 justify-start">
        <router-link :to="`/devices/${deviceStore.current.device_id}/edit`">
          <AppButton variant="primary">Modifier</AppButton>
        </router-link>
        <AppButton 
          variant="danger"
          @click="handleDelete"
          :loading="isDeleting"
        >
          Supprimer
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDeviceStore } from '@/stores/devices.store'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const route = useRoute()
const deviceStore = useDeviceStore()
const isDeleting = ref(false)

onMounted(async () => {
  try {
    const deviceId = Number(route.params.id)
    await deviceStore.fetchDeviceById(deviceId)
  } catch (err) {
    console.error('Erreur lors du chargement:', err)
  }
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

const handleDelete = async () => {
  if (!confirm('Êtes-vous sûr(e) de vouloir supprimer ce dispositif ?')) {
    return
  }

  try {
    isDeleting.value = true
    const deviceId = Number(route.params.id)
    await deviceStore.deleteDevice(deviceId)
    await router.push('/devices')
  } catch (error) {
    console.error('Erreur lors de la suppression:', error)
  } finally {
    isDeleting.value = false
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
