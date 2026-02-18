<template>
  <div v-if="modelValue" :class="['rounded-xl border p-4', variantClasses]">
    <div class="flex items-start justify-between gap-4">
      <div>
        <div v-if="title" class="text-sm font-semibold" :class="titleClasses">{{ title }}</div>
        <div v-if="message" class="text-sm mt-1" :class="messageClasses">{{ message }}</div>
        <div v-if="details" class="text-xs mt-2 opacity-80" :class="messageClasses">{{ details }}</div>
      </div>
      <button
        type="button"
        class="text-xs font-semibold uppercase tracking-wide opacity-70 hover:opacity-100"
        :class="titleClasses"
        @click="close"
      >
        Fermer
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  modelValue?: boolean;
  variant?: "error" | "success" | "info" | "warning";
  title?: string;
  message?: string;
  details?: string;
}>();

const emit = defineEmits<{ "update:modelValue": [value: boolean] }>();

const variantClasses = computed(() => {
  switch (props.variant) {
    case "success":
      return "border-emerald-200 bg-emerald-50 text-emerald-900";
    case "warning":
      return "border-amber-200 bg-amber-50 text-amber-900";
    case "info":
      return "border-sky-200 bg-sky-50 text-sky-900";
    case "error":
    default:
      return "border-red-200 bg-red-50 text-red-900";
  }
});

const titleClasses = computed(() => {
  switch (props.variant) {
    case "success":
      return "text-emerald-900";
    case "warning":
      return "text-amber-900";
    case "info":
      return "text-sky-900";
    case "error":
    default:
      return "text-red-900";
  }
});

const messageClasses = computed(() => {
  switch (props.variant) {
    case "success":
      return "text-emerald-800";
    case "warning":
      return "text-amber-800";
    case "info":
      return "text-sky-800";
    case "error":
    default:
      return "text-red-800";
  }
});

function close() {
  emit("update:modelValue", false);
}
</script>
