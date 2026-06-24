<template>
  <div class="max-w-2xl space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <AppButton @click="goBack">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour
      </AppButton>
      <h2 class="text-xl font-semibold text-slate-900">
        {{ isEdit ? "Modifier le patient" : "Nouveau patient" }}
      </h2>
    </div>

    <AppAlert
      v-if="apiError"
      v-model="showError"
      variant="error"
      title="Erreur"
      :message="apiError.message"
      :details="apiError.details"
    />

    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-card p-6">
      <form class="grid gap-5 sm:grid-cols-2" @submit.prevent="onSubmit">
        <div class="form-group">
          <label class="label">Identifiant interne <span class="text-red-500">*</span></label>
          <input v-model="form.identifiantInterne" class="input" type="text" required placeholder="PAT-0001"
            @blur="validateIdentifiant" @input="validateIdentifiant" />
          <p v-if="errors.identifiantInterne" class="text-xs text-red-600 mt-1">{{ errors.identifiantInterne }}</p>
        </div>

        <div class="form-group">
          <label class="label">Nom <span class="text-red-500">*</span></label>
          <input v-model="form.nom" class="input" type="text" required placeholder="Dupont"
            @blur="validateNom" @input="validateNom" />
          <p v-if="errors.nom" class="text-xs text-red-600 mt-1">{{ errors.nom }}</p>
        </div>

        <div class="form-group">
          <label class="label">Prénom <span class="text-red-500">*</span></label>
          <input v-model="form.prenom" class="input" type="text" required placeholder="Jean"
            @blur="validatePrenom" @input="validatePrenom" />
          <p v-if="errors.prenom" class="text-xs text-red-600 mt-1">{{ errors.prenom }}</p>
        </div>

        <div class="form-group">
          <label class="label">Date de naissance <span class="text-red-500">*</span></label>
          <input v-model="form.naissance" class="input" type="date" required
            @blur="validateNaissance" @input="validateNaissance" />
          <p v-if="errors.naissance" class="text-xs text-red-600 mt-1">{{ errors.naissance }}</p>
        </div>

        <div class="form-group">
          <label class="label">N° sécurité sociale <span class="text-red-500">*</span></label>
          <input v-model="form.secu" class="input" type="text" required maxlength="13"
            placeholder="1234567890123" @input="onSecuInput" @blur="validateSecu" />
          <p v-if="errors.secu" class="text-xs text-red-600 mt-1">{{ errors.secu }}</p>
          <p v-else class="text-xs text-slate-400 mt-1">13 chiffres requis</p>
        </div>

        <div class="form-group">
          <label class="label">Sexe <span class="text-red-500">*</span></label>
          <select v-model="form.sexe" class="input" required>
            <option disabled value="">Sélectionner...</option>
            <option value="homme">Homme</option>
            <option value="femme">Femme</option>
          </select>
          <p v-if="errors.sexe" class="text-xs text-red-600 mt-1">{{ errors.sexe }}</p>
        </div>

        <div class="form-group">
          <label class="label">Service</label>
          <select v-model="form.service" class="input">
            <option value="">Aucun</option>
            <option v-for="s in servicesOptions" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="label">Médecin référent</label>
          <select v-model="form.medecin" class="input">
            <option value="">Aucun</option>
            <option v-for="m in medecinsOptions" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <div class="form-group sm:col-span-2">
          <label class="label">Remarque</label>
          <textarea v-model="form.remarque" class="input min-h-[100px] resize-y" placeholder="Observations cliniques..."></textarea>
        </div>

        <div class="sm:col-span-2 flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <AppButton type="button" @click="goBack">Annuler</AppButton>
          <AppButton variant="primary" type="submit" :loading="isSubmitting">
            {{ isEdit ? "Enregistrer les modifications" : "Créer le patient" }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import AppButton from "@/components/ui/AppButton.vue";
import AppAlert from "@/components/ui/AppAlert.vue";
import { usePatientsStore } from "@/stores/patients.store";
import { parseApiError, logError, type ApiError } from "@/utils/api-errors";
import * as PatientsAPI from "@/api/patients.api";
import { validatePatientName, validateSecurityNumber, validateInternalId, validateDate, hasErrors } from "@/utils/form-validation";

const router = useRouter();
const route = useRoute();
const patientsStore = usePatientsStore();

const isSubmitting = ref(false);
const apiError = ref<ApiError | null>(null);
const showError = ref(true);
const servicesOptions = ref<string[]>([]);
const medecinsOptions = ref<string[]>([]);
const isEdit = ref(!!route.params.id);

const form = reactive({ identifiantInterne: "", nom: "", prenom: "", naissance: "", secu: "", sexe: "", service: "", medecin: "", remarque: "" });
const errors = reactive({ identifiantInterne: "", nom: "", prenom: "", naissance: "", secu: "", sexe: "" });

onMounted(async () => {
  try {
    const [services, medecins] = await Promise.all([PatientsAPI.listServices(), PatientsAPI.listMedecins()]);
    servicesOptions.value = services || [];
    medecinsOptions.value = medecins || [];
    if (isEdit.value) {
      await patientsStore.fetchPatientById(String(route.params.id));
      const p = patientsStore.current;
      if (p) {
        form.identifiantInterne = p.identifiant_interne || "";
        form.nom = p.nom || "";
        form.prenom = p.prenom || "";
        form.naissance = p.date_naissance || "";
        form.secu = p.numero_securite_sociale || "";
        form.sexe = p.sexe || "";
        form.service = p.service || "";
        form.medecin = p.medecin_referent || "";
        form.remarque = p.remarque || "";
      }
    }
  } catch (err) {
    logError(err, "PatientCreatePage.loadOptions");
  }
});

function goBack() { router.back(); }
function onSecuInput(e: Event) { form.secu = (e.target as HTMLInputElement).value.replace(/\D/g, ""); }
function validateIdentifiant() { errors.identifiantInterne = validateInternalId(form.identifiantInterne).join(" "); }
function validateNom() { errors.nom = validatePatientName(form.nom).join(" "); }
function validatePrenom() { errors.prenom = validatePatientName(form.prenom).join(" "); }
function validateNaissance() { errors.naissance = validateDate(form.naissance).join(" "); }
function validateSecu() { errors.secu = validateSecurityNumber(form.secu).join(" "); }

function validate() {
  Object.assign(errors, { identifiantInterne: "", nom: "", prenom: "", naissance: "", secu: "", sexe: "" });
  apiError.value = null;
  showError.value = true;
  validateIdentifiant(); validateNom(); validatePrenom(); validateNaissance(); validateSecu();
  if (!form.sexe) errors.sexe = "Le sexe est obligatoire.";
  return !hasErrors(errors);
}

async function onSubmit() {
  if (!validate()) {
    apiError.value = { message: "Vérifie les champs obligatoires.", details: "Validation locale échouée" };
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
</script>
