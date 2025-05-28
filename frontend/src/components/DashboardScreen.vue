<template>
  <div class="dashboard-container">
    <!-- Enhanced Header Section -->
    <div class="dashboard-header">
      <div class="welcome-section">
        <h1>Welcome back, {{ authStore.user?.username || 'User' }}!</h1>
        <p class="welcome-subtitle">{{ getCurrentDateString() }} • {{ getCurrentTimeString() }}</p>
      </div>
      <div class="header-stats">
        <div class="header-stat-item">
          <div class="stat-icon">🏥</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalORsActive }}</div>
            <div class="stat-label">Active ORs</div>
          </div>
        </div>
        <div class="header-stat-item">
          <div class="stat-icon">⏱️</div>
          <div class="stat-info">
            <div class="stat-value">{{ upcomingSurgeries }}</div>
            <div class="stat-label">Upcoming Today</div>
          </div>
        </div>
        <div class="header-stat-item urgent" v-if="urgentAlerts > 0">
          <div class="stat-icon">🚨</div>
          <div class="stat-info">
            <div class="stat-value">{{ urgentAlerts }}</div>
            <div class="stat-label">Urgent Alerts</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="scheduleStore.isLoading" class="loading-message">
      <div class="loading-spinner"></div>
      <p>Loading dashboard data...</p>
    </div>

    <div v-else class="dashboard-widgets">
      <!-- Enhanced Quick Actions Widget -->
      <div class="widget quick-actions-widget">
        <div class="widget-header">
          <h2>Quick Actions</h2>
          <span class="widget-subtitle">Common tasks and shortcuts</span>
        </div>
        <div class="quick-action-grid">
          <button @click="scheduleNewSurgery" class="action-card primary">
            <div class="action-icon">📅</div>
            <div class="action-content">
              <div class="action-title">Schedule Surgery</div>
              <div class="action-description">Add new elective surgery</div>
            </div>
          </button>
          <button @click="addEmergencyCase" class="action-card emergency">
            <div class="action-icon">🚨</div>
            <div class="action-content">
              <div class="action-title">Emergency Case</div>
              <div class="action-description">Add urgent surgery</div>
            </div>
          </button>
          <button @click="goToMasterSchedule" class="action-card featured">
            <div class="action-icon">📊</div>
            <div class="action-content">
              <div class="action-title">Master Schedule</div>
              <div class="action-description">View Gantt chart</div>
            </div>
          </button>
          <button @click="manageResources" class="action-card secondary">
            <div class="action-icon">🛠️</div>
            <div class="action-content">
              <div class="action-title">Manage Resources</div>
              <div class="action-description">ORs, staff, equipment</div>
            </div>
          </button>
          <button @click="runOptimization" class="action-card optimization">
            <div class="action-icon">🚀</div>
            <div class="action-content">
              <div class="action-title">Run Optimization</div>
              <div class="action-description">Optimize schedule</div>
            </div>
          </button>
          <button @click="viewReports" class="action-card secondary">
            <div class="action-icon">📈</div>
            <div class="action-content">
              <div class="action-title">View Reports</div>
              <div class="action-description">Analytics & insights</div>
            </div>
          </button>
        </div>
      </div>

      <!-- Enhanced KPIs Widget -->
      <div class="widget kpis-widget">
        <div class="widget-header">
          <h2>Performance Dashboard</h2>
          <span class="widget-subtitle">Real-time metrics and insights</span>
        </div>
        <div class="kpi-grid">
          <div class="kpi-card" :class="getKPIClass('utilization', orUtilizationToday)">
            <div class="kpi-icon">🏥</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ orUtilizationToday }}%</div>
              <div class="kpi-label">OR Utilization</div>
              <div class="kpi-trend" :class="getTrendClass('utilization')">
                <span class="trend-icon">{{ getTrendIcon('utilization') }}</span>
                <span class="trend-text">{{ getTrendText('utilization') }}</span>
              </div>
            </div>
          </div>
          <div class="kpi-card" :class="getKPIClass('sdst', avgSdstToday)">
            <div class="kpi-icon">⏱️</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ avgSdstToday }}m</div>
              <div class="kpi-label">Average SDST</div>
              <div class="kpi-trend" :class="getTrendClass('sdst')">
                <span class="trend-icon">{{ getTrendIcon('sdst') }}</span>
                <span class="trend-text">{{ getTrendText('sdst') }}</span>
              </div>
            </div>
          </div>
          <div class="kpi-card" :class="getKPIClass('emergency', emergencyCasesToday)">
            <div class="kpi-icon">🚨</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ emergencyCasesToday }}</div>
              <div class="kpi-label">Emergency Cases</div>
              <div class="kpi-trend" :class="getTrendClass('emergency')">
                <span class="trend-icon">{{ getTrendIcon('emergency') }}</span>
                <span class="trend-text">{{ getTrendText('emergency') }}</span>
              </div>
            </div>
          </div>
          <div class="kpi-card" :class="getKPIClass('cancelled', cancelledSurgeriesToday)">
            <div class="kpi-icon">❌</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ cancelledSurgeriesToday }}</div>
              <div class="kpi-label">Cancelled Today</div>
              <div class="kpi-trend" :class="getTrendClass('cancelled')">
                <span class="trend-icon">{{ getTrendIcon('cancelled') }}</span>
                <span class="trend-text">{{ getTrendText('cancelled') }}</span>
              </div>
            </div>
          </div>
        </div>
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
  console.log('Navigate to Master Schedule (Gantt Chart)');
  router.push({ name: 'MasterSchedule' });
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

const viewReports = () => {
  console.log('Navigate to Reports and Analytics');
  // router.push({ name: 'ReportsAnalytics' });
};
// -------------------------------------

// --- Enhanced Dashboard Methods ---
const getCurrentDateString = () => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const getCurrentTimeString = () => {
  return new Date().toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Computed properties for header stats
const totalORsActive = computed(() => {
  // Count ORs that have surgeries scheduled today
  const today = new Date().toDateString();
  const activeORs = new Set();

  visibleScheduledSurgeries.value.forEach(surgery => {
    const surgeryDate = new Date(surgery.startTime).toDateString();
    if (surgeryDate === today) {
      activeORs.add(surgery.orName);
    }
  });

  return activeORs.size;
});

const upcomingSurgeries = computed(() => {
  const now = new Date();
  const endOfDay = new Date(now);
  endOfDay.setHours(23, 59, 59, 999);

  return visibleScheduledSurgeries.value.filter(surgery => {
    const surgeryTime = new Date(surgery.startTime);
    return surgeryTime > now && surgeryTime <= endOfDay;
  }).length;
});

const urgentAlerts = computed(() => {
  return criticalAlerts.value.length + sdstConflictsFromStore.value.length;
});

// KPI Enhancement Methods
const getKPIClass = (type, value) => {
  switch (type) {
    case 'utilization':
      if (value >= 85) return 'excellent';
      if (value >= 70) return 'good';
      if (value >= 50) return 'warning';
      return 'poor';
    case 'sdst':
      if (value <= 20) return 'excellent';
      if (value <= 30) return 'good';
      if (value <= 45) return 'warning';
      return 'poor';
    case 'emergency':
      if (value <= 1) return 'excellent';
      if (value <= 3) return 'good';
      if (value <= 5) return 'warning';
      return 'poor';
    case 'cancelled':
      if (value === 0) return 'excellent';
      if (value <= 2) return 'good';
      if (value <= 4) return 'warning';
      return 'poor';
    default:
      return 'good';
  }
};

const getTrendClass = (type) => {
  // Simulated trend data - in real app, this would come from historical data
  const trends = {
    utilization: 'up',
    sdst: 'down',
    emergency: 'stable',
    cancelled: 'down'
  };
  return trends[type] || 'stable';
};

const getTrendIcon = (type) => {
  const trendClass = getTrendClass(type);
  switch (trendClass) {
    case 'up': return '↗️';
    case 'down': return '↘️';
    case 'stable': return '→';
    default: return '→';
  }
};

const getTrendText = (type) => {
  const trendClass = getTrendClass(type);
  const improvements = {
    utilization: { up: '+5% vs yesterday', down: '-3% vs yesterday', stable: 'No change' },
    sdst: { up: '+2min vs avg', down: '-5min vs avg', stable: 'Within range' },
    emergency: { up: '+1 vs yesterday', down: '-1 vs yesterday', stable: 'Normal level' },
    cancelled: { up: '+1 vs yesterday', down: '-2 vs yesterday', stable: 'No change' }
  };

  return improvements[type]?.[trendClass] || 'No data';
};

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
  padding: var(--spacing-lg);
  background-color: var(--color-background);
  min-height: 100vh;
}

/* Enhanced Dashboard Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.welcome-section h1 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
}

.welcome-subtitle {
  margin: 0;
  font-size: var(--font-size-base);
  opacity: 0.9;
  font-weight: var(--font-weight-normal);
}

.header-stats {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.header-stat-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: rgba(255, 255, 255, 0.1);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.header-stat-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.header-stat-item.urgent {
  background: rgba(220, 53, 69, 0.2);
  border-color: rgba(220, 53, 69, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.stat-icon {
  font-size: var(--font-size-xl);
}

.stat-info {
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  line-height: 1;
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  font-size: var(--font-size-sm);
  opacity: 0.9;
  font-weight: var(--font-weight-medium);
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

/* Enhanced Widget Headers */
.widget-header {
  margin-bottom: var(--spacing-lg);
}

.widget-header h2 {
  margin-bottom: var(--spacing-xs);
  border-bottom: none;
  padding-bottom: 0;
}

.widget-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-normal);
}

/* Enhanced Quick Actions Widget */
.quick-action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.action-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border: none;
  border-radius: var(--border-radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border-left: 4px solid transparent;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-card.primary {
  border-left-color: var(--color-primary);
}

.action-card.primary:hover {
  background: var(--color-primary-light);
  color: white;
}

.action-card.emergency {
  border-left-color: var(--color-danger);
}

.action-card.emergency:hover {
  background: var(--color-danger);
  color: white;
}

.action-card.featured {
  border-left-color: var(--color-success);
  background: linear-gradient(135deg, var(--color-success) 0%, var(--color-success-dark) 100%);
  color: white;
}

.action-card.featured:hover {
  background: linear-gradient(135deg, var(--color-success-dark) 0%, var(--color-success) 100%);
}

.action-card.secondary {
  border-left-color: var(--color-secondary);
}

.action-card.secondary:hover {
  background: var(--color-secondary);
  color: white;
}

.action-card.optimization {
  border-left-color: var(--color-warning);
}

.action-card.optimization:hover {
  background: var(--color-warning);
  color: white;
}

.action-icon {
  font-size: var(--font-size-xl);
  flex-shrink: 0;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-xs);
}

.action-description {
  font-size: var(--font-size-sm);
  opacity: 0.8;
}


/* Enhanced KPI Widget Styles */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-surface);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-left: 4px solid var(--color-border);
  cursor: pointer;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.kpi-card.excellent {
  border-left-color: var(--color-success);
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.05) 0%, rgba(40, 167, 69, 0.02) 100%);
}

.kpi-card.good {
  border-left-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(0, 117, 194, 0.05) 0%, rgba(0, 117, 194, 0.02) 100%);
}

.kpi-card.warning {
  border-left-color: var(--color-warning);
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05) 0%, rgba(255, 193, 7, 0.02) 100%);
}

.kpi-card.poor {
  border-left-color: var(--color-danger);
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.05) 0%, rgba(220, 53, 69, 0.02) 100%);
}

.kpi-icon {
  font-size: var(--font-size-xxl);
  flex-shrink: 0;
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  line-height: 1;
  margin-bottom: var(--spacing-xs);
}

.kpi-card.excellent .kpi-value {
  color: var(--color-success);
}

.kpi-card.good .kpi-value {
  color: var(--color-primary);
}

.kpi-card.warning .kpi-value {
  color: var(--color-warning);
}

.kpi-card.poor .kpi-value {
  color: var(--color-danger);
}

.kpi-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--spacing-xs);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.kpi-trend.up {
  color: var(--color-success);
}

.kpi-trend.down {
  color: var(--color-danger);
}

.kpi-trend.stable {
  color: var(--color-text-secondary);
}

.trend-icon {
  font-size: var(--font-size-sm);
}

.trend-text {
  opacity: 0.8;
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

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .dashboard-container {
    padding: var(--spacing-md);
  }

  .dashboard-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
    padding: var(--spacing-lg);
  }

  .welcome-section h1 {
    font-size: var(--font-size-xl);
  }

  .header-stats {
    justify-content: center;
    gap: var(--spacing-md);
  }

  .header-stat-item {
    flex-direction: column;
    text-align: center;
    padding: var(--spacing-sm);
    min-width: 80px;
  }

  .stat-icon {
    font-size: var(--font-size-lg);
  }

  .stat-value {
    font-size: var(--font-size-base);
  }

  .stat-label {
    font-size: var(--font-size-xs);
  }

  .dashboard-widgets {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  .quick-action-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .action-card {
    padding: var(--spacing-md);
  }

  .action-icon {
    font-size: var(--font-size-lg);
  }

  .action-title {
    font-size: var(--font-size-sm);
  }

  .action-description {
    font-size: var(--font-size-xs);
  }

  .kpi-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .kpi-card {
    padding: var(--spacing-md);
  }

  .kpi-icon {
    font-size: var(--font-size-xl);
  }

  .kpi-value {
    font-size: var(--font-size-xl);
  }

  .kpi-label {
    font-size: var(--font-size-xs);
  }
}

@media (max-width: 480px) {
  .dashboard-header {
    padding: var(--spacing-md);
  }

  .welcome-section h1 {
    font-size: var(--font-size-lg);
  }

  .welcome-subtitle {
    font-size: var(--font-size-sm);
  }

  .header-stats {
    gap: var(--spacing-sm);
  }

  .header-stat-item {
    padding: var(--spacing-xs);
    min-width: 60px;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .kpi-card {
    flex-direction: column;
    text-align: center;
    padding: var(--spacing-sm);
  }

  .kpi-icon {
    font-size: var(--font-size-lg);
  }

  .kpi-value {
    font-size: var(--font-size-lg);
  }
}
</style>
