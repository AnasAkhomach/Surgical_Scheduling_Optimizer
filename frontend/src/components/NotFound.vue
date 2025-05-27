<template>
  <div>
    <h1>404 Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <router-link to="/">Go to Home</router-link>
  </div>
</template>

<script setup>
// No script needed for a simple 404 page
</script>

<style scoped>
div {
  text-align: center;
  padding: 50px;
}
h1 {
  color: var(--primary-color);
  margin-bottom: 20px;
}
</style>