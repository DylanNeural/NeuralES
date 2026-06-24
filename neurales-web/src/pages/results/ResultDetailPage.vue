<template>
  <div class="max-w-3xl space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <AppButton @click="goBack">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </AppButton>
      <AppButton variant="danger" @click="handleDelete" :loading="isDeleting">
        Supprimer
      </AppButton>
    </div>

    <AppAlert v-if="apiError" v-model="showError" variant="error" title="Erreur" :message="apiError" />

    <!-- Session header -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <div class="flex items-center gap-5 flex-wrap">
        <div class="h-12 w-12 rounded-xl bg-primary-muted text-primary grid place-items-center shrink-0">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <div class="text-xs text-slate-400">Session</div>
          <div class="text-2xl font-bold font-mono text-slate-900">#{{ session?.session_id ?? '—' }}</div>
        </div>
        <div class="ml-auto flex items-center gap-4 flex-wrap">
          <div class="text-right">
            <div class="text-xs text-slate-400">Début</div>
            <div class="text-sm font-semibold text-slate-800">{{ formatDate(session?.started_at) }}</div>
          </div>
          <div class="text-right">
            <div class="text-xs text-slate-400">Fin</div>
            <div class="text-sm font-semibold text-slate-800">{{ formatDate(session?.ended_at) }}</div>
          </div>
          <span v-if="session?.mode" class="badge badge-indigo">{{ session.mode }}</span>
        </div>
      </div>
    </div>

    <!-- Details -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <div class="text-sm font-semibold text-slate-900 mb-5">Métadonnées</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
        <div v-for="field in fields" :key="field.label">
          <div class="text-xs text-slate-400 mb-1">{{ field.label }}</div>
          <div class="text-sm font-medium text-slate-800">{{ field.value || '—' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
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

function goBack() { router.back(); }

function formatDate(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  return isNaN(d.getTime()) ? value : d.toLocaleString("fr-FR");
}

const fields = computed(() => {
  const s = session.value;
  if (!s) return [];
  return [
    { label: 'Patient', value: s.patient_id ? `#${s.patient_id}` : null },
    { label: 'Dispositif', value: s.device_id ? `#${s.device_id}` : null },
    { label: 'Organisation', value: s.organisation_id ? `#${s.organisation_id}` : null },
    { label: 'Créé par', value: s.created_by_user_id ? `#${s.created_by_user_id}` : null },
    { label: 'Consentement', value: s.consent_id },
    { label: 'Version app', value: s.app_version },
    { label: 'Notes', value: s.notes },
  ];
});

const handleDelete = async () => {
  if (!confirm('Supprimer cette session ?')) return;
  try {
    isDeleting.value = true;
    await resultsStore.deleteSession(String(route.params.id));
    await router.push('/results');
  } catch {
    apiError.value = 'Erreur lors de la suppression de la session';
  } finally {
    isDeleting.value = false;
  }
};

onMounted(async () => {
  try {
    await resultsStore.fetchSessionById(String(route.params.id));
  } catch {
    apiError.value = resultsStore.error ?? "Erreur inconnue.";
  }
});
</script>
