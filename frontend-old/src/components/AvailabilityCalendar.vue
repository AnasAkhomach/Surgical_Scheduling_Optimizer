<template>
  <div class="availability-calendar">
    <Card>
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-calendar text-primary mr-2"></i>
          <span>{{ title }}</span>
        </div>
      </template>
      <template #content>
        <div class="filter-controls mb-3">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="viewMode">View Mode</label>
                <Dropdown id="viewMode" v-model="selectedViewMode" :options="viewModes" optionLabel="label" optionValue="value" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="resource">{{ resourceLabel }}</label>
                <Dropdown id="resource" v-model="selectedResource" :options="resources" optionLabel="label" optionValue="value" class="w-full" />
              </div>
            </div>
          </div>
        </div>
        
        <div class="calendar-container">
          <div v-if="selectedViewMode === 'week'" class="week-view">
            <div class="grid">
              <div class="col-12">
                <div class="week-header flex">
                  <div class="time-column"></div>
                  <div v-for="day in weekDays" :key="day.date" class="day-column">
                    <div class="day-header">
                      <div class="day-name">{{ day.name }}</div>
                      <div class="day-date">{{ day.date }}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12">
                <div class="week-body flex">
                  <div class="time-column">
                    <div v-for="hour in hours" :key="hour" class="time-slot">
                      {{ formatHour(hour) }}
                    </div>
                  </div>
                  <div v-for="day in weekDays" :key="day.date" class="day-column">
                    <div v-for="hour in hours" :key="`${day.date}-${hour}`" 
                         class="time-slot" 
                         :class="{ 'available': isAvailable(day.date, hour), 'unavailable': !isAvailable(day.date, hour) }"
                         @click="toggleAvailability(day.date, hour)">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else-if="selectedViewMode === 'month'" class="month-view">
            <div class="grid">
              <div class="col-12">
                <div class="month-header flex">
                  <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="day-header">
                    {{ day }}
                  </div>
                </div>
              </div>
              <div class="col-12">
                <div class="month-body">
                  <div v-for="week in monthWeeks" :key="week.weekNumber" class="week-row flex">
                    <div v-for="day in week.days" :key="day.date" 
                         class="day-cell" 
                         :class="{ 'other-month': day.otherMonth, 'today': day.isToday }">
                      <div class="day-number">{{ day.dayNumber }}</div>
                      <div class="availability-indicator" 
                           :class="{ 'available': day.availability > 0.7, 'partially-available': day.availability > 0.3 && day.availability <= 0.7, 'unavailable': day.availability <= 0.3 }">
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'AvailabilityCalendar',
  props: {
    title: {
      type: String,
      default: 'Availability Calendar'
    },
    type: {
      type: String,
      default: 'surgeon', // 'surgeon' or 'room'
      validator: (value) => ['surgeon', 'room'].includes(value)
    },
    data: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const selectedViewMode = ref('week');
    const selectedResource = ref(null);
    
    const viewModes = [
      { label: 'Week', value: 'week' },
      { label: 'Month', value: 'month' }
    ];
    
    const resourceLabel = computed(() => {
      return props.type === 'surgeon' ? 'Surgeon' : 'Operating Room';
    });
    
    // Mock resources
    const resources = computed(() => {
      if (props.type === 'surgeon') {
        return [
          { label: 'Dr. Smith', value: 1 },
          { label: 'Dr. Johnson', value: 2 },
          { label: 'Dr. Williams', value: 3 },
          { label: 'Dr. Brown', value: 4 }
        ];
      } else {
        return [
          { label: 'OR-1', value: 1 },
          { label: 'OR-2', value: 2 },
          { label: 'OR-3', value: 3 },
          { label: 'OR-4', value: 4 }
        ];
      }
    });
    
    // Set default selected resource
    onMounted(() => {
      if (resources.value.length > 0) {
        selectedResource.value = resources.value[0].value;
      }
    });
    
    // Week view data
    const hours = Array.from({ length: 12 }, (_, i) => i + 8); // 8:00 to 19:00
    
    const weekDays = computed(() => {
      const days = [];
      const today = new Date();
      const startOfWeek = new Date(today);
      startOfWeek.setDate(today.getDate() - today.getDay() + 1); // Start from Monday
      
      for (let i = 0; i < 5; i++) { // Monday to Friday
        const date = new Date(startOfWeek);
        date.setDate(startOfWeek.getDate() + i);
        days.push({
          name: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()],
          date: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`,
          isToday: date.toDateString() === today.toDateString()
        });
      }
      
      return days;
    });
    
    // Month view data
    const monthWeeks = computed(() => {
      const weeks = [];
      const today = new Date();
      const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
      const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      
      // Start from the first day of the week that contains the first day of the month
      const startDate = new Date(firstDayOfMonth);
      startDate.setDate(startDate.getDate() - (startDate.getDay() === 0 ? 6 : startDate.getDay() - 1));
      
      // End at the last day of the week that contains the last day of the month
      const endDate = new Date(lastDayOfMonth);
      endDate.setDate(endDate.getDate() + (7 - endDate.getDay()) % 7);
      
      let currentDate = new Date(startDate);
      let weekNumber = 1;
      
      while (currentDate <= endDate) {
        const week = {
          weekNumber,
          days: []
        };
        
        for (let i = 0; i < 7; i++) {
          const date = new Date(currentDate);
          week.days.push({
            date: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`,
            dayNumber: date.getDate(),
            otherMonth: date.getMonth() !== today.getMonth(),
            isToday: date.toDateString() === today.toDateString(),
            availability: Math.random() // Mock availability (0-1)
          });
          
          currentDate.setDate(currentDate.getDate() + 1);
        }
        
        weeks.push(week);
        weekNumber++;
      }
      
      return weeks;
    });
    
    // Mock availability data
    const availabilityData = ref({});
    
    // Initialize mock availability data
    onMounted(() => {
      weekDays.value.forEach(day => {
        availabilityData.value[day.date] = {};
        hours.forEach(hour => {
          // Random availability (70% chance of being available)
          availabilityData.value[day.date][hour] = Math.random() > 0.3;
        });
      });
    });
    
    const formatHour = (hour) => {
      return `${hour}:00`;
    };
    
    const isAvailable = (date, hour) => {
      return availabilityData.value[date]?.[hour] || false;
    };
    
    const toggleAvailability = (date, hour) => {
      if (!availabilityData.value[date]) {
        availabilityData.value[date] = {};
      }
      availabilityData.value[date][hour] = !isAvailable(date, hour);
    };
    
    return {
      selectedViewMode,
      selectedResource,
      viewModes,
      resourceLabel,
      resources,
      hours,
      weekDays,
      monthWeeks,
      formatHour,
      isAvailable,
      toggleAvailability
    };
  }
}
</script>

<style scoped>
.availability-calendar {
  height: 100%;
}

.calendar-container {
  height: 500px;
  overflow-y: auto;
}

/* Week View Styles */
.week-header, .week-body {
  display: flex;
  width: 100%;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
}

.day-column {
  flex: 1;
  min-width: 100px;
  border-left: 1px solid #e0e0e0;
}

.day-header {
  padding: 8px;
  text-align: center;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.day-name {
  font-weight: bold;
}

.time-slot {
  height: 40px;
  padding: 8px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
}

.available {
  background-color: #e3f2fd;
  cursor: pointer;
}

.unavailable {
  background-color: #ffebee;
  cursor: pointer;
}

/* Month View Styles */
.month-header {
  display: flex;
  width: 100%;
}

.month-header .day-header {
  flex: 1;
  padding: 8px;
  text-align: center;
  font-weight: bold;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.month-body {
  display: flex;
  flex-direction: column;
}

.week-row {
  display: flex;
  width: 100%;
}

.day-cell {
  flex: 1;
  height: 80px;
  border: 1px solid #e0e0e0;
  padding: 4px;
  position: relative;
}

.day-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.other-month {
  background-color: #f9f9f9;
  color: #aaa;
}

.today {
  background-color: #e3f2fd;
}

.availability-indicator {
  position: absolute;
  bottom: 4px;
  left: 4px;
  right: 4px;
  height: 8px;
  border-radius: 4px;
}

.available {
  background-color: #66BB6A;
}

.partially-available {
  background-color: #FFA726;
}

.unavailable {
  background-color: #EF5350;
}
</style>
