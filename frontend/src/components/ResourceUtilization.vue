<template>
  <div class="resource-utilization">
    <Card>
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-chart-bar text-primary mr-2"></i>
          <span>{{ title }}</span>
        </div>
      </template>
      <template #content>
        <div class="filter-controls mb-3">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="dateRange">Date Range</label>
                <Dropdown id="dateRange" v-model="selectedDateRange" :options="dateRanges" optionLabel="label" optionValue="value" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="groupBy">Group By</label>
                <Dropdown id="groupBy" v-model="selectedGroupBy" :options="groupByOptions" optionLabel="label" optionValue="value" class="w-full" />
              </div>
            </div>
          </div>
        </div>
        
        <Chart type="bar" :data="chartData" :options="chartOptions" />
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';

export default {
  name: 'ResourceUtilization',
  props: {
    title: {
      type: String,
      default: 'Resource Utilization'
    },
    type: {
      type: String,
      default: 'room', // 'room' or 'surgeon'
      validator: (value) => ['room', 'surgeon'].includes(value)
    },
    data: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const selectedDateRange = ref('week');
    const selectedGroupBy = ref('day');
    
    const dateRanges = [
      { label: 'Today', value: 'today' },
      { label: 'This Week', value: 'week' },
      { label: 'This Month', value: 'month' }
    ];
    
    const groupByOptions = [
      { label: 'Day', value: 'day' },
      { label: 'Week', value: 'week' },
      { label: 'Month', value: 'month' }
    ];
    
    // Mock data for room utilization
    const roomUtilizationData = {
      today: {
        day: {
          labels: ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
          datasets: [
            {
              label: 'OR-1',
              backgroundColor: '#42A5F5',
              data: [100, 100, 100, 0, 0, 100, 100, 100, 0, 0]
            },
            {
              label: 'OR-2',
              backgroundColor: '#66BB6A',
              data: [0, 100, 100, 100, 0, 0, 100, 100, 100, 0]
            },
            {
              label: 'OR-3',
              backgroundColor: '#FFA726',
              data: [0, 0, 100, 100, 100, 0, 0, 100, 100, 100]
            },
            {
              label: 'OR-4',
              backgroundColor: '#26C6DA',
              data: [100, 0, 0, 100, 100, 100, 0, 0, 100, 100]
            }
          ]
        }
      },
      week: {
        day: {
          labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
          datasets: [
            {
              label: 'OR-1',
              backgroundColor: '#42A5F5',
              data: [85, 90, 75, 80, 70]
            },
            {
              label: 'OR-2',
              backgroundColor: '#66BB6A',
              data: [70, 85, 90, 75, 80]
            },
            {
              label: 'OR-3',
              backgroundColor: '#FFA726',
              data: [60, 70, 85, 90, 75]
            },
            {
              label: 'OR-4',
              backgroundColor: '#26C6DA',
              data: [90, 60, 70, 85, 90]
            }
          ]
        }
      },
      month: {
        week: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [
            {
              label: 'OR-1',
              backgroundColor: '#42A5F5',
              data: [80, 85, 75, 90]
            },
            {
              label: 'OR-2',
              backgroundColor: '#66BB6A',
              data: [75, 80, 85, 75]
            },
            {
              label: 'OR-3',
              backgroundColor: '#FFA726',
              data: [70, 75, 80, 85]
            },
            {
              label: 'OR-4',
              backgroundColor: '#26C6DA',
              data: [85, 70, 75, 80]
            }
          ]
        }
      }
    };
    
    // Mock data for surgeon utilization
    const surgeonUtilizationData = {
      today: {
        day: {
          labels: ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
          datasets: [
            {
              label: 'Dr. Smith',
              backgroundColor: '#42A5F5',
              data: [100, 100, 0, 0, 0, 100, 100, 0, 0, 0]
            },
            {
              label: 'Dr. Johnson',
              backgroundColor: '#66BB6A',
              data: [0, 100, 100, 0, 0, 0, 100, 100, 0, 0]
            },
            {
              label: 'Dr. Williams',
              backgroundColor: '#FFA726',
              data: [0, 0, 100, 100, 0, 0, 0, 100, 100, 0]
            },
            {
              label: 'Dr. Brown',
              backgroundColor: '#26C6DA',
              data: [0, 0, 0, 100, 100, 0, 0, 0, 100, 100]
            }
          ]
        }
      },
      week: {
        day: {
          labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
          datasets: [
            {
              label: 'Dr. Smith',
              backgroundColor: '#42A5F5',
              data: [80, 70, 60, 90, 75]
            },
            {
              label: 'Dr. Johnson',
              backgroundColor: '#66BB6A',
              data: [75, 80, 70, 60, 90]
            },
            {
              label: 'Dr. Williams',
              backgroundColor: '#FFA726',
              data: [90, 75, 80, 70, 60]
            },
            {
              label: 'Dr. Brown',
              backgroundColor: '#26C6DA',
              data: [60, 90, 75, 80, 70]
            }
          ]
        }
      },
      month: {
        week: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [
            {
              label: 'Dr. Smith',
              backgroundColor: '#42A5F5',
              data: [75, 80, 85, 70]
            },
            {
              label: 'Dr. Johnson',
              backgroundColor: '#66BB6A',
              data: [70, 75, 80, 85]
            },
            {
              label: 'Dr. Williams',
              backgroundColor: '#FFA726',
              data: [85, 70, 75, 80]
            },
            {
              label: 'Dr. Brown',
              backgroundColor: '#26C6DA',
              data: [80, 85, 70, 75]
            }
          ]
        }
      }
    };
    
    const chartData = computed(() => {
      const dataSource = props.type === 'room' ? roomUtilizationData : surgeonUtilizationData;
      
      // Try to get data for the selected date range and group by
      let data = dataSource[selectedDateRange.value]?.[selectedGroupBy.value];
      
      // If not available, fall back to a default
      if (!data) {
        if (selectedDateRange.value === 'today') {
          data = dataSource.today.day;
        } else if (selectedDateRange.value === 'week') {
          data = dataSource.week.day;
        } else {
          data = dataSource.month.week;
        }
      }
      
      return data;
    });
    
    const chartOptions = computed(() => {
      return {
        plugins: {
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${context.raw}%`;
              }
            }
          }
        },
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            stacked: true
          },
          y: {
            stacked: true,
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: 'Utilization (%)'
            }
          }
        }
      };
    });
    
    // Watch for changes in props.data and update the chart
    watch(() => props.data, (newData) => {
      // In a real application, we would process the new data here
      // For now, we're using mock data
    });
    
    return {
      selectedDateRange,
      selectedGroupBy,
      dateRanges,
      groupByOptions,
      chartData,
      chartOptions
    };
  }
}
</script>

<style scoped>
.resource-utilization {
  height: 100%;
}
</style>
