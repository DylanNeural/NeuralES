<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useDeviceStore } from "@/stores/devices.store";
import AppButton from "@/components/ui/AppButton.vue";
import AppCard from "@/components/ui/AppCard.vue";

const router = useRouter();
const deviceStore = useDeviceStore();
const deletingId = ref<string | null>(null);

onMounted(() => { deviceStore.fetchDevices(); });

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

async function handleDelete(id: string) {
  if (!confirm("Supprimer ce dispositif ?")) return;
  try {
    deletingId.value = id;
    await deviceStore.deleteDevice(id);
  } catch (err) {
    console.error("Erreur suppression:", err);
  } finally {
    deletingId.value = null;
  }
}

function goToDetail(id: string) { router.push(`/devices/${id}`); }
function goToEdit(id: string) { router.push(`/devices/${id}/edit`); }
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-foreground">Dispositifs</h1>
        <p class="text-sm text-muted-foreground mt-0.5">Gestion des équipements EEG</p>
      </div>
      <RouterLink to="/devices/new">
        <AppButton variant="primary">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nouveau dispositif
        </AppButton>
      </RouterLink>
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

    <!-- Empty -->
    <AppCard v-else-if="deviceStore.isEmpty">
      <div class="flex flex-col items-center py-10 text-center">
        <div class="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-3">
          <svg class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <p class="text-sm font-medium text-foreground mb-1">Aucun dispositif enregistré</p>
        <p class="text-xs text-muted-foreground mb-4">Ajoutez votre premier équipement EEG.</p>
        <RouterLink to="/devices/new">
          <AppButton variant="primary" size="sm">Créer un dispositif</AppButton>
        </RouterLink>
      </div>
    </AppCard>

    <!-- Table -->
    <AppCard v-else class="!p-0 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full text-left">
          <thead>
            <tr class="border-b border-border">
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Marque / Modèle</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">N° de série</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Connexion</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">État</th>
              <th class="py-3 px-5 text-xs font-medium text-muted-foreground uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="device in deviceStore.items"
              :key="device.device_id"
              class="border-b border-border/60 last:border-0 hover:bg-secondary/20 transition-colors"
            >
              <td class="py-3.5 px-5 text-sm font-medium text-foreground">{{ device.marque_modele }}</td>
              <td class="py-3.5 px-5 text-sm text-muted-foreground font-mono">{{ device.serial_number || "—" }}</td>
              <td class="py-3.5 px-5 text-sm text-foreground">{{ connectionMap[device.connection_type] || device.connection_type }}</td>
              <td class="py-3.5 px-5">
                <span
                  :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border', statusClasses[device.etat] || 'bg-secondary text-muted-foreground border-border']"
                >
                  {{ statusMap[device.etat] || device.etat }}
                </span>
              </td>
              <td class="py-3.5 px-5">
                <div class="flex gap-2">
                  <AppButton size="sm" variant="ghost" @click="goToDetail(device.device_id)">Voir</AppButton>
                  <AppButton size="sm" variant="secondary" @click="goToEdit(device.device_id)">Modifier</AppButton>
                  <AppButton
                    size="sm"
                    variant="danger"
                    :loading="deletingId === device.device_id"
                    @click="handleDelete(device.device_id)"
                  >
                    Supprimer
                  </AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppCard>
  </div>
</template>
