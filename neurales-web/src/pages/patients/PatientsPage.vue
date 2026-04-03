<template>
  <div class="space-y-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-primary-dark">Patients</h1>
      <AppButton variant="primary" @click="goToCreate">Nouveau patient</AppButton>
    </div>
    <div class="card overflow-x-auto">
      <table class="min-w-full text-left">
        <thead>
          <tr class="text-primary-light uppercase text-xs tracking-widest border-b border-primary-light/20">
            <th class="py-3 px-4">Nom</th>
            <th class="py-3 px-4">Prénom</th>
            <th class="py-3 px-4">Date de naissance</th>
            <th class="py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="4" class="py-6 px-4 text-center text-sm text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="patients.length === 0">
            <td colspan="4" class="py-6 px-4 text-center text-sm text-slate-500">Aucun patient</td>
          </tr>
          <tr
            v-else
            v-for="patient in patients"
            :key="patient.patient_id"
            class="border-b last:border-0 border-primary-light/10 hover:bg-primary-light/5"
          >
            <td class="py-3 px-4">{{ patient.nom }}</td>
            <td class="py-3 px-4">{{ patient.prenom }}</td>
            <td class="py-3 px-4">{{ patient.date_naissance ?? "-" }}</td>
            <td class="py-3 px-4">
              <div class="flex gap-2">
                <AppButton
                  variant="primary"
                  class="!px-3 !py-1 text-sm"
                  @click="goToDetail(patient.patient_id)"
                >
                  Voir
                </AppButton>
                <router-link :to="`/patients/${patient.patient_id}/edit`">
                  <AppButton
                    variant="secondary"
                    class="!px-3 !py-1 text-sm"
                  >
                    Modifier
                  </AppButton>
                </router-link>
                <AppButton
                  variant="danger"
                  class="!px-3 !py-1 text-sm"
                  @click="handleDelete(patient.patient_id, patient.nom, patient.prenom)"
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
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import { usePatientsStore } from "@/stores/patients.store";

const router = useRouter();
const patientsStore = usePatientsStore();

const patients = computed(() => patientsStore.items);
const isLoading = computed(() => patientsStore.isLoading);

function goToCreate() {
  router.push('/patients/new');
}

function goToDetail(patientId: number) {
  router.push(`/patients/${patientId}`);
}

async function handleDelete(patientId: number, nom: string, prenom: string) {
  if (!confirm(`Êtes-vous sûr(e) de vouloir supprimer le patient ${nom} ${prenom} ?`)) {
    return;
  }
  try {
    await patientsStore.deletePatient(patientId);
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
  }
}

onMounted(() => {
  patientsStore.fetchPatients();
});
</script>

<style scoped>
</style>
