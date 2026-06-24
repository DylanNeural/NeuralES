<template>
  <div :class="['bg-white rounded-2xl border border-slate-200/80 shadow-card', sizeClass]">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ size?: 'sm' | 'md' | 'lg' }>();

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'p-4';
  if (props.size === 'lg') return 'p-8';
  return 'p-6';
});
</script>
