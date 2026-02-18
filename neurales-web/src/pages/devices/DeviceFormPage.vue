<template>
  <div class="space-y-8">
    <div class="flex items-center gap-4 mb-6">
      <router-link to="/devices">
        <AppButton variant="secondary" class="!px-3">← Retour</AppButton>
      </router-link>
      <h1 class="text-3xl font-bold text-primary-dark">
        {{ isEdit ? 'Modifier le dispositif' : 'Nouveau dispositif' }}
      </h1>
    </div>

    <div class="card">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Marque / Modèle -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Marque / Modèle <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.marque_modele"
            type="text"
            placeholder="Ex: Emotiv EPOC X"
            class="w-full px-4 py-2 border border-primary-light/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>

        <!-- Numéro de série -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Numéro de série
          </label>
          <input
            v-model="form.serial_number"
            type="text"
            placeholder="Ex: SN123456789"
            class="w-full px-4 py-2 border border-primary-light/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <!-- Type de connexion -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Type de connexion <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.connection_type"
            class="w-full px-4 py-2 border border-primary-light/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            required
          >
            <option value="">Sélectionner un type...</option>
            <option value="usb">USB</option>
            <option value="bluetooth">Bluetooth</option>
            <option value="ethernet">Ethernet</option>
            <option value="wifi">Wi-Fi</option>
          </select>
        </div>

        <!-- État -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            État <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.etat"
            class="w-full px-4 py-2 border border-primary-light/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            required
          >
            <option value="">Sélectionner un état...</option>
            <option value="actif">Actif</option>
            <option value="inactif">Inactif</option>
            <option value="defaillant">Défaillant</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-800">{{ error }}</p>
        </div>

        <!-- Actions -->
        <div class="flex gap-4 justify-end pt-4 border-t border-primary-light/20">
          <router-link to="/devices">
            <AppButton variant="secondary">Annuler</AppButton>
          </router-link>
          <AppButton 
            variant="primary" 
            type="submit"
            :loading="isSubmitting"
          >
            {{ isEdit ? 'Mettre à jour' : 'Créer' }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDeviceStore } from '@/stores/devices.store'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const route = useRoute()
const deviceStore = useDeviceStore()

const isEdit = !!route.params.id
const isSubmitting = ref(false)
const error = ref<string | null>(null)

const form = reactive({
  marque_modele: '',
  serial_number: '',
  connection_type: '',
  etat: 'actif'
})

onMounted(async () => {
  if (isEdit) {
    try {
      const deviceId = Number(route.params.id)
      const device = await deviceStore.fetchDeviceById(deviceId)
      form.marque_modele = device.marque_modele
      form.serial_number = device.serial_number || ''
      form.connection_type = device.connection_type
      form.etat = device.etat
    } catch (err) {
      error.value = 'Erreur lors du chargement du dispositif'
      console.error(err)
    }
  }
})

const handleSubmit = async () => {
  if (!form.marque_modele || !form.connection_type || !form.etat) {
    error.value = 'Veuillez remplir tous les champs obligatoires'
    return
  }

  isSubmitting.value = true
  error.value = null

  try {
    if (isEdit) {
      await deviceStore.updateDevice(Number(route.params.id), form)
    } else {
      await deviceStore.createDevice(form as any)
    }
    await router.push('/devices')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Une erreur est survenue'
    console.error(err)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
</style>
