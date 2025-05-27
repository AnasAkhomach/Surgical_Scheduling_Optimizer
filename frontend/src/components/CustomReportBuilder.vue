<template>
  <div class="custom-report-builder">
    <h1>Custom Report Builder</h1>
    
    <div class="report-builder-container">
      <!-- Report Configuration Form -->
      <div class="report-config-form">
        <h2>Report Configuration</h2>
        
        <div class="form-group">
          <label for="report-name">Report Name</label>
          <input 
            type="text" 
            id="report-name" 
            v-model="reportConfig.name" 
            placeholder="Enter a name for your report"
          >
        </div>
        
        <div class="form-group">
          <label for="report-type">Report Type</label>
          <select id="report-type" v-model="reportConfig.type">
            <option value="orUtilization">OR Utilization</option>
            <option value="surgeonUtilization">Surgeon Utilization</option>
            <option value="surgeryTypeDistribution">Surgery Type Distribution</option>
            <option value="sdstEfficiency">SDST Efficiency</option>
            <option value="dailyMetrics">Daily Metrics</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Date Range</label>
          <div class="date-range-inputs">
            <div class="date-input">
              <label for="start-date">Start Date</label>
              <input 
                type="date" 
                id="start-date" 
                v-model="reportConfig.dateRange.start"
              >
            </div>
            <div class="date-input">
              <label for="end-date">End Date</label>
              <input 
                type="date" 
                id="end-date" 
                v-model="reportConfig.dateRange.end"
              >
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label>Metrics to Include</label>
          <div class="metrics-selection">
            <div v-if="reportConfig.type === 'orUtilization'" class="checkbox-group">
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="utilizationRate">
                Utilization Rate
              </label>
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="idleTime">
                Idle Time
              </label>
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="overtimeRate">
                Overtime Rate
              </label>
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="surgeryCount">
                Surgery Count
              </label>
            </div>
            
            <div v-else-if="reportConfig.type === 'surgeonUtilization'" class="checkbox-group">
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="surgeryCount">
                Surgery Count
              </label>
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="totalHours">
                Total Hours
              </label>
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="averageDuration">
                Average Duration
              </label>
              <label>
                <input type="checkbox" v-model="reportConfig.metrics" value="onTimeStart">
                On-Time Start %
              </label>
            </div>
            
            <!-- Other metric options for different report types would go here -->
            <div v-else class="checkbox-group">
              <p>Select a report type to see available metrics</p>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="chart-type">Chart Type</label>
          <select id="chart-type" v-model="reportConfig.chartType">
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
            <option value="pie">Pie Chart</option>
            <option value="table">Table Only</option>
          </select>
        </div>
        
        <div class="form-actions">
          <button class="secondary-button" @click="resetForm">Reset</button>
          <button class="primary-button" @click="generateReport" :disabled="!isFormValid">Generate Report</button>
        </div>
      </div>
      
      <!-- Report Preview -->
      <div class="report-preview">
        <h2>Report Preview</h2>
        
        <div v-if="isLoading" class="loading-overlay">
          <div class="spinner"></div>
          <p>Generating report preview...</p>
        </div>
        
        <div v-else-if="!reportGenerated" class="empty-preview">
          <p>Configure your report and click "Generate Report" to see a preview</p>
        </div>
        
        <div v-else class="preview-content">
          <h3>{{ reportConfig.name }}</h3>
          
          <!-- Chart Preview -->
          <div class="chart-preview">
            <div class="chart-placeholder">
              <div class="chart-mock" :class="reportConfig.chartType">
                <!-- Mock chart content based on chartType -->
                <template v-if="reportConfig.chartType === 'bar'">
                  <div 
                    v-for="(item, index) in previewData" 
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
          
          <!-- Table Preview -->
          <div class="table-preview">
            <table>
              <thead>
                <tr>
                  <th>Resource</th>
                  <th v-for="metric in reportConfig.metrics" :key="metric">
                    {{ formatMetricName(metric) }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in previewData" :key="index">
                  <td>{{ item.label }}</td>
                  <td v-for="metric in reportConfig.metrics" :key="`${index}-${metric}`">
                    {{ formatMetricValue(item[metric], metric) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="preview-actions">
            <button class="secondary-button" @click="saveReport">Save Report</button>
            <button class="primary-button" @click="exportReport">Export Report</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Saved Reports Section -->
    <div class="saved-reports">
      <h2>Saved Reports</h2>
      
      <div v-if="savedReports.length === 0" class="no-saved-reports">
        <p>You haven't saved any custom reports yet</p>
      </div>
      
      <div v-else class="saved-reports-list">
        <div v-for="report in savedReports" :key="report.id" class="saved-report-card">
          <div class="report-info">
            <h3>{{ report.name }}</h3>
            <p>{{ getReportTypeLabel(report.type) }}</p>
            <p class="date-range">{{ formatDateRange(report.dateRange) }}</p>
          </div>
          <div class="report-actions">
            <button class="icon-button" @click="loadReport(report)">
              <span class="icon">📋</span>
              <span class="label">Load</span>
            </button>
            <button class="icon-button" @click="deleteReport(report.id)">
              <span class="icon">🗑️</span>
              <span class="label">Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { storeToRefs } from 'pinia';

const analyticsStore = useAnalyticsStore();
const { isLoading, savedReports } = storeToRefs(analyticsStore);

// Report configuration state
const reportConfig = ref({
  name: '',
  type: '',
  dateRange: {
    start: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  },
  metrics: [],
  chartType: 'bar'
});

// Preview data state
const reportGenerated = ref(false);
const previewData = ref([]);

// Computed properties
const isFormValid = computed(() => {
  return (
    reportConfig.value.name.trim() !== '' &&
    reportConfig.value.type !== '' &&
    reportConfig.value.metrics.length > 0
  );
});

// Methods
const resetForm = () => {
  reportConfig.value = {
    name: '',
    type: '',
    dateRange: {
      start: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0]
    },
    metrics: [],
    chartType: 'bar'
  };
  reportGenerated.value = false;
};

const generateReport = async () => {
  if (!isFormValid.value) return;
  
  isLoading.value = true;
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate mock preview data based on report type
    if (reportConfig.value.type === 'orUtilization') {
      previewData.value = [
        { label: 'OR 1', utilizationRate: 0.85, idleTime: 1.2, overtimeRate: 0.0, surgeryCount: 12 },
        { label: 'OR 2', utilizationRate: 0.72, idleTime: 2.2, overtimeRate: 0.0, surgeryCount: 8 },
        { label: 'OR 3', utilizationRate: 0.65, idleTime: 2.8, overtimeRate: 0.0, surgeryCount: 6 },
        { label: 'OR 4', utilizationRate: 0.91, idleTime: 0.7, overtimeRate: 0.0, surgeryCount: 14 },
        { label: 'OR 5', utilizationRate: 0.78, idleTime: 1.8, overtimeRate: 0.0, surgeryCount: 10 },
      ];
    } else if (reportConfig.value.type === 'surgeonUtilization') {
      previewData.value = [
        { label: 'Dr. Smith', surgeryCount: 45, totalHours: 90, averageDuration: 120, onTimeStart: 0.9, value: 0.9 },
        { label: 'Dr. Adams', surgeryCount: 38, totalHours: 76, averageDuration: 120, onTimeStart: 0.85, value: 0.75 },
        { label: 'Dr. Chen', surgeryCount: 30, totalHours: 45, averageDuration: 90, onTimeStart: 0.8, value: 0.6 },
        { label: 'Dr. Wong', surgeryCount: 20, totalHours: 30, averageDuration: 90, onTimeStart: 0.75, value: 0.4 },
      ];
    }
    
    // Set value property for chart visualization
    previewData.value.forEach(item => {
      if (!item.value) {
        // Default to first metric if value not set
        const firstMetric = reportConfig.value.metrics[0];
        item.value = item[firstMetric] || 0.5;
      }
    });
    
    reportGenerated.value = true;
  } catch (error) {
    console.error('Error generating report:', error);
  } finally {
    isLoading.value = false;
  }
};

const saveReport = async () => {
  if (!reportGenerated.value) return;
  
  try {
    const reportId = await analyticsStore.saveCustomReport({
      name: reportConfig.value.name,
      type: reportConfig.value.type,
      dateRange: {
        start: new Date(reportConfig.value.dateRange.start),
        end: new Date(reportConfig.value.dateRange.end)
      },
      metrics: [...reportConfig.value.metrics],
      chartType: reportConfig.value.chartType
    });
    
    console.log('Report saved with ID:', reportId);
    alert('Report saved successfully!');
  } catch (error) {
    console.error('Error saving report:', error);
    alert('Failed to save report. Please try again.');
  }
};

const exportReport = () => {
  if (!reportGenerated.value) return;
  
  console.log('Exporting report:', reportConfig.value);
  alert('Report export functionality will be implemented in the next phase.');
};

const loadReport = (report) => {
  reportConfig.value = {
    name: report.name,
    type: report.type,
    dateRange: {
      start: new Date(report.dateRange.start).toISOString().split('T')[0],
      end: new Date(report.dateRange.end).toISOString().split('T')[0]
    },
    metrics: [...report.metrics],
    chartType: report.chartType
  };
  
  generateReport();
};

const deleteReport = async (reportId) => {
  if (confirm('Are you sure you want to delete this report?')) {
    await analyticsStore.deleteCustomReport(reportId);
    console.log('Report deleted:', reportId);
  }
};

const formatMetricName = (metric) => {
  switch (metric) {
    case 'utilizationRate': return 'Utilization Rate';
    case 'idleTime': return 'Idle Time (hrs)';
    case 'overtimeRate': return 'Overtime Rate';
    case 'surgeryCount': return 'Surgery Count';
    case 'totalHours': return 'Total Hours';
    case 'averageDuration': return 'Avg. Duration (min)';
    case 'onTimeStart': return 'On-Time Start %';
    default: return metric;
  }
};

const formatMetricValue = (value, metric) => {
  if (value === undefined) return 'N/A';
  
  switch (metric) {
    case 'utilizationRate':
    case 'overtimeRate':
    case 'onTimeStart':
      return `${Math.round(value * 100)}%`;
    case 'idleTime':
    case 'totalHours':
      return value.toFixed(1);
    case 'averageDuration':
      return `${Math.round(value)} min`;
    default:
      return value;
  }
};

const getReportTypeLabel = (type) => {
  switch (type) {
    case 'orUtilization': return 'OR Utilization';
    case 'surgeonUtilization': return 'Surgeon Utilization';
    case 'surgeryTypeDistribution': return 'Surgery Type Distribution';
    case 'sdstEfficiency': return 'SDST Efficiency';
    case 'dailyMetrics': return 'Daily Metrics';
    default: return type;
  }
};

const formatDateRange = (dateRange) => {
  const start = new Date(dateRange.start);
  const end = new Date(dateRange.end);
  
  return `${start.toLocaleDateString()} - ${end.toLocaleDateString()}`;
};

// Initialize the component
onMounted(() => {
  // Nothing to do on mount for now
});
</script>

<style scoped>
.custom-report-builder {
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

/* Report Builder Container */
.report-builder-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

/* Form Styles */
.report-config-form {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

input[type="text"],
select {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background);
}

.date-range-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
}

.date-input label {
  font-weight: var(--font-weight-normal);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.checkbox-group label {
  display: flex;
  align-items: center;
  font-weight: var(--font-weight-normal);
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  margin-right: var(--spacing-xs);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.primary-button,
.secondary-button {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  border: none;
  cursor: pointer;
}

.primary-button {
  background-color: var(--color-primary);
  color: white;
}

.primary-button:disabled {
  background-color: var(--color-background-mute);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.secondary-button {
  background-color: var(--color-background-mute);
  color: var(--color-text);
}

/* Report Preview */
.report-preview {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.empty-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  color: var(--color-text-secondary);
  text-align: center;
  padding: var(--spacing-md);
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
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

.preview-content h3 {
  text-align: center;
  margin-bottom: var(--spacing-md);
}

.chart-preview {
  margin-bottom: var(--spacing-md);
}

.chart-placeholder {
  height: 300px;
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

.table-preview {
  margin-bottom: var(--spacing-md);
  overflow-x: auto;
}

.table-preview table {
  width: 100%;
  border-collapse: collapse;
}

.table-preview th,
.table-preview td {
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table-preview th {
  background-color: var(--color-background-mute);
  font-weight: var(--font-weight-bold);
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

/* Saved Reports */
.saved-reports {
  margin-top: var(--spacing-xl);
}

.no-saved-reports {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  text-align: center;
  color: var(--color-text-secondary);
}

.saved-reports-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

.saved-report-card {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  display: flex;
  flex-direction: column;
}

.report-info {
  flex-grow: 1;
}

.report-info h3 {
  margin-bottom: var(--spacing-xs);
}

.report-info p {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--color-text-secondary);
}

.date-range {
  font-size: var(--font-size-sm);
}

.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.icon-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

.icon-button:hover {
  background-color: var(--color-background-hover);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .report-builder-container {
    grid-template-columns: 1fr;
  }
  
  .date-range-inputs {
    grid-template-columns: 1fr;
  }
}
</style>
