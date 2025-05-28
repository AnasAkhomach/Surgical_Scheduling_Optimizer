<template>
  <div class="scheduling-container">
    <ToastNotification ref="toastRef" />
    <KeyboardShortcutsHelp ref="keyboardShortcutsRef" />

    <h1>Surgery Scheduling</h1>

    <div class="scheduling-layout">
      <aside class="left-panel">
        <h2>Pending Surgeries</h2>
        <p>Drag and drop surgeries from this list onto the schedule.</p>

        <div class="filters-section">
            <div class="filters-header">
              <h3>Filters</h3>
              <button
                @click="filters.showAdvancedFilters = !filters.showAdvancedFilters"
                class="btn btn-sm btn-link"
              >
                {{ filters.showAdvancedFilters ? 'Hide Advanced' : 'Show Advanced' }}
              </button>
            </div>

            <div class="filter-group">
              <label for="filter-priority">Priority:</label>
              <select id="filter-priority" v-model="filters.priority" @change="applyFilters" class="form-control">
                  <option value="">All</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
              </select>
            </div>
            <div class="filter-group">
              <label for="filter-specialty">Specialty:</label>
              <input type="text" id="filter-specialty" v-model="filters.specialty" placeholder="e.g., Cardiac" @input="applyFilters" class="form-control">
            </div>
            <div class="filter-group">
              <label for="filter-status">Status:</label>
              <select id="filter-status" v-model="filters.status" @change="applyFilters" class="form-control">
                  <option value="">All</option>
                  <option value="Pending">Pending</option>
                  <option value="Scheduled">Scheduled</option>
                  <option value="Cancelled">Cancelled</option>
              </select>
            </div>

            <div v-if="filters.showAdvancedFilters" class="advanced-filters">
              <div class="filter-group">
                  <label for="filter-surgeon">Surgeon:</label>
                  <input type="text" id="filter-surgeon" v-model="filters.surgeon" placeholder="e.g., Dr. Smith" @input="applyFilters" class="form-control">
              </div>
              <div class="filter-group">
                  <label for="filter-equipment">Equipment:</label>
                  <input type="text" id="filter-equipment" v-model="filters.equipment" placeholder="e.g., Heart-Lung Machine" @input="applyFilters" class="form-control">
              </div>
              <div class="filter-group">
                  <label>Date Range:</label>
                  <div class="date-range-inputs">
                    <input
                      type="date"
                      v-model="filters.dateRange.start"
                      class="form-control"
                      @change="applyFilters"
                    >
                    <span class="date-range-separator">to</span>
                    <input
                      type="date"
                      v-model="filters.dateRange.end"
                      class="form-control"
                      @change="applyFilters"
                    >
                  </div>
              </div>
            </div>

            <div class="filter-actions">
              <button @click="applyFilters" class="btn btn-sm btn-primary">Apply Filters</button>
              <button @click="resetFilters" class="btn btn-sm btn-secondary">Reset</button>
            </div>
        </div>

        <div class="sort-section">
            <h3>Sort By</h3>
            <div class="sort-controls">
              <select v-model="sortOptions.field" @change="applyFilters" class="form-control"> <option value="priority">Priority</option>
                  <option value="patientName">Patient Name</option>
                  <option value="type">Surgery Type</option>
                  <option value="estimatedDuration">Duration</option>
              </select>
              <div class="sort-direction">
                  <button
                    @click="sortOptions.direction = 'asc'; applyFilters()" class="btn btn-sm"
                    :class="{'btn-primary': sortOptions.direction === 'asc', 'btn-secondary': sortOptions.direction !== 'asc'}"
                  >
                    ↑ Asc
                  </button>
                  <button
                    @click="sortOptions.direction = 'desc'; applyFilters()" class="btn btn-sm"
                    :class="{'btn-primary': sortOptions.direction === 'desc', 'btn-secondary': sortOptions.direction !== 'desc'}"
                  >
                    ↓ Desc
                  </button>
              </div>
            </div>
        </div>

        <div class="pending-surgeries-list">
            <ul>
                <li
                  v-for="surgery in filteredPendingSurgeries"
                  :key="surgery.id"
                  class="pending-surgery-item"
                  :class="{
                    'selected': selectedSurgery && selectedSurgery.id === surgery.id,
                    [`priority-${surgery.priority.toLowerCase()}`]: true
                  }"
                  draggable="true"
                  @dragstart="handleDragStart(surgery, $event)"
                  @dragend="handleDragEnd($event)"
                  @click="selectSurgeryForDetails(surgery, 'pending')"
                >
                  <div class="item-header">
                    <div class="patient-info">
                      <span class="patient-name">{{ surgery.patientName || surgery.patientId }}</span>
                      <span class="patient-id" v-if="surgery.patientName">({{ surgery.patientId }})</span>
                    </div>
                    <span class="priority-badge" :class="`priority-${surgery.priority.toLowerCase()}`">
                      {{ surgery.priority }}
                    </span>
                  </div>
                  <div class="item-details">
                    <div class="surgery-type">
                      <span class="label">Type:</span>
                      <span class="value">{{ surgery.type }}</span>
                    </div>
                    <div class="surgery-full-type">
                      <span class="value">{{ surgery.fullType }}</span>
                    </div>
                    <div class="surgery-duration">
                      <span class="label">Duration:</span>
                      <span class="value">{{ surgery.estimatedDuration }} min</span>
                    </div>
                  </div>
                  <div class="item-status">
                    <span class="status-indicator" :class="`status-${surgery.status?.toLowerCase() || 'pending'}`"></span>
                    <span>{{ surgery.status || 'Pending' }}</span>
                  </div>
                  <div class="item-actions">
                      <button class="btn btn-sm btn-secondary" @click.stop="selectSurgeryForDetails(surgery, 'pending')">
                        <span class="icon">👁️</span> View
                      </button>
                      <button class="btn btn-sm btn-primary" @click.stop="promptScheduleSurgery(surgery)"> <span class="icon">📅</span> Schedule
                      </button>
                  </div>
                </li>
                <li v-if="filteredPendingSurgeries.length === 0" class="no-items">No pending surgeries matching filters.</li>
            </ul>
        </div>
      </aside>

      <main class="main-panel">
        <div class="schedule-header">
            <h2>Master Schedule View</h2>
            <div class="schedule-controls">
                <button @click="ganttNavigate('prev')" class="btn btn-sm btn-secondary">◀ Previous</button>
                <span class="current-date-range">{{ currentGanttViewDateRangeForDisplay }}</span>
                <button @click="ganttNavigate('next')" class="btn btn-sm btn-secondary">Next ▶</button>
                <button @click="ganttZoom('day')" class="btn btn-sm btn-secondary">Day View</button> <button @click="ganttZoom('week')" class="btn btn-sm btn-secondary">Week View</button> <button @click="showCreateNewSurgeryForm" class="btn btn-sm btn-primary">Create New Surgery</button>
            </div>
        </div>

        <OptimizationSuggestions />

        <div class="mt-8 bg-white p-4 rounded-lg shadow gantt-chart-wrapper">
          <h3 class="text-lg font-semibold mb-4 text-gray-700">Gantt Chart (vue-ganttastic)</h3>
          <g-gantt-chart
            :chart-start="ganttChartStart"
            :chart-end="ganttChartEnd"
            precision="hour"
            bar-start="myBeginDate"
            bar-end="myEndDate"
            row-label-width="150px"
            grid-label-width="100px"
            :grid="true"
            :highlighted-dates="ganttHighlightedDates"
            @click-bar="handleClickGanttBar($event.bar, $event.e, $event.datetime)"
            @dragend-bar="handleDragEndGanttBar($event.bar, $event.e)"
            @contextmenu-bar="handleContextmenuGanttBar($event.bar, $event.e, $event.datetime)"
            :row-label-font="'12px sans-serif'"
            :row-height="40"
            :highlight-on-hover="true"
            :push-on-overlap="false"
            :snap-back-on-overlap="true"
            :overlap-sensitivity="5"
            :bar-config-key="'ganttBarConfig'"
          >
            <g-gantt-row
              v-for="or in operatingRooms"
              :key="or.id"
              :label="or.name"
              :bars="getBarsForRow(or.id)"
              :highlight-on-hover="true"
            />
            <g-gantt-row v-if="!operatingRooms.length" label="No ORs Loaded" :bars="[]" />
          </g-gantt-chart>
        </div>

        <!--
        <div
          id="gantt-chart-container"
          class="gantt-chart-container"
          :class="{
            'drag-over': draggedSurgery && dropTarget.orId,
            'invalid': draggedSurgery && !dropTarget.isValid
          }"
          :data-drop-message="dropTarget.message"
          @drop="handleDropOnGantt($event)"
          @dragover="handleDragOver($event, 'OR1')"
        >
          <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
            <p>Loading schedule data...</p>
          </div>
          <div v-else-if="!isGanttInitialized" class="gantt-placeholder-text">
            Gantt Chart Area - Awaiting Library Integration
            <br>
            (Drop pending surgeries here to schedule)
          </div>
          <div v-else>
            <GanttChart />
            <div class="gantt-drop-message">
              Drag pending surgeries here to schedule them.
            </div>
          </div>
        </div>
        -->

        <div class="gantt-info-panel">
            <p><strong>SDST (Setup, Disinfection, Sterilization Time):</strong> Not yet calculated. Will be factored into scheduling.</p>
            <p><strong>Resource Conflicts:</strong> Conflict detection pending Gantt integration.</p>
        </div>
      </main>

      <aside class="right-panel">
        <div v-if="selectedSurgery">
          <h2>Surgery Details ({{ selectedSurgerySource === 'pending' ? 'Pending' : 'Scheduled' }})</h2>
          <form @submit.prevent="saveSurgeryDetails">
            <div v-if="formErrors.general" class="form-error-message general-error">
              {{ formErrors.general }}
            </div>

            <div class="form-group" :class="{'has-error': formSubmitted && formErrors.patientId}">
              <label for="patientId">Patient ID: <span class="required">*</span></label>
              <input
                type="text"
                id="patientId"
                v-model="selectedSurgery.patientId"
                :disabled="formMode === 'view'"
                class="form-control"
                :class="{'is-invalid': formSubmitted && formErrors.patientId}"
              >
              <div v-if="formSubmitted && formErrors.patientId" class="form-error-message">
                {{ formErrors.patientId }}
              </div>
            </div>

            <div class="form-group" :class="{'has-error': formSubmitted && formErrors.patientName}">
              <label for="patientName">Patient Name: <span class="required">*</span></label>
              <input
                type="text"
                id="patientName"
                v-model="selectedSurgery.patientName"
                :disabled="formMode === 'view'"
                class="form-control"
                :class="{'is-invalid': formSubmitted && formErrors.patientName}"
              >
              <div v-if="formSubmitted && formErrors.patientName" class="form-error-message">
                {{ formErrors.patientName }}
              </div>
            </div>

            <div class="form-group" :class="{'has-error': formSubmitted && formErrors.type}">
              <label for="surgeryType">Surgery Type: <span class="required">*</span></label>
              <select
                id="surgeryType"
                v-model="selectedSurgery.type"
                :disabled="formMode === 'view'"
                class="form-control"
                :class="{'is-invalid': formSubmitted && formErrors.type}"
                @change="updateFullType"
              >
                <option value="">Select a surgery type</option>
                <option value="CABG">CABG</option>
                <option value="KNEE">Knee Replacement</option>
                <option value="APPEN">Appendectomy</option>
                <option value="HERNI">Hernia Repair</option>
                <option value="CATAR">Cataract Surgery</option>
                <option value="HIPRE">Hip Replacement</option>
              </select>
              <div v-if="formSubmitted && formErrors.type" class="form-error-message">
                {{ formErrors.type }}
              </div>
            </div>

            <div class="form-group" :class="{'has-error': formSubmitted && formErrors.fullType}">
              <label for="fullType">Full Type: <span class="required">*</span></label>
              <input
                type="text"
                id="fullType"
                v-model="selectedSurgery.fullType"
                :disabled="formMode === 'view'"
                class="form-control"
                :class="{'is-invalid': formSubmitted && formErrors.fullType}"
              >
              <div v-if="formSubmitted && formErrors.fullType" class="form-error-message">
                {{ formErrors.fullType }}
              </div>
            </div>

            <div class="form-group" :class="{'has-error': formSubmitted && formErrors.estimatedDuration}">
              <label for="estimatedDuration">Estimated Duration (min): <span class="required">*</span></label>
              <input
                type="number"
                id="estimatedDuration"
                v-model.number="selectedSurgery.estimatedDuration"
                :disabled="formMode === 'view'"
                class="form-control"
                :class="{'is-invalid': formSubmitted && formErrors.estimatedDuration}"
                min="1"
              >
              <div v-if="formSubmitted && formErrors.estimatedDuration" class="form-error-message">
                {{ formErrors.estimatedDuration }}
              </div>
            </div>
            <div class="form-group">
              <label for="priority">Priority Level:</label>
              <select id="priority" v-model="selectedSurgery.priority" :disabled="formMode === 'view'" class="form-control">
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div class="form-group" v-if="selectedSurgerySource === 'scheduled'">
              <label for="scheduledTime">Scheduled Time:</label>
              <input type="datetime-local" id="scheduledTime" v-model="selectedSurgery.scheduledTime" :disabled="formMode === 'view'" class="form-control">
            </div>
             <div class="form-group" v-if="selectedSurgerySource === 'scheduled'">
              <label for="operatingRoom">Operating Room:</label>
              <select id="operatingRoom" v-model="selectedSurgery.orId" :disabled="formMode === 'view'" class="form-control">
                <option v-for="or in operatingRooms" :key="or.id" :value="or.id">{{ or.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label for="status">Status:</label>
              <select id="status" v-model="selectedSurgery.status" :disabled="formMode === 'view'" class="form-control">
                <option value="Pending">Pending</option>
                <option value="Scheduled">Scheduled</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>

            <div class="form-group">
              <label for="requiredSurgeons">Required Surgeons:</label>
              <input type="text" id="requiredSurgeons" v-model="selectedSurgery.requiredSurgeons" :disabled="formMode === 'view'" class="form-control">
              <small class="form-text text-muted">Enter surgeon names separated by commas</small>
            </div>

            <div class="form-group">
              <label for="requiredStaffRoles">Required Staff Roles:</label>
              <input type="text" id="requiredStaffRoles" v-model="selectedSurgery.requiredStaffRoles" :disabled="formMode === 'view'" class="form-control">
              <small class="form-text text-muted">Enter staff roles separated by commas</small>
            </div>

            <div class="form-group">
              <label for="requiredEquipment">Required Equipment:</label>
              <input type="text" id="requiredEquipment" v-model="selectedSurgery.requiredEquipment" :disabled="formMode === 'view'" class="form-control">
              <small class="form-text text-muted">Enter equipment names separated by commas</small>
            </div>

            <div class="form-actions">
              <button type="button" v-if="formMode === 'view'" @click="formMode = 'edit'" class="btn btn-primary">Edit</button>
              <button type="submit" v-if="formMode !== 'view'" class="btn btn-primary">Save Changes</button>
              <button type="button" @click="clearSelectionOrCancel" class="btn btn-secondary">{{ formMode === 'new' ? 'Cancel' : 'Close' }}</button>
              <button type="button" v-if="selectedSurgerySource === 'pending' && formMode !== 'new'" @click="promptScheduleSurgery(selectedSurgery)" class="btn btn-primary">Schedule This Surgery</button>
            </div>
          </form>
        </div>
        <div v-else>
          <h2>Surgery Details</h2>
          <p>Select a pending surgery to view its details, or drag it to the schedule. Click "Create New Surgery" to add a new entry.</p>
          <div class="form-preview">
            </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import { useNotificationStore } from '@/stores/notificationStore';
import { storeToRefs } from 'pinia';
// import GanttChart from './GanttChart.vue'; // Custom component, kept but not used for vue-ganttastic
import ToastNotification from './ToastNotification.vue';
import KeyboardShortcutsHelp from './KeyboardShortcutsHelp.vue';
import OptimizationSuggestions from './OptimizationSuggestions.vue';
import keyboardShortcuts from '@/services/keyboardShortcuts';

// NOTE: If GGanttChart and GGanttRow are not globally available after plugin registration,
// you might need to import them here:
// import { GGanttChart, GGanttRow } from '@infectoone/vue-ganttastic';

const scheduleStore = useScheduleStore();
const notificationStore = useNotificationStore();
const {
  pendingSurgeries: storePendingSurgeries,
  scheduledSurgeries: storeScheduledSurgeries,
  selectedSurgeryId,
  isLoading,
  currentDateRange, // Provides { start: Date, end: Date }
  ganttViewMode, // 'Day' or 'Week'
  operatingRooms // Assuming you have this in your store: [{id: 'OR1', name: 'Operating Room 1'}, ...]
} = storeToRefs(scheduleStore);

const toastRef = ref(null);
const keyboardShortcutsRef = ref(null);

const selectedSurgery = ref(null);
const selectedSurgerySource = ref(''); // 'pending' or 'scheduled'
const formMode = ref('view'); // 'view', 'edit', 'new'
const formErrors = ref({});
const formSubmitted = ref(false);

const filters = ref({
  priority: '',
  specialty: '',
  status: '',
  surgeon: '',
  equipment: '',
  dateRange: { start: null, end: null },
  showAdvancedFilters: false
});

const sortOptions = ref({
  field: 'priority',
  direction: 'desc'
});

// const isGanttInitialized = ref(false); // For custom Gantt, may not be needed now

// Data for vue-ganttastic bars, structured per OR
// This will be populated dynamically from storeScheduledSurgeries
const ganttChartBarsByRow = ref({}); // Example: { OR1: [bar1, bar2], OR2: [bar3] }

// Helper to format date string as YYYY-MM-DD HH:MM for vue-ganttastic
function formatDateForGantt(date) {
  if (!(date instanceof Date) || isNaN(date.valueOf())) {
    // Try to parse if it's a string that might be a date
    const d = new Date(date);
    if (isNaN(d.valueOf())) return "2000-01-01 00:00"; // Fallback for invalid date
    date = d;
  }
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
}


const ganttChartStart = computed(() => {
  return currentDateRange.value?.start ? formatDateForGantt(currentDateRange.value.start) : formatDateForGantt(new Date());
});

const ganttChartEnd = computed(() => {
  if (currentDateRange.value?.end) {
    const endDate = new Date(currentDateRange.value.end);
    // vue-ganttastic chart-end is often exclusive for the last day, or needs to cover the full day.
    // If it's a 'Day' view, end might be start + 1 day. If 'Week', it's the end of the week.
    // Let's ensure it covers the full last day of the range.
    endDate.setHours(23, 59, 59, 999);
    if (ganttViewMode.value === 'Day' && currentDateRange.value.start.toDateString() === endDate.toDateString()) {
        // For day view, make sure end is at least end of the start day or start of next day
        return formatDateForGantt(new Date(endDate.getTime() + 1)); // Effectively start of next day
    }
    return formatDateForGantt(endDate);
  }
  // Fallback for ganttChartEnd
  const fallbackStartDate = currentDateRange.value?.start ? new Date(currentDateRange.value.start) : new Date();
  return formatDateForGantt(new Date(fallbackStartDate.setDate(fallbackStartDate.getDate() + (ganttViewMode.value === 'Week' ? 7 : 1))));
});


const ganttHighlightedDates = computed(() => {
  // Example: highlight weekends or specific dates
  // This needs to be an array of date strings in "YYYY-MM-DD HH:MM" format
  // For now, let's return an empty array or a sample
  return []; // e.g., ["2024-07-27 00:00", "2024-07-28 00:00"]
});


const filteredPendingSurgeries = computed(() => {
  if (!storePendingSurgeries.value) return [];
  let surgeries = [...storePendingSurgeries.value]; // Create a shallow copy for filtering

  // Apply basic filters
  if (filters.value.priority) {
    surgeries = surgeries.filter(s => s.priority === filters.value.priority);
  }
  if (filters.value.specialty) {
    const specialtyLower = filters.value.specialty.toLowerCase();
    surgeries = surgeries.filter(s => s.fullType && s.fullType.toLowerCase().includes(specialtyLower));
  }
  if (filters.value.status) {
    surgeries = surgeries.filter(s => s.status === filters.value.status);
  }

  // Apply advanced filters
  if (filters.value.showAdvancedFilters) {
    if (filters.value.surgeon) {
      const surgeonLower = filters.value.surgeon.toLowerCase();
      surgeries = surgeries.filter(s =>
        s.requiredSurgeons && (Array.isArray(s.requiredSurgeons)
          ? s.requiredSurgeons.some(surgeon => surgeon.toLowerCase().includes(surgeonLower))
          : String(s.requiredSurgeons).toLowerCase().includes(surgeonLower))
      );
    }
    if (filters.value.equipment) {
      const equipmentLower = filters.value.equipment.toLowerCase();
      surgeries = surgeries.filter(s =>
        s.requiredEquipment && (Array.isArray(s.requiredEquipment)
          ? s.requiredEquipment.some(eq => eq.toLowerCase().includes(equipmentLower))
          : String(s.requiredEquipment).toLowerCase().includes(equipmentLower))
      );
    }
    if (filters.value.dateRange.start && filters.value.dateRange.end) {
      const filterStart = new Date(filters.value.dateRange.start).setHours(0,0,0,0);
      const filterEnd = new Date(filters.value.dateRange.end).setHours(23,59,59,999);
      surgeries = surgeries.filter(s => {
        if (!s.requestedDate) return false;
        const reqDate = new Date(s.requestedDate).getTime();
        return reqDate >= filterStart && reqDate <= filterEnd;
      });
    }
  }

  // Apply sorting
  return sortSurgeries(surgeries, sortOptions.value.field, sortOptions.value.direction);
});

const sortSurgeries = (surgeries, field, direction) => {
  return surgeries.sort((a, b) => {
    let comparison = 0;
    const priorityValues = { 'High': 3, 'Medium': 2, 'Low': 1, '': 0 };

    switch (field) {
      case 'priority':
        comparison = (priorityValues[a.priority] || 0) - (priorityValues[b.priority] || 0);
        break;
      case 'estimatedDuration':
        comparison = (a.estimatedDuration || 0) - (b.estimatedDuration || 0);
        break;
      case 'patientName':
        comparison = (a.patientName || a.patientId || '').localeCompare(b.patientName || b.patientId || '');
        break;
      case 'type':
        comparison = (a.type || '').localeCompare(b.type || '');
        break;
    }
    return direction === 'asc' ? comparison : -comparison;
  });
};


const currentGanttViewDateRangeForDisplay = computed(() => {
  if (currentDateRange.value && currentDateRange.value.start instanceof Date) {
    const start = currentDateRange.value.start;
    // Ensure end is also a Date object for formatting
    const end = currentDateRange.value.end instanceof Date ? currentDateRange.value.end : new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);

    if (ganttViewMode.value === 'Day') {
      return start.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
    } else if (ganttViewMode.value === 'Week') {
      return `${start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
  }
  return 'Date range not set';
});

// Transform scheduled surgeries for vue-ganttastic
const updateGanttasticBars = () => {
  const newBarsByRow = {};
  if (!operatingRooms.value || operatingRooms.value.length === 0) {
    console.warn("No operating rooms defined in store. Gantt chart rows will be empty.");
    ganttChartBarsByRow.value = {};
    return;
  }

  operatingRooms.value.forEach(or => {
    newBarsByRow[or.id] = [];
  });

  storeScheduledSurgeries.value.forEach(surgery => {
    if (!surgery.startTime || !surgery.endTime || !surgery.orId) {
      console.warn(`Surgery ${surgery.id} is missing startTime, endTime, or orId. Skipping.`);
      return;
    }
    if (!newBarsByRow[surgery.orId]) {
        console.warn(`Operating room ${surgery.orId} for surgery ${surgery.id} not found in operatingRooms list. Skipping.`);
        return;
    }

    const bar = {
      myBeginDate: formatDateForGantt(new Date(surgery.startTime)),
      myEndDate: formatDateForGantt(new Date(surgery.endTime)),
      ganttBarConfig: {
        id: surgery.id, // Must be unique
        label: `${surgery.patientName || surgery.patientId} (${surgery.type})`,
        style: {
          background: surgery.priority === 'High' ? '#E57373' : (surgery.priority === 'Medium' ? '#FFB74D' : '#81C784'),
          borderRadius: '5px',
          color: 'white',
          boxShadow: '1px 1px 3px rgba(0,0,0,0.2)'
        },
        // You can add more properties like `immobile`, `progress`, etc.
        // Store original surgery data for easy access on events
        bundle: surgery, // Custom property to hold the original surgery data
      }
    };
    newBarsByRow[surgery.orId].push(bar);
  });
  ganttChartBarsByRow.value = newBarsByRow;
};

// Computed property to get bars for a specific row (OR)
const getBarsForRow = (orId) => {
  return ganttChartBarsByRow.value[orId] || [];
};


watch(storeScheduledSurgeries, updateGanttasticBars, { deep: true, immediate: true });
watch(operatingRooms, updateGanttasticBars, { deep: true, immediate: true }); // Also update if ORs change


const applyFilters = () => {
  // Computed property `filteredPendingSurgeries` handles this.
  // If additional actions are needed, add them here.
  console.log('Filters applied/changed:', filters.value, sortOptions.value);
};

const resetFilters = () => {
  filters.value = {
    priority: '', specialty: '', status: '', surgeon: '', equipment: '',
    dateRange: { start: null, end: null },
    showAdvancedFilters: filters.value.showAdvancedFilters
  };
  sortOptions.value = { field: 'priority', direction: 'desc' }; // Reset sort as well
  applyFilters(); // Re-apply to update list
};

const selectSurgeryForDetails = (surgeryData, source) => {
  // If surgeryData is from a Gantt bar, it's in surgeryData.ganttBarConfig.bundle
  const surgery = source === 'gantt' && surgeryData.ganttBarConfig?.bundle ? surgeryData.ganttBarConfig.bundle : surgeryData;

  selectedSurgery.value = { ...surgery };
  // Ensure scheduledTime is in YYYY-MM-DDTHH:mm format for datetime-local input
  if (surgery.startTime && source === 'scheduled') {
    const d = new Date(surgery.startTime);
    selectedSurgery.value.scheduledTime = `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}T${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  }
  selectedSurgerySource.value = source === 'gantt' ? 'scheduled' : source;
  formMode.value = 'view';
  if (source === 'scheduled' || source === 'gantt') {
    scheduleStore.selectSurgery(surgery.id);
  }
};

const showCreateNewSurgeryForm = () => {
  formSubmitted.value = false;
  formErrors.value = {};
  selectedSurgery.value = {
    patientId: `PAT-${Date.now().toString().slice(-4)}`, // Example ID
    patientName: '', type: '', fullType: '',
    estimatedDuration: 60, priority: 'Medium', status: 'Pending',
    requiredSurgeons: '', requiredStaffRoles: '', requiredEquipment: '' // Keep as strings for input
  };
  selectedSurgerySource.value = 'new';
  formMode.value = 'new';
};

const validateSurgeryForm = () => {
  formSubmitted.value = true;
  const errors = {};
  const surgery = selectedSurgery.value;
  if (!surgery.patientId?.trim()) errors.patientId = 'Patient ID is required';
  if (!surgery.patientName?.trim()) errors.patientName = 'Patient Name is required';
  if (!surgery.type?.trim()) errors.type = 'Surgery Type is required';
  if (!surgery.fullType?.trim()) errors.fullType = 'Full Type is required';
  if (!surgery.estimatedDuration || surgery.estimatedDuration <= 0) errors.estimatedDuration = 'Duration must be > 0';
  formErrors.value = errors;
  return Object.keys(errors).length === 0;
};

const saveSurgeryDetails = async () => {
  if (!selectedSurgery.value || !validateSurgeryForm()) {
    notificationStore.error('Please fix validation errors.');
    return;
  }

  // Convert comma-separated strings to arrays for store/backend if needed
  const surgeryToSave = {
    ...selectedSurgery.value,
    requiredSurgeons: selectedSurgery.value.requiredSurgeons?.split(',').map(s => s.trim()).filter(Boolean) || [],
    requiredStaffRoles: selectedSurgery.value.requiredStaffRoles?.split(',').map(s => s.trim()).filter(Boolean) || [],
    requiredEquipment: selectedSurgery.value.requiredEquipment?.split(',').map(s => s.trim()).filter(Boolean) || [],
  };
   // If it's a scheduled surgery being edited, ensure startTime and orId are correctly handled
  if (selectedSurgerySource.value === 'scheduled' && selectedSurgery.value.scheduledTime) {
    surgeryToSave.startTime = new Date(selectedSurgery.value.scheduledTime).toISOString();
    // orId should already be part of selectedSurgery.value if editing a scheduled one
  }


  try {
    if (formMode.value === 'new') {
      await scheduleStore.addPendingSurgery(surgeryToSave);
      notificationStore.success('New surgery added to pending list.');
    } else if (selectedSurgerySource.value === 'pending') {
      await scheduleStore.updatePendingSurgery(surgeryToSave);
      notificationStore.success('Pending surgery details updated.');
    } else if (selectedSurgerySource.value === 'scheduled') {
      await scheduleStore.updateScheduledSurgery(surgeryToSave);
      notificationStore.success('Scheduled surgery details updated.');
    }
    formMode.value = 'view'; // Revert to view mode after save
  } catch (error) {
    console.error(`Error saving surgery:`, error);
    formErrors.value.general = `Error: ${error.message}`;
    notificationStore.error(`Error saving surgery: ${error.message}`);
  }
};

const updateFullType = () => {
  if (!selectedSurgery.value) return;
  const typeMap = {
    'CABG': 'Coronary Artery Bypass Graft', 'KNEE': 'Total Knee Replacement',
    'APPEN': 'Appendectomy', 'HERNI': 'Hernia Repair',
    'CATAR': 'Cataract Surgery', 'HIPRE': 'Total Hip Replacement'
  };
  selectedSurgery.value.fullType = typeMap[selectedSurgery.value.type] || '';
};

const clearSelectionOrCancel = () => {
  selectedSurgery.value = null;
  selectedSurgerySource.value = '';
  formMode.value = 'view';
  formSubmitted.value = false;
  formErrors.value = {};
  scheduleStore.clearSelectedSurgery();
};

const promptScheduleSurgery = (surgery) => {
  // This is a placeholder. In a real scenario, you'd open a modal
  // to select OR and time, or allow dropping onto vue-ganttastic.
  // For now, let's use a default OR and current time for quick scheduling.
  const targetOR = operatingRooms.value?.[0]?.id || 'OR1'; // Default to first OR or 'OR1'
  const scheduleTime = new Date(); // Default to now

  // Ensure minutes are rounded to 00, 15, 30, 45 for example
  scheduleTime.setMinutes(Math.round(scheduleTime.getMinutes() / 15) * 15, 0, 0);


  if (window.confirm(`Schedule "${surgery.patientName || surgery.patientId}" in ${targetOR} at ${scheduleTime.toLocaleString()}?`)) {
    scheduleStore.schedulePendingSurgery(surgery.id, targetOR, scheduleTime.toISOString())
      .then(scheduled => {
        if (scheduled) {
          notificationStore.success(`Surgery scheduled in ${targetOR}.`);
          selectSurgeryForDetails(scheduled, 'scheduled');
        }
      })
      .catch(error => notificationStore.error(`Scheduling failed: ${error.message}`));
  }
};


// --- Drag and Drop Handlers (for pending list items) ---
const draggedSurgery = ref(null);
const dragGhost = ref(null);
// const dropTarget = ref({ orId: null, time: null, isValid: true, message: '' }); // For custom Gantt

const handleDragStart = (surgery, event) => {
  draggedSurgery.value = surgery;
  event.dataTransfer.setData('application/json', JSON.stringify(surgery));
  event.dataTransfer.effectAllowed = 'move';
  event.target.classList.add('dragging');

  const ghostElement = document.createElement('div');
  ghostElement.classList.add('surgery-drag-ghost');
  ghostElement.innerHTML = `
    <div class="ghost-priority ${surgery.priority.toLowerCase()}"></div>
    <div class="ghost-content">
      <div class="ghost-title">${surgery.patientName || surgery.patientId}</div>
      <div class="ghost-type">${surgery.type} - ${surgery.estimatedDuration} min</div>
    </div>
  `;
  document.body.appendChild(ghostElement);
  dragGhost.value = ghostElement;
  event.dataTransfer.setDragImage(ghostElement, 20, 20);
  setTimeout(() => { ghostElement.style.position = 'absolute'; ghostElement.style.left = '-9999px'; }, 0);
};

const handleDragEnd = (event) => {
  event.target.classList.remove('dragging');
  if (dragGhost.value && dragGhost.value.parentNode) {
    dragGhost.value.parentNode.removeChild(dragGhost.value);
    dragGhost.value = null;
  }
  draggedSurgery.value = null;
  // Reset any drop target indicators for vue-ganttastic if needed
};

// --- vue-ganttastic Event Handlers ---
const handleClickGanttBar = (bar, event, datetime) => {
  console.log('Clicked Gantt Bar:', bar, 'at time:', datetime);
  // bar.ganttBarConfig.bundle should contain the original surgery object
  if (bar.ganttBarConfig?.bundle) {
    selectSurgeryForDetails(bar, 'gantt'); // Pass the bar itself, selectSurgeryForDetails will extract bundle
  }
};

const handleDragEndGanttBar = async (bar, event) => {
  console.log('Dragged Gantt Bar to new time:', bar.beginDate, bar.endDate);
  const originalSurgery = bar.ganttBarConfig?.bundle;
  if (!originalSurgery) return;

  // Assuming bar.beginDate and bar.endDate are updated by vue-ganttastic to Date objects or parsable strings
  const newStartTime = new Date(bar.beginDate);
  const newEndTime = new Date(bar.endDate); // vue-ganttastic might provide this directly

  // Find the OR (row) this bar belongs to. This is a bit tricky as vue-ganttastic doesn't directly tell you the row of the event.
  // You might need to iterate ganttChartBarsByRow or have a mapping.
  // For simplicity, we'll assume the orId is stored in originalSurgery.orId
  const orId = originalSurgery.orId;

  if (!orId) {
      notificationStore.error("Could not determine Operating Room for the moved surgery.");
      updateGanttasticBars(); // Revert visual change by re-rendering from store
      return;
  }


  // Optimistically update UI or confirm with user
  // For now, directly update the store
  try {
    const updatedSurgeryData = {
      ...originalSurgery,
      startTime: newStartTime.toISOString(),
      endTime: newEndTime.toISOString(), // Ensure this is calculated correctly if not provided by event
      orId: orId, // The OR might have changed if you implement cross-row dragging
      status: 'Scheduled' // Ensure status is correct
    };
    await scheduleStore.updateScheduledSurgery(updatedSurgeryData);
    notificationStore.success(`Surgery ${originalSurgery.patientName || originalSurgery.patientId} moved to ${newStartTime.toLocaleString()}.`);
    // The watch on storeScheduledSurgeries should update the ganttChartBarsByRow automatically
  } catch (error) {
    notificationStore.error(`Failed to update surgery time: ${error.message}`);
    updateGanttasticBars(); // Revert if store update fails
  }
};

const handleContextmenuGanttBar = (bar, event, datetime) => {
  event.preventDefault();
  console.log('Context Menu on Gantt Bar:', bar, 'at time:', datetime);
  // Implement custom context menu logic here (e.g., show options to edit, unschedule, etc.)
  const surgery = bar.ganttBarConfig?.bundle;
  if (surgery) {
    selectSurgeryForDetails(bar, 'gantt'); // Select it for context
    // Example:
    // showContextMenu(event.clientX, event.clientY, surgery);
    notificationStore.info(`Right-clicked on ${surgery.patientName || surgery.patientId}. Implement context menu.`);
  }
};


// Gantt Chart Navigation and Controls
const ganttNavigate = (direction) => { scheduleStore.navigateGanttDate(direction); };
const ganttZoom = (viewMode) => { // viewMode is 'Day' or 'Week'
  scheduleStore.updateGanttViewMode(viewMode);
};

onMounted(() => {
  scheduleStore.loadInitialData().then(() => {
     // Ensure operatingRooms are loaded before first bar update
    if (!operatingRooms.value || operatingRooms.value.length === 0) {
      // If ORs are fetched asynchronously and not yet available,
      // you might need to watch for their availability or ensure they are part of initial data.
      // For now, we assume they are part of the initial load or available synchronously.
      console.log("Operating rooms might still be loading or are empty.");
    }
    updateGanttasticBars(); // Initial population of Gantt bars
  });

  nextTick(() => { if (toastRef.value) notificationStore.setToastRef(toastRef.value); });
  registerKeyboardShortcuts();
  watch(() => selectedSurgeryId.value, (newId) => {
    if (newId) {
      const surgery = storeScheduledSurgeries.value.find(s => s.id === newId);
      if (surgery) selectSurgeryForDetails(surgery, 'scheduled');
    } else {
      // If selectedSurgeryId is cleared, and form is not for 'new', clear the form.
      if (selectedSurgery.value && formMode.value !== 'new') {
        clearSelectionOrCancel();
      }
    }
  });
});

const registerKeyboardShortcuts = () => {
  keyboardShortcuts.register('n', showCreateNewSurgeryForm, { description: 'Create new surgery', scope: 'scheduling' });
  keyboardShortcuts.register('s', () => {
    if (selectedSurgery.value && formMode.value !== 'view') saveSurgeryDetails();
  }, { ctrlKey: true, description: 'Save surgery details', scope: 'scheduling' });
  keyboardShortcuts.register('escape', () => {
    if (selectedSurgery.value) clearSelectionOrCancel();
  }, { description: 'Cancel/close form', scope: 'scheduling' });
  // ... other shortcuts
};

</script>


<style scoped>
.scheduling-container {
  padding: var(--spacing-md);
  background-color: var(--color-background);
  color: var(--color-text);
  height: calc(100vh - 60px); /* Assuming header is 60px */
  display: flex;
  flex-direction: column;
}

h1 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
  text-align: center;
}

.scheduling-layout {
  display: flex;
  flex-grow: 1;
  gap: var(--spacing-md);
  overflow: hidden; /* Prevent layout from exceeding container height */
}

.left-panel, .right-panel {
  width: 25%;
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* Allow scrolling within panels */
}

.main-panel {
  flex-grow: 1;
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Important for Gantt chart layout */
}

.left-panel h2, .main-panel h2, .right-panel h2 {
  color: var(--color-text);
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--spacing-sm);
}

.filters-section, .sort-section {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.filters-section h3, .sort-section h3 {
  margin-top: 0;
  margin-bottom: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
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

.filter-group select,
.filter-group input[type="text"],
.filter-group input[type="date"] {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background);
  color: var(--color-text);
}

.advanced-filters {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-sm);
  border-left: 3px solid var(--color-primary);
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.date-range-separator {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  text-decoration: underline;
  padding: 0;
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.btn-link:hover {
  color: var(--color-primary-dark, #0056b3);
  text-decoration: none;
}

.sort-controls {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.sort-direction {
  display: flex;
  gap: var(--spacing-xs);
}

.sort-direction button {
  flex: 1;
}

.pending-surgeries-list {
  flex-grow: 1;
  overflow-y: auto;
}

.pending-surgeries-list ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.pending-surgery-item {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: grab;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.pending-surgery-item:hover {
  background-color: var(--color-background-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.pending-surgery-item.selected {
  border-color: var(--color-primary);
  background-color: var(--color-background-active);
}

.pending-surgery-item.priority-high {
  border-left: 4px solid var(--color-error);
}

.pending-surgery-item.priority-medium {
  border-left: 4px solid var(--color-warning, #f59e0b);
}

.pending-surgery-item.priority-low {
  border-left: 4px solid var(--color-success, #10b981);
}

.pending-surgery-item.dragging {
  opacity: 0.4;
  transform: scale(1.02);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
  border-style: dashed;
}

/* Drag ghost element */
.surgery-drag-ghost {
  display: flex;
  background-color: var(--color-background);
  border: 2px solid var(--color-primary);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  width: 250px;
  pointer-events: none;
  z-index: 1000;
}

.ghost-priority {
  width: 8px;
  margin-right: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
}

.ghost-priority.high {
  background-color: var(--color-error);
}

.ghost-priority.medium {
  background-color: var(--color-warning, #f59e0b);
}

.ghost-priority.low {
  background-color: var(--color-success, #10b981);
}

.ghost-content {
  flex: 1;
}

.ghost-title {
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ghost-type {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Drop target indicator */
.gantt-chart-container::after {
  content: attr(data-drop-message);
  display: none;
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: var(--color-background);
  color: var(--color-text);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
  font-size: var(--font-size-sm);
  pointer-events: none;
}

.gantt-chart-container.drag-over::after {
  display: block;
}

.gantt-chart-container.drag-over.invalid::after {
  background-color: var(--color-error-bg, rgba(255, 0, 0, 0.1));
  color: var(--color-error);
  border: 1px solid var(--color-error);
}

.item-header {
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.patient-info {
  display: flex;
  flex-direction: column;
}

.patient-name {
  font-size: var(--font-size-md);
  color: var(--color-text);
}

.patient-id {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-normal);
}

.priority-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: white;
}

.priority-badge.priority-high {
  background-color: var(--color-error);
}

.priority-badge.priority-medium {
  background-color: var(--color-warning, #f59e0b);
}

.priority-badge.priority-low {
  background-color: var(--color-success, #10b981);
}

.item-details {
  font-size: var(--font-size-sm);
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
  padding: var(--spacing-sm);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-sm);
}

.surgery-type, .surgery-duration {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.surgery-full-type {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.label {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.value {
  font-weight: var(--font-weight-medium);
}

.item-status {
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: var(--spacing-xs);
}

.status-indicator.status-pending {
  background-color: var(--color-warning, #f59e0b);
}

.status-indicator.status-scheduled {
  background-color: var(--color-primary);
}

.status-indicator.status-completed {
  background-color: var(--color-success, #10b981);
}

.status-indicator.status-cancelled {
  background-color: var(--color-error);
}

.item-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.item-actions .icon {
  margin-right: var(--spacing-xs);
}

.no-items, .no-scheduled-items {
    padding: 10px;
    text-align: center;
    color: var(--text-color-secondary); /* Ensure this CSS var is defined */
    font-style: italic;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.schedule-controls button {
  margin-left: 10px;
  padding: 8px 12px;
  background-color: var(--primary-color); /* Ensure this CSS var is defined */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.schedule-controls button:hover {
  background-color: var(--primary-color-dark); /* Ensure this CSS var is defined */
}

.schedule-controls span {
    margin: 0 10px;
    font-weight: bold;
}

.gantt-chart-placeholder {
  flex-grow: 1;
  border: 2px dashed var(--border-color); /* Ensure this CSS var is defined */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-color-secondary); /* Ensure this CSS var is defined */
  border-radius: 4px;
  background-color: var(--background-color-light); /* Ensure this CSS var is defined */
  min-height: 300px;
  overflow-y: auto;
}

.gantt-chart-container {
  position: relative;
}

.scheduled-surgery-list-debug {
    list-style: none;
    padding: 0;
    margin-top: 10px;
    font-size: 0.9em;
}
.scheduled-surgery-list-debug li {
    padding: 5px;
    border-bottom: 1px solid var(--border-color-light); /* Ensure this CSS var is defined */
    cursor: pointer;
}
.scheduled-surgery-list-debug li:hover {
    background-color: var(--hover-color); /* Ensure this CSS var is defined */
}


.right-panel form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-md);
}

.form-group label {
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.form-group .required {
  color: var(--color-error);
  margin-left: var(--spacing-xs);
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="datetime-local"],
.form-group select,
.form-group textarea {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: var(--font-size-base);
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb, 0, 120, 212), 0.25); /* Ensure --color-primary-rgb is defined */
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background-color: var(--color-background-mute);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.form-group.has-error input,
.form-group.has-error select,
.form-group.has-error textarea,
.form-group input.is-invalid,
.form-group select.is-invalid,
.form-group textarea.is-invalid {
  border-color: var(--color-error);
}

.form-error-message {
  color: var(--color-error);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
}

.form-error-message.general-error {
  background-color: rgba(var(--color-error-rgb, 255, 0, 0), 0.1); /* Ensure --color-error-rgb is defined */
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-md);
}

.form-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.form-actions {
  margin-top: var(--spacing-lg);
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: var(--font-weight-medium);
  transition: background-color 0.2s ease;
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark, #0056b3);
}

.btn-secondary {
  background-color: var(--color-background-mute);
  color: var(--color-text);
}

.btn-secondary:hover {
  background-color: var(--color-background-active);
}

/* Responsive adjustments if needed */
@media (max-width: 1200px) {
  .scheduling-layout {
    flex-direction: column; /* Stack panels on smaller screens */
    overflow: visible;
  }
  .left-panel, .right-panel, .main-panel {
    width: 100%;
    margin-bottom: 20px;
    max-height: 50vh; /* Limit height when stacked */
    overflow-y: auto;
  }
  .main-panel {
      min-height: 400px; /* Ensure Gantt area is usable */
  }
}

/* Add some basic styling for the gantt chart wrapper if needed */
.gantt-chart-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-height: 400px; /* Ensure it has some height */
  overflow: hidden; /* Prevent content overflow issues */
}

/* vue-ganttastic might require its container to have a specific height or flex properties */
:deep(.g-gantt-chart) { /* Using :deep to target child component styles if necessary */
  /* Adjust height as needed, or make it flexible */
  height: 100%;
  width: 100%;
}
:deep(.g-timeaxis) {
    /* Example: Make timeaxis text smaller if it overlaps */
    font-size: 10px;
}
:deep(.g-gantt-row-label) {
    font-size: 12px !important; /* Example to ensure label size */
}
.loading-overlay {
  /* ... your existing styles ... */
}
.spinner {
  /* ... your existing styles ... */
}
.gantt-placeholder-text {
   /* ... your existing styles ... */
}
.gantt-info-panel {
   /* ... your existing styles ... */
}

/* Ensure the form control class is applied to selects in filters for consistency */
.filters-section select.form-control,
.sort-section select.form-control {
  /* Styles should already be covered by .filter-group select and global .form-control if any */
}
</style>