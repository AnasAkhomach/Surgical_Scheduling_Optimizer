<template>
  <div class="sdst-management-container">
    <h1>SDST Data Management</h1>
    <p class="description">
      Manage Sequence-Dependent Setup Times (SDST) data, including surgery types, 
      setup time matrix, and initial setup times.
    </p>

    <!-- Tab Navigation -->
    <div class="tabs-container">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          class="tab-button" 
          :class="{ 'active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Surgery Types Tab -->
      <div v-if="activeTab === 'surgeryTypes'" class="tab-pane">
        <h2>Surgery Types</h2>
        <p>Define and manage surgery types used for SDST calculations.</p>
        <p class="placeholder-message">Surgery Types management will be implemented in the next iteration.</p>
      </div>

      <!-- SDST Matrix Tab -->
      <div v-if="activeTab === 'sdstMatrix'" class="tab-pane">
        <h2>SDST Matrix</h2>
        <p>Define setup times between pairs of surgery types.</p>
        <p class="placeholder-message">SDST Matrix management will be implemented in the next iteration.</p>
      </div>

      <!-- Initial Setup Times Tab -->
      <div v-if="activeTab === 'initialSetupTimes'" class="tab-pane">
        <h2>Initial Setup Times</h2>
        <p>Define setup times for the first surgery of the day in an OR.</p>
        <p class="placeholder-message">Initial Setup Times management will be implemented in the next iteration.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Define tabs
const tabs = [
  { id: 'surgeryTypes', label: 'Surgery Types' },
  { id: 'sdstMatrix', label: 'SDST Matrix' },
  { id: 'initialSetupTimes', label: 'Initial Setup Times' }
];

// Active tab state
const activeTab = ref('surgeryTypes');
</script>

<style scoped>
.sdst-management-container {
  padding: var(--spacing-md);
  background-color: var(--color-background);
  color: var(--color-text);
  height: calc(100vh - 60px); /* Assuming header is 60px */
  display: flex;
  flex-direction: column;
}

h1 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
}

.description {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-secondary);
}

.tabs-container {
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.tabs {
  display: flex;
  gap: var(--spacing-xs);
}

.tab-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-weight: var(--font-weight-medium);
  transition: all 0.2s ease;
}

.tab-button:hover {
  color: var(--color-primary);
  background-color: var(--color-background-hover);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  background-color: var(--color-background-active);
}

.tab-content {
  flex-grow: 1;
  overflow-y: auto;
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
}

.tab-pane {
  height: 100%;
}

h2 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--spacing-sm);
}

.placeholder-message {
  padding: var(--spacing-md);
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-primary);
  margin-top: var(--spacing-lg);
  color: var(--color-text-secondary);
  font-style: italic;
}
</style>
