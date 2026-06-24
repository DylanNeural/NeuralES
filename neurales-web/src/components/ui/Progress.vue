<script setup lang="ts">
import { cn } from "@/lib/utils";
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    value?: number;
    max?: number;
    color?: "primary" | "cyan" | "emerald" | "violet" | "rose" | "amber";
    class?: string;
  }>(),
  { value: 0, max: 100, color: "primary" }
);

const pct = computed(() => Math.min(100, Math.max(0, (props.value / props.max) * 100)));

const barColors = {
  primary: "bg-primary",
  cyan: "bg-eeg-cyan",
  emerald: "bg-eeg-emerald",
  violet: "bg-eeg-violet",
  rose: "bg-eeg-rose",
  amber: "bg-eeg-amber",
};
</script>

<template>
  <div
    :class="cn('relative h-2 w-full overflow-hidden rounded-full bg-secondary', props.class)"
    role="progressbar"
    :aria-valuenow="value"
    :aria-valuemax="max"
  >
    <div
      :class="cn('h-full rounded-full transition-all duration-500 ease-out', barColors[color])"
      :style="{ width: pct + '%' }"
    />
  </div>
</template>
