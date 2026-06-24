<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useDeviceStore } from "@/stores/devices.store";
import type { DeviceCreatePayload } from "@/api/devices.api";
import AppButton from "@/components/ui/AppButton.vue";
import AppCard from "@/components/ui/AppCard.vue";
import { validateDeviceName, hasErrors } from "@/utils/form-validation";

const router = useRouter();
const route = useRoute();
const deviceStore = useDeviceStore();

const isEdit = !!route.params.id;
const isSubmitting = ref(false);
const error = ref<string | null>(null);

const form = reactive({
  marque_modele: "",
  serial_number: "",
  connection_type: "",
  etat: "actif",
});

const errors = reactive({ marque_modele: "", connection_type: "", etat: "" });

onMounted(async () => {
  if (isEdit) {
    try {
      const device = await deviceStore.fetchDeviceById(String(route.params.id));
      form.marque_modele = device.marque_modele;
      form.serial_number = device.serial_number || "";
      form.connection_type = device.connection_type;
      form.etat = device.etat;
    } catch (err) {
      error.value = "Erreur lors du chargement du dispositif";
    }
  }
});

function validateForm() {
  errors.marque_modele = "";
  errors.connection_type = "";
  errors.etat = "";
  error.value = null;
  const marqueErrs = validateDeviceName(form.marque_modele);
  if (marqueErrs.length) errors.marque_modele = marqueErrs.join(" ");
  if (!form.connection_type) errors.connection_type = "Le type de connexion est obligatoire.";
  if (!form.etat) errors.etat = "L'état est obligatoire.";
  return !hasErrors(errors);
}

function buildPayload(): DeviceCreatePayload {
  return {
    marque_modele: form.marque_modele.trim(),
    serial_number: form.serial_number.trim() || undefined,
    connection_type: form.connection_type,
    etat: form.etat,
  };
}

async function handleSubmit() {
  if (!validateForm()) { error.value = "Veuillez corriger les champs invalides"; return; }
  isSubmitting.value = true;
  error.value = null;
  try {
    const payload = buildPayload();
    if (isEdit) {
      await deviceStore.updateDevice(String(route.params.id), payload);
    } else {
      await deviceStore.createDevice(payload);
    }
    router.push("/devices");
  } catch (err: unknown) {
    const e = err as any;
    error.value = e?.response?.data?.detail || e?.message || "Une erreur est survenue";
  } finally {
    isSubmitting.value = false;
  }
}

const inputClass = "flex h-9 w-full rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 focus:ring-offset-background transition-colors";
const labelClass = "block text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5";
const errorClass = "text-xs text-destructive mt-1";
</script>

<template>
  <div class="max-w-2xl space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <RouterLink to="/devices">
        <AppButton variant="ghost" size="sm">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Retour
        </AppButton>
      </RouterLink>
      <h1 class="text-2xl font-bold text-foreground">{{ isEdit ? "Modifier le dispositif" : "Nouveau dispositif" }}</h1>
    </div>

    <!-- Error -->
    <div v-if="error" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ error }}
    </div>

    <AppCard>
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <!-- Marque / Modèle -->
        <div>
          <label :class="labelClass">Marque / Modèle <span class="text-destructive">*</span></label>
          <input
            v-model="form.marque_modele"
            type="text"
            :class="inputClass"
            required
            placeholder="Ex: Emotiv EPOC X"
            @input="() => { errors.marque_modele = validateDeviceName(form.marque_modele).join(' '); }"
            @blur="() => { errors.marque_modele = validateDeviceName(form.marque_modele).join(' '); }"
          />
          <p v-if="errors.marque_modele" :class="errorClass">{{ errors.marque_modele }}</p>
        </div>

        <!-- N° série -->
        <div>
          <label :class="labelClass">Numéro de série</label>
          <input v-model="form.serial_number" type="text" :class="inputClass" placeholder="Ex: SN123456789" />
        </div>

        <!-- Connexion -->
        <div>
          <label :class="labelClass">Type de connexion <span class="text-destructive">*</span></label>
          <select v-model="form.connection_type" :class="inputClass" required>
            <option value="">Sélectionner un type…</option>
            <option value="usb">USB</option>
            <option value="bluetooth">Bluetooth</option>
            <option value="ethernet">Ethernet</option>
            <option value="wifi">Wi-Fi</option>
          </select>
          <p v-if="errors.connection_type" :class="errorClass">{{ errors.connection_type }}</p>
        </div>

        <!-- État -->
        <div>
          <label :class="labelClass">État <span class="text-destructive">*</span></label>
          <select v-model="form.etat" :class="inputClass" required>
            <option value="">Sélectionner un état…</option>
            <option value="actif">Actif</option>
            <option value="inactif">Inactif</option>
            <option value="defaillant">Défaillant</option>
            <option value="maintenance">Maintenance</option>
          </select>
          <p v-if="errors.etat" :class="errorClass">{{ errors.etat }}</p>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-2 border-t border-border">
          <AppButton type="submit" variant="primary" :loading="isSubmitting">
            {{ isEdit ? "Mettre à jour" : "Créer" }}
          </AppButton>
          <RouterLink to="/devices">
            <AppButton type="button" variant="secondary">Annuler</AppButton>
          </RouterLink>
        </div>
      </form>
    </AppCard>
  </div>
</template>
