<template>
  <div v-if="show" :class="alertClasses" class="rounded-xl px-4 py-3 border flex items-start gap-3">
    <div class="flex-1">
      <div v-if="title" class="font-semibold text-sm mb-1">{{ title }}</div>
      <div class="text-sm">{{ message }}</div>
      <div v-if="details" class="text-xs opacity-75 mt-1">{{ details }}</div>
    </div>
    <button v-if="dismissible" class="text-lg leading-none opacity-75 hover:opacity-100" @click="close">
      ×
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

const props = defineProps({
  variant: {
    type: String as () => "info" | "success" | "warning" | "error",
    default: "info",
  },
  title: { type: String, default: "" },
  message: { type: String, required: true },
  details: { type: String, default: "" },
  dismissible: { type: Boolean, default: true },
  modelValue: { type: Boolean, default: true },
});

const emit = defineEmits<{ (e: "update:modelValue", value: boolean): void }>();

const show = ref(props.modelValue);

watch(
  () => props.modelValue,
  (val) => {
    show.value = val;
  }
);

const alertClasses = computed(() => {
  switch (props.variant) {
    case "success":
      return "bg-green-50 border-green-300 text-green-800";
    case "warning":
      return "bg-yellow-50 border-yellow-300 text-yellow-800";
    case "error":
      return "bg-red-50 border-red-300 text-red-800";
    default:
      return "bg-blue-50 border-blue-300 text-blue-800";
  }
});

function close() {
  show.value = false;
  emit("update:modelValue", false);
}
</script>
