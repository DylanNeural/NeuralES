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

const route = useRoute();
const layout = computed(() => (route.path.startsWith("/login") ? AuthLayout : MainLayout));
</script>
