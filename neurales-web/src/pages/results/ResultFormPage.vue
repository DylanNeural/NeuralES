<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center gap-3">
      <AppButton @click="goBack">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </AppButton>
      <h2 class="text-xl font-semibold text-slate-900">
        {{ isEdit ? 'Modifier la session' : 'Nouvelle session' }}
      </h2>
    </div>

    <AppAlert v-if="apiError" v-model="showError" variant="error" title="Erreur" :message="apiError" />

    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div class="form-group">
          <label class="label">Mode <span class="text-red-500">*</span></label>
          <input v-model="form.mode" class="input" type="text" placeholder="fatigue, moteur, attention..." required
            @input="validateMode" @blur="validateMode" />
          <p v-if="errors.mode" class="text-xs text-red-600 mt-1">{{ errors.mode }}</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div class="form-group">
            <label class="label">Date/Heure début <span class="text-red-500">*</span></label>
            <input v-model="form.started_at" class="input" type="datetime-local" required
              @input="validateStartDate" @blur="validateStartDate" />
            <p v-if="errors.started_at" class="text-xs text-red-600 mt-1">{{ errors.started_at }}</p>
          </div>
          <div class="form-group">
            <label class="label">Date/Heure fin</label>
            <input v-model="form.ended_at" class="input" type="datetime-local"
              @input="validateEndDate" @blur="validateEndDate" />
            <p v-if="errors.ended_at" class="text-xs text-red-600 mt-1">{{ errors.ended_at }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div class="form-group">
            <label class="label">ID Patient</label>
            <input v-model="form.patient_id" class="input" type="text" placeholder="Identifiant du patient" />
          </div>
          <div class="form-group">
            <label class="label">ID Dispositif</label>
            <input v-model="form.device_id" class="input" type="text" placeholder="Identifiant du dispositif" />
          </div>
        </div>

        <div class="form-group">
          <label class="label">Notes</label>
          <textarea v-model="form.notes" class="input min-h-[80px] resize-y" placeholder="Observations supplémentaires..."></textarea>
        </div>

        <div class="form-group">
          <label class="label">Version app</label>
          <input v-model="form.app_version" class="input" type="text" placeholder="ex: 1.0.0" />
        </div>

        <div class="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <AppButton type="button" @click="goBack">Annuler</AppButton>
          <AppButton variant="primary" type="submit" :loading="isLoading">
            {{ isEdit ? 'Enregistrer les modifications' : 'Créer la session' }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppAlert from "@/components/ui/AppAlert.vue";
import { useResultsStore } from "@/stores/results.store";
import { validateSessionName, validateDate, hasErrors } from "@/utils/form-validation";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();

const isEdit = ref(!!route.params.id);
const isLoading = ref(false);
const apiError = ref<string | null>(null);
const showError = ref(true);

const form = reactive({ mode: "", started_at: "", ended_at: "", patient_id: null as string | null, device_id: null as string | null, notes: "", app_version: "" });
const errors = reactive({ mode: "", started_at: "", ended_at: "" });

const goBack = () => router.back();

const validateMode = () => { errors.mode = validateSessionName(form.mode).join(" "); };
const validateStartDate = () => { errors.started_at = validateDate(form.started_at).join(" "); };
const validateEndDate = () => { errors.ended_at = form.ended_at ? validateDate(form.ended_at).join(" ") : ""; };

const validateForm = () => {
  Object.assign(errors, { mode: "", started_at: "", ended_at: "" });
  errors.mode = validateSessionName(form.mode).join(" ");
  errors.started_at = validateDate(form.started_at).join(" ");
  if (form.ended_at) errors.ended_at = validateDate(form.ended_at).join(" ");
  return !hasErrors(errors);
};

const handleSubmit = async () => {
  if (!validateForm()) return;
  try {
    isLoading.value = true;
    apiError.value = null;
    const payload = {
      mode: form.mode,
      started_at: form.started_at,
      ended_at: form.ended_at || undefined,
      patient_id: form.patient_id ?? undefined,
      device_id: form.device_id ?? undefined,
      notes: form.notes,
      app_version: form.app_version,
    };
    if (isEdit.value) {
      await resultsStore.updateSession(String(route.params.id), payload);
      await router.push(`/results/${route.params.id}`);
    } else {
      const s = await resultsStore.createSession(payload);
      await router.push(`/results/${s.session_id}`);
    }
  } catch (err: any) {
    apiError.value = err.response?.data?.detail || "Erreur lors de l'opération";
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  if (isEdit.value) {
    try {
      await resultsStore.fetchSessionById(String(route.params.id));
      const s = resultsStore.current;
      if (s) {
        form.mode = s.mode;
        form.started_at = s.started_at;
        form.ended_at = s.ended_at || "";
        form.patient_id = s.patient_id || null;
        form.device_id = s.device_id || null;
        form.notes = s.notes || "";
        form.app_version = s.app_version || "";
      }
    } catch {
      apiError.value = "Erreur lors du chargement de la session";
    }
  }
});
</script>
