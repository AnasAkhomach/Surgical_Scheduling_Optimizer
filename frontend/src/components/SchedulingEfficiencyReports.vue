<template>
  <div class="efficiency-reports">
    <h1>Scheduling Efficiency Reports</h1>
    
    <!-- Report Controls -->
    <div class="report-controls">
      <div class="filter-section">
        <h3>Filters</h3>
        <div class="filter-group">
          <label for="metric-type">Efficiency Metric</label>
          <select id="metric-type" v-model="selectedMetricType">
            <option value="sdst">SDST Efficiency</option>
            <option value="turnaround">Turnaround Time</option>
            <option value="ontime">On-Time Start Rate</option>
            <option value="overtime">Overtime Analysis</option>
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
    </div>
    
    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading report data...</p>
    </div>
    
    <!-- Report Content -->
    <div v-else class="report-content">
      <h2>{{ reportTitle }}</h2>
      
      <!-- SDST Efficiency Report -->
      <div v-if="selectedMetricType === 'sdst'" class="sdst-efficiency">
        <div class="summary-cards">
          <div class="metric-card">
            <h3>Average SDST</h3>
            <div class="metric-value">{{ sdstData.averageSDST }} min</div>
            <div class="metric-description">Average setup time between surgeries</div>
          </div>
          
          <div class="metric-card">
            <h3>SDST % of OR Time</h3>
            <div class="metric-value">{{ formatPercentage(sdstData.sdstPercentage) }}</div>
            <div class="metric-description">Percentage of total OR time spent on setup</div>
          </div>
          
          <div class="metric-card">
            <h3>Potential Time Savings</h3>
            <div class="metric-value">{{ sdstData.potentialSavings }} min/day</div>
            <div class="metric-description">Estimated time that could be saved with optimal scheduling</div>
          </div>
        </div>
        
        <div class="efficiency-tables">
          <div class="efficiency-table">
            <h3>Most Efficient Transitions</h3>
            <table>
              <thead>
                <tr>
                  <th>From</th>
                  <th>To</th>
                  <th>Avg. Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>APPEN</td>
                  <td>KNEE</td>
                  <td>15 min</td>
                </tr>
                <tr>
                  <td>KNEE</td>
                  <td>HIPRE</td>
                  <td>15 min</td>
                </tr>
                <tr>
                  <td>HERNI</td>
                  <td>APPEN</td>
                  <td>15 min</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="efficiency-table">
            <h3>Least Efficient Transitions</h3>
            <table>
              <thead>
                <tr>
                  <th>From</th>
                  <th>To</th>
                  <th>Avg. Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>CABG</td>
                  <td>APPEN</td>
                  <td>45 min</td>
                </tr>
                <tr>
                  <td>CABG</td>
                  <td>CATAR</td>
                  <td>45 min</td>
                </tr>
                <tr>
                  <td>HIPRE</td>
                  <td>CABG</td>
                  <td>45 min</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div class="recommendations">
          <h3>Recommendations</h3>
          <ul>
            <li>Group similar surgery types together to minimize SDST</li>
            <li>Schedule CABG procedures at the end of the day when possible</li>
            <li>Consider dedicated ORs for specific surgery types to reduce setup times</li>
          </ul>
        </div>
      </div>
      
      <!-- Turnaround Time Report -->
      <div v-else-if="selectedMetricType === 'turnaround'" class="turnaround-time">
        <!-- Turnaround time report content would go here -->
        <p>Turnaround Time Report content will be implemented in the next phase.</p>
      </div>
      
      <!-- On-Time Start Rate Report -->
      <div v-else-if="selectedMetricType === 'ontime'" class="ontime-start">
        <!-- On-time start report content would go here -->
        <p>On-Time Start Rate Report content will be implemented in the next phase.</p>
      </div>
      
      <!-- Overtime Analysis Report -->
      <div v-else-if="selectedMetricType === 'overtime'" class="overtime-analysis">
        <!-- Overtime analysis report content would go here -->
        <p>Overtime Analysis Report content will be implemented in the next phase.</p>
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
import { ref, computed, onMounted } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { storeToRefs } from 'pinia';

const analyticsStore = useAnalyticsStore();
const { isLoading, error } = storeToRefs(analyticsStore);

// Filter state
const selectedMetricType = ref('sdst');
const selectedDateRange = ref('last30');
const customDateRange = ref({
  start: '',
  end: ''
});

// Mock data for SDST efficiency
const sdstData = ref({
  averageSDST: 22.5,
  sdstPercentage: 0.12,
  potentialSavings: 120,
  mostEfficientTransitions: [
    { from: 'APPEN', to: 'KNEE', time: 15 },
    { from: 'KNEE', to: 'HIPRE', time: 15 },
    { from: 'HERNI', to: 'APPEN', time: 15 }
  ],
  leastEfficientTransitions: [
    { from: 'CABG', to: 'APPEN', time: 45 },
    { from: 'CABG', to: 'CATAR', time: 45 },
    { from: 'HIPRE', to: 'CABG', time: 45 }
  ]
});

// Computed properties
const reportTitle = computed(() => {
  switch (selectedMetricType.value) {
    case 'sdst':
      return 'SDST Efficiency Report';
    case 'turnaround':
      return 'Turnaround Time Analysis';
    case 'ontime':
      return 'On-Time Start Rate Analysis';
    case 'overtime':
      return 'Overtime Analysis';
    default:
      return 'Scheduling Efficiency Report';
  }
});

// Methods
const formatPercentage = (value) => {
  return `${Math.round(value * 100)}%`;
};

const applyFilters = async () => {
  // In a real app, this would update the date range in the store and reload the data
  console.log('Applying filters:', {
    metricType: selectedMetricType.value,
    dateRange: selectedDateRange.value,
    customDateRange: customDateRange.value
  });
  
  // Simulate loading
  isLoading.value = true;
  await new Promise(resolve => setTimeout(resolve, 1000));
  isLoading.value = false;
  
  // In a real app, we would update the report data here
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
</script>

<style scoped>
.efficiency-reports {
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
  margin-bottom: var(--spacing-lg);
}

.filter-section {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.filter-group {
  margin-bottom: var(--spacing-sm);
}

.filter-group label {
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

/* SDST Efficiency Report */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.metric-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.efficiency-tables {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.efficiency-table {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.efficiency-table table {
  width: 100%;
  border-collapse: collapse;
}

.efficiency-table th, .efficiency-table td {
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.efficiency-table th {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-secondary);
}

.recommendations {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.recommendations ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.recommendations li {
  margin-bottom: var(--spacing-xs);
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
  .custom-date-range {
    grid-template-columns: 1fr;
  }
  
  .export-options {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
