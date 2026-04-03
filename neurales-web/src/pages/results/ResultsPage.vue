<template>
  <div class="space-y-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-primary-dark">Sessions</h1>
      <AppButton variant="primary" @click="goToCreate">
        Nouvelle session
      </AppButton>
    </div>

    <div class="card overflow-x-auto">
      <table class="min-w-full text-left">
        <thead>
          <tr class="text-primary-light uppercase text-xs tracking-widest border-b border-primary-light/20">
            <th class="py-3 px-4">Session</th>
            <th class="py-3 px-4">Patient</th>
            <th class="py-3 px-4">Debut</th>
            <th class="py-3 px-4">Mode</th>
            <th class="py-3 px-4">Fin</th>
            <th class="py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="6" class="py-6 px-4 text-center text-sm text-slate-500">Chargement...</td>
          </tr>
          <tr v-else-if="sessions.length === 0">
            <td colspan="6" class="py-6 px-4 text-center text-sm text-slate-500">Aucune session</td>
          </tr>
          <tr
            v-else
            v-for="session in sessions"
            :key="session.session_id"
            class="border-b last:border-0 border-primary-light/10 hover:bg-primary-light/5"
          >
            <td class="py-3 px-4 font-mono">#{{ session.session_id }}</td>
            <td class="py-3 px-4">
              {{ session.patient_id ? `#${session.patient_id}` : "-" }}
            </td>
            <td class="py-3 px-4">{{ formatDate(session.started_at) }}</td>
            <td class="py-3 px-4">{{ session.mode }}</td>
            <td class="py-3 px-4">{{ formatDate(session.ended_at) }}</td>
            <td class="py-3 px-4">
              <div class="flex gap-2">
                <AppButton
                  variant="primary"
                  class="!px-3 !py-1 text-sm"
                  @click="goToDetail(session.session_id)"
                >
                  Voir
                </AppButton>
                <router-link :to="`/results/${session.session_id}/edit`">
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
                  @click="handleDelete(session.session_id)"
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
import { useResultsStore } from "@/stores/results.store";

const router = useRouter();
const resultsStore = useResultsStore();

const sessions = computed(() => resultsStore.items);
const isLoading = computed(() => resultsStore.isLoading);

function formatDate(value?: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("fr-FR");
}

function goToCreate() {
  router.push('/results/new');
}

function goToDetail(sessionId: number) {
  router.push(`/results/${sessionId}`);
}

async function handleDelete(sessionId: number) {
  if (!confirm('Êtes-vous sûr(e) de vouloir supprimer cette session ?')) {
    return;
  }
  try {
    await resultsStore.deleteSession(sessionId);
  } catch (error) {
    console.error('Erreur lors de la suppression:', error);
  }
}

onMounted(() => {
  resultsStore.fetchSessions();
});
</script>

<style scoped>
table {
  border-collapse: separate;
  border-spacing: 0;
}
</style>