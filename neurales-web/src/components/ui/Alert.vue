<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = withDefaults(
  defineProps<{
    variant?: "default" | "destructive" | "success" | "warning";
    class?: string;
  }>(),
  { variant: "default" }
);

const variants = {
  default: "border-border bg-card text-foreground",
  destructive: "border-destructive/40 bg-destructive/10 text-destructive",
  success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-400",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-400",
};

const classes = cn(
  "relative w-full rounded-xl border p-4 text-sm [&>svg~*]:pl-7 [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:h-4 [&>svg]:w-4",
  variants[props.variant],
  props.class
);
</script>

<template>
  <div :class="classes" role="alert" v-bind="$attrs">
    <slot />
  </div>
</template>
