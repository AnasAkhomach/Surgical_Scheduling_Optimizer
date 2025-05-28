<template>
  <div class="master-schedule-container">
    <div class="schedule-header">
      <div class="header-content">
        <h1>Master Surgery Schedule</h1>
        <p class="schedule-description">
          Interactive Gantt chart showing all scheduled surgeries with SDST (Sequence-Dependent Setup Times) visualization
        </p>
      </div>
      <div class="header-actions">
        <button @click="addNewSurgery" class="btn btn-primary">
          <span class="icon">➕</span> Add New Surgery
        </button>
        <button @click="goToScheduling" class="btn btn-secondary">
          <span class="icon">📝</span> Scheduling Interface
        </button>
      </div>
    </div>

    <div v-if="scheduleStore.isLoading" class="loading-message">
      <div class="loading-spinner"></div>
      <p>Loading schedule data...</p>
    </div>

    <div v-else class="gantt-section">
      <!-- Gantt Chart Integration -->
      <div class="gantt-wrapper">
        <GanttChart />
      </div>

      <!-- Quick Stats Panel -->
      <div class="quick-stats">
        <div class="stat-card">
          <div class="stat-value">{{ totalSurgeriesToday }}</div>
          <div class="stat-label">Surgeries Today</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ averageSDSTToday }}m</div>
          <div class="stat-label">Avg. SDST</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ orUtilizationToday }}%</div>
          <div class="stat-label">OR Utilization</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ conflictsToday }}</div>
          <div class="stat-label">Conflicts</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';
import GanttChart from './GanttChart.vue';

const router = useRouter();
const scheduleStore = useScheduleStore();

// Use storeToRefs to get reactive state from the store
const { visibleScheduledSurgeries, isLoading } = storeToRefs(scheduleStore);

// Computed properties for quick stats
const totalSurgeriesToday = computed(() => {
  const today = new Date().toDateString();
  return visibleScheduledSurgeries.value.filter(surgery => {
    const surgeryDate = new Date(surgery.startTime).toDateString();
    return surgeryDate === today;
  }).length;
});

const averageSDSTToday = computed(() => {
  const todaySurgeries = visibleScheduledSurgeries.value.filter(surgery => {
    const today = new Date().toDateString();
    const surgeryDate = new Date(surgery.startTime).toDateString();
    return surgeryDate === today && surgery.sdsTime;
  });

  if (todaySurgeries.length === 0) return 0;

  const totalSDST = todaySurgeries.reduce((sum, surgery) => sum + (surgery.sdsTime || 0), 0);
  return Math.round(totalSDST / todaySurgeries.length);
});

const orUtilizationToday = computed(() => {
  // Calculate OR utilization based on scheduled time vs available time
  // This is a simplified calculation
  const totalScheduledMinutes = visibleScheduledSurgeries.value
    .filter(surgery => {
      const today = new Date().toDateString();
      const surgeryDate = new Date(surgery.startTime).toDateString();
      return surgeryDate === today;
    })
    .reduce((sum, surgery) => sum + (surgery.duration || 0), 0);

  // Assuming 8 ORs with 12 hours each = 5760 minutes total capacity per day
  const totalCapacity = 8 * 12 * 60;
  return Math.round((totalScheduledMinutes / totalCapacity) * 100);
});

const conflictsToday = computed(() => {
  const today = new Date().toDateString();
  return visibleScheduledSurgeries.value.filter(surgery => {
    const surgeryDate = new Date(surgery.startTime).toDateString();
    return surgeryDate === today && surgery.conflicts && surgery.conflicts.length > 0;
  }).length;
});

// Navigation methods
const addNewSurgery = () => {
  console.log("Navigating to add new surgery");
  router.push({ name: 'Scheduling' });
};

const goToScheduling = () => {
  console.log("Navigating to scheduling interface");
  router.push({ name: 'Scheduling' });
};

// Load initial data when component mounts
onMounted(() => {
  console.log('MasterScheduleScreen mounted. Loading schedule data...');
  // The scheduleStore should already have data loaded, but we can ensure it's loaded
  if (!scheduleStore.isDataLoaded) {
    scheduleStore.loadInitialData();
  }
});
</script>

<style scoped>
.master-schedule-container {
  padding: var(--spacing-lg);
  background-color: var(--color-background);
  min-height: 100vh;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border-radius: var(--border-radius-lg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
}

.schedule-description {
  margin: 0;
  font-size: var(--font-size-base);
  opacity: 0.9;
  max-width: 600px;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.header-actions .btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s ease;
}

.header-actions .btn-primary {
  background-color: white;
  color: var(--color-primary);
  border: 2px solid white;
}

.header-actions .btn-primary:hover {
  background-color: var(--color-primary-light);
  color: white;
  transform: translateY(-1px);
}

.header-actions .btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.header-actions .btn-secondary:hover {
  background-color: white;
  color: var(--color-primary);
  transform: translateY(-1px);
}

.loading-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.gantt-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.gantt-wrapper {
  background-color: var(--color-surface);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-height: 600px;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.stat-card {
  background-color: var(--color-surface);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .master-schedule-container {
    padding: var(--spacing-md);
  }

  .schedule-header {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }

  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .quick-stats {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--spacing-sm);
  }

  .stat-card {
    padding: var(--spacing-md);
  }

  .stat-value {
    font-size: var(--font-size-xl);
  }
}

@media (max-width: 480px) {
  .header-content h1 {
    font-size: var(--font-size-xl);
  }

  .schedule-description {
    font-size: var(--font-size-sm);
  }

  .quick-stats {
    grid-template-columns: 1fr 1fr;
  }
}
</style>