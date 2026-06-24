<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Registre patients</h2>
        <p class="text-sm text-slate-500 mt-0.5">{{ patients.length }} patient{{ patients.length !== 1 ? 's' : '' }} enregistré{{ patients.length !== 1 ? 's' : '' }}</p>
      </div>
      <AppButton variant="primary" @click="goToCreate">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nouveau patient
      </AppButton>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
      <table class="min-w-full table-auto">
        <thead>
          <tr>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">
              Patient
            </th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">
              Date de naissance
            </th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">
              Service
            </th>
            <th class="py-3 px-5 bg-slate-50/60 border-b border-slate-200 w-36"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="4" class="py-12 px-5 text-center">
              <div class="flex flex-col items-center gap-3 text-slate-400">
                <svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span class="text-sm">Chargement...</span>
              </div>
            </td>
          </tr>
          <tr v-else-if="patients.length === 0">
            <td colspan="4" class="py-16 px-5 text-center">
              <div class="flex flex-col items-center gap-3">
                <div class="h-14 w-14 rounded-2xl bg-slate-100 grid place-items-center">
                  <svg class="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-slate-700">Aucun patient</p>
                  <p class="text-xs text-slate-400 mt-0.5">Créez le premier patient pour commencer</p>
                </div>
                <AppButton variant="primary" @click="goToCreate">Créer un patient</AppButton>
              </div>
            </td>
          </tr>
          <tr
            v-else
            v-for="patient in patients"
            :key="patient.patient_id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/60 transition-colors"
          >
            <td class="py-3.5 px-5">
              <div class="flex items-center gap-3">
                <div class="h-8 w-8 rounded-lg bg-primary-muted text-primary grid place-items-center text-xs font-bold shrink-0">
                  {{ (patient.prenom[0] || '').toUpperCase() }}{{ (patient.nom[0] || '').toUpperCase() }}
                </div>
                <div>
                  <div class="text-sm font-medium text-slate-900">{{ patient.prenom }} {{ patient.nom }}</div>
                  <div class="text-xs text-slate-400">{{ patient.identifiant_interne }}</div>
                </div>
              </div>
            </td>
            <td class="py-3.5 px-5 text-sm text-slate-600">
              {{ patient.date_naissance ?? '—' }}
            </td>
            <td class="py-3.5 px-5">
              <span v-if="patient.service" class="badge badge-slate">{{ patient.service }}</span>
              <span v-else class="text-sm text-slate-400">—</span>
            </td>
            <td class="py-3.5 px-5">
              <div class="flex items-center gap-2 justify-end">
                <AppButton size="sm" @click="goToDetail(patient.patient_id)" class="!px-3 !py-1.5 !text-xs">
                  Voir
                </AppButton>
                <router-link :to="`/patients/${patient.patient_id}/edit`">
                  <AppButton size="sm" class="!px-3 !py-1.5 !text-xs">Modifier</AppButton>
                </router-link>
                <AppButton
                  size="sm"
                  variant="danger"
                  class="!px-3 !py-1.5 !text-xs"
                  @click="handleDelete(patient.patient_id, patient.nom, patient.prenom)"
                >
                  ✕
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

function goToDetail(patientId: string) {
  router.push(`/patients/${patientId}`);
}

async function handleDelete(patientId: string, nom: string, prenom: string) {
  if (!confirm(`Supprimer le patient ${prenom} ${nom} ?`)) return;
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
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>
