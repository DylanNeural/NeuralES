<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
import AppButton from "@/components/ui/AppButton.vue";
import { usePatientsStore } from "@/stores/patients.store";

const route = useRoute();
const router = useRouter();
const patientsStore = usePatientsStore();

const apiError = ref<string | null>(null);
const patient = computed(() => patientsStore.current);
const isDeleting = ref(false);

function goBack() { router.back(); }

function formatDate(value?: string | null) {
  if (!value) return "—";
  return value;
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("fr-FR");
}

const fields = computed(() => [
  { label: "Identifiant interne", value: patient.value?.identifiant_interne },
  { label: "Organisation", value: patient.value?.organisation_id },
  { label: "Nom", value: patient.value?.nom },
  { label: "Prénom", value: patient.value?.prenom },
  { label: "Date de naissance", value: formatDate(patient.value?.date_naissance) },
  { label: "Sexe", value: patient.value?.sexe },
  { label: "N° sécurité sociale", value: patient.value?.numero_securite_sociale },
  { label: "Service", value: patient.value?.service },
  { label: "Médecin référent", value: patient.value?.medecin_referent },
  { label: "Remarque", value: patient.value?.remarque },
  { label: "Notes", value: patient.value?.notes },
  { label: "Créé le", value: formatDateTime(patient.value?.created_at) },
]);

async function handleDelete() {
  if (!confirm("Supprimer ce patient ?")) return;
  try {
    isDeleting.value = true;
    await patientsStore.deletePatient(String(route.params.id));
    router.push("/patients");
  } catch (err) {
    apiError.value = "Erreur lors de la suppression";
  } finally {
    isDeleting.value = false;
  }
}

onMounted(async () => {
  const id = String(route.params.id);
  if (!id) { apiError.value = "Identifiant invalide."; return; }
  try {
    await patientsStore.fetchPatientById(id);
  } catch {
    apiError.value = patientsStore.error ?? "Erreur inconnue.";
  }
});
</script>

<template>
  <div class="max-w-3xl space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <AppButton variant="ghost" size="sm" @click="goBack">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour
      </AppButton>
      <h1 class="text-2xl font-bold text-foreground">Détail du patient</h1>
    </div>

    <!-- Error -->
    <div v-if="apiError" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ apiError }}
    </div>

    <!-- Patient header card -->
    <AppCard v-if="patient">
      <div class="flex items-center gap-4 mb-6">
        <div class="h-14 w-14 rounded-2xl bg-primary/20 ring-2 ring-primary/30 flex items-center justify-center text-xl font-bold text-primary shrink-0">
          {{ (patient.prenom?.[0] || "") + (patient.nom?.[0] || "") }}
        </div>
        <div>
          <h2 class="text-xl font-bold text-foreground">{{ patient.prenom }} {{ patient.nom }}</h2>
          <p class="text-sm text-muted-foreground">{{ patient.identifiant_interne || "—" }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="field in fields" :key="field.label" class="space-y-1">
          <div class="text-xs text-muted-foreground font-medium uppercase tracking-wide">{{ field.label }}</div>
          <div class="text-sm font-medium text-foreground">{{ field.value ?? "—" }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Actions -->
    <div class="flex gap-3">
      <RouterLink :to="`/patients/${patient?.patient_id}/edit`">
        <AppButton variant="primary">Modifier</AppButton>
      </RouterLink>
      <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">
        Supprimer
      </AppButton>
    </div>
  </div>
</template>
