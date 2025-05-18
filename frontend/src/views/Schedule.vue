<template>
  <div class="schedule">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold">Surgery Schedule</h1>
      <div>
        <Button label="Optimize Schedule" icon="pi pi-cog" @click="optimizeSchedule" class="mr-2" />
        <Button label="Apply Schedule" icon="pi pi-check" @click="applySchedule" :disabled="!optimizedSchedule.length" />
      </div>
    </div>
    
    <Card class="mb-4">
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-sliders-h text-primary mr-2"></i>
          <span>Optimization Parameters</span>
        </div>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="date">Date</label>
              <Calendar id="date" v-model="optimizationParams.date" dateFormat="yy-mm-dd" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="maxIterations">Max Iterations</label>
              <InputText id="maxIterations" v-model.number="optimizationParams.max_iterations" type="number" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="tabuTenure">Tabu Tenure</label>
              <InputText id="tabuTenure" v-model.number="optimizationParams.tabu_tenure" type="number" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="timeLimit">Time Limit (seconds)</label>
              <InputText id="timeLimit" v-model.number="optimizationParams.time_limit_seconds" type="number" />
            </div>
          </div>
        </div>
        
        <h3 class="text-xl font-bold mt-4 mb-2">Optimization Weights</h3>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="orUtilization">OR Utilization</label>
              <InputText id="orUtilization" v-model.number="optimizationParams.weights.or_utilization" type="number" step="0.1" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="setupTimes">Setup Times</label>
              <InputText id="setupTimes" v-model.number="optimizationParams.weights.setup_times" type="number" step="0.1" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="surgeonPreferences">Surgeon Preferences</label>
              <InputText id="surgeonPreferences" v-model.number="optimizationParams.weights.surgeon_preferences" type="number" step="0.1" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="patientWaitTime">Patient Wait Time</label>
              <InputText id="patientWaitTime" v-model.number="optimizationParams.weights.patient_wait_time" type="number" step="0.1" />
            </div>
          </div>
        </div>
      </template>
    </Card>
    
    <Card>
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-calendar text-primary mr-2"></i>
          <span>{{ optimizedSchedule.length ? 'Optimized Schedule' : 'Current Schedule' }}</span>
        </div>
      </template>
      <template #content>
        <div v-if="loading" class="flex justify-content-center">
          <ProgressSpinner />
        </div>
        <div v-else>
          <div v-if="optimizationResult" class="mb-4">
            <h3 class="text-xl font-bold mb-2">Optimization Results</h3>
            <div class="grid">
              <div class="col-12 md:col-6 lg:col-3">
                <Card>
                  <template #title>Score</template>
                  <template #content>
                    <div class="text-2xl font-bold text-center">{{ optimizationResult.score.toFixed(2) }}</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-6 lg:col-3">
                <Card>
                  <template #title>Iterations</template>
                  <template #content>
                    <div class="text-2xl font-bold text-center">{{ optimizationResult.iteration_count }}</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-6 lg:col-3">
                <Card>
                  <template #title>Execution Time</template>
                  <template #content>
                    <div class="text-2xl font-bold text-center">{{ optimizationResult.execution_time_seconds.toFixed(2) }}s</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-6 lg:col-3">
                <Card>
                  <template #title>Surgeries</template>
                  <template #content>
                    <div class="text-2xl font-bold text-center">{{ optimizationResult.assignments.length }}</div>
                  </template>
                </Card>
              </div>
            </div>
          </div>
          
          <DataTable :value="scheduleData" responsiveLayout="scroll" class="p-datatable-sm">
            <Column field="time" header="Time"></Column>
            <Column field="surgery_id" header="Surgery ID"></Column>
            <Column field="surgery_type" header="Surgery Type"></Column>
            <Column field="duration" header="Duration"></Column>
            <Column field="surgeon" header="Surgeon"></Column>
            <Column field="room" header="Room"></Column>
          </DataTable>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'Schedule',
  setup() {
    const store = useStore()
    const toast = useToast()
    
    const loading = ref(false)
    const optimizedSchedule = ref([])
    const optimizationResult = ref(null)
    
    const optimizationParams = ref({
      date: new Date(),
      max_iterations: 100,
      tabu_tenure: 10,
      max_no_improvement: 20,
      time_limit_seconds: 300,
      weights: {
        or_utilization: 1.0,
        setup_times: 0.8,
        surgeon_preferences: 0.7,
        workload_balance: 0.6,
        patient_wait_time: 0.5,
        emergency_priority: 1.0,
        operational_costs: 0.4,
        staff_overtime: 0.3
      }
    })
    
    // Mock data for demonstration
    const currentSchedule = ref([
      { time: '08:00 - 09:30', surgery_id: 101, surgery_type: 'Appendectomy', duration: '1h 30m', surgeon: 'Dr. Smith', room: 'OR-1' },
      { time: '09:45 - 11:15', surgery_id: 102, surgery_type: 'Hernia Repair', duration: '1h 30m', surgeon: 'Dr. Johnson', room: 'OR-2' },
      { time: '10:00 - 12:30', surgery_id: 103, surgery_type: 'Gallbladder Removal', duration: '2h 30m', surgeon: 'Dr. Williams', room: 'OR-3' },
      { time: '13:00 - 15:00', surgery_id: 104, surgery_type: 'Hip Replacement', duration: '2h', surgeon: 'Dr. Brown', room: 'OR-1' },
      { time: '14:30 - 16:00', surgery_id: 105, surgery_type: 'Cataract Surgery', duration: '1h 30m', surgeon: 'Dr. Davis', room: 'OR-4' }
    ])
    
    const scheduleData = computed(() => {
      return optimizedSchedule.value.length ? optimizedSchedule.value : currentSchedule.value
    })
    
    const optimizeSchedule = async () => {
      loading.value = true
      
      try {
        // In a real application, this would be an API call
        // const response = await axios.post('/api/schedules/optimize', optimizationParams.value)
        
        // Mock response for demonstration
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        const mockResponse = {
          assignments: [
            { time: '08:00 - 09:30', surgery_id: 101, surgery_type: 'Appendectomy', duration: '1h 30m', surgeon: 'Dr. Smith', room: 'OR-2' },
            { time: '08:00 - 10:00', surgery_id: 104, surgery_type: 'Hip Replacement', duration: '2h', surgeon: 'Dr. Brown', room: 'OR-1' },
            { time: '09:45 - 11:15', surgery_id: 102, surgery_type: 'Hernia Repair', duration: '1h 30m', surgeon: 'Dr. Johnson', room: 'OR-3' },
            { time: '10:15 - 11:45', surgery_id: 105, surgery_type: 'Cataract Surgery', duration: '1h 30m', surgeon: 'Dr. Davis', room: 'OR-2' },
            { time: '10:30 - 13:00', surgery_id: 103, surgery_type: 'Gallbladder Removal', duration: '2h 30m', surgeon: 'Dr. Williams', room: 'OR-1' }
          ],
          score: 87.5,
          metrics: {
            or_utilization: 0.92,
            setup_times: 0.85,
            surgeon_preferences: 0.78,
            workload_balance: 0.88
          },
          iteration_count: 78,
          execution_time_seconds: 2.34
        }
        
        optimizedSchedule.value = mockResponse.assignments
        optimizationResult.value = mockResponse
        
        toast.add({
          severity: 'success',
          summary: 'Optimization Complete',
          detail: `Schedule optimized with score: ${mockResponse.score.toFixed(2)}`,
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Optimization Failed',
          detail: error.message || 'An error occurred during optimization',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    const applySchedule = async () => {
      if (!optimizedSchedule.value.length) {
        return
      }
      
      loading.value = true
      
      try {
        // In a real application, this would be an API call
        // await axios.post('/api/schedules/apply', { assignments: optimizedSchedule.value })
        
        // Mock response for demonstration
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        toast.add({
          severity: 'success',
          summary: 'Schedule Applied',
          detail: 'The optimized schedule has been applied successfully',
          life: 3000
        })
        
        // Update current schedule with optimized schedule
        currentSchedule.value = [...optimizedSchedule.value]
        optimizedSchedule.value = []
        optimizationResult.value = null
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Apply Failed',
          detail: error.message || 'An error occurred while applying the schedule',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      // In a real application, you would fetch the current schedule from the API
    })
    
    return {
      loading,
      optimizationParams,
      scheduleData,
      optimizedSchedule,
      optimizationResult,
      optimizeSchedule,
      applySchedule
    }
  }
}
</script>
