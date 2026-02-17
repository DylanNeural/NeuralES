<template>
  <button :class="classes" :type="type" :disabled="disabled">
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
const props = defineProps({
  type: { type: String as () => 'button' | 'reset' | 'submit', default: 'button' },
  variant: { type: String, default: 'primary' },
  disabled: { type: Boolean, default: false },
});

const classes = computed(() => {
  let base = 'btn';
  if (props.variant === 'primary') base += ' btn-primary';
  if (props.variant === 'danger') base += ' btn-danger';
  return base;
});
</script>

<style scoped>
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>