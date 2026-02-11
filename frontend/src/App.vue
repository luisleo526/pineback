<template>
  <router-view />
</template>

<script setup>
// Root component — just renders the active route.
// Import useUIScale to apply the saved zoom level on app startup.
import { useUIScale } from './composables/useUIScale.js'
useUIScale()
</script>
