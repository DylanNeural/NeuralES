<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = defineProps<{
  modelValue?: string | number;
  placeholder?: string;
  type?: string;
  disabled?: boolean;
  error?: boolean;
  class?: string;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const classes = cn(
  "flex h-9 w-full rounded-lg border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground",
  "transition-colors duration-150",
  "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 focus:ring-offset-background",
  "disabled:cursor-not-allowed disabled:opacity-50",
  props.error ? "border-destructive focus:ring-destructive" : "border-border",
  props.class
);
</script>

<template>
  <input
    :class="classes"
    :type="type ?? 'text'"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    v-bind="$attrs"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
