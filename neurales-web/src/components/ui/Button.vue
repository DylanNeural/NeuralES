<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = withDefaults(
  defineProps<{
    variant?: "default" | "outline" | "ghost" | "destructive" | "secondary" | "link";
    size?: "sm" | "md" | "lg" | "icon";
    disabled?: boolean;
    loading?: boolean;
    class?: string;
  }>(),
  { variant: "default", size: "md" }
);

const base =
  "inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 cursor-pointer select-none";

const variants = {
  default:
    "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
  outline:
    "border border-border bg-transparent text-foreground hover:bg-secondary hover:text-foreground",
  ghost:
    "text-muted-foreground hover:bg-secondary hover:text-foreground",
  destructive:
    "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm",
  secondary:
    "bg-secondary text-secondary-foreground hover:bg-secondary/80",
  link: "text-primary underline-offset-4 hover:underline p-0 h-auto",
};

const sizes = {
  sm: "h-8 px-3 text-xs",
  md: "h-9 px-4 text-sm",
  lg: "h-11 px-6 text-base",
  icon: "h-9 w-9 p-0",
};

const classes = cn(base, variants[props.variant], sizes[props.size], props.class);
</script>

<template>
  <button :class="classes" :disabled="disabled || loading" v-bind="$attrs">
    <svg
      v-if="loading"
      class="h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
    <slot />
  </button>
</template>
