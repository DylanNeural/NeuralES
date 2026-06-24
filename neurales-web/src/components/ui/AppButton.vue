<template>
  <button :class="classes" :type="type" :disabled="disabled || loading">
    <svg
      v-if="loading"
      class="w-4 h-4 animate-spin shrink-0"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  type?: 'button' | 'reset' | 'submit';
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  disabled?: boolean;
  loading?: boolean;
}>();

const classes = computed(() => {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all duration-150 cursor-pointer select-none disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]';
  if (props.variant === 'primary')   return `${base} bg-primary text-white shadow-sm hover:bg-primary/90`;
  if (props.variant === 'danger')    return `${base} bg-accent text-white shadow-sm hover:bg-red-500`;
  if (props.variant === 'ghost')     return `${base} text-slate-600 hover:bg-slate-100 hover:text-slate-900`;
  return `${base} bg-white text-slate-700 border border-slate-200 hover:bg-slate-50`;
});
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>
