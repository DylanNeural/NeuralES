<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = defineProps<{
  class?: string;
  hover?: boolean;
}>();
</script>

<template>
  <div
    :class="cn(
      'rounded-xl border border-border bg-card text-card-foreground shadow-sm p-6 transition-all duration-200',
      hover && 'hover:border-primary/40 hover:shadow-primary/10 hover:shadow-lg cursor-pointer',
      props.class
    )"
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>
