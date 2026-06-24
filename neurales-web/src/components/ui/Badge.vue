<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = withDefaults(
  defineProps<{
    variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning";
    class?: string;
  }>(),
  { variant: "default" }
);

const variants = {
  default: "bg-primary/15 text-primary border-primary/30",
  secondary: "bg-secondary text-secondary-foreground border-border",
  destructive: "bg-destructive/15 text-destructive border-destructive/30",
  outline: "bg-transparent text-foreground border-border",
  success: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
};

const classes = cn(
  "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  variants[props.variant],
  props.class
);
</script>

<template>
  <span :class="classes" v-bind="$attrs">
    <slot />
  </span>
</template>
