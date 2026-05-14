<template>
  <AppShell v-if="auth.isAuthenticated">
    <RouterView />
  </AppShell>
  <RouterView v-else />
</template>

<script setup>
import { RouterView } from 'vue-router';

import AppShell from './components/AppShell.vue';
import { useAuthStore } from './stores/auth';

const auth = useAuthStore();
</script>
