<script setup lang="ts">
const props = defineProps<{
  modelValue?: boolean;
  variant?: "error" | "success" | "info" | "warning";
  title?: string;
  message?: string;
  details?: string;
}>();

const emit = defineEmits<{ "update:modelValue": [value: boolean] }>();

const variantClasses: Record<string, string> = {
  success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-400",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-400",
  info: "border-primary/40 bg-primary/10 text-primary",
  error: "border-destructive/40 bg-destructive/10 text-destructive",
};

const cls = variantClasses[props.variant ?? "error"];

function close() {
  emit("update:modelValue", false);
}
</script>

<template>
  <div v-if="modelValue !== false" :class="['rounded-xl border p-4 text-sm', cls]">
    <div class="flex items-start justify-between gap-4">
      <div>
        <div v-if="title" class="font-semibold mb-1">{{ title }}</div>
        <div v-if="message">{{ message }}</div>
        <div v-if="details" class="text-xs mt-1 opacity-80 font-mono">{{ details }}</div>
      </div>
      <button
        type="button"
        class="text-xs font-semibold opacity-70 hover:opacity-100 transition-opacity shrink-0"
        @click="close"
      >
        ✕
      </button>
    </div>
  </div>
</template>
