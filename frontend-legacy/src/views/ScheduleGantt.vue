<template>
  <div class="schedule-gantt">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold">Surgery Schedule Gantt</h1>
      <div>
        <Button label="Optimize Schedule" icon="pi pi-cog" @click="optimizeSchedule" class="mr-2" />
        <Button label="Apply Schedule" icon="pi pi-check" @click="applySchedule" :disabled="!optimizedSchedule.length" />
      </div>
    </div>
    
    <Card class="mb-4">
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-sliders-h text-primary mr-2"></i>
          <span>Schedule Parameters</span>
        </div>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="date">Date</label>
              <Calendar id="date" v-model="scheduleParams.date" dateFormat="yy-mm-dd" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="viewMode">View Mode</label>
              <Dropdown id="viewMode" v-model="scheduleParams.viewMode" :options="viewModes" optionLabel="label" optionValue="value" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label for="groupBy">Group By</label>
              <Dropdown id="groupBy" v-model="scheduleParams.groupBy" :options="groupByOptions" optionLabel="label" optionValue="value" />
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="field">
              <label>&nbsp;</label>
              <div>
                <Button label="Refresh" icon="pi pi-refresh" @click="fetchSchedule" class="w-full" />
              </div>
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
        <div v-else class="gantt-wrapper">
          <GanttChart 
            :tasks="ganttTasks" 
            :links="ganttLinks" 
            :readonly="!isEditable"
            :scales="getScales()"
            @task-updated="onTaskUpdated"
            @task-clicked="onTaskClicked"
            @task-double-clicked="onTaskDoubleClicked"
          />
        </div>
      </template>
    </Card>
    
    <Dialog v-model:visible="surgeryDetailsVisible" header="Surgery Details" :style="{ width: '50vw' }">
      <div v-if="selectedSurgery" class="p-fluid">
        <div class="field">
          <label>Surgery ID</label>
          <InputText v-model="selectedSurgery.id" disabled />
        </div>
        <div class="field">
          <label>Surgery Type</label>
          <InputText v-model="selectedSurgery.type" disabled />
        </div>
        <div class="field">
          <label>Surgeon</label>
          <InputText v-model="selectedSurgery.surgeon" disabled />
        </div>
        <div class="field">
          <label>Room</label>
          <InputText v-model="selectedSurgery.room" disabled />
        </div>
        <div class="field">
          <label>Start Time</label>
          <InputText v-model="selectedSurgery.start_time" disabled />
        </div>
        <div class="field">
          <label>End Time</label>
          <InputText v-model="selectedSurgery.end_time" disabled />
        </div>
        <div class="field">
          <label>Duration</label>
          <InputText v-model="selectedSurgery.duration" disabled />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'primevue/usetoast';
import GanttChart from '@/components/GanttChart.vue';
import axios from 'axios';

export default {
  name: 'ScheduleGantt',
  components: {
    GanttChart
  },
  setup() {
    const store = useStore();
    const toast = useToast();
    
    const loading = ref(false);
    const optimizedSchedule = ref([]);
    const currentSchedule = ref([]);
    const surgeryDetailsVisible = ref(false);
    const selectedSurgery = ref(null);
    const isEditable = ref(true);
    
    const scheduleParams = ref({
      date: new Date(),
      viewMode: 'day',
      groupBy: 'room'
    });
    
    const viewModes = [
      { label: 'Day', value: 'day' },
      { label: 'Week', value: 'week' },
      { label: 'Month', value: 'month' }
    ];
    
    const groupByOptions = [
      { label: 'Room', value: 'room' },
      { label: 'Surgeon', value: 'surgeon' },
      { label: 'Surgery Type', value: 'surgery_type' }
    ];
    
    // Computed property to transform schedule data into Gantt tasks format
    const ganttTasks = computed(() => {
      const schedule = optimizedSchedule.value.length ? optimizedSchedule.value : currentSchedule.value;
      
      if (!schedule.length) return [];
      
      // Group tasks based on the selected groupBy option
      const groupedTasks = {};
      const tasks = [];
      
      // Add root task
      tasks.push({
        id: 0,
        text: 'Schedule',
        start_date: new Date(scheduleParams.value.date),
        duration: 0,
        type: 'project',
        open: true,
        readonly: true
      });
      
      // Group tasks and create parent tasks for each group
      schedule.forEach(surgery => {
        const groupKey = surgery[scheduleParams.value.groupBy];
        if (!groupedTasks[groupKey]) {
          const groupId = `group_${Object.keys(groupedTasks).length + 1}`;
          groupedTasks[groupKey] = {
            id: groupId,
            tasks: []
          };
          
          // Add parent task for the group
          tasks.push({
            id: groupId,
            text: groupKey,
            start_date: new Date(scheduleParams.value.date),
            duration: 0,
            parent: 0,
            type: 'project',
            open: true,
            readonly: true
          });
        }
        
        // Add surgery task to the group
        const startDate = new Date(surgery.start_time);
        const endDate = new Date(surgery.end_time);
        const durationMs = endDate - startDate;
        const durationHours = durationMs / (1000 * 60 * 60);
        
        groupedTasks[groupKey].tasks.push({
          id: `surgery_${surgery.surgery_id}`,
          text: `${surgery.surgery_type} (ID: ${surgery.surgery_id})`,
          start_date: startDate,
          duration: durationHours,
          parent: groupedTasks[groupKey].id,
          surgery_id: surgery.surgery_id,
          room: surgery.room,
          surgeon: surgery.surgeon,
          type: 'task',
          readonly: !isEditable.value
        });
      });
      
      // Add all tasks to the result array
      Object.values(groupedTasks).forEach(group => {
        tasks.push(...group.tasks);
      });
      
      return tasks;
    });
    
    // Empty links for now, can be used for dependencies later
    const ganttLinks = computed(() => []);
    
    // Function to get scales based on view mode
    const getScales = () => {
      switch (scheduleParams.value.viewMode) {
        case 'day':
          return [
            { unit: 'hour', step: 1, format: '%H:%i' }
          ];
        case 'week':
          return [
            { unit: 'day', step: 1, format: '%d %M' },
            { unit: 'hour', step: 6, format: '%H:%i' }
          ];
        case 'month':
          return [
            { unit: 'week', step: 1, format: 'Week #%W' },
            { unit: 'day', step: 1, format: '%d %M' }
          ];
        default:
          return [
            { unit: 'hour', step: 1, format: '%H:%i' }
          ];
      }
    };
    
    // Fetch schedule data from API
    const fetchSchedule = async () => {
      loading.value = true;
      
      try {
        const response = await axios.get('/api/schedules/current', {
          params: {
            date: scheduleParams.value.date.toISOString().split('T')[0]
          }
        });
        
        currentSchedule.value = response.data.map(assignment => ({
          surgery_id: assignment.surgery_id,
          room: `OR-${assignment.room_id}`,
          surgeon: `Dr. ${assignment.surgeon_id}`, // This would be replaced with actual surgeon name
          surgery_type: `Surgery Type ${assignment.surgery_type_id}`, // This would be replaced with actual surgery type
          start_time: assignment.start_time,
          end_time: assignment.end_time,
          duration: `${Math.round((new Date(assignment.end_time) - new Date(assignment.start_time)) / (1000 * 60))} min`
        }));
        
        optimizedSchedule.value = [];
        
        toast.add({
          severity: 'success',
          summary: 'Schedule Loaded',
          detail: `Loaded ${currentSchedule.value.length} surgeries`,
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Load Failed',
          detail: error.message || 'An error occurred while loading the schedule',
          life: 3000
        });
        
        // Use mock data for demonstration
        currentSchedule.value = [
          { surgery_id: 101, room: 'OR-1', surgeon: 'Dr. Smith', surgery_type: 'Appendectomy', start_time: '2023-05-18T08:00:00', end_time: '2023-05-18T09:30:00', duration: '1h 30m' },
          { surgery_id: 102, room: 'OR-2', surgeon: 'Dr. Johnson', surgery_type: 'Hernia Repair', start_time: '2023-05-18T09:45:00', end_time: '2023-05-18T11:15:00', duration: '1h 30m' },
          { surgery_id: 103, room: 'OR-3', surgeon: 'Dr. Williams', surgery_type: 'Gallbladder Removal', start_time: '2023-05-18T10:00:00', end_time: '2023-05-18T12:30:00', duration: '2h 30m' },
          { surgery_id: 104, room: 'OR-1', surgeon: 'Dr. Brown', surgery_type: 'Hip Replacement', start_time: '2023-05-18T13:00:00', end_time: '2023-05-18T15:00:00', duration: '2h' },
          { surgery_id: 105, room: 'OR-4', surgeon: 'Dr. Davis', surgery_type: 'Cataract Surgery', start_time: '2023-05-18T14:30:00', end_time: '2023-05-18T16:00:00', duration: '1h 30m' }
        ];
      } finally {
        loading.value = false;
      }
    };
    
    // Optimize schedule
    const optimizeSchedule = async () => {
      loading.value = true;
      
      try {
        const response = await axios.post('/api/schedules/optimize', {
          date: scheduleParams.value.date.toISOString().split('T')[0],
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
        });
        
        optimizedSchedule.value = response.data.assignments.map(assignment => ({
          surgery_id: assignment.surgery_id,
          room: `OR-${assignment.room_id}`,
          surgeon: `Dr. ${assignment.surgeon_id}`, // This would be replaced with actual surgeon name
          surgery_type: `Surgery Type ${assignment.surgery_type_id}`, // This would be replaced with actual surgery type
          start_time: assignment.start_time,
          end_time: assignment.end_time,
          duration: `${Math.round((new Date(assignment.end_time) - new Date(assignment.start_time)) / (1000 * 60))} min`
        }));
        
        toast.add({
          severity: 'success',
          summary: 'Optimization Complete',
          detail: `Schedule optimized with score: ${response.data.score.toFixed(2)}`,
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Optimization Failed',
          detail: error.message || 'An error occurred during optimization',
          life: 3000
        });
        
        // Use mock data for demonstration
        optimizedSchedule.value = [
          { surgery_id: 101, room: 'OR-2', surgeon: 'Dr. Smith', surgery_type: 'Appendectomy', start_time: '2023-05-18T08:00:00', end_time: '2023-05-18T09:30:00', duration: '1h 30m' },
          { surgery_id: 104, room: 'OR-1', surgeon: 'Dr. Brown', surgery_type: 'Hip Replacement', start_time: '2023-05-18T08:00:00', end_time: '2023-05-18T10:00:00', duration: '2h' },
          { surgery_id: 102, room: 'OR-3', surgeon: 'Dr. Johnson', surgery_type: 'Hernia Repair', start_time: '2023-05-18T09:45:00', end_time: '2023-05-18T11:15:00', duration: '1h 30m' },
          { surgery_id: 105, room: 'OR-2', surgeon: 'Dr. Davis', surgery_type: 'Cataract Surgery', start_time: '2023-05-18T10:15:00', end_time: '2023-05-18T11:45:00', duration: '1h 30m' },
          { surgery_id: 103, room: 'OR-1', surgeon: 'Dr. Williams', surgery_type: 'Gallbladder Removal', start_time: '2023-05-18T10:30:00', end_time: '2023-05-18T13:00:00', duration: '2h 30m' }
        ];
      } finally {
        loading.value = false;
      }
    };
    
    // Apply optimized schedule
    const applySchedule = async () => {
      if (!optimizedSchedule.value.length) {
        return;
      }
      
      loading.value = true;
      
      try {
        await axios.post('/api/schedules/apply', {
          assignments: optimizedSchedule.value.map(surgery => ({
            surgery_id: surgery.surgery_id,
            room_id: parseInt(surgery.room.replace('OR-', '')),
            start_time: surgery.start_time,
            end_time: surgery.end_time
          }))
        });
        
        toast.add({
          severity: 'success',
          summary: 'Schedule Applied',
          detail: 'The optimized schedule has been applied successfully',
          life: 3000
        });
        
        // Update current schedule with optimized schedule
        currentSchedule.value = [...optimizedSchedule.value];
        optimizedSchedule.value = [];
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Apply Failed',
          detail: error.message || 'An error occurred while applying the schedule',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    // Event handlers for Gantt chart
    const onTaskUpdated = ({ id, task }) => {
      toast.add({
        severity: 'info',
        summary: 'Task Updated',
        detail: `Task ${id} updated`,
        life: 3000
      });
    };
    
    const onTaskClicked = ({ id, task }) => {
      // Extract surgery ID from task ID
      const surgeryId = task.surgery_id;
      if (!surgeryId) return;
      
      // Find surgery in schedule
      const schedule = optimizedSchedule.value.length ? optimizedSchedule.value : currentSchedule.value;
      const surgery = schedule.find(s => s.surgery_id === surgeryId);
      
      if (surgery) {
        selectedSurgery.value = {
          id: surgery.surgery_id,
          type: surgery.surgery_type,
          surgeon: surgery.surgeon,
          room: surgery.room,
          start_time: new Date(surgery.start_time).toLocaleString(),
          end_time: new Date(surgery.end_time).toLocaleString(),
          duration: surgery.duration
        };
        surgeryDetailsVisible.value = true;
      }
    };
    
    const onTaskDoubleClicked = ({ id, task }) => {
      // Could be used to open edit dialog
    };
    
    onMounted(() => {
      fetchSchedule();
    });
    
    return {
      loading,
      scheduleParams,
      viewModes,
      groupByOptions,
      currentSchedule,
      optimizedSchedule,
      ganttTasks,
      ganttLinks,
      surgeryDetailsVisible,
      selectedSurgery,
      isEditable,
      fetchSchedule,
      optimizeSchedule,
      applySchedule,
      getScales,
      onTaskUpdated,
      onTaskClicked,
      onTaskDoubleClicked
    };
  }
}
</script>

<style scoped>
.gantt-wrapper {
  width: 100%;
  height: 600px;
}
</style>
