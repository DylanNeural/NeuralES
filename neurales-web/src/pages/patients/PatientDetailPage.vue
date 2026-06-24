<template>
  <div class="max-w-3xl space-y-6">
    <!-- Back + Actions -->
    <div class="flex items-center justify-between">
      <AppButton @click="goBack">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </AppButton>
      <div class="flex gap-2">
        <router-link :to="`/patients/${patient?.patient_id}/edit`">
          <AppButton variant="primary">Modifier</AppButton>
        </router-link>
        <AppButton variant="danger" @click="handleDelete" :loading="isDeleting">
          Supprimer
        </AppButton>
      </div>
    </div>

    <AppAlert v-if="apiError" v-model="showError" variant="error" title="Erreur" :message="apiError" />

    <!-- Patient header card -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <div class="flex items-center gap-4">
        <div class="h-14 w-14 rounded-2xl bg-primary-muted text-primary grid place-items-center text-xl font-bold shrink-0">
          {{ initials }}
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-900">{{ patient?.prenom }} {{ patient?.nom }}</h2>
          <p class="text-sm text-slate-500 mt-0.5">{{ patient?.identifiant_interne }}</p>
        </div>
        <div class="ml-auto">
          <span v-if="patient?.sexe" class="badge badge-slate capitalize">{{ patient.sexe }}</span>
        </div>
      </div>
    </div>

    <!-- Details grid -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <div class="text-sm font-semibold text-slate-900 mb-5">Informations médicales</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
        <div v-for="field in fields" :key="field.label">
          <div class="text-xs text-slate-400 mb-1">{{ field.label }}</div>
          <div class="text-sm font-medium text-slate-800">{{ field.value || '—' }}</div>
        </div>
      </div>
    </div>

    <!-- Notes -->
    <div v-if="patient?.remarque || patient?.notes" class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <div class="text-sm font-semibold text-slate-900 mb-3">Notes & remarques</div>
      <p v-if="patient?.remarque" class="text-sm text-slate-700 mb-2">{{ patient.remarque }}</p>
      <p v-if="patient?.notes" class="text-sm text-slate-600">{{ patient.notes }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppAlert from "@/components/ui/AppAlert.vue";
import { usePatientsStore } from "@/stores/patients.store";

const route = useRoute();
const router = useRouter();
const patientsStore = usePatientsStore();

const showError = ref(true);
const apiError = ref<string | null>(null);
const patient = computed(() => patientsStore.current);
const isDeleting = ref(false);

const initials = computed(() => {
  const p = patient.value;
  if (!p) return '?';
  return `${(p.prenom?.[0] || '').toUpperCase()}${(p.nom?.[0] || '').toUpperCase()}`;
});

const fields = computed(() => {
  const p = patient.value;
  if (!p) return [];
  return [
    { label: 'Date de naissance', value: p.date_naissance },
    { label: 'N° sécurité sociale', value: p.numero_securite_sociale },
    { label: 'Service', value: p.service },
    { label: 'Médecin référent', value: p.medecin_referent },
    { label: 'Organisation', value: p.organisation_id ? `#${p.organisation_id}` : null },
    { label: 'Créé le', value: p.created_at ? new Date(p.created_at).toLocaleString('fr-FR') : null },
  ];
});

function goBack() {
  router.back();
}

const handleDelete = async () => {
  if (!confirm('Supprimer ce patient ?')) return;
  try {
    isDeleting.value = true;
    await patientsStore.deletePatient(String(route.params.id));
    await router.push('/patients');
  } catch {
    apiError.value = 'Erreur lors de la suppression du patient';
  } finally {
    isDeleting.value = false;
  }
};

onMounted(async () => {
  const patientId = String(route.params.id);
  try {
    await patientsStore.fetchPatientById(patientId);
  } catch {
    apiError.value = patientsStore.error ?? "Erreur inconnue.";
  }
});
</script>
