<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import MainLayout from "@/layouts/MainLayout.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import EmptyLayout from "@/layouts/EmptyLayout.vue";

const route = useRoute();
const layout = computed(() => {
  if (route.path.startsWith("/login")) return AuthLayout;
  if (route.path.startsWith("/dev")) return EmptyLayout;
  return MainLayout;
});
</script>
