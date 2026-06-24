<script setup lang="ts">
import { cn } from "@/lib/utils";
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    src?: string;
    alt?: string;
    name?: string;
    size?: "sm" | "md" | "lg";
    class?: string;
  }>(),
  { size: "md" }
);

const sizes = { sm: "h-7 w-7 text-xs", md: "h-9 w-9 text-sm", lg: "h-12 w-12 text-base" };

const initials = computed(() => {
  if (!props.name) return "?";
  return props.name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
});

const classes = cn(
  "relative flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/20 font-semibold text-primary ring-2 ring-primary/30",
  sizes[props.size],
  props.class
);
</script>

<template>
  <div :class="classes" v-bind="$attrs">
    <img v-if="src" :src="src" :alt="alt" class="h-full w-full object-cover" />
    <span v-else>{{ initials }}</span>
  </div>
</template>
