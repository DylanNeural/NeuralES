<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppCard from "@/components/ui/AppCard.vue";
import { usePatientsStore } from "@/stores/patients.store";

const router = useRouter();
const patientsStore = usePatientsStore();
const patients = computed(() => patientsStore.items);
const isLoading = computed(() => patientsStore.isLoading);

function goToCreate() { router.push("/patients/new"); }
function goToDetail(patientId: string) { router.push(`/patients/${patientId}`); }

async function handleDelete(patientId: string, nom: string, prenom: string) {
  if (!confirm(`Supprimer le patient ${nom} ${prenom} ?`)) return;
  try {
    await patientsStore.deletePatient(patientId);
  } catch (err) {
    console.error("Erreur suppression:", err);
  }
}

onMounted(() => { patientsStore.fetchPatients(); });
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-foreground">Patients</h1>
        <p class="text-sm text-muted-foreground mt-0.5">Gestion des dossiers patients</p>
      </div>
      <AppButton variant="primary" @click="goToCreate">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nouveau patient
      </AppButton>
    </div>

    <!-- Table card -->
    <AppCard class="!p-0 overflow-hidden">
      <!-- Loading -->
      <div v-if="isLoading" class="flex items-center justify-center py-16 text-muted-foreground text-sm">
        <svg class="h-5 w-5 animate-spin mr-2 text-primary" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        Chargement…
      </div>

      <!-- Empty -->
      <div v-else-if="patients.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
        <div class="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-3">
          <svg class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <p class="text-sm font-medium text-foreground mb-1">Aucun patient enregistré</p>
        <p class="text-xs text-muted-foreground mb-4">Commencez par ajouter un premier patient.</p>
        <AppButton variant="primary" size="sm" @click="goToCreate">Ajouter un patient</AppButton>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-left">
          <thead>
            <tr class="border-b border-border">
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Patient</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Nom</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Date de naissance</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="patient in patients"
              :key="patient.patient_id"
              class="border-b border-border/60 last:border-0 hover:bg-secondary/20 transition-colors"
            >
              <td class="py-3.5 px-5">
                <div class="flex items-center gap-3">
                  <div class="h-8 w-8 rounded-full bg-primary/15 text-primary flex items-center justify-center text-xs font-semibold shrink-0">
                    {{ (patient.prenom?.[0] || "") + (patient.nom?.[0] || "") }}
                  </div>
                  <span class="text-sm font-medium text-foreground">{{ patient.prenom }}</span>
                </div>
              </td>
              <td class="py-3.5 px-5 text-sm text-foreground">{{ patient.nom }}</td>
              <td class="py-3.5 px-5 text-sm text-muted-foreground">{{ patient.date_naissance ?? "—" }}</td>
              <td class="py-3.5 px-5">
                <div class="flex gap-2">
                  <AppButton size="sm" variant="ghost" @click="goToDetail(patient.patient_id)">Voir</AppButton>
                  <RouterLink :to="`/patients/${patient.patient_id}/edit`">
                    <AppButton size="sm" variant="secondary">Modifier</AppButton>
                  </RouterLink>
                  <AppButton
                    size="sm"
                    variant="danger"
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
    </AppCard>
  </div>
</template>
