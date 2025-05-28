<template>
  <div class="chart-container" :class="{ 'chart-loading': isLoading }">
    <div v-if="isLoading" class="chart-loading-overlay">
      <div class="loading-spinner"></div>
      <span>Loading chart data...</span>
    </div>
    
    <div v-else-if="error" class="chart-error">
      <div class="error-icon">⚠️</div>
      <div class="error-message">{{ error }}</div>
      <button @click="$emit('retry')" class="retry-button">Retry</button>
    </div>
    
    <div v-else-if="!hasData" class="chart-no-data">
      <div class="no-data-icon">📊</div>
      <div class="no-data-message">No data available for the selected period</div>
    </div>
    
    <div v-else class="chart-wrapper">
      <div v-if="title" class="chart-title">
        <h3>{{ title }}</h3>
        <div v-if="subtitle" class="chart-subtitle">{{ subtitle }}</div>
      </div>
      
      <div class="chart-canvas-container" :style="{ height: `${height}px` }">
        <canvas ref="chartCanvas"></canvas>
      </div>
      
      <div v-if="showLegend && legendData.length > 0" class="chart-legend">
        <div 
          v-for="(item, index) in legendData" 
          :key="index"
          class="legend-item"
          @click="toggleDataset(index)"
          :class="{ 'legend-item-hidden': item.hidden }"
        >
          <div 
            class="legend-color" 
            :style="{ backgroundColor: item.color }"
          ></div>
          <span class="legend-label">{{ item.label }}</span>
          <span v-if="item.value" class="legend-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  TimeScale,
  Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  TimeScale,
  Filler
);

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['line', 'bar', 'pie', 'doughnut', 'area'].includes(value)
  },
  data: {
    type: Object,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  height: {
    type: Number,
    default: 300
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  responsive: {
    type: Boolean,
    default: true
  },
  maintainAspectRatio: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['retry', 'datasetToggle', 'chartClick']);

const chartCanvas = ref(null);
const chartInstance = ref(null);

// Computed properties
const hasData = computed(() => {
  return props.data && 
         props.data.datasets && 
         props.data.datasets.length > 0 &&
         props.data.datasets.some(dataset => dataset.data && dataset.data.length > 0);
});

const legendData = computed(() => {
  if (!chartInstance.value || !props.data.datasets) return [];
  
  return props.data.datasets.map((dataset, index) => ({
    label: dataset.label,
    color: dataset.backgroundColor || dataset.borderColor,
    value: dataset.total || '',
    hidden: chartInstance.value.isDatasetVisible(index) === false
  }));
});

// Default chart options
const defaultOptions = computed(() => ({
  responsive: props.responsive,
  maintainAspectRatio: props.maintainAspectRatio,
  plugins: {
    legend: {
      display: false // We use custom legend
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
      callbacks: {
        title: (context) => {
          return context[0].label || '';
        },
        label: (context) => {
          const label = context.dataset.label || '';
          const value = context.parsed.y || context.parsed;
          return `${label}: ${formatValue(value)}`;
        }
      }
    }
  },
  scales: props.type === 'pie' || props.type === 'doughnut' ? {} : {
    x: {
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: '#666'
      }
    },
    y: {
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        color: '#666',
        callback: function(value) {
          return formatValue(value);
        }
      }
    }
  },
  onClick: (event, elements) => {
    if (elements.length > 0) {
      emit('chartClick', {
        event,
        elements,
        datasetIndex: elements[0].datasetIndex,
        index: elements[0].index
      });
    }
  }
}));

// Merged options
const mergedOptions = computed(() => {
  return {
    ...defaultOptions.value,
    ...props.options
  };
});

// Methods
const formatValue = (value) => {
  if (typeof value === 'number') {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K';
    } else if (value % 1 !== 0) {
      return value.toFixed(2);
    }
  }
  return value;
};

const createChart = async () => {
  if (!chartCanvas.value || !hasData.value) return;
  
  await nextTick();
  
  const ctx = chartCanvas.value.getContext('2d');
  
  // Destroy existing chart
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }
  
  // Create new chart
  chartInstance.value = new Chart(ctx, {
    type: props.type === 'area' ? 'line' : props.type,
    data: props.data,
    options: mergedOptions.value
  });
};

const updateChart = () => {
  if (!chartInstance.value) return;
  
  chartInstance.value.data = props.data;
  chartInstance.value.options = mergedOptions.value;
  chartInstance.value.update();
};

const toggleDataset = (index) => {
  if (!chartInstance.value) return;
  
  chartInstance.value.toggleDataVisibility(index);
  chartInstance.value.update();
  
  emit('datasetToggle', {
    index,
    visible: chartInstance.value.isDatasetVisible(index)
  });
};

// Watchers
watch(() => props.data, () => {
  if (chartInstance.value) {
    updateChart();
  } else {
    createChart();
  }
}, { deep: true });

watch(() => props.options, () => {
  if (chartInstance.value) {
    updateChart();
  }
}, { deep: true });

// Lifecycle
onMounted(() => {
  createChart();
});

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }
});
</script>

<style scoped>
.chart-container {
  position: relative;
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-loading-overlay,
.chart-error,
.chart-no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(var(--color-primary-rgb), 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-sm);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.no-data-icon {
  font-size: 2rem;
  margin-bottom: var(--spacing-sm);
}

.error-message,
.no-data-message {
  margin-bottom: var(--spacing-sm);
  text-align: center;
}

.retry-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

.chart-title h3 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--color-text);
  font-weight: var(--font-weight-bold);
}

.chart-subtitle {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

.chart-canvas-container {
  position: relative;
  margin: var(--spacing-md) 0;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-soft);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--border-radius-sm);
  transition: background-color 0.2s ease;
}

.legend-item:hover {
  background-color: var(--color-background-hover);
}

.legend-item-hidden {
  opacity: 0.5;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.legend-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-left: auto;
}
</style>
