<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
import AppButton from "@/components/ui/AppButton.vue";
import { useResultsStore } from "@/stores/results.store";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();

const apiError = ref<string | null>(null);
const session = computed(() => resultsStore.current);
const isDeleting = ref(false);

function goBack() { router.back(); }

function formatDate(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("fr-FR");
}

async function handleDelete() {
  if (!confirm("Supprimer cette session ?")) return;
  try {
    isDeleting.value = true;
    await resultsStore.deleteSession(String(route.params.id));
    router.push("/results");
  } catch {
    apiError.value = "Erreur lors de la suppression";
  } finally {
    isDeleting.value = false;
  }
}

onMounted(async () => {
  const id = String(route.params.id);
  if (!id) { apiError.value = "Identifiant invalide."; return; }
  try {
    await resultsStore.fetchSessionById(id);
  } catch {
    apiError.value = resultsStore.error ?? "Erreur inconnue.";
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
      <h1 class="text-2xl font-bold text-foreground">Détail de la session</h1>
    </div>

    <!-- Error -->
    <div v-if="apiError" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ apiError }}
    </div>

    <!-- Summary card -->
    <AppCard v-if="session">
      <div class="flex items-center gap-4 mb-6">
        <div class="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
          <svg class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-foreground font-mono">Session #{{ session.session_id }}</h2>
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20 mt-1">
            {{ session.mode || "—" }}
          </span>
        </div>
      </div>

      <!-- Meta grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 rounded-xl bg-secondary/20 border border-border">
        <div>
          <div class="text-xs text-muted-foreground mb-1">Patient</div>
          <div class="text-sm font-semibold text-foreground">{{ session.patient_id ? `#${session.patient_id}` : "—" }}</div>
        </div>
        <div>
          <div class="text-xs text-muted-foreground mb-1">Début</div>
          <div class="text-sm font-semibold text-foreground">{{ formatDate(session.started_at) }}</div>
        </div>
        <div>
          <div class="text-xs text-muted-foreground mb-1">Fin</div>
          <div class="text-sm font-semibold text-foreground">{{ formatDate(session.ended_at) }}</div>
        </div>
        <div>
          <div class="text-xs text-muted-foreground mb-1">Dispositif</div>
          <div class="text-sm font-semibold text-foreground">{{ session.device_id ?? "—" }}</div>
        </div>
      </div>

      <!-- Details -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="[label, value] in [
          ['Organisation', session.organisation_id],
          ['Utilisateur créateur', session.created_by_user_id],
          ['Consentement', session.consent_id],
          ['Version app', session.app_version],
          ['Notes', session.notes],
        ]" :key="label" class="space-y-1">
          <div class="text-xs text-muted-foreground font-medium uppercase tracking-wide">{{ label }}</div>
          <div class="text-sm font-medium text-foreground">{{ value ?? "—" }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Actions -->
    <div class="flex gap-3">
      <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">
        Supprimer
      </AppButton>
    </div>
  </div>
</template>
