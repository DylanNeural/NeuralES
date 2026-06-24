<template>
  <div class="max-w-lg space-y-6">
    <div class="flex items-center gap-3">
      <AppButton @click="() => router.push('/devices')">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </AppButton>
      <h2 class="text-xl font-semibold text-slate-900">
        {{ isEdit ? 'Modifier le dispositif' : 'Nouveau dispositif' }}
      </h2>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div class="form-group">
          <label class="label">Marque / Modèle <span class="text-red-500">*</span></label>
          <input
            v-model="form.marque_modele"
            class="input"
            type="text"
            placeholder="Ex: Emotiv EPOC X"
            required
            @input="() => { errors.marque_modele = validateDeviceName(form.marque_modele).join(' '); }"
            @blur="() => { errors.marque_modele = validateDeviceName(form.marque_modele).join(' '); }"
          />
          <p v-if="errors.marque_modele" class="text-xs text-red-600 mt-1">{{ errors.marque_modele }}</p>
        </div>

        <div class="form-group">
          <label class="label">Numéro de série</label>
          <input v-model="form.serial_number" class="input" type="text" placeholder="Ex: SN123456789" />
        </div>

        <div class="form-group">
          <label class="label">Type de connexion <span class="text-red-500">*</span></label>
          <select v-model="form.connection_type" class="input" required @change="validateConnectionType">
            <option value="">Sélectionner un type...</option>
            <option value="usb">USB</option>
            <option value="bluetooth">Bluetooth</option>
            <option value="ethernet">Ethernet</option>
            <option value="wifi">Wi-Fi</option>
          </select>
          <p v-if="errors.connection_type" class="text-xs text-red-600 mt-1">{{ errors.connection_type }}</p>
        </div>

        <div class="form-group">
          <label class="label">État <span class="text-red-500">*</span></label>
          <select v-model="form.etat" class="input" required @change="validateEtat">
            <option value="">Sélectionner un état...</option>
            <option value="actif">Actif</option>
            <option value="inactif">Inactif</option>
            <option value="defaillant">Défaillant</option>
            <option value="maintenance">Maintenance</option>
          </select>
          <p v-if="errors.etat" class="text-xs text-red-600 mt-1">{{ errors.etat }}</p>
        </div>

        <div v-if="error" class="rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>

        <div class="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <router-link to="/devices">
            <AppButton type="button">Annuler</AppButton>
          </router-link>
          <AppButton variant="primary" type="submit" :loading="isSubmitting">
            {{ isEdit ? 'Enregistrer' : 'Créer' }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useDeviceStore } from '@/stores/devices.store';
import type { DeviceCreatePayload } from '@/api/devices.api';
import AppButton from '@/components/ui/AppButton.vue';
import { validateDeviceName, hasErrors } from '@/utils/form-validation';

const router = useRouter();
const route = useRoute();
const deviceStore = useDeviceStore();

const isEdit = !!route.params.id;
const isSubmitting = ref(false);
const error = ref<string | null>(null);

const form = reactive({ marque_modele: '', serial_number: '', connection_type: '', etat: 'actif' });
const errors = reactive({ marque_modele: '', connection_type: '', etat: '' });

onMounted(async () => {
  if (isEdit) {
    try {
      const device = await deviceStore.fetchDeviceById(String(route.params.id));
      form.marque_modele = device.marque_modele;
      form.serial_number = device.serial_number || '';
      form.connection_type = device.connection_type;
      form.etat = device.etat;
    } catch (err) {
      error.value = 'Erreur lors du chargement du dispositif';
    }
  }
});

const validateConnectionType = () => { errors.connection_type = form.connection_type ? '' : 'Le type de connexion est obligatoire.'; };
const validateEtat = () => { errors.etat = form.etat ? '' : "L'état est obligatoire."; };

const validateForm = (): boolean => {
  Object.assign(errors, { marque_modele: '', connection_type: '', etat: '' });
  error.value = null;
  errors.marque_modele = validateDeviceName(form.marque_modele).join(' ');
  if (!form.connection_type) errors.connection_type = 'Le type de connexion est obligatoire.';
  if (!form.etat) errors.etat = "L'état est obligatoire.";
  return !hasErrors(errors);
};

const handleSubmit = async () => {
  if (!validateForm()) { error.value = 'Veuillez corriger les champs invalides'; return; }
  isSubmitting.value = true;
  error.value = null;
  try {
    const payload: DeviceCreatePayload = {
      marque_modele: form.marque_modele.trim(),
      serial_number: form.serial_number.trim() || undefined,
      connection_type: form.connection_type,
      etat: form.etat,
    };
    if (isEdit) {
      await deviceStore.updateDevice(String(route.params.id), payload);
    } else {
      await deviceStore.createDevice(payload);
    }
    await router.push('/devices');
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || 'Une erreur est survenue';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
