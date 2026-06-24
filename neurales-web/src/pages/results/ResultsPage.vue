<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Sessions d'acquisition</h2>
        <p class="text-sm text-slate-500 mt-0.5">{{ sessions.length }} session{{ sessions.length !== 1 ? 's' : '' }} enregistrée{{ sessions.length !== 1 ? 's' : '' }}</p>
      </div>
      <AppButton variant="primary" @click="goToCreate">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nouvelle session
      </AppButton>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
      <table class="min-w-full table-auto">
        <thead>
          <tr>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Session</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Patient</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Début</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Mode</th>
            <th class="text-left py-3 px-5 text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/60 border-b border-slate-200">Fin</th>
            <th class="py-3 px-5 bg-slate-50/60 border-b border-slate-200 w-36"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="6" class="py-12 text-center">
              <div class="flex flex-col items-center gap-3 text-slate-400">
                <svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span class="text-sm">Chargement...</span>
              </div>
            </td>
          </tr>
          <tr v-else-if="sessions.length === 0">
            <td colspan="6" class="py-16 text-center">
              <div class="flex flex-col items-center gap-3">
                <div class="h-14 w-14 rounded-2xl bg-slate-100 grid place-items-center">
                  <svg class="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-slate-700">Aucune session</p>
                  <p class="text-xs text-slate-400 mt-0.5">Lancez une acquisition pour créer des sessions</p>
                </div>
              </div>
            </td>
          </tr>
          <tr
            v-else
            v-for="session in sessions"
            :key="session.session_id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/60 transition-colors"
          >
            <td class="py-3.5 px-5">
              <span class="text-sm font-mono font-medium text-slate-700">#{{ session.session_id }}</span>
            </td>
            <td class="py-3.5 px-5 text-sm text-slate-600">
              {{ session.patient_id ? `#${session.patient_id}` : '—' }}
            </td>
            <td class="py-3.5 px-5 text-sm text-slate-600">{{ formatDate(session.started_at) }}</td>
            <td class="py-3.5 px-5">
              <span v-if="session.mode" class="badge badge-indigo">{{ session.mode }}</span>
              <span v-else class="text-sm text-slate-400">—</span>
            </td>
            <td class="py-3.5 px-5 text-sm text-slate-600">{{ formatDate(session.ended_at) }}</td>
            <td class="py-3.5 px-5">
              <div class="flex items-center gap-2 justify-end">
                <AppButton class="!px-3 !py-1.5 !text-xs" @click="goToDetail(session.session_id)">Voir</AppButton>
                <AppButton class="!px-3 !py-1.5 !text-xs" @click="goToEdit(session.session_id)">Modifier</AppButton>
                <AppButton variant="danger" class="!px-3 !py-1.5 !text-xs" @click="handleDelete(session.session_id)">✕</AppButton>
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
import { useResultsStore } from "@/stores/results.store";

const router = useRouter();
const resultsStore = useResultsStore();

const sessions = computed(() => resultsStore.items);
const isLoading = computed(() => resultsStore.isLoading);

function formatDate(value?: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  return isNaN(d.getTime()) ? value : d.toLocaleString("fr-FR", { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function goToCreate() { router.push('/results/new'); }
function goToDetail(id: string) { router.push(`/results/${id}`); }
function goToEdit(id: string) { router.push(`/results/${id}/edit`); }

async function handleDelete(sessionId: string) {
  if (!confirm('Supprimer cette session ?')) return;
  try {
    await resultsStore.deleteSession(sessionId);
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
  }
}

onMounted(() => { resultsStore.fetchSessions(); });
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>
