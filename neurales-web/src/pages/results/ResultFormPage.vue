<template>
  <div class="space-y-8 max-w-3xl mx-auto">
    <div class="flex items-center gap-3">
      <AppButton class="!px-3" @click="goBack">Retour</AppButton>
      <h1 class="text-3xl font-bold text-primary-dark">
        {{ isEdit ? 'Modifier' : 'Créer' }} une session
      </h1>
    </div>

    <AppAlert
      v-if="apiError"
      v-model="showError"
      variant="error"
      title="Erreur"
      :message="apiError"
    />

    <AppCard>
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Mode -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Mode *
          </label>
          <input
            v-model="form.mode"
            type="text"
            placeholder="Mode de mesure"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            required
            @input="validateMode"
            @blur="validateMode"
          />
          <p v-if="errors.mode" class="text-red-600 text-sm mt-1">
            {{ errors.mode }}
          </p>
        </div>

        <!-- Début -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Date/Heure début *
          </label>
          <input
            v-model="form.started_at"
            type="datetime-local"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            required
            @input="validateStartDate"
            @blur="validateStartDate"
          />
          <p v-if="errors.started_at" class="text-red-600 text-sm mt-1">
            {{ errors.started_at }}
          </p>
        </div>

        <!-- Fin -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Date/Heure fin
          </label>
          <input
            v-model="form.ended_at"
            type="datetime-local"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            @input="validateEndDate"
            @blur="validateEndDate"
          />
          <p v-if="errors.ended_at" class="text-red-600 text-sm mt-1">
            {{ errors.ended_at }}
          </p>
        </div>

        <!-- Patient ID -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            ID Patient
          </label>
          <input
            v-model.number="form.patient_id"
            type="number"
            placeholder="Identifiant du patient"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Device ID -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            ID Dispositif
          </label>
          <input
            v-model.number="form.device_id"
            type="number"
            placeholder="Identifiant du dispositif"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Notes
          </label>
          <textarea
            v-model="form.notes"
            placeholder="Notes supplémentaires"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
          ></textarea>
        </div>

        <!-- Version App -->
        <div>
          <label class="block text-sm font-semibold text-primary-dark mb-2">
            Version App
          </label>
          <input
            v-model="form.app_version"
            type="text"
            placeholder="ex: 1.0.0"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Boutons -->
        <div class="flex gap-4 pt-4">
          <AppButton
            type="submit"
            :loading="isLoading"
          >
            {{ isEdit ? 'Mettre à jour' : 'Créer' }}
          </AppButton>
          <AppButton
            type="button"
            variant="secondary"
            @click="goBack"
          >
            Annuler
          </AppButton>
        </div>
      </form>
    </AppCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
import AppButton from "@/components/ui/AppButton.vue";
import AppAlert from "@/components/ui/AppAlert.vue";
import { useResultsStore } from "@/stores/results.store";
import { validateSessionName, validateDate, validateDuration, hasErrors } from "@/utils/form-validation";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();

const isEdit = ref(!!route.params.id);
const isLoading = ref(false);
const apiError = ref<string | null>(null);
const showError = ref(true);

const form = reactive({
  mode: "",
  started_at: "",
  ended_at: "",
  patient_id: null as number | null,
  device_id: null as number | null,
  notes: "",
  app_version: "",
});

const errors = reactive({
  mode: "",
  started_at: "",
  ended_at: "",
});

const goBack = () => {
  router.back();
};

const validateMode = () => {
  const errors_list = validateSessionName(form.mode);
  errors.mode = errors_list.length > 0 ? errors_list.join(" ") : "";
};

const validateStartDate = () => {
  const errors_list = validateDate(form.started_at);
  errors.started_at = errors_list.length > 0 ? errors_list.join(" ") : "";
};

const validateEndDate = () => {
  if (!form.ended_at) {
    errors.ended_at = "";
    return;
  }
  const errors_list = validateDate(form.ended_at);
  errors.ended_at = errors_list.length > 0 ? errors_list.join(" ") : "";
};

const validateForm = (): boolean => {
  errors.mode = "";
  errors.started_at = "";

  // Validation mode (nom de session)
  const modeErrors = validateSessionName(form.mode);
  if (modeErrors.length > 0) {
    errors.mode = modeErrors.join(" ");
  }

  // Validation date début
  const startDateErrors = validateDate(form.started_at);
  if (startDateErrors.length > 0) {
    errors.started_at = startDateErrors.join(" ");
  }

  // Validation date fin si présente
  if (form.ended_at) {
    const endDateErrors = validateDate(form.ended_at);
    if (endDateErrors.length > 0) {
      errors.ended_at = endDateErrors.join(" ");
    }
  }

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
      patient_id: form.patient_id,
      device_id: form.device_id,
      notes: form.notes,
      app_version: form.app_version,
    };

    if (isEdit.value) {
      const sessionId = Number(route.params.id);
      await resultsStore.updateSession(sessionId, payload);
      await router.push(`/results/${sessionId}`);
    } else {
      const newSession = await resultsStore.createSession(payload);
      await router.push(`/results/${newSession.session_id}`);
    }
  } catch (error: any) {
    apiError.value = error.response?.data?.detail || "Erreur lors de l'opération";
    console.error("Erreur:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  if (isEdit.value) {
    const sessionId = Number(route.params.id);
    try {
      await resultsStore.fetchSessionById(sessionId);
      const session = resultsStore.current;
      if (session) {
        form.mode = session.mode;
        form.started_at = session.started_at;
        form.ended_at = session.ended_at || "";
        form.patient_id = session.patient_id || null;
        form.device_id = session.device_id || null;
        form.notes = session.notes || "";
        form.app_version = session.app_version || "";
      }
    } catch (error) {
      apiError.value = "Erreur lors du chargement de la session";
    }
  }
});
</script>
