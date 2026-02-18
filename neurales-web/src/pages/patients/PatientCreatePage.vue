<template>
  <div class="space-y-8">
    <div class="flex items-center gap-3">
      <AppButton class="!px-3" @click="goBack">Retour</AppButton>
      <h1 class="text-3xl font-bold text-primary-dark">
        {{ isEdit ? "Modifier le patient" : "Creation d'un nouveau patient" }}
      </h1>
    </div>

    <AppAlert
      v-if="apiError"
      v-model="showError"
      variant="error"
      title="Erreur"
      :message="apiError.message"
      :details="apiError.details"
    />

    <div class="card">
      <form class="grid gap-5 md:grid-cols-2" @submit.prevent="onSubmit">
        <div>
          <label class="block text-xs text-slate-600 mb-1">Identifiant interne <span class="text-red-500">*</span></label>
          <input 
            v-model="form.identifiantInterne" 
            type="text" 
            class="input" 
            required 
            placeholder="PAT-0001"
            @blur="validateIdentifiant"
            @input="validateIdentifiant"
          />
          <p v-if="errors.identifiantInterne" class="text-xs text-red-600 mt-1">{{ errors.identifiantInterne }}</p>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Nom <span class="text-red-500">*</span></label>
          <input 
            v-model="form.nom" 
            type="text" 
            class="input" 
            required 
            placeholder="Dupont"
            @blur="validateNom"
            @input="validateNom"
          />
          <p v-if="errors.nom" class="text-xs text-red-600 mt-1">{{ errors.nom }}</p>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Prenom <span class="text-red-500">*</span></label>
          <input 
            v-model="form.prenom" 
            type="text" 
            class="input" 
            required 
            placeholder="Jean"
            @blur="validatePrenom"
            @input="validatePrenom"
          />
          <p v-if="errors.prenom" class="text-xs text-red-600 mt-1">{{ errors.prenom }}</p>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Date de naissance <span class="text-red-500">*</span></label>
          <input 
            v-model="form.naissance" 
            type="date" 
            class="input" 
            required
            @blur="validateNaissance"
            @input="validateNaissance"
          />
          <p v-if="errors.naissance" class="text-xs text-red-600 mt-1">{{ errors.naissance }}</p>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">N° de securite sociale <span class="text-red-500">*</span></label>
          <input 
            v-model="form.secu" 
            type="text" 
            class="input" 
            required 
            maxlength="13" 
            placeholder="1234567890123"
            @input="onSecuInput"
            @blur="validateSecu"
          />
          <p v-if="errors.secu" class="text-xs text-red-600 mt-1">{{ errors.secu }}</p>
          <p class="text-xs text-slate-500 mt-1">13 chiffres requis</p>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Sexe <span class="text-red-500">*</span></label>
          <select v-model="form.sexe" class="input" required>
            <option disabled value="">Selectionner...</option>
            <option value="homme">Homme</option>
            <option value="femme">Femme</option>
          </select>
          <p v-if="errors.sexe" class="text-xs text-red-600 mt-1">{{ errors.sexe }}</p>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Service</label>
          <select v-model="form.service" class="input">
            <option value="">Aucun</option>
            <option v-for="service in servicesOptions" :key="service" :value="service">
              {{ service }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Medecin referent</label>
          <select v-model="form.medecin" class="input">
            <option value="">Aucun</option>
            <option v-for="medecin in medecinsOptions" :key="medecin" :value="medecin">
              {{ medecin }}
            </option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="block text-xs text-slate-600 mb-1">Remarque</label>
          <textarea v-model="form.remarque" class="input min-h-[120px]"></textarea>
        </div>

        <div class="md:col-span-2 flex items-center justify-end gap-3">
          <AppButton type="button" @click="goBack">Annuler</AppButton>
          <AppButton variant="primary" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? (isEdit ? "Modification..." : "Enregistrement...") : (isEdit ? "Modifier" : "Enregistrer") }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppAlert from "@/components/ui/AppAlert.vue";
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
import { useRoute } from "vue-router";

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
    const [services, medecins] = await Promise.all([
      PatientsAPI.listServices(),
      PatientsAPI.listMedecins(),
    ]);
    servicesOptions.value = services || [];
    medecinsOptions.value = medecins || [];

    // Si mode édition, charger les données du patient
    if (isEdit.value) {
      const patientId = Number(route.params.id);
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
    console.warn("Failed to load data");
  } finally {
    isLoadingOptions.value = false;
  }
});

function goBack() {
  router.back();
}

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
  const input = event.target as HTMLInputElement;
  // Ne garder que les chiffres
  form.secu = input.value.replace(/\D/g, "");
}

function validateIdentifiant() {
  const validationErrors = validateInternalId(form.identifiantInterne);
  errors.identifiantInterne = validationErrors.length > 0 ? validationErrors.join(" ") : "";
}

function validateNom() {
  const validationErrors = validatePatientName(form.nom);
  errors.nom = validationErrors.length > 0 ? validationErrors.join(" ") : "";
}

function validatePrenom() {
  const validationErrors = validatePatientName(form.prenom);
  errors.prenom = validationErrors.length > 0 ? validationErrors.join(" ") : "";
}

function validateNaissance() {
  const validationErrors = validateDate(form.naissance);
  errors.naissance = validationErrors.length > 0 ? validationErrors.join(" ") : "";
}

function validateSecu() {
  const validationErrors = validateSecurityNumber(form.secu);
  errors.secu = validationErrors.length > 0 ? validationErrors.join(" ") : "";
}

function validate() {
  resetErrors();

  validateIdentifiant();
  validateNom();
  validatePrenom();
  validateNaissance();
  validateSecu();

  if (!form.sexe) {
    errors.sexe = "Le sexe est obligatoire.";
  }

  return !hasErrors(errors);
}

async function onSubmit() {
  if (!validate()) {
    apiError.value = {
      message: "Verifie les champs obligatoires.",
      details: "Validation locale echouee",
    };
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
      const patientId = Number(route.params.id);
      await patientsStore.updatePatient(patientId, payload);
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
</script>
