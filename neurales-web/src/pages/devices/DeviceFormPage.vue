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
            @input="() => { const err = validateDeviceName(form.marque_modele); errors.marque_modele = err.length > 0 ? err.join(' ') : ''; }"
            @blur="() => { const err = validateDeviceName(form.marque_modele); errors.marque_modele = err.length > 0 ? err.join(' ') : ''; }"
          />
          <p v-if="errors.marque_modele" class="text-red-600 text-sm mt-1">
            {{ errors.marque_modele }}
          </p>
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
            @change="validateConnectionType"
          >
            <option value="">Sélectionner un type...</option>
            <option value="usb">USB</option>
            <option value="bluetooth">Bluetooth</option>
            <option value="ethernet">Ethernet</option>
            <option value="wifi">Wi-Fi</option>
          </select>
          <p v-if="errors.connection_type" class="text-red-600 text-sm mt-1">
            {{ errors.connection_type }}
          </p>
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
            @change="validateEtat"
          >
            <option value="">Sélectionner un état...</option>
            <option value="actif">Actif</option>
            <option value="inactif">Inactif</option>
            <option value="defaillant">Défaillant</option>
            <option value="maintenance">Maintenance</option>
          </select>
          <p v-if="errors.etat" class="text-red-600 text-sm mt-1">
            {{ errors.etat }}
          </p>
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
import { validateDeviceName, hasErrors } from '@/utils/form-validation'

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

const errors = reactive({
  marque_modele: '',
  connection_type: '',
  etat: ''
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

const validateForm = (): boolean => {
  errors.marque_modele = ''
  errors.connection_type = ''
  errors.etat = ''
  error.value = null

  // Validation marque/modèle
  const marqueErrors = validateDeviceName(form.marque_modele)
  if (marqueErrors.length > 0) {
    errors.marque_modele = marqueErrors.join(' ')
  }

  // Validation connexion
  if (!form.connection_type) {
    errors.connection_type = 'Le type de connexion est obligatoire.'
  }

  // Validation état
  if (!form.etat) {
    errors.etat = "L'état est obligatoire."
  }

  return !hasErrors(errors)
}

const validateConnectionType = () => {
  errors.connection_type = form.connection_type ? '' : 'Le type de connexion est obligatoire.'
}

const validateEtat = () => {
  errors.etat = form.etat ? '' : "L'état est obligatoire."
}

const handleSubmit = async () => {
  if (!validateForm()) {
    error.value = 'Veuillez corriger les champs invalides'
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
