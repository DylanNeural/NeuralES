<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppCard from "@/components/ui/AppCard.vue";
import AppButton from "@/components/ui/AppButton.vue";
import { useResultsStore } from "@/stores/results.store";
import { validateSessionName, validateDate, hasErrors } from "@/utils/form-validation";

const route = useRoute();
const router = useRouter();
const resultsStore = useResultsStore();

const isEdit = ref(!!route.params.id);
const isLoading = ref(false);
const apiError = ref<string | null>(null);

const form = reactive({
  mode: "",
  started_at: "",
  ended_at: "",
  patient_id: null as string | null,
  device_id: null as string | null,
  notes: "",
  app_version: "",
});

const errors = reactive({ mode: "", started_at: "", ended_at: "" });

function goBack() { router.back(); }

function validateMode() { errors.mode = validateSessionName(form.mode).join(" "); }
function validateStartDate() { errors.started_at = validateDate(form.started_at).join(" "); }
function validateEndDate() {
  errors.ended_at = form.ended_at ? validateDate(form.ended_at).join(" ") : "";
}

function validateForm() {
  errors.mode = "";
  errors.started_at = "";
  const modeErrs = validateSessionName(form.mode);
  if (modeErrs.length) errors.mode = modeErrs.join(" ");
  const startErrs = validateDate(form.started_at);
  if (startErrs.length) errors.started_at = startErrs.join(" ");
  if (form.ended_at) {
    const endErrs = validateDate(form.ended_at);
    if (endErrs.length) errors.ended_at = endErrs.join(" ");
  }
  return !hasErrors(errors);
}

async function handleSubmit() {
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
      const id = String(route.params.id);
      await resultsStore.updateSession(id, payload);
      router.push(`/results/${id}`);
    } else {
      const s = await resultsStore.createSession(payload);
      router.push(`/results/${s.session_id}`);
    }
  } catch (err: any) {
    apiError.value = err.response?.data?.detail || "Erreur lors de l'opération";
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  if (isEdit.value) {
    const id = String(route.params.id);
    try {
      await resultsStore.fetchSessionById(id);
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

const inputClass = "flex h-9 w-full rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 focus:ring-offset-background transition-colors";
const labelClass = "block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5";
const errorClass = "text-xs text-destructive mt-1";
</script>

<template>
  <div class="max-w-2xl space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <AppButton variant="ghost" size="sm" @click="goBack">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour
      </AppButton>
      <h1 class="text-2xl font-bold text-foreground">{{ isEdit ? "Modifier" : "Créer" }} une session</h1>
    </div>

    <!-- API error -->
    <div v-if="apiError" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ apiError }}
    </div>

    <AppCard>
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label :class="labelClass">Mode <span class="text-destructive">*</span></label>
          <input v-model="form.mode" type="text" :class="inputClass" placeholder="Mode de mesure" required @input="validateMode" @blur="validateMode" />
          <p v-if="errors.mode" :class="errorClass">{{ errors.mode }}</p>
        </div>

        <div>
          <label :class="labelClass">Date/Heure début <span class="text-destructive">*</span></label>
          <input v-model="form.started_at" type="datetime-local" :class="inputClass" required @input="validateStartDate" @blur="validateStartDate" />
          <p v-if="errors.started_at" :class="errorClass">{{ errors.started_at }}</p>
        </div>

        <div>
          <label :class="labelClass">Date/Heure fin</label>
          <input v-model="form.ended_at" type="datetime-local" :class="inputClass" @input="validateEndDate" @blur="validateEndDate" />
          <p v-if="errors.ended_at" :class="errorClass">{{ errors.ended_at }}</p>
        </div>

        <div>
          <label :class="labelClass">ID Patient</label>
          <input v-model="form.patient_id" type="text" :class="inputClass" placeholder="Identifiant du patient" />
        </div>

        <div>
          <label :class="labelClass">ID Dispositif</label>
          <input v-model="form.device_id" type="text" :class="inputClass" placeholder="Identifiant du dispositif" />
        </div>

        <div>
          <label :class="labelClass">Notes</label>
          <textarea v-model="form.notes" :class="inputClass + ' min-h-[80px] resize-none'" placeholder="Notes supplémentaires" />
        </div>

        <div>
          <label :class="labelClass">Version App</label>
          <input v-model="form.app_version" type="text" :class="inputClass" placeholder="ex: 1.0.0" />
        </div>

        <div class="flex gap-3 pt-2 border-t border-border">
          <AppButton type="submit" variant="primary" :loading="isLoading">
            {{ isEdit ? "Mettre à jour" : "Créer" }}
          </AppButton>
          <AppButton type="button" variant="secondary" @click="goBack">Annuler</AppButton>
        </div>
      </form>
    </AppCard>
  </div>
</template>
