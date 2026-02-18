<template>
  <div class="space-y-8 max-w-3xl mx-auto">
    <div class="flex items-center gap-3">
      <AppButton class="!px-3" @click="goBack">Retour</AppButton>
      <h1 class="text-3xl font-bold text-primary-dark">Détail du patient</h1>
    </div>

    <AppAlert
      v-if="apiError"
      v-model="showError"
      variant="error"
      title="Erreur"
      :message="apiError"
    />

    <AppCard>
      <div class="grid gap-4 md:grid-cols-2">
        <div>
          <div class="text-xs text-primary-light mb-1">Identifiant interne</div>
          <div class="text-base font-semibold">{{ patient?.identifiant_interne ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Organisation</div>
          <div class="text-base font-semibold">{{ patient?.organisation_id ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Nom</div>
          <div class="text-base font-semibold">{{ patient?.nom ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Prenom</div>
          <div class="text-base font-semibold">{{ patient?.prenom ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Date de naissance</div>
          <div class="text-base font-semibold">{{ formatDate(patient?.date_naissance) }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Sexe</div>
          <div class="text-base font-semibold">{{ patient?.sexe ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">N° securite sociale</div>
          <div class="text-base font-semibold">{{ patient?.numero_securite_sociale ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Service</div>
          <div class="text-base font-semibold">{{ patient?.service ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Medecin referent</div>
          <div class="text-base font-semibold">{{ patient?.medecin_referent ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Remarque</div>
          <div class="text-base font-semibold">{{ patient?.remarque ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Notes</div>
          <div class="text-base font-semibold">{{ patient?.notes ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Cree le</div>
          <div class="text-base font-semibold">{{ formatDateTime(patient?.created_at) }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Actions -->
    <div class="flex gap-4 justify-start">
      <router-link :to="`/patients/${patient?.patient_id}/edit`">
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
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
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

function goBack() {
  router.back();
}

function formatDate(value?: string | null) {
  if (!value) return "-";
  return value;
}

function formatDateTime(value?: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("fr-FR");
}

const handleDelete = async () => {
  if (!confirm('Êtes-vous sûr(e) de vouloir supprimer ce patient ?')) {
    return;
  }

  try {
    isDeleting.value = true;
    const patientId = Number(route.params.id);
    await patientsStore.deletePatient(patientId);
    await router.push('/patients');
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
    apiError.value = 'Erreur lors de la suppression du patient';
  } finally {
    isDeleting.value = false;
  }
};

onMounted(async () => {
  const patientId = Number(route.params.id);
  if (!patientId || Number.isNaN(patientId)) {
    apiError.value = "Identifiant patient invalide.";
    return;
  }
  try {
    await patientsStore.fetchPatientById(patientId);
  } catch (err) {
    apiError.value = patientsStore.error ?? "Erreur inconnue.";
  }
});
</script>
