<template>
  <div class="dashboard">
    <h1 class="text-3xl font-bold mb-4">Dashboard</h1>
    
    <div class="grid">
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-calendar text-primary mr-2"></i>
              <span>Today's Surgeries</span>
            </div>
          </template>
          <template #content>
            <div class="text-4xl font-bold text-center">{{ todaySurgeries }}</div>
            <div class="text-center text-sm text-gray-600">Scheduled for today</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-building text-primary mr-2"></i>
              <span>Operating Rooms</span>
            </div>
          </template>
          <template #content>
            <div class="text-4xl font-bold text-center">{{ operatingRoomsCount }}</div>
            <div class="text-center text-sm text-gray-600">Available rooms</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-user-plus text-primary mr-2"></i>
              <span>Surgeons</span>
            </div>
          </template>
          <template #content>
            <div class="text-4xl font-bold text-center">{{ surgeonsCount }}</div>
            <div class="text-center text-sm text-gray-600">Active surgeons</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-calendar-times text-primary mr-2"></i>
              <span>Upcoming Appointments</span>
            </div>
          </template>
          <template #content>
            <div class="text-4xl font-bold text-center">{{ upcomingAppointments }}</div>
            <div class="text-center text-sm text-gray-600">Next 7 days</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-8">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-chart-line text-primary mr-2"></i>
              <span>Surgery Schedule</span>
            </div>
          </template>
          <template #content>
            <Chart type="bar" :data="surgeryScheduleData" :options="chartOptions" />
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-4">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-chart-pie text-primary mr-2"></i>
              <span>Room Utilization</span>
            </div>
          </template>
          <template #content>
            <Chart type="doughnut" :data="roomUtilizationData" :options="pieChartOptions" />
          </template>
        </Card>
      </div>
      
      <div class="col-12">
        <Card>
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-calendar text-primary mr-2"></i>
              <span>Today's Schedule</span>
            </div>
          </template>
          <template #content>
            <DataTable :value="todaySchedule" :loading="loading" responsiveLayout="scroll">
              <Column field="time" header="Time"></Column>
              <Column field="surgery" header="Surgery"></Column>
              <Column field="surgeon" header="Surgeon"></Column>
              <Column field="room" header="Room"></Column>
              <Column field="status" header="Status">
                <template #body="slotProps">
                  <span :class="getStatusClass(slotProps.data.status)">
                    {{ slotProps.data.status }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Dashboard',
  setup() {
    const store = useStore()
    const loading = ref(true)
    
    // Mock data for demonstration
    const todaySurgeries = ref(8)
    const operatingRoomsCount = ref(5)
    const surgeonsCount = ref(12)
    const upcomingAppointments = ref(23)
    
    const surgeryScheduleData = ref({
      labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      datasets: [
        {
          label: 'Scheduled',
          backgroundColor: '#42A5F5',
          data: [7, 9, 5, 8, 6]
        },
        {
          label: 'Completed',
          backgroundColor: '#66BB6A',
          data: [6, 8, 5, 7, 0]
        }
      ]
    })
    
    const roomUtilizationData = ref({
      labels: ['OR-1', 'OR-2', 'OR-3', 'OR-4', 'OR-5'],
      datasets: [
        {
          data: [85, 70, 60, 90, 75],
          backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726', '#26C6DA', '#7E57C2']
        }
      ]
    })
    
    const chartOptions = ref({
      plugins: {
        legend: {
          position: 'bottom'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Surgeries'
          }
        }
      }
    })
    
    const pieChartOptions = ref({
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    })
    
    const todaySchedule = ref([
      { time: '08:00 - 09:30', surgery: 'Appendectomy', surgeon: 'Dr. Smith', room: 'OR-1', status: 'Completed' },
      { time: '09:45 - 11:15', surgery: 'Hernia Repair', surgeon: 'Dr. Johnson', room: 'OR-2', status: 'In Progress' },
      { time: '10:00 - 12:30', surgery: 'Gallbladder Removal', surgeon: 'Dr. Williams', room: 'OR-3', status: 'Scheduled' },
      { time: '13:00 - 15:00', surgery: 'Hip Replacement', surgeon: 'Dr. Brown', room: 'OR-1', status: 'Scheduled' },
      { time: '14:30 - 16:00', surgery: 'Cataract Surgery', surgeon: 'Dr. Davis', room: 'OR-4', status: 'Scheduled' }
    ])
    
    const getStatusClass = (status) => {
      switch (status) {
        case 'Completed':
          return 'p-tag p-tag-success'
        case 'In Progress':
          return 'p-tag p-tag-warning'
        case 'Scheduled':
          return 'p-tag p-tag-info'
        case 'Cancelled':
          return 'p-tag p-tag-danger'
        default:
          return 'p-tag'
      }
    }
    
    onMounted(() => {
      // In a real application, you would fetch data from the API here
      setTimeout(() => {
        loading.value = false
      }, 1000)
    })
    
    return {
      loading,
      todaySurgeries,
      operatingRoomsCount,
      surgeonsCount,
      upcomingAppointments,
      surgeryScheduleData,
      roomUtilizationData,
      chartOptions,
      pieChartOptions,
      todaySchedule,
      getStatusClass
    }
  }
}
</script>
