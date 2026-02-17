<template>
  <div class="fixed inset-0 bg-black/50 grid place-items-center z-50" @click.self="emit('close')">
    <div class="card w-full max-w-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Nouveau patient</h2>
        <button class="text-slate-500" type="button" @click="emit('close')">X</button>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-xs text-slate-600 mb-1">Nom</label>
          <input v-model="form.nom" class="input" required />
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Prenom</label>
          <input v-model="form.prenom" class="input" required />
        </div>

        <div>
          <label class="block text-xs text-slate-600 mb-1">Date de naissance</label>
          <input v-model="form.naissance" type="date" class="input" required />
        </div>

        <AppButton variant="primary" class="w-full" type="submit">Envoyer</AppButton>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import AppButton from "@/components/ui/AppButton.vue";

const emit = defineEmits<{
  (e: "close"): void;
  (e: "submit", payload: { nom: string; prenom: string; naissance: string }): void;
}>();

const form = reactive({
  nom: "",
  prenom: "",
  naissance: "",
});

function submit() {
  emit("submit", { ...form });
}
</script>
