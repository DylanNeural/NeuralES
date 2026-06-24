<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = withDefaults(
  defineProps<{
    orientation?: "horizontal" | "vertical";
    class?: string;
  }>(),
  { orientation: "horizontal" }
);

const classes = cn(
  "shrink-0 bg-border",
  props.orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
  props.class
);
</script>

<template>
  <div :class="classes" v-bind="$attrs" />
</template>
