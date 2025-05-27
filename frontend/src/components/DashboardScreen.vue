<template>
  <div class="dashboard-container">
    <h1>Welcome, {{ authStore.user?.username || 'User' }}!</h1>

    <div v-if="scheduleStore.isLoading" class="loading-message">
      Loading dashboard data...
    </div>

    <div v-else class="dashboard-widgets">
      <!-- Quick Actions Widget -->
      <div class="widget quick-actions-widget">
        <h2>Quick Actions</h2>
        <div class="quick-action-buttons">
          <button @click="scheduleNewSurgery">Schedule New Elective Surgery</button>
          <button class="btn btn-secondary" @click="addEmergencyCase">Add Emergency Case</button>
          <button @click="goToMasterSchedule">Go to Master Schedule</button>
          <button @click="manageResources">Manage Resources</button>
          <button class="btn btn-secondary" @click="runOptimization">Run Optimization</button>
        </div>
      </div>

      <!-- Key Performance Indicators (KPIs) Widget -->
      <div class="widget kpis-widget">
        <h2>Key Performance Indicators</h2>
        <div class="kpi-list">
          <!-- KPIs will likely come from the scheduleStore or a dedicated reporting store later -->
          <div class="kpi-item" @click="navigateToReport('OR Utilization')">
            <span class="kpi-label">OR Utilization (Today):</span>
            <!-- Using simulated data for now -->
            <span class="kpi-value">{{ orUtilizationToday }}%</span>
          </div>
          <div class="kpi-item" @click="navigateToReport('Avg. SDST')">
            <span class="kpi-label">Avg. SDST (Today):</span>
             <!-- Using simulated data for now -->
            <span class="kpi-value">{{ avgSdstToday }} min</span>
          </div>
          <div class="kpi-item" @click="navigateToReport('Emergency Cases')">
            <span class="kpi-label">Emergency Cases (Today):</span>
             <!-- Using simulated data for now -->
            <span class="kpi-value">{{ emergencyCasesToday }}</span>
          </div>
          <div class="kpi-item" @click="navigateToReport('Cancelled Surgeries')">
            <span class="kpi-label">Cancelled Surgeries (Today):</span>
             <!-- Using simulated data for now -->
            <span class="kpi-value">{{ cancelledSurgeriesToday }}</span>
          </div>
        </div>
        <!-- Placeholder for charts/visualizations -->
        <p><em>(Placeholder for KPI charts/visualizations)</em></p>
      </div>

      <!-- Today's OR Schedule Overview Widget -->
      <div class="widget schedule-overview-widget">
        <h2>Today's OR Schedule Overview</h2>
        <!-- Display a snippet of today's scheduled surgeries from the store -->
        <ul v-if="todayScheduleSnippet.length > 0" class="schedule-list">
           <li v-for="surgery in todayScheduleSnippet" :key="surgery.id">
              {{ formatTime(surgery.startTime) }} - OR {{ surgery.orName }}: {{ surgery.patientName }} - {{ surgery.type }}
              <span v-if="surgery.conflicts && surgery.conflicts.length > 0" class="schedule-item-conflict">⚠️</span>
           </li>
        </ul>
        <p v-else class="no-items">No surgeries scheduled for today in the current view.</p>
        <p>Provides at-a-glance view of today's operations across all ORs.</p>
      </div>

      <!-- Critical Resource Alerts Widget -->
      <div class="widget alerts-widget">
        <h2>Critical Resource Alerts</h2>
        <!-- Alerts would ideally come from a dedicated alerts store or the schedule store's processed data -->
        <ul>
          <li v-for="alert in criticalAlerts" :key="alert.id" class="alert-item" @click="handleAlertClick(alert)">{{ alert.message }}</li>
          <li v-if="criticalAlerts.length === 0" class="no-items">No critical alerts</li>
        </ul>
      </div>

      <!-- SDST Conflict Summary Widget -->
      <div class="widget sdst-conflicts-widget">
        <h2>SDST Conflict Summary</h2>
        <!-- SDST Conflicts come from the scheduleStore's processed data -->
        <ul>
          <li v-for="conflict in sdstConflictsFromStore" :key="conflict.id" class="conflict-item" @click="handleConflictClick(conflict)">{{ conflict.message }}</li>
          <li v-if="sdstConflictsFromStore.length === 0" class="no-items">No SDST conflicts</li>
        </ul>
      </div>

      <!-- Conflict Details Display Area - Might be a modal or separate view later -->
      <div v-if="selectedConflict" class="widget conflict-details-widget">
        <h2>Conflict Details</h2>
        <p>Conflict details will be displayed here.</p>
        <p>Selected Conflict: {{ selectedConflict.message }}</p>

        <!-- Conflict Resolution Actions -->
        <div class="conflict-actions">
            <button @click="viewConflictingSurgeries">View Conflicting Surgeries</button>
            <button class="btn btn-secondary" @click="ignoreConflict">Ignore Conflict</button>
        </div>
      </div>

      <!-- Pending Surgeries Queue Widget -->
      <div class="widget pending-surgeries-widget">
        <h2>Pending Surgeries Queue</h2>
        <!-- Display pending surgeries from the store -->
        <ul class="pending-surgeries-list">
          <li v-for="surgery in pendingSurgeriesFromStore" :key="surgery.id" class="pending-surgery-item" @click="handlePendingSurgeryClick(surgery)">{{ surgery.patientName }} - {{ surgery.type }} ({{ surgery.estimatedDuration }} min)</li>
          <li v-if="pendingSurgeriesFromStore.length === 0" class="no-items">No pending surgeries</li>
        </ul>
        <p>Sortable list of surgeries awaiting scheduling.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const authStore = useAuthStore();
const scheduleStore = useScheduleStore();

// Use storeToRefs to get reactive state and getters from stores
const { user } = storeToRefs(authStore);
const { visibleScheduledSurgeries, pendingSurgeries } = storeToRefs(scheduleStore);

// Local state for the dashboard component
// const isLoading = ref(true); // Use scheduleStore.isLoading instead
const selectedConflict = ref(null); // State to hold selected conflict details for the details widget

// Simulated data for KPIs (replace with data from stores/APIs later)
const orUtilizationToday = ref(85);
const avgSdstToday = ref(30);
const emergencyCasesToday = ref(2);
const cancelledSurgeriesToday = ref(1);

// Simulated data for other widgets (replace with data from stores later)
const criticalAlerts = ref([
  { id: 1, message: 'OR 3: A/C Maintenance Overdue' },
  { id: 2, message: 'Anesthesia Machine X: Unavailable' },
]);

// Computed property to get SDST conflicts from the schedule store
const sdstConflictsFromStore = computed(() => {
    // Assuming conflicts array on surgery objects includes SDST violations
    const conflicts = [];
    scheduleStore.scheduledSurgeries.forEach(surgery => {
        if (surgery.conflicts && surgery.conflicts.length > 0) {
            surgery.conflicts.forEach(conflictMsg => {
                if (conflictMsg.includes('SDST')) { // Filter for SDST specific conflicts (simple check)
                    conflicts.push({ id: surgery.id + conflictMsg.slice(0, 10), message: `${surgery.patientName} (${surgery.type}): ${conflictMsg}` });
                }
            });
        }
    });
    return conflicts;
});

// Computed property to get pending surgeries from the store
const pendingSurgeriesFromStore = computed(() => {
    return pendingSurgeries.value; // Direct use of storeToRefs ref
});

// Computed property for a snippet of today's schedule (e.g., first few surgeries or key ones)
const todayScheduleSnippet = computed(() => {
    // For a dashboard snippet, we might just show a limited number
    // Or filter for high priority/upcoming ones.
    // Let's show the first 5 surgeries from the visible scheduled list for OR1 and OR2 as an example
    const snippet = [];
    const orsToShow = ['OR1', 'OR2']; // Example: show schedule for key ORs

    orsToShow.forEach(orId => {
         const surgeriesInOR = scheduleStore.getSurgeriesForOR(orId);
         // Add a header or separator for each OR in the snippet if desired
        // snippet.push({ id: 'or-header-' + orId, isHeader: true, name: scheduleStore.operatingRooms.find(o => o.id === orId)?.name || orId });
         snippet.push(...surgeriesInOR.slice(0, 3)); // Take first 3 from each OR
    });

    // Sort the final snippet by time if combining from multiple ORs
    snippet.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

    return snippet.slice(0, 10); // Limit total snippet size
});


// --- Quick Action Button Handlers ---
const scheduleNewSurgery = () => {
  console.log('Navigate to Schedule New Surgery form');
  // Assuming a route named 'CreateSurgeryForm' or similar
  // router.push({ name: 'CreateSurgeryForm' });
};

const addEmergencyCase = () => {
  console.log('Navigate to Add Emergency Case form');
  // Assuming a route named 'AddEmergencyCaseForm' or similar
  // router.push({ name: 'AddEmergencyCaseForm' });
};

const goToMasterSchedule = () => {
  console.log('Navigate to Master Schedule');
  router.push({ name: 'Scheduling' });
};

const manageResources = () => {
  console.log('Navigate to Resource Management');
  router.push({ name: 'ResourceManagement' });
};

const runOptimization = () => {
  console.log('Trigger Optimization Engine');
  // This might open a modal or dispatch a store action
  // scheduleStore.runOptimization();
  // If it navigates, assuming a route named 'OptimizationControl'
  // router.push({ name: 'OptimizationControl' });
};
// -------------------------------------

// --- KPI Click Handler ---
const navigateToReport = (kpiName) => {
  console.log(`Navigating to report for: ${kpiName}`);
  // Assuming a Reporting route with query parameters or dynamic segments
  // router.push({ name: 'ReportingAnalytics', query: { report: kpiName.replace(/[^a-zA-Z0-9]/g, '') } });
};

// --- Alert Click Handler ---
const handleAlertClick = (alert) => {
  console.log('View details for alert:', alert);
  // Implement modal or navigation to alert details later
};

// --- Pending Surgery Click Handler ---
const handlePendingSurgeryClick = (surgery) => {
  console.log('View details for pending surgery:', surgery);
  // This should likely navigate to the Surgery Scheduling screen
  // with this surgery pre-selected or highlighted, or open a modal.
  // For now, we can simulate selecting it in the store, which the Details Panel listens to.
   scheduleStore.selectSurgery(surgery.id);
   router.push({ name: 'Scheduling' }); // Optional: Navigate to scheduling screen
};

// --- Conflict Click Handler ---
const handleConflictClick = (conflict) => {
  selectedConflict.value = conflict; // Set the selected conflict for display in the widget
   console.log('Viewing conflict details for:', conflict);
   // This might also navigate or highlight on the scheduling screen later
};

const viewConflictingSurgeries = () => {
  console.log('View conflicting surgeries for:', selectedConflict.value);
  // In a real app, open a modal or navigate to a view showing related surgeries
  // This would likely involve navigating to the Scheduling screen and highlighting the relevant surgeries
};

const ignoreConflict = () => {
  console.log('Ignore conflict:', selectedConflict.value);
  // In a real app, send an API call to mark the conflict as ignored or resolved
  // After successful API call, update the store or refetch relevant data
};


const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Load initial data for the dashboard when the component is mounted
// This might involve calling scheduleStore actions to fetch data relevant to the dashboard view
onMounted(() => {
  console.log('DashboardScreen mounted. Loading data...');
  // The scheduleStore.loadInitialData() might be called here or earlier (e.g., on app startup)
  // If data is already loaded, the store will provide it reactively.
  // If not, calling it here ensures data is fetched when the dashboard is accessed.
  // scheduleStore.loadInitialData(); // Ensure data is loaded
  // Note: scheduleStore.loadInitialData is already called in SurgerySchedulingScreen on mount.
  // We might need a separate, lighter dashboard-specific data fetch action later.
});
</script>

<style scoped>
/* Remove local :root - global variables are in src/style.css */
/*
:root {
  --color-white: #ffffff;
  --color-primary: #0075c2;
  --color-secondary: #6c757d;
  --color-danger: #dc3545;
  --color-warning: #ffc107;
  --color-light-gray: #f5f5f5;
  --color-mid-light-gray: #e0e0e0;
  --color-mid-gray: #aaaaaa;
  --color-dark-gray: #555555;
  --color-very-dark-gray: #333333;
}
*/

.dashboard-container {
  padding: var(--spacing-md); /* Use global spacing variable */
}

.dashboard-widgets {
  display: grid;
  /* Use global spacing variables for gap */
  gap: var(--spacing-md); /* Space between widgets */
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* Responsive grid */
  margin-top: var(--spacing-md); /* Use global spacing variable */
}

.widget {
  background-color: var(--color-white); /* Use global white variable */
  padding: var(--spacing-md); /* Use global spacing variable */
  border-radius: var(--border-radius-sm); /* Use global border radius variable */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-border); /* Use global border variable */
}

.widget h2 {
  font-size: var(--font-size-lg); /* Use global font size variable */
  margin-top: 0;
  margin-bottom: var(--spacing-md); /* Use global spacing variable */
  padding-bottom: var(--spacing-sm); /* Use global spacing variable */
  border-bottom: 1px solid var(--color-border-soft); /* Use global border variable */
  color: var(--color-very-dark-gray); /* Use global text color variable */
}

/* Quick Actions Widget Specific Styles */
.quick-actions-widget .quick-action-buttons,
.conflict-details-widget .conflict-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm); /* Use global spacing variable */
}

.quick-actions-widget button,
.conflict-details-widget button {
  /* Inherits base button styles from global style.css */
  /* You can add minor overrides here if needed */
}

.quick-actions-widget .btn-secondary,
.conflict-details-widget .btn-secondary {
    /* Inherits .btn-secondary styles from global style.css */
}


/* KPI Widget Specific Styles */
.kpi-list {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two columns for KPI items */
  gap: var(--spacing-sm); /* Use global spacing variable */
}

.kpi-item {
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
  padding: var(--spacing-sm); /* Use global spacing variable */
  border-radius: var(--border-radius-sm); /* Use global border radius variable */
}

.kpi-item:hover {
  background-color: var(--color-background-soft); /* Use global background variable */
}

.kpi-item .kpi-label {
  display: block;
  font-size: var(--font-size-sm); /* Use global font size variable */
  color: var(--color-dark-gray); /* Use global text color variable */
  margin-bottom: var(--spacing-xs); /* Use global spacing variable */
}

.kpi-item .kpi-value {
  font-size: var(--font-size-xl); /* Use global font size variable */
  font-weight: var(--font-weight-bold); /* Use global font weight variable */
  color: var(--color-primary); /* Use global primary color variable */
  line-height: 1.2;
}

/* Specific widget adjustments */
.schedule-overview-widget p,
.pending-surgeries-widget p {
  font-size: var(--font-size-sm); /* Use global font size variable */
  color: var(--color-dark-gray); /* Use global text color variable */
}

.alerts-widget ul,
.sdst-conflicts-widget ul,
.pending-surgeries-widget ul,
.schedule-overview-widget ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.alerts-widget li,
.sdst-conflicts-widget li,
.pending-surgeries-widget li,
.schedule-overview-widget li {
  margin-bottom: var(--spacing-xs); /* Use global spacing variable */
  padding: var(--spacing-xs); /* Use global spacing variable */
  border-bottom: 1px dashed var(--color-border-soft); /* Use global border variable */
  font-size: var(--font-size-base); /* Use global font size variable */
}

.alerts-widget li:last-child,
.sdst-conflicts-widget li:last-child,
.pending-surgeries-widget li:last-child,
.schedule-overview-widget li:last-child {
  border-bottom: none;
}

.pending-surgeries-widget li,
.alerts-widget li,
.sdst-conflicts-widget li {
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-left: 5px solid transparent; /* Add space for potential status indicator */
  padding-left: var(--spacing-sm); /* Adjust padding */
}

.pending-surgeries-widget li:hover,
.alerts-widget li:hover,
.sdst-conflicts-widget li:hover {
  background-color: var(--color-background-soft); /* Use global background variable */
}

.no-items {
  text-align: center;
  color: var(--color-dark-gray); /* Use global text color variable */
  font-style: italic;
}

.loading-message {
  font-size: var(--font-size-lg); /* Use global font size variable */
  color: var(--color-dark-gray); /* Use global text color variable */
  text-align: center;
  padding: var(--spacing-md); /* Use global spacing variable */
}

/* Specific styling for alerts/conflicts using global color variables */
.alert-item {
  border-left-color: var(--color-danger); /* Red color for alerts */
  color: var(--color-danger); /* Use danger color for alerts */
  font-weight: var(--font-weight-medium); /* Use global font weight variable */
}

.conflict-item {
  border-left-color: var(--color-warning); /* Yellow color for conflicts */
  color: var(--color-warning); /* Use warning color for conflicts */
  font-weight: var(--font-weight-medium); /* Use global font weight variable */
}

.schedule-item-conflict {
    color: var(--color-warning); /* Warning icon color */
    margin-left: var(--spacing-xs); /* Space after text */
}

.conflict-details-widget .conflict-actions {
    margin-top: var(--spacing-md); /* Space above action buttons */
    padding-top: var(--spacing-md); /* Space above action buttons */
     border-top: 1px solid var(--color-border-soft);
}
</style>
