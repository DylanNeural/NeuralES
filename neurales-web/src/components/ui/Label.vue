<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = defineProps<{
  for?: string;
  required?: boolean;
  class?: string;
}>();

const classes = cn(
  "block text-sm font-medium text-foreground leading-none",
  props.class
);
</script>

<template>
  <label :for="props.for" :class="classes" v-bind="$attrs">
    <slot />
    <span v-if="required" class="ml-1 text-destructive">*</span>
  </label>
</template>
