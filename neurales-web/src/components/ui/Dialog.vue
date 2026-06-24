<script setup lang="ts">
import { cn } from "@/lib/utils";
import { onMounted, onUnmounted } from "vue";

const props = withDefaults(
  defineProps<{
    open?: boolean;
    title?: string;
    description?: string;
    size?: "sm" | "md" | "lg";
    class?: string;
  }>(),
  { open: false, size: "md" }
);

const emit = defineEmits<{ close: [] }>();

const sizes = {
  sm: "max-w-sm",
  md: "max-w-lg",
  lg: "max-w-2xl",
};

function onKey(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close");
}

onMounted(() => window.addEventListener("keydown", onKey));
onUnmounted(() => window.removeEventListener("keydown", onKey));
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="emit('close')"
        />
        <div
          :class="cn(
            'relative z-10 w-full rounded-2xl border border-border bg-card shadow-2xl animate-fade-in',
            sizes[size],
            props.class
          )"
        >
          <div class="p-6">
            <div v-if="title || $slots.title" class="mb-1">
              <slot name="title">
                <h2 class="text-lg font-semibold text-foreground">{{ title }}</h2>
              </slot>
            </div>
            <p v-if="description" class="text-sm text-muted-foreground mb-4">{{ description }}</p>
            <slot />
          </div>
          <div v-if="$slots.footer" class="border-t border-border px-6 py-4 flex gap-3 justify-end">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
