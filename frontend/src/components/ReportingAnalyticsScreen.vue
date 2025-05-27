<template>
  <div class="analytics-container">
    <!-- Analytics Navigation -->
    <div class="analytics-nav">
      <router-link to="/reporting-analytics" class="nav-item" exact-active-class="active">
        Dashboard
      </router-link>
      <router-link to="/reporting-analytics/utilization" class="nav-item" active-class="active">
        Utilization Reports
      </router-link>
      <router-link to="/reporting-analytics/efficiency" class="nav-item" active-class="active">
        Efficiency Reports
      </router-link>
      <router-link to="/reporting-analytics/custom" class="nav-item" active-class="active">
        Custom Reports
      </router-link>
    </div>

    <!-- Router View for Nested Routes -->
    <div class="analytics-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
// No additional logic needed - this component just serves as a container for nested routes
</script>

<style scoped>
.analytics-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.analytics-nav {
  display: flex;
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--spacing-md);
  overflow-x: auto;
}

.nav-item {
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text);
  text-decoration: none;
  border-bottom: 3px solid transparent;
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

.nav-item:hover {
  color: var(--color-primary);
  background-color: var(--color-background-hover);
}

.nav-item.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  background-color: var(--color-background-active);
}

.analytics-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

@media (max-width: 768px) {
  .analytics-nav {
    padding: 0;
  }

  .nav-item {
    padding: var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}
</style>