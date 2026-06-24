<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useDeviceStore } from "@/stores/devices.store";
import AppButton from "@/components/ui/AppButton.vue";
import AppCard from "@/components/ui/AppCard.vue";

const router = useRouter();
const route = useRoute();
const deviceStore = useDeviceStore();
const isDeleting = ref(false);

onMounted(async () => {
  try { await deviceStore.fetchDeviceById(String(route.params.id)); }
  catch (err) { console.error("Erreur chargement:", err); }
});

const connectionMap: Record<string, string> = {
  usb: "USB", bluetooth: "Bluetooth", ethernet: "Ethernet", wifi: "Wi-Fi",
};
const statusMap: Record<string, string> = {
  actif: "Actif", inactif: "Inactif", defaillant: "Défaillant", maintenance: "Maintenance",
};
const statusClasses: Record<string, string> = {
  actif: "bg-eeg-emerald/10 text-eeg-emerald border-eeg-emerald/30",
  inactif: "bg-secondary text-muted-foreground border-border",
  defaillant: "bg-destructive/10 text-destructive border-destructive/30",
  maintenance: "bg-eeg-amber/10 text-eeg-amber border-eeg-amber/30",
};

async function handleDelete() {
  if (!confirm("Supprimer ce dispositif ?")) return;
  try {
    isDeleting.value = true;
    await deviceStore.deleteDevice(String(route.params.id));
    router.push("/devices");
  } catch (err) {
    console.error("Erreur suppression:", err);
  } finally {
    isDeleting.value = false;
  }
}

function goToEdit() { router.push(`/devices/${route.params.id}/edit`); }
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
      <h1 class="text-2xl font-bold text-foreground">Détail du dispositif</h1>
    </div>

    <!-- Loading -->
    <div v-if="deviceStore.isLoading" class="flex items-center justify-center py-16 text-muted-foreground text-sm">
      <svg class="h-5 w-5 animate-spin mr-2 text-primary" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      Chargement…
    </div>

    <!-- Error -->
    <div v-else-if="deviceStore.error" class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      {{ deviceStore.error }}
    </div>

    <!-- Device detail -->
    <AppCard v-else-if="deviceStore.current">
      <div class="flex items-center gap-4 mb-6">
        <div class="h-12 w-12 rounded-xl bg-eeg-violet/10 flex items-center justify-center shrink-0">
          <svg class="h-6 w-6 text-eeg-violet" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h2 class="text-xl font-bold text-foreground">{{ deviceStore.current.marque_modele }}</h2>
          <span
            :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border mt-1', statusClasses[deviceStore.current.etat] || 'bg-secondary text-muted-foreground border-border']"
          >
            {{ statusMap[deviceStore.current.etat] || deviceStore.current.etat }}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-1">
          <div class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Numéro de série</div>
          <div class="text-sm font-medium text-foreground font-mono">{{ deviceStore.current.serial_number || "—" }}</div>
        </div>
        <div class="space-y-1">
          <div class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Type de connexion</div>
          <div class="text-sm font-medium text-foreground">{{ connectionMap[deviceStore.current.connection_type] || deviceStore.current.connection_type }}</div>
        </div>
      </div>
    </AppCard>

    <!-- Actions -->
    <div class="flex gap-3">
      <AppButton variant="primary" @click="goToEdit">Modifier</AppButton>
      <AppButton variant="danger" :loading="isDeleting" @click="handleDelete">Supprimer</AppButton>
    </div>
  </div>
</template>
