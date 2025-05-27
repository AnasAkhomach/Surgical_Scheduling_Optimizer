
<template>
  <div class="surgery-scheduling-screen">
    <!-- Assuming a header/layout component is outside this -->
    <div class="surgery-scheduling-layout">

      <!-- Left Panel: Pending Surgeries List -->
      <div class="pending-surgeries-panel">
        <PendingSurgeriesList />
      </div>

      <!-- Main Content Area: Gantt Chart -->
      <div class="main-schedule-area">
        <!-- Add Filters/Controls row here later if needed -->
        <GanttChart />
      </div>

      <!-- Right Panel: Surgery Details -->
      <div class="details-panel-container">
         <!-- SurgeryDetailsPanel is inside this container -->
        <SurgeryDetailsPanel />
      </div>

    </div>
     <!-- Optional: Loading indicator for the whole screen -->
    <div v-if="store.isLoading" class="loading-overlay">Loading...</div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import PendingSurgeriesList from './PendingSurgeriesList.vue';
import GanttChart from './GanttChart.vue';
import SurgeryDetailsPanel from './SurgeryDetailsPanel.vue';

const store = useScheduleStore();

// Load initial data when the screen component is mounted
onMounted(() => {
    store.loadInitialData();
});

</script>

<style scoped>
/* Styles for the main screen layout */
.surgery-scheduling-screen {
    display: flex;
    flex-direction: column;
    height: 100vh; /* Full viewport height */
    overflow: hidden; /* Prevent scrollbars on the screen itself */
    position: relative; /* For positioning loading overlay */
}

.surgery-scheduling-layout {
  display: flex;
  /* Use calc for height if there's a fixed header/footer */
  /* height: calc(100vh - var(--header-height, 0) - var(--footer-height, 0)); */
  height: 100%; /* Take full height of parent */
  overflow: hidden; /* Ensure child panels manage their own scrolling */
}

.pending-surgeries-panel {
  /* Styles are mostly in PendingSurgeriesList.vue, but can add layout overrides here if necessary */
  /* width: 250px; */ /* Defined in component for encapsulation */
  /* flex-shrink: 0; */
}

.main-schedule-area {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* GanttChart handles its own scrolling */
}

.details-panel-container {
  /* Styles are mostly in SurgeryDetailsPanel.vue */
  /* width: 300px; */ /* Defined in component for encapsulation */
  /* flex-shrink: 0; */
}

/* Loading overlay for the entire screen */
.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: var(--font-size-lg);
    color: var(--color-primary);
    z-index: var(--z-index-modal); /* Above all other screen content */
}
</style>
