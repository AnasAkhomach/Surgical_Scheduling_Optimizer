<template>
  <div class="resource-availability-calendar">
    <div class="calendar-header">
      <h3>{{ resource.name }} Availability</h3>
      <div class="resource-info">
        <div class="resource-type">{{ resourceType }}</div>
        <div class="resource-status" :class="getStatusClass(resource.status)">
          {{ resource.status }}
        </div>
      </div>
    </div>

    <div class="calendar-navigation">
      <button class="btn btn-icon" @click="previousMonth" aria-label="Previous month">
        ◀
      </button>
      <div class="current-month">{{ currentMonthName }} {{ currentYear }}</div>
      <button class="btn btn-icon" @click="nextMonth" aria-label="Next month">
        ▶
      </button>
    </div>

    <div class="calendar-grid">
      <!-- Day headers -->
      <div v-for="day in weekDays" :key="day" class="day-header">{{ day }}</div>

      <!-- Calendar days -->
      <div 
        v-for="(day, index) in calendarDays" 
        :key="index"
        class="calendar-day"
        :class="{ 
          'other-month': !day.isCurrentMonth,
          'today': day.isToday,
          'unavailable': day.isUnavailable,
          'has-unavailable-periods': day.hasUnavailablePeriods
        }"
        @click="day.isCurrentMonth && selectDay(day)"
      >
        <div class="day-number">{{ day.day }}</div>
        <div v-if="day.hasUnavailablePeriods" class="unavailable-indicator">
          <div 
            v-for="(period, i) in day.unavailablePeriods" 
            :key="i" 
            class="period-marker"
            :title="period.reason"
          ></div>
        </div>
      </div>
    </div>

    <!-- Day detail view when a day is selected -->
    <div v-if="selectedDay" class="day-detail">
      <div class="day-detail-header">
        <h4>{{ formatDate(selectedDay.date) }}</h4>
        <button class="btn btn-icon" @click="selectedDay = null" aria-label="Close detail view">✕</button>
      </div>

      <div class="availability-status">
        <div class="status-label">Day Status:</div>
        <div class="status-toggle">
          <label class="toggle-switch">
            <input 
              type="checkbox" 
              :checked="!selectedDay.isUnavailable" 
              @change="toggleDayAvailability"
            >
            <span class="toggle-slider"></span>
          </label>
          <span>{{ selectedDay.isUnavailable ? 'Unavailable' : 'Available' }}</span>
        </div>
      </div>

      <div v-if="!selectedDay.isUnavailable">
        <h5>Unavailable Time Periods</h5>
        <div v-if="selectedDay.unavailablePeriods.length === 0" class="no-periods">
          No unavailable periods set for this day.
        </div>
        <div v-else class="periods-list">
          <div 
            v-for="(period, index) in selectedDay.unavailablePeriods" 
            :key="index"
            class="period-item"
          >
            <div class="period-time">{{ period.start }} - {{ period.end }}</div>
            <div class="period-reason">{{ period.reason }}</div>
            <button 
              class="btn btn-icon btn-danger" 
              @click="removePeriod(index)"
              aria-label="Remove period"
            >
              ✕
            </button>
          </div>
        </div>

        <div class="add-period-form">
          <h5>Add Unavailable Period</h5>
          <div class="form-row">
            <div class="form-group">
              <label for="start-time">Start Time</label>
              <input 
                type="time" 
                id="start-time" 
                v-model="newPeriod.start"
                class="form-control"
              >
            </div>
            <div class="form-group">
              <label for="end-time">End Time</label>
              <input 
                type="time" 
                id="end-time" 
                v-model="newPeriod.end"
                class="form-control"
              >
            </div>
          </div>
          <div class="form-group">
            <label for="reason">Reason</label>
            <input 
              type="text" 
              id="reason" 
              v-model="newPeriod.reason"
              class="form-control"
              placeholder="e.g., Meeting, Maintenance, Lunch"
            >
          </div>
          <button 
            class="btn btn-primary" 
            @click="addPeriod"
            :disabled="!isNewPeriodValid"
          >
            Add Period
          </button>
        </div>
      </div>

      <div class="day-detail-actions">
        <button class="btn btn-secondary" @click="selectedDay = null">Close</button>
        <button class="btn btn-primary" @click="saveAvailability">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useResourceStore } from '@/stores/resourceStore';
import { useToast } from 'vue-toastification';

const props = defineProps({
  resource: {
    type: Object,
    required: true
  },
  resourceType: {
    type: String,
    required: true,
    validator: (value) => ['operatingRoom', 'staff', 'equipment'].includes(value)
  }
});

const emit = defineEmits(['close', 'update']);

const toast = useToast();
const resourceStore = useResourceStore();

// Calendar state
const currentDate = ref(new Date());
const selectedDay = ref(null);
const newPeriod = ref({
  start: '08:00',
  end: '09:00',
  reason: ''
});

// Computed properties for calendar
const currentYear = computed(() => currentDate.value.getFullYear());
const currentMonth = computed(() => currentDate.value.getMonth());
const currentMonthName = computed(() => {
  return new Date(currentYear.value, currentMonth.value, 1).toLocaleString('default', { month: 'long' });
});

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Generate calendar days for the current month
const calendarDays = computed(() => {
  const year = currentYear.value;
  const month = currentMonth.value;
  
  // Get first day of the month
  const firstDay = new Date(year, month, 1);
  // Get last day of the month
  const lastDay = new Date(year, month + 1, 0);
  
  // Get the day of the week for the first day (0-6, where 0 is Sunday)
  const firstDayOfWeek = firstDay.getDay();
  
  // Calculate days from previous month to show
  const daysFromPrevMonth = firstDayOfWeek;
  
  // Calculate total days to show (previous month + current month + next month)
  const totalDays = 42; // 6 rows of 7 days
  
  const days = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // Add days from previous month
  const prevMonth = new Date(year, month, 0);
  const prevMonthDays = prevMonth.getDate();
  
  for (let i = prevMonthDays - daysFromPrevMonth + 1; i <= prevMonthDays; i++) {
    const date = new Date(year, month - 1, i);
    days.push(createDayObject(date, false));
  }
  
  // Add days from current month
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i);
    days.push(createDayObject(date, true));
  }
  
  // Add days from next month
  const remainingDays = totalDays - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(year, month + 1, i);
    days.push(createDayObject(date, false));
  }
  
  return days;
});

// Create a day object with availability information
function createDayObject(date, isCurrentMonth) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const isToday = date.getTime() === today.getTime();
  const day = date.getDate();
  
  // Check resource availability for this day
  const dateKey = formatDateKey(date);
  const resourceId = props.resource.id;
  const availability = resourceStore.resourceAvailability[dateKey]?.[resourceId];
  
  const isUnavailable = availability ? !availability.available : false;
  const unavailablePeriods = availability?.unavailablePeriods || [];
  
  return {
    date,
    day,
    isCurrentMonth,
    isToday,
    isUnavailable,
    unavailablePeriods,
    hasUnavailablePeriods: unavailablePeriods.length > 0
  };
}

// Format date for display
function formatDate(date) {
  return date.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

// Format date as YYYY-MM-DD for use as a key
function formatDateKey(date) {
  return date.toISOString().split('T')[0];
}

// Navigation methods
function previousMonth() {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 1, 1);
  selectedDay.value = null;
}

function nextMonth() {
  currentDate.value = new Date(currentYear.value, currentMonth.value + 1, 1);
  selectedDay.value = null;
}

// Day selection
function selectDay(day) {
  selectedDay.value = { ...day };
  newPeriod.value = {
    start: '08:00',
    end: '09:00',
    reason: ''
  };
}

// Toggle day availability
function toggleDayAvailability() {
  if (!selectedDay.value) return;
  
  selectedDay.value.isUnavailable = !selectedDay.value.isUnavailable;
  
  // If day is marked as unavailable, clear all periods
  if (selectedDay.value.isUnavailable) {
    selectedDay.value.unavailablePeriods = [];
  }
}

// Add a new unavailable period
function addPeriod() {
  if (!isNewPeriodValid.value) return;
  
  selectedDay.value.unavailablePeriods.push({
    start: newPeriod.value.start,
    end: newPeriod.value.end,
    reason: newPeriod.value.reason
  });
  
  // Sort periods by start time
  selectedDay.value.unavailablePeriods.sort((a, b) => {
    return a.start.localeCompare(b.start);
  });
  
  // Reset form
  newPeriod.value = {
    start: '08:00',
    end: '09:00',
    reason: ''
  };
}

// Remove an unavailable period
function removePeriod(index) {
  selectedDay.value.unavailablePeriods.splice(index, 1);
}

// Save availability changes
async function saveAvailability() {
  if (!selectedDay.value) return;
  
  const dateKey = formatDateKey(selectedDay.value.date);
  const resourceId = props.resource.id;
  
  const availability = {
    available: !selectedDay.value.isUnavailable,
    unavailablePeriods: selectedDay.value.unavailablePeriods
  };
  
  try {
    const result = await resourceStore.updateResourceAvailability(resourceId, dateKey, availability);
    
    if (result.success) {
      toast.success('Availability updated successfully');
      emit('update');
    } else {
      toast.error('Failed to update availability');
    }
  } catch (error) {
    toast.error(`Error: ${error.message}`);
  }
}

// Validation for new period
const isNewPeriodValid = computed(() => {
  if (!newPeriod.value.start || !newPeriod.value.end) return false;
  if (newPeriod.value.start >= newPeriod.value.end) return false;
  return true;
});

// Helper function to get status class
function getStatusClass(status) {
  if (!status) return '';
  
  const statusLower = status.toLowerCase();
  if (statusLower.includes('active') || statusLower.includes('available')) {
    return 'status-active';
  } else if (statusLower.includes('maintenance')) {
    return 'status-maintenance';
  } else {
    return 'status-inactive';
  }
}

// Load initial data
onMounted(() => {
  // Nothing to load initially, as we're using the data from the store
});
</script>

<style scoped>
.resource-availability-calendar {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: var(--spacing-md);
  max-width: 800px;
  margin: 0 auto;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.calendar-header h3 {
  margin: 0;
  color: var(--color-text);
}

.resource-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.resource-type {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.resource-status {
  padding: 2px 8px;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.status-active {
  background-color: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status-inactive {
  background-color: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.status-maintenance {
  background-color: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.calendar-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-sm);
}

.current-month {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-md);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: var(--color-border-soft);
  border: 1px solid var(--color-border-soft);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.day-header {
  background-color: var(--color-background-soft);
  padding: var(--spacing-sm);
  text-align: center;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.calendar-day {
  background-color: var(--color-background);
  min-height: 80px;
  padding: var(--spacing-xs);
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.calendar-day:hover {
  background-color: var(--color-background-hover);
}

.other-month {
  opacity: 0.5;
  cursor: default;
}

.today {
  background-color: rgba(var(--color-primary-rgb, 0, 120, 212), 0.1);
}

.unavailable {
  background-color: rgba(var(--color-error-rgb, 220, 53, 69), 0.1);
}

.has-unavailable-periods .day-number::after {
  content: "•";
  color: var(--color-error);
  margin-left: 4px;
}

.day-number {
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
}

.unavailable-indicator {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.period-marker {
  height: 4px;
  background-color: var(--color-error);
  border-radius: 2px;
}

.day-detail {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-border);
}

.day-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.day-detail-header h4 {
  margin: 0;
  color: var(--color-text);
}

.availability-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
}

.status-label {
  font-weight: var(--font-weight-medium);
}

.status-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 20px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--color-primary);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

h5 {
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
  font-size: var(--font-size-md);
}

.no-periods {
  padding: var(--spacing-sm);
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  color: var(--color-text-secondary);
  font-style: italic;
}

.periods-list {
  margin-bottom: var(--spacing-md);
}

.period-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-xs);
}

.period-time {
  font-weight: var(--font-weight-medium);
  min-width: 120px;
}

.period-reason {
  flex-grow: 1;
  color: var(--color-text-secondary);
}

.add-period-form {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-border-soft);
}

.form-row {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.form-group {
  margin-bottom: var(--spacing-sm);
  flex-grow: 1;
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.form-control {
  width: 100%;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.day-detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .calendar-grid {
    font-size: var(--font-size-xs);
  }
  
  .calendar-day {
    min-height: 60px;
  }
}
</style>
