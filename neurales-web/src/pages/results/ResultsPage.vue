<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppCard from "@/components/ui/AppCard.vue";
import { useResultsStore } from "@/stores/results.store";

const router = useRouter();
const resultsStore = useResultsStore();
const sessions = computed(() => resultsStore.items);
const isLoading = computed(() => resultsStore.isLoading);

function formatDate(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("fr-FR");
}

function goToCreate() { router.push("/results/new"); }
function goToDetail(id: string) { router.push(`/results/${id}`); }
function goToEdit(id: string) { router.push(`/results/${id}/edit`); }

async function handleDelete(id: string) {
  if (!confirm("Supprimer cette session ?")) return;
  try { await resultsStore.deleteSession(id); }
  catch (err) { console.error("Erreur suppression:", err); }
}

onMounted(() => { resultsStore.fetchSessions(); });
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-foreground">Résultats & Sessions</h1>
        <p class="text-sm text-muted-foreground mt-0.5">Historique des sessions d'acquisition EEG</p>
      </div>
      <AppButton variant="primary" @click="goToCreate">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nouvelle session
      </AppButton>
    </div>

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
      <div v-else-if="sessions.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
        <div class="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-3">
          <svg class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <p class="text-sm font-medium text-foreground mb-1">Aucune session</p>
        <p class="text-xs text-muted-foreground mb-4">Démarrez une acquisition pour créer la première session.</p>
        <AppButton variant="primary" size="sm" @click="goToCreate">Créer une session</AppButton>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-left">
          <thead>
            <tr class="border-b border-border">
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Session</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Patient</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Début</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Mode</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Fin</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="session in sessions"
              :key="session.session_id"
              class="border-b border-border/60 last:border-0 hover:bg-secondary/20 transition-colors"
            >
              <td class="py-3.5 px-5 font-mono text-xs text-muted-foreground">#{{ session.session_id }}</td>
              <td class="py-3.5 px-5 text-sm text-foreground">{{ session.patient_id ? `#${session.patient_id}` : "—" }}</td>
              <td class="py-3.5 px-5 text-sm text-muted-foreground">{{ formatDate(session.started_at) }}</td>
              <td class="py-3.5 px-5">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20">
                  {{ session.mode || "—" }}
                </span>
              </td>
              <td class="py-3.5 px-5 text-sm text-muted-foreground">{{ formatDate(session.ended_at) }}</td>
              <td class="py-3.5 px-5">
                <div class="flex gap-2">
                  <AppButton size="sm" variant="ghost" @click="goToDetail(session.session_id)">Voir</AppButton>
                  <AppButton size="sm" variant="secondary" @click="goToEdit(session.session_id)">Modifier</AppButton>
                  <AppButton size="sm" variant="danger" @click="handleDelete(session.session_id)">Supprimer</AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppCard>
  </div>
</template>
