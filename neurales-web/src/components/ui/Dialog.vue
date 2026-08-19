<script setup lang="ts">
import { cn } from "@/lib/utils";
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue";

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

const panelRef = ref<HTMLElement | null>(null);
let lastFocused: HTMLElement | null = null;

function focusableEls(): HTMLElement[] {
  if (!panelRef.value) return [];
  return Array.from(
    panelRef.value.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  );
}

function onKey(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close");
  if (e.key === "Tab" && props.open) {
    // Piège à focus : empêche Tab/Shift+Tab de sortir de la boîte de dialogue.
    const els = focusableEls();
    if (els.length === 0) return;
    const first = els[0];
    const last = els[els.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      lastFocused = document.activeElement as HTMLElement | null;
      await nextTick();
      (focusableEls()[0] ?? panelRef.value)?.focus();
    } else {
      lastFocused?.focus();
    }
  }
);

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
          ref="panelRef"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          tabindex="-1"
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
