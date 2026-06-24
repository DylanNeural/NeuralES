<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppAlert from "@/components/ui/AppAlert.vue";
import AppCard from "@/components/ui/AppCard.vue";
import { usePatientsStore } from "@/stores/patients.store";
import { parseApiError, logError, type ApiError } from "@/utils/api-errors";
import * as PatientsAPI from "@/api/patients.api";
import {
  validatePatientName,
  validateSecurityNumber,
  validateInternalId,
  validateDate,
  hasErrors,
} from "@/utils/form-validation";

const router = useRouter();
const route = useRoute();
const patientsStore = usePatientsStore();

const isSubmitting = ref(false);
const apiError = ref<ApiError | null>(null);
const showError = ref(true);
const servicesOptions = ref<string[]>([]);
const medecinsOptions = ref<string[]>([]);
const isLoadingOptions = ref(false);
const isEdit = ref(!!route.params.id);

const form = reactive({
  identifiantInterne: "",
  nom: "",
  prenom: "",
  naissance: "",
  secu: "",
  sexe: "",
  service: "",
  medecin: "",
  remarque: "",
});

const errors = reactive({
  identifiantInterne: "",
  nom: "",
  prenom: "",
  naissance: "",
  secu: "",
  sexe: "",
});

onMounted(async () => {
  isLoadingOptions.value = true;
  try {
    const [services, medecins] = await Promise.all([PatientsAPI.listServices(), PatientsAPI.listMedecins()]);
    servicesOptions.value = services || [];
    medecinsOptions.value = medecins || [];
    if (isEdit.value) {
      const patientId = String(route.params.id);
      await patientsStore.fetchPatientById(patientId);
      const patient = patientsStore.current;
      if (patient) {
        form.identifiantInterne = patient.identifiant_interne || "";
        form.nom = patient.nom || "";
        form.prenom = patient.prenom || "";
        form.naissance = patient.date_naissance || "";
        form.secu = patient.numero_securite_sociale || "";
        form.sexe = patient.sexe || "";
        form.service = patient.service || "";
        form.medecin = patient.medecin_referent || "";
        form.remarque = patient.remarque || "";
      }
    }
  } catch (err) {
    logError(err, "PatientCreatePage.loadOptions");
  } finally {
    isLoadingOptions.value = false;
  }
});

function goBack() { router.back(); }

function resetErrors() {
  errors.identifiantInterne = "";
  errors.nom = "";
  errors.prenom = "";
  errors.naissance = "";
  errors.secu = "";
  errors.sexe = "";
  apiError.value = null;
  showError.value = true;
}

function onSecuInput(event: Event) {
  form.secu = (event.target as HTMLInputElement).value.replace(/\D/g, "");
}

function validateIdentifiant() { errors.identifiantInterne = validateInternalId(form.identifiantInterne).join(" "); }
function validateNom() { errors.nom = validatePatientName(form.nom).join(" "); }
function validatePrenom() { errors.prenom = validatePatientName(form.prenom).join(" "); }
function validateNaissance() { errors.naissance = validateDate(form.naissance).join(" "); }
function validateSecu() { errors.secu = validateSecurityNumber(form.secu).join(" "); }

function validate() {
  resetErrors();
  validateIdentifiant();
  validateNom();
  validatePrenom();
  validateNaissance();
  validateSecu();
  if (!form.sexe) errors.sexe = "Le sexe est obligatoire.";
  return !hasErrors(errors);
}

async function onSubmit() {
  if (!validate()) {
    apiError.value = { message: "Vérifiez les champs obligatoires.", details: "Validation locale échouée" };
    return;
  }
  isSubmitting.value = true;
  apiError.value = null;
  showError.value = true;
  try {
    const payload = {
      identifiant_interne: form.identifiantInterne.trim(),
      nom: form.nom.trim(),
      prenom: form.prenom.trim(),
      date_naissance: form.naissance,
      numero_securite_sociale: form.secu.trim() || undefined,
      sexe: form.sexe,
      service: form.service.trim() || undefined,
      medecin_referent: form.medecin.trim() || undefined,
      remarque: form.remarque.trim() || undefined,
    };
    if (isEdit.value) {
      await patientsStore.updatePatient(String(route.params.id), payload);
    } else {
      await patientsStore.createPatient(payload);
    }
    router.back();
  } catch (err: unknown) {
    logError(err, "PatientCreatePage.onSubmit");
    apiError.value = parseApiError(err);
  } finally {
    isSubmitting.value = false;
  }
}

const inputClass = "flex h-9 w-full rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 focus:ring-offset-background transition-colors";
const labelClass = "block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5";
const errorClass = "text-xs text-destructive mt-1";
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
      <h1 class="text-2xl font-bold text-foreground">
        {{ isEdit ? "Modifier le patient" : "Nouveau patient" }}
      </h1>
    </div>

    <!-- API error -->
    <AppAlert v-if="apiError" v-model="showError" variant="error" title="Erreur" :message="apiError.message" :details="apiError.details" />

    <!-- Form -->
    <AppCard>
      <form class="grid gap-5 md:grid-cols-2" @submit.prevent="onSubmit">
        <!-- Identifiant -->
        <div>
          <label :class="labelClass">Identifiant interne <span class="text-destructive">*</span></label>
          <input v-model="form.identifiantInterne" type="text" :class="inputClass" required placeholder="PAT-0001" @blur="validateIdentifiant" @input="validateIdentifiant" />
          <p v-if="errors.identifiantInterne" :class="errorClass">{{ errors.identifiantInterne }}</p>
        </div>

        <!-- Nom -->
        <div>
          <label :class="labelClass">Nom <span class="text-destructive">*</span></label>
          <input v-model="form.nom" type="text" :class="inputClass" required placeholder="Dupont" @blur="validateNom" @input="validateNom" />
          <p v-if="errors.nom" :class="errorClass">{{ errors.nom }}</p>
        </div>

        <!-- Prénom -->
        <div>
          <label :class="labelClass">Prénom <span class="text-destructive">*</span></label>
          <input v-model="form.prenom" type="text" :class="inputClass" required placeholder="Jean" @blur="validatePrenom" @input="validatePrenom" />
          <p v-if="errors.prenom" :class="errorClass">{{ errors.prenom }}</p>
        </div>

        <!-- Date naissance -->
        <div>
          <label :class="labelClass">Date de naissance <span class="text-destructive">*</span></label>
          <input v-model="form.naissance" type="date" :class="inputClass" required @blur="validateNaissance" @input="validateNaissance" />
          <p v-if="errors.naissance" :class="errorClass">{{ errors.naissance }}</p>
        </div>

        <!-- Sécu -->
        <div>
          <label :class="labelClass">N° sécurité sociale <span class="text-destructive">*</span></label>
          <input v-model="form.secu" type="text" :class="inputClass" required maxlength="13" placeholder="1234567890123" @input="onSecuInput" @blur="validateSecu" />
          <p v-if="errors.secu" :class="errorClass">{{ errors.secu }}</p>
          <p class="text-xs text-muted-foreground mt-1">13 chiffres requis</p>
        </div>

        <!-- Sexe -->
        <div>
          <label :class="labelClass">Sexe <span class="text-destructive">*</span></label>
          <select v-model="form.sexe" :class="inputClass" required>
            <option disabled value="">Sélectionner…</option>
            <option value="homme">Homme</option>
            <option value="femme">Femme</option>
          </select>
          <p v-if="errors.sexe" :class="errorClass">{{ errors.sexe }}</p>
        </div>

        <!-- Service -->
        <div>
          <label :class="labelClass">Service</label>
          <select v-model="form.service" :class="inputClass">
            <option value="">Aucun</option>
            <option v-for="s in servicesOptions" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <!-- Médecin -->
        <div>
          <label :class="labelClass">Médecin référent</label>
          <select v-model="form.medecin" :class="inputClass">
            <option value="">Aucun</option>
            <option v-for="m in medecinsOptions" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Remarque -->
        <div class="md:col-span-2">
          <label :class="labelClass">Remarque</label>
          <textarea v-model="form.remarque" :class="inputClass + ' min-h-[100px] resize-none'" />
        </div>

        <!-- Actions -->
        <div class="md:col-span-2 flex items-center justify-end gap-3 pt-2 border-t border-border">
          <AppButton type="button" variant="secondary" @click="goBack">Annuler</AppButton>
          <AppButton type="submit" variant="primary" :loading="isSubmitting">
            {{ isEdit ? "Enregistrer les modifications" : "Créer le patient" }}
          </AppButton>
        </div>
      </form>
    </AppCard>
  </div>
</template>
