<template>
  <div class="utilization-reports">
    <h1>Utilization Reports</h1>
    
    <!-- Report Controls -->
    <div class="report-controls">
      <div class="filter-section">
        <h3>Filters</h3>
        <div class="filter-group">
          <label for="resource-type">Resource Type</label>
          <select id="resource-type" v-model="selectedResourceType">
            <option value="or">Operating Rooms</option>
            <option value="surgeon">Surgeons</option>
            <option value="equipment">Equipment</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="date-range">Date Range</label>
          <select id="date-range" v-model="selectedDateRange">
            <option value="last7">Last 7 Days</option>
            <option value="last30">Last 30 Days</option>
            <option value="thisMonth">This Month</option>
            <option value="lastMonth">Last Month</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        
        <div v-if="selectedDateRange === 'custom'" class="custom-date-range">
          <div class="date-input">
            <label for="start-date">Start Date</label>
            <input 
              type="date" 
              id="start-date" 
              v-model="customDateRange.start"
            >
          </div>
          <div class="date-input">
            <label for="end-date">End Date</label>
            <input 
              type="date" 
              id="end-date" 
              v-model="customDateRange.end"
            >
          </div>
        </div>
        
        <button class="apply-button" @click="applyFilters">Apply Filters</button>
      </div>
      
      <div class="view-options">
        <h3>View Options</h3>
        <div class="view-option-group">
          <label for="chart-type">Chart Type</label>
          <select id="chart-type" v-model="selectedChartType">
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
            <option value="pie">Pie Chart</option>
          </select>
        </div>
        
        <div class="view-option-group">
          <label for="metric">Primary Metric</label>
          <select id="metric" v-model="selectedMetric">
            <option value="utilizationRate">Utilization Rate</option>
            <option value="idleTime">Idle Time</option>
            <option value="overtimeRate">Overtime Rate</option>
            <option value="surgeryCount">Surgery Count</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading report data...</p>
    </div>
    
    <!-- Report Content -->
    <div v-else class="report-content">
      <h2>{{ reportTitle }}</h2>
      
      <!-- Chart Area -->
      <div class="chart-area">
        <div class="chart-container">
          <!-- Chart would be rendered here using a charting library -->
          <div class="chart-placeholder">
            <div class="chart-mock" :class="selectedChartType">
              <!-- Mock chart content based on selectedChartType -->
              <template v-if="selectedChartType === 'bar'">
                <div 
                  v-for="(item, index) in chartData" 
                  :key="index" 
                  class="chart-bar" 
                  :style="{ height: `${item.value * 100}%` }"
                >
                  <div class="bar-label">{{ item.label }}</div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Data Table -->
      <div class="data-table-container">
        <h3>Detailed Data</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Resource</th>
              <th>Utilization Rate</th>
              <th>Idle Time (hrs)</th>
              <th>Overtime Rate</th>
              <th>Surgery Count</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in tableData" :key="index">
              <td>{{ item.name }}</td>
              <td>{{ formatPercentage(item.utilizationRate) }}</td>
              <td>{{ item.idleTime.toFixed(1) }}</td>
              <td>{{ formatPercentage(item.overtimeRate) }}</td>
              <td>{{ item.surgeryCount }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td><strong>Average</strong></td>
              <td>{{ formatPercentage(averageUtilization) }}</td>
              <td>{{ averageIdleTime.toFixed(1) }}</td>
              <td>{{ formatPercentage(averageOvertimeRate) }}</td>
              <td>{{ totalSurgeryCount }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
      
      <!-- Export Options -->
      <div class="export-options">
        <button @click="exportToPDF">Export to PDF</button>
        <button @click="exportToCSV">Export to CSV</button>
        <button @click="saveAsCustomReport">Save as Custom Report</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { storeToRefs } from 'pinia';

const analyticsStore = useAnalyticsStore();
const { isLoading, error } = storeToRefs(analyticsStore);

// Filter state
const selectedResourceType = ref('or');
const selectedDateRange = ref('last30');
const customDateRange = ref({
  start: '',
  end: ''
});
const selectedChartType = ref('bar');
const selectedMetric = ref('utilizationRate');

// Mock data for demonstration
const chartData = ref([
  { label: 'OR 1', value: 0.85 },
  { label: 'OR 2', value: 0.72 },
  { label: 'OR 3', value: 0.65 },
  { label: 'OR 4', value: 0.91 },
  { label: 'OR 5', value: 0.78 },
]);

const tableData = ref([
  { name: 'OR 1', utilizationRate: 0.85, idleTime: 1.2, overtimeRate: 0.0, surgeryCount: 12 },
  { name: 'OR 2', utilizationRate: 0.72, idleTime: 2.2, overtimeRate: 0.0, surgeryCount: 8 },
  { name: 'OR 3', utilizationRate: 0.65, idleTime: 2.8, overtimeRate: 0.0, surgeryCount: 6 },
  { name: 'OR 4', utilizationRate: 0.91, idleTime: 0.7, overtimeRate: 0.0, surgeryCount: 14 },
  { name: 'OR 5', utilizationRate: 0.78, idleTime: 1.8, overtimeRate: 0.0, surgeryCount: 10 },
]);

// Computed properties
const reportTitle = computed(() => {
  const resourceTypeText = selectedResourceType.value === 'or' 
    ? 'Operating Room' 
    : selectedResourceType.value === 'surgeon' 
      ? 'Surgeon' 
      : 'Equipment';
  
  const metricText = selectedMetric.value === 'utilizationRate' 
    ? 'Utilization Rate' 
    : selectedMetric.value === 'idleTime' 
      ? 'Idle Time' 
      : selectedMetric.value === 'overtimeRate' 
        ? 'Overtime Rate' 
        : 'Surgery Count';
  
  return `${resourceTypeText} ${metricText} Report`;
});

const averageUtilization = computed(() => {
  return tableData.value.reduce((sum, item) => sum + item.utilizationRate, 0) / tableData.value.length;
});

const averageIdleTime = computed(() => {
  return tableData.value.reduce((sum, item) => sum + item.idleTime, 0) / tableData.value.length;
});

const averageOvertimeRate = computed(() => {
  return tableData.value.reduce((sum, item) => sum + item.overtimeRate, 0) / tableData.value.length;
});

const totalSurgeryCount = computed(() => {
  return tableData.value.reduce((sum, item) => sum + item.surgeryCount, 0);
});

// Methods
const formatPercentage = (value) => {
  return `${Math.round(value * 100)}%`;
};

const applyFilters = async () => {
  // In a real app, this would update the date range in the store and reload the data
  console.log('Applying filters:', {
    resourceType: selectedResourceType.value,
    dateRange: selectedDateRange.value,
    customDateRange: customDateRange.value,
    chartType: selectedChartType.value,
    metric: selectedMetric.value
  });
  
  // Simulate loading
  isLoading.value = true;
  await new Promise(resolve => setTimeout(resolve, 1000));
  isLoading.value = false;
  
  // In a real app, we would update the chart and table data here
};

const exportToPDF = () => {
  console.log('Exporting to PDF...');
  // In a real app, this would generate a PDF of the report
};

const exportToCSV = () => {
  console.log('Exporting to CSV...');
  // In a real app, this would generate a CSV of the report data
};

const saveAsCustomReport = () => {
  console.log('Saving as custom report...');
  // In a real app, this would save the current report configuration to the store
};

// Initialize the component
onMounted(async () => {
  // Set default date range
  const today = new Date();
  const thirtyDaysAgo = new Date(today);
  thirtyDaysAgo.setDate(today.getDate() - 30);
  
  customDateRange.value.start = thirtyDaysAgo.toISOString().split('T')[0];
  customDateRange.value.end = today.toISOString().split('T')[0];
  
  // Load initial data
  await applyFilters();
});

// Watch for changes in resource type to update the chart and table data
watch(selectedResourceType, async () => {
  await applyFilters();
});
</script>

<style scoped>
.utilization-reports {
  padding: var(--spacing-md);
  max-width: 1200px;
  margin: 0 auto;
}

h1, h2, h3 {
  margin-top: 0;
  color: var(--color-text);
}

h1 {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

h3 {
  margin-bottom: var(--spacing-sm);
}

/* Report Controls */
.report-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.filter-section, .view-options {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.filter-group, .view-option-group {
  margin-bottom: var(--spacing-sm);
}

.filter-group label, .view-option-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

select, input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background);
}

.custom-date-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.apply-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  margin-top: var(--spacing-sm);
}

/* Loading Overlay */
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

/* Chart Area */
.chart-area {
  margin-bottom: var(--spacing-lg);
}

.chart-container {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  height: 400px;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
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

.chart-bar {
  background-color: var(--color-primary);
  width: 60px;
  border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
  position: relative;
}

.bar-label {
  position: absolute;
  bottom: -25px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: var(--font-size-sm);
}

/* Data Table */
.data-table-container {
  margin-bottom: var(--spacing-lg);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  overflow: hidden;
}

.data-table th, .data-table td {
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background-color: var(--color-background-mute);
  font-weight: var(--font-weight-bold);
}

.data-table tbody tr:hover {
  background-color: var(--color-background-hover);
}

.data-table tfoot {
  background-color: var(--color-background-mute);
  font-weight: var(--font-weight-medium);
}

/* Export Options */
.export-options {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
}

.export-options button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .report-controls {
    grid-template-columns: 1fr;
  }
  
  .custom-date-range {
    grid-template-columns: 1fr;
  }
  
  .export-options {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
