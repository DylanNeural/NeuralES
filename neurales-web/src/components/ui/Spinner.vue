<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = withDefaults(
  defineProps<{
    size?: "sm" | "md" | "lg";
    class?: string;
  }>(),
  { size: "md" }
);

const sizes = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-10 w-10" };
const classes = cn("animate-spin text-primary", sizes[props.size], props.class);
</script>

<template>
  <svg
    :class="classes"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
    <path
      class="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
    />
  </svg>
</template>
