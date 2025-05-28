<template>
  <div class="analytics-dashboard">
    <h1>Analytics Dashboard</h1>

    <!-- Date Range Selector -->
    <div class="date-range-selector">
      <h3>Date Range</h3>
      <div class="date-inputs">
        <div class="date-input">
          <label for="start-date">Start Date</label>
          <input
            type="date"
            id="start-date"
            :value="formatDateForInput(dateRange.start)"
            @change="updateStartDate"
          >
        </div>
        <div class="date-input">
          <label for="end-date">End Date</label>
          <input
            type="date"
            id="end-date"
            :value="formatDateForInput(dateRange.end)"
            @change="updateEndDate"
          >
        </div>
        <button class="apply-button" @click="applyDateRange">Apply</button>
      </div>
      <div class="quick-ranges">
        <button @click="setQuickRange('last7')">Last 7 Days</button>
        <button @click="setQuickRange('last30')">Last 30 Days</button>
        <button @click="setQuickRange('thisMonth')">This Month</button>
        <button @click="setQuickRange('lastMonth')">Last Month</button>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading analytics data...</p>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadAnalyticsData">Retry</button>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Summary Metrics -->
      <div class="summary-metrics">
        <div class="metric-card">
          <h3>Total Surgeries</h3>
          <div class="metric-value">{{ totalSurgeries }}</div>
          <div class="metric-trend" :class="surgeryTrend.direction">
            {{ surgeryTrend.value }}% {{ surgeryTrend.direction === 'up' ? '↑' : '↓' }}
          </div>
        </div>

        <div class="metric-card">
          <h3>Average OR Utilization</h3>
          <div class="metric-value">{{ formatPercentage(averageORUtilization) }}</div>
          <div class="metric-trend" :class="utilizationTrend.direction">
            {{ utilizationTrend.value }}% {{ utilizationTrend.direction === 'up' ? '↑' : '↓' }}
          </div>
        </div>

        <div class="metric-card">
          <h3>On-Time Start Rate</h3>
          <div class="metric-value">{{ formatPercentage(onTimeStartRate) }}</div>
          <div class="metric-trend" :class="onTimeTrend.direction">
            {{ onTimeTrend.value }}% {{ onTimeTrend.direction === 'up' ? '↑' : '↓' }}
          </div>
        </div>

        <div class="metric-card">
          <h3>Average SDST</h3>
          <div class="metric-value">{{ Math.round(kpiData?.averageSDST || 0) }} min</div>
          <div class="metric-trend" :class="turnaroundTrend.direction === 'up' ? 'down' : 'up'">
            {{ turnaroundTrend.value }}% {{ turnaroundTrend.direction === 'up' ? '↑' : '↓' }}
          </div>
        </div>

        <div class="metric-card">
          <h3>Daily Conflicts</h3>
          <div class="metric-value">{{ Math.round(kpiData?.conflictRate || 0) }}</div>
          <div class="metric-trend" :class="conflictTrend.direction">
            {{ conflictTrend.value }}% {{ conflictTrend.direction === 'up' ? '↑' : '↓' }}
          </div>
        </div>
      </div>

      <!-- SDST Insights Section -->
      <div v-if="sdstEfficiency" class="sdst-insights">
        <h3>SDST Optimization Insights</h3>
        <div class="insights-grid">
          <div class="insight-card">
            <h4>Most Efficient Transition</h4>
            <div class="transition-info">
              <span class="transition">{{ sdstEfficiency?.mostEfficientTransition?.from }} → {{ sdstEfficiency?.mostEfficientTransition?.to }}</span>
              <span class="time">{{ sdstEfficiency?.mostEfficientTransition?.averageTime }} min</span>
            </div>
          </div>

          <div class="insight-card">
            <h4>Least Efficient Transition</h4>
            <div class="transition-info">
              <span class="transition">{{ sdstEfficiency?.leastEfficientTransition?.from }} → {{ sdstEfficiency?.leastEfficientTransition?.to }}</span>
              <span class="time">{{ sdstEfficiency?.leastEfficientTransition?.averageTime }} min</span>
            </div>
          </div>

          <div class="insight-card">
            <h4>Potential Daily Savings</h4>
            <div class="savings-info">
              <span class="savings">{{ sdstEfficiency?.potentialSavings }} min</span>
              <span class="description">Through optimization</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Optimization Suggestions Component -->
      <OptimizationSuggestions />

      <!-- Optimization Opportunities -->
      <div v-if="optimizationOpportunities && optimizationOpportunities.length > 0" class="optimization-opportunities">
        <h3>Optimization Opportunities</h3>
        <div class="opportunities-list">
          <div v-for="opportunity in optimizationOpportunities.slice(0, 3)" :key="opportunity.type"
               class="opportunity-card" :class="`priority-${opportunity.priority.toLowerCase()}`">
            <div class="opportunity-header">
              <h4>{{ opportunity.type }}</h4>
              <span class="priority-badge">{{ opportunity.priority }}</span>
            </div>
            <p class="opportunity-description">{{ opportunity.description }}</p>
            <div class="opportunity-savings">
              <strong>Potential Savings: {{ opportunity.potentialSavings }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Charts -->
      <div class="chart-row">
        <div class="chart-container">
          <h3>Daily Surgery Volume</h3>
          <div class="chart-placeholder">
            <!-- Chart would be rendered here using a charting library -->
            <div class="chart-mock">
              <div v-for="(value, index) in dailySurgeryData" :key="index"
                   class="chart-bar"
                   :style="{ height: `${value * 100}%` }">
              </div>
            </div>
          </div>
        </div>

        <div class="chart-container">
          <h3>OR Utilization by Room</h3>
          <div class="chart-placeholder">
            <!-- Chart would be rendered here using a charting library -->
            <div class="chart-mock horizontal">
              <div v-for="(or, index) in orUtilizationData" :key="index" class="chart-item">
                <div class="chart-label">{{ or.name }}</div>
                <div class="chart-bar-container">
                  <div class="chart-bar" :style="{ width: `${or.value * 100}%` }"></div>
                </div>
                <div class="chart-value">{{ formatPercentage(or.value) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-container">
          <h3>Surgery Type Distribution</h3>
          <div class="chart-placeholder">
            <!-- Chart would be rendered here using a charting library -->
            <div class="chart-mock pie">
              <div v-for="(segment, index) in surgeryTypeData" :key="index"
                   class="pie-segment"
                   :style="{
                     backgroundColor: segment.color,
                     transform: `rotate(${segment.startAngle}deg)`,
                     clipPath: `polygon(50% 50%, 100% 0, 100% 100%, 0 100%, 0 0)`
                   }">
              </div>
              <div class="pie-legend">
                <div v-for="(segment, index) in surgeryTypeData" :key="`legend-${index}`" class="legend-item">
                  <div class="color-box" :style="{ backgroundColor: segment.color }"></div>
                  <div>{{ segment.name }}: {{ formatPercentage(segment.value) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-container">
          <h3>Surgeon Performance</h3>
          <div class="chart-placeholder">
            <!-- Chart would be rendered here using a charting library -->
            <div class="chart-mock horizontal">
              <div v-for="(surgeon, index) in surgeonPerformanceData" :key="index" class="chart-item">
                <div class="chart-label">{{ surgeon.name }}</div>
                <div class="chart-bar-container">
                  <div class="chart-bar" :style="{ width: `${surgeon.value * 100}%` }"></div>
                </div>
                <div class="chart-value">{{ surgeon.surgeries }} surgeries</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Report Links -->
      <div class="report-links">
        <h3>Detailed Reports</h3>
        <div class="report-buttons">
          <button @click="navigateTo('utilization')">OR Utilization Report</button>
          <button @click="navigateTo('efficiency')">Scheduling Efficiency Report</button>
          <button @click="navigateTo('custom')">Custom Report Builder</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { storeToRefs } from 'pinia';
import OptimizationSuggestions from './OptimizationSuggestions.vue';

const router = useRouter();
const analyticsStore = useAnalyticsStore();
const {
  isLoading,
  error,
  dateRange,
  cachedData,
  keyPerformanceIndicators,
  sdstPatterns,
  sdstEfficiency,
  resourceOptimization,
  schedulingEfficiency,
  conflictAnalysis,
  optimizationOpportunities
} = storeToRefs(analyticsStore);

// Mock data for charts (in a real app, this would come from the store)
const dailySurgeryData = ref([0.5, 0.7, 0.6, 0.8, 0.9, 0.4, 0.6]);
const orUtilizationData = ref([
  { name: 'OR 1', value: 0.85 },
  { name: 'OR 2', value: 0.72 },
  { name: 'OR 3', value: 0.65 },
  { name: 'OR 4', value: 0.91 },
  { name: 'OR 5', value: 0.78 },
]);
const surgeryTypeData = ref([
  { name: 'CABG', value: 0.35, color: '#007bff', startAngle: 0 },
  { name: 'KNEE', value: 0.25, color: '#28a745', startAngle: 126 },
  { name: 'APPEN', value: 0.15, color: '#ffc107', startAngle: 216 },
  { name: 'HIPRE', value: 0.15, color: '#20c997', startAngle: 270 },
  { name: 'Other', value: 0.10, color: '#6c757d', startAngle: 324 },
]);
const surgeonPerformanceData = ref([
  { name: 'Dr. Smith', value: 0.9, surgeries: 45 },
  { name: 'Dr. Adams', value: 0.75, surgeries: 38 },
  { name: 'Dr. Chen', value: 0.6, surgeries: 30 },
  { name: 'Dr. Wong', value: 0.4, surgeries: 20 },
]);

// Computed properties for enhanced analytics
const kpiData = computed(() => {
  try {
    return keyPerformanceIndicators?.value || null;
  } catch (error) {
    console.warn('Failed to access keyPerformanceIndicators:', error);
    return null;
  }
});

// Summary metrics
const totalSurgeries = ref(133);
const averageORUtilization = computed(() => kpiData.value?.averageORUtilization || 0.78);
const onTimeStartRate = computed(() => kpiData.value?.onTimeStartRate || 0.82);
const averageTurnaround = ref(24);

// Trend data (would be calculated from historical data)
const surgeryTrend = ref({ value: 12, direction: 'up' });
const utilizationTrend = ref({ value: 5, direction: 'up' });
const onTimeTrend = ref({ value: 3, direction: 'up' });
const turnaroundTrend = ref({ value: 8, direction: 'down' });
const conflictTrend = ref({ value: 15, direction: 'down' });

// Load analytics data on component mount
onMounted(async () => {
  await loadAnalyticsData();
});

// Load analytics data
const loadAnalyticsData = async () => {
  await analyticsStore.loadAnalyticsData();

  // In a real app, we would update the chart data from the store
  // For now, we'll use the mock data
};

// Format date for input element
const formatDateForInput = (date) => {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Format percentage
const formatPercentage = (value) => {
  return `${Math.round(value * 100)}%`;
};

// Update date range
const updateStartDate = (event) => {
  const newDate = new Date(event.target.value);
  if (!isNaN(newDate.getTime())) {
    dateRange.value.start = newDate;
  }
};

const updateEndDate = (event) => {
  const newDate = new Date(event.target.value);
  if (!isNaN(newDate.getTime())) {
    dateRange.value.end = newDate;
  }
};

const applyDateRange = async () => {
  analyticsStore.setDateRange(dateRange.value.start, dateRange.value.end);
  await loadAnalyticsData();
};

// Set quick date range
const setQuickRange = async (range) => {
  const today = new Date();
  let start, end;

  switch (range) {
    case 'last7':
      start = new Date(today);
      start.setDate(today.getDate() - 7);
      end = new Date(today);
      break;
    case 'last30':
      start = new Date(today);
      start.setDate(today.getDate() - 30);
      end = new Date(today);
      break;
    case 'thisMonth':
      start = new Date(today.getFullYear(), today.getMonth(), 1);
      end = new Date(today);
      break;
    case 'lastMonth':
      start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      end = new Date(today.getFullYear(), today.getMonth(), 0);
      break;
    default:
      return;
  }

  dateRange.value.start = start;
  dateRange.value.end = end;
  await applyDateRange();
};

// Navigate to detailed reports
const navigateTo = (route) => {
  router.push(`/reporting-analytics/${route}`);
};
</script>

<style scoped>
.analytics-dashboard {
  padding: var(--spacing-md);
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: var(--spacing-lg);
}

h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
}

/* Date Range Selector */
.date-range-selector {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.date-inputs {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  align-items: flex-end;
}

.date-input {
  flex: 1;
}

.date-input label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.date-input input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

.apply-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

.quick-ranges {
  display: flex;
  gap: var(--spacing-sm);
}

.quick-ranges button {
  background-color: var(--color-background-mute);
  border: 1px solid var(--color-border);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.quick-ranges button:hover {
  background-color: var(--color-background-hover);
}

/* Loading and Error */
.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(var(--color-primary-rgb), 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: rgba(var(--color-error-rgb), 0.1);
  color: var(--color-error);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  text-align: center;
  margin: var(--spacing-lg) 0;
}

.error-message button {
  background-color: var(--color-error);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  margin-top: var(--spacing-sm);
  cursor: pointer;
}

/* Summary Metrics */
.summary-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.metric-card {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  text-align: center;
}

.metric-value {
  font-size: 2rem;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-sm) 0;
}

.metric-trend {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.metric-trend.up {
  color: var(--color-success);
}

.metric-trend.down {
  color: var(--color-error);
}

/* SDST Insights */
.sdst-insights {
  background-color: var(--color-background-soft);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.insight-card {
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-primary);
}

.insight-card h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.transition-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.transition {
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
}

.time {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.savings-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.savings {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-success);
}

.description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Optimization Opportunities */
.optimization-opportunities {
  background-color: var(--color-background-soft);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.opportunities-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.opportunity-card {
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-border);
}

.opportunity-card.priority-high {
  border-left-color: var(--color-error);
}

.opportunity-card.priority-medium {
  border-left-color: var(--color-warning);
}

.opportunity-card.priority-low {
  border-left-color: var(--color-success);
}

.opportunity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.opportunity-header h4 {
  margin: 0;
  color: var(--color-text);
  font-size: var(--font-size-md);
}

.priority-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
}

.priority-high .priority-badge {
  background-color: rgba(var(--color-error-rgb), 0.1);
  color: var(--color-error);
}

.priority-medium .priority-badge {
  background-color: rgba(var(--color-warning-rgb), 0.1);
  color: var(--color-warning);
}

.priority-low .priority-badge {
  background-color: rgba(var(--color-success-rgb), 0.1);
  color: var(--color-success);
}

.opportunity-description {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.opportunity-savings {
  color: var(--color-success);
  font-size: var(--font-size-sm);
}

/* Charts */
.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.chart-container {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

/* Mock charts for demonstration */
.chart-mock {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: var(--spacing-md);
}

.chart-mock.horizontal {
  flex-direction: column;
  align-items: stretch;
  justify-content: space-around;
}

.chart-bar {
  background-color: var(--color-primary);
  width: 30px;
  border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
}

.chart-mock.horizontal .chart-item {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.chart-mock.horizontal .chart-label {
  width: 80px;
  text-align: right;
  margin-right: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.chart-mock.horizontal .chart-bar-container {
  flex-grow: 1;
  height: 20px;
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.chart-mock.horizontal .chart-bar {
  height: 100%;
  width: 0%; /* Will be set dynamically */
}

.chart-mock.horizontal .chart-value {
  width: 80px;
  margin-left: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.chart-mock.pie {
  position: relative;
  border-radius: 50%;
  width: 200px;
  height: 200px;
  margin: 0 auto;
}

.pie-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-origin: 50% 50%;
}

.pie-legend {
  position: absolute;
  top: 220px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--spacing-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
}

.color-box {
  width: 12px;
  height: 12px;
  margin-right: 4px;
  border-radius: 2px;
}

/* Report Links */
.report-links {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin-top: var(--spacing-lg);
}

.report-buttons {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.report-buttons button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

.report-buttons button:hover {
  background-color: var(--color-primary-dark);
}

/* Enhanced Mobile Responsive Design */

/* Tablet adjustments (768px - 1024px) */
@media (max-width: 1024px) {
  .analytics-dashboard {
    padding: var(--spacing-sm);
  }

  .chart-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  .summary-metrics {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-sm);
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }

  .opportunities-list {
    grid-template-columns: 1fr;
  }
}

/* Mobile adjustments (up to 768px) */
@media (max-width: 768px) {
  .analytics-dashboard {
    padding: var(--spacing-sm);
  }

  h1 {
    font-size: var(--font-size-xl);
    margin-bottom: var(--spacing-md);
  }

  /* Date range selector mobile optimization */
  .date-range-selector {
    padding: var(--spacing-sm);
  }

  .date-inputs {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .date-input input,
  .apply-button {
    min-height: var(--touch-target-comfortable);
    font-size: var(--font-size-base);
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .quick-ranges {
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }

  .quick-ranges button {
    min-height: var(--touch-target-min);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
    flex: 1;
    min-width: 120px;
  }

  /* Summary metrics mobile layout */
  .summary-metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
  }

  .metric-card {
    padding: var(--spacing-sm);
  }

  .metric-card h3 {
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-xs);
  }

  .metric-value {
    font-size: 1.5rem;
    margin: var(--spacing-xs) 0;
  }

  .metric-trend {
    font-size: var(--font-size-xs);
  }

  /* SDST insights mobile layout */
  .sdst-insights {
    padding: var(--spacing-sm);
  }

  .insights-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .insight-card {
    padding: var(--spacing-sm);
  }

  .insight-card h4 {
    font-size: var(--font-size-xs);
  }

  .time,
  .savings {
    font-size: var(--font-size-base);
  }

  /* Optimization opportunities mobile layout */
  .optimization-opportunities {
    padding: var(--spacing-sm);
  }

  .opportunities-list {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .opportunity-card {
    padding: var(--spacing-sm);
  }

  .opportunity-header h4 {
    font-size: var(--font-size-sm);
  }

  .priority-badge {
    font-size: 10px;
    padding: 2px var(--spacing-xs);
  }

  /* Charts mobile optimization */
  .chart-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .chart-container {
    padding: var(--spacing-sm);
  }

  .chart-container h3 {
    font-size: var(--font-size-base);
    margin-bottom: var(--spacing-sm);
  }

  .chart-placeholder {
    height: 250px;
  }

  .chart-mock {
    padding: var(--spacing-sm);
  }

  .chart-mock.horizontal .chart-label {
    width: 60px;
    font-size: var(--font-size-xs);
  }

  .chart-mock.horizontal .chart-value {
    width: 60px;
    font-size: var(--font-size-xs);
  }

  .chart-mock.pie {
    width: 150px;
    height: 150px;
  }

  .pie-legend {
    top: 170px;
    gap: var(--spacing-xs);
  }

  .legend-item {
    font-size: var(--font-size-xs);
  }

  /* Report links mobile layout */
  .report-links {
    padding: var(--spacing-sm);
  }

  .report-buttons {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .report-buttons button {
    width: 100%;
    min-height: var(--touch-target-comfortable);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-base);
  }
}

/* Small mobile adjustments (up to 480px) */
@media (max-width: 480px) {
  .analytics-dashboard {
    padding: var(--spacing-xs);
  }

  h1 {
    font-size: var(--font-size-lg);
    text-align: center;
  }

  /* Single column layout for metrics */
  .summary-metrics {
    grid-template-columns: 1fr;
    gap: var(--spacing-xs);
  }

  .metric-card {
    padding: var(--spacing-xs);
  }

  .metric-value {
    font-size: 1.25rem;
  }

  /* Compact date range selector */
  .date-range-selector {
    padding: var(--spacing-xs);
  }

  .quick-ranges button {
    min-width: 100px;
    font-size: var(--font-size-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
  }

  /* Compact charts */
  .chart-placeholder {
    height: 200px;
  }

  .chart-mock.pie {
    width: 120px;
    height: 120px;
  }

  .pie-legend {
    top: 140px;
  }

  /* Compact insight cards */
  .insight-card,
  .opportunity-card {
    padding: var(--spacing-xs);
  }

  .insight-card h4,
  .opportunity-header h4 {
    font-size: var(--font-size-xs);
  }

  .time,
  .savings {
    font-size: var(--font-size-sm);
  }

  .opportunity-description {
    font-size: var(--font-size-xs);
    line-height: 1.4;
  }
}

/* Touch-specific enhancements */
@media (hover: none) and (pointer: coarse) {
  .quick-ranges button:active,
  .apply-button:active,
  .report-buttons button:active {
    transform: scale(0.95);
    transition: transform 0.1s ease;
  }

  .metric-card:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }
}

/* Landscape orientation for mobile */
@media (max-height: 500px) and (orientation: landscape) {
  .analytics-dashboard {
    padding: var(--spacing-xs);
  }

  .date-inputs {
    flex-direction: row;
    gap: var(--spacing-sm);
  }

  .summary-metrics {
    grid-template-columns: repeat(5, 1fr);
    gap: var(--spacing-xs);
  }

  .metric-card {
    padding: var(--spacing-xs);
  }

  .metric-value {
    font-size: 1rem;
    margin: 2px 0;
  }

  .chart-placeholder {
    height: 180px;
  }

  .insights-grid,
  .opportunities-list {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
