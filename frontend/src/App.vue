<template>
  <router-view />
</template>

<script setup>
// This is the main App component.
// It renders the router-view, which handles the display of different screens based on the URL.
// The router is configured in src/router/index.js.

// Pinia setup would typically be done in main.js
// import { useScheduleStore } from './stores/scheduleStore';
// const store = useScheduleStore();
// Data loading should ideally happen within specific screen components or triggered by routing navigation.

</script>

<style scoped>
/* Add any global styles for the #app container here if needed */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left; /* Align content left */
  color: var(--color-very-dark-gray); /* Use CSS variable */
  height: 100vh; /* Ensure app container takes full height */
  overflow: hidden; /* Prevent scrollbars on #app if child handles it */
}

/* Remove default margin/padding if a layout component manages it */
body {
    margin: 0;
    padding: 0;
}

</style>
