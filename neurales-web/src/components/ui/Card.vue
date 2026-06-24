<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = defineProps<{
  class?: string;
  hover?: boolean;
}>();

const classes = cn(
  "rounded-xl border border-border bg-card text-card-foreground shadow-sm transition-all duration-200",
  props.hover && "hover:border-primary/40 hover:shadow-primary/10 hover:shadow-lg cursor-pointer",
  props.class
);
</script>

<template>
  <div :class="classes" v-bind="$attrs">
    <slot />
  </div>
</template>
