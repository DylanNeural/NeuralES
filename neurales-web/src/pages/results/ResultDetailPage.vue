<template>
  <div class="space-y-8 max-w-3xl mx-auto">
    <div class="flex items-center gap-3">
      <AppButton class="!px-3" @click="goBack">Retour</AppButton>
      <h1 class="text-3xl font-bold text-primary-dark">Détail de la session</h1>
    </div>

    <AppAlert
      v-if="apiError"
      v-model="showError"
      variant="error"
      title="Erreur"
      :message="apiError"
    />

    <AppCard>
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <div class="text-xs text-primary-light mb-1">Session</div>
          <div class="text-lg font-mono font-semibold">#{{ session?.session_id ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Patient</div>
          <div class="text-lg font-semibold">{{ session?.patient_id ? `#${session.patient_id}` : "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Debut</div>
          <div class="text-lg font-semibold">{{ formatDate(session?.started_at) }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Fin</div>
          <div class="text-lg font-semibold">{{ formatDate(session?.ended_at) }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Mode</div>
          <div class="text-lg font-semibold">{{ session?.mode ?? "-" }}</div>
        </div>
      </div>
    </AppCard>
    <AppCard>
      <div class="grid gap-4 md:grid-cols-2">
        <div>
          <div class="text-xs text-primary-light mb-1">Organisation</div>
          <div class="text-base font-semibold">{{ session?.organisation_id ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Utilisateur createur</div>
          <div class="text-base font-semibold">{{ session?.created_by_user_id ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Dispositif</div>
          <div class="text-base font-semibold">{{ session?.device_id ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Consentement</div>
          <div class="text-base font-semibold">{{ session?.consent_id ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Version app</div>
          <div class="text-base font-semibold">{{ session?.app_version ?? "-" }}</div>
        </div>
        <div>
          <div class="text-xs text-primary-light mb-1">Notes</div>
          <div class="text-base font-semibold">{{ session?.notes ?? "-" }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Actions -->
    <div class="flex gap-4 justify-start">
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
import { useResultsStore } from "@/stores/results.store";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();

const showError = ref(true);
const apiError = ref<string | null>(null);
const session = computed(() => resultsStore.current);
const isDeleting = ref(false);

function goBack() {
  router.back();
}

function formatDate(value?: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("fr-FR");
}
const handleDelete = async () => {
  if (!confirm('Êtes-vous sûr(e) de vouloir supprimer cette session ?')) {
    return;
  }

  try {
    isDeleting.value = true;
    const sessionId = Number(route.params.id);
    await resultsStore.deleteSession(sessionId);
    await router.push('/results');
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
    apiError.value = 'Erreur lors de la suppression de la session';
  } finally {
    isDeleting.value = false;
  }
};
onMounted(async () => {
  const sessionId = Number(route.params.id);
  if (!sessionId || Number.isNaN(sessionId)) {
    apiError.value = "Identifiant de session invalide.";
    return;
  }
  try {
    await resultsStore.fetchSessionById(sessionId);
  } catch (err) {
    apiError.value = resultsStore.error ?? "Erreur inconnue.";
  }
});
</script>

<style scoped>
</style>