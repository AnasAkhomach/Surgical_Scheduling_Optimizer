<template>
  <div class="scheduling-container">
    <!-- Toast Notifications and Keyboard Shortcuts Help -->
    <ToastNotification ref="toastRef" />
    <KeyboardShortcutsHelp ref="keyboardShortcutsRef" />

    <h1>Surgery Scheduling</h1>

    <div class="scheduling-layout">
      <!-- Left Panel: Pending Surgeries & Filters -->
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

             <!-- Basic Filters -->
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

             <!-- Advanced Filters -->
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
                <select v-model="sortOptions.field" class="form-control">
                    <option value="priority">Priority</option>
                    <option value="patientName">Patient Name</option>
                    <option value="type">Surgery Type</option>
                    <option value="estimatedDuration">Duration</option>
                </select>
                <div class="sort-direction">
                    <button
                        @click="sortOptions.direction = 'asc'"
                        class="btn btn-sm"
                        :class="{'btn-primary': sortOptions.direction === 'asc', 'btn-secondary': sortOptions.direction !== 'asc'}"
                    >
                        ↑ Asc
                    </button>
                    <button
                        @click="sortOptions.direction = 'desc'"
                        class="btn btn-sm"
                        :class="{'btn-primary': sortOptions.direction === 'desc', 'btn-secondary': sortOptions.direction !== 'desc'}"
                    >
                        ↓ Desc
                    </button>
                </div>
             </div>
         </div>

        <!-- TODO: Implement drag functionality for these items -->
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
                        <button class="btn btn-sm btn-primary" @click.stop="scheduleSelectedSurgery(surgery)">
                          <span class="icon">📅</span> Schedule
                        </button>
                    </div>
                </li>
                <li v-if="filteredPendingSurgeries.length === 0" class="no-items">No pending surgeries matching filters.</li>
            </ul>
        </div>
      </aside>

      <!-- Main Panel: Master Schedule View (Gantt Chart) -->
      <main class="main-panel">
        <div class="schedule-header">
            <h2>Master Schedule View</h2>
            <div class="schedule-controls">
                <button @click="ganttNavigate('prev')" class="btn btn-sm btn-secondary">◀ Previous</button>
                <span class="current-date-range">{{ currentGanttViewDateRange }}</span>
                <button @click="ganttNavigate('next')" class="btn btn-sm btn-secondary">Next ▶</button>
                <button @click="ganttZoom('in')" class="btn btn-sm btn-secondary">Day View</button>
                <button @click="ganttZoom('out')" class="btn btn-sm btn-secondary">Week View</button>
                <button @click="showCreateNewSurgeryForm" class="btn btn-sm btn-primary">Create New Surgery</button>
            </div>
        </div>

        <!--
          Gantt Chart Integration Point
          This div will host the Gantt chart component.
          Consider creating a dedicated child component (e.g., <GanttChartComponent />)
          to encapsulate the Gantt library's logic and pass data via props.
        -->
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
            <!-- Actual Gantt Chart Component -->
            <GanttChart />

            <div class="gantt-drop-message">
              Drag pending surgeries here to schedule them.
            </div>
          </div>
        </div>

        <div class="gantt-info-panel">
            <p><strong>SDST (Setup, Disinfection, Sterilization Time):</strong> Not yet calculated. Will be factored into scheduling.</p>
            <p><strong>Resource Conflicts:</strong> Conflict detection pending Gantt integration.</p>
        </div>
      </main>

      <!-- Right Panel: Surgery Details / Create New -->
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
              <button type="button" v-if="selectedSurgerySource === 'pending' && formMode !== 'new'" @click="scheduleSelectedSurgery" class="btn btn-primary">Schedule This Surgery</button>
            </div>
          </form>
        </div>
        <div v-else>
          <h2>Surgery Details</h2>
          <p>Select a pending surgery to view its details, or drag it to the schedule. Click "Create New Surgery" to add a new entry.</p>

          <!-- Show form fields for reference/testing -->
          <div class="form-preview">
            <h3>Surgery Form Fields</h3>
            <div class="form-group">
              <label>Patient ID:</label>
              <input type="text" class="form-control" disabled placeholder="Enter Patient ID">
            </div>
            <div class="form-group">
              <label>Patient Name:</label>
              <input type="text" class="form-control" disabled placeholder="Enter Patient Name">
            </div>
            <div class="form-group">
              <label>Surgery Type:</label>
              <select class="form-control" disabled>
                <option>Select a surgery type</option>
              </select>
            </div>
            <div class="form-group">
              <label>Estimated Duration (min):</label>
              <input type="number" class="form-control" disabled placeholder="Enter duration">
            </div>
            <div class="form-group">
              <label>Priority Level:</label>
              <select class="form-control" disabled>
                <option>Select priority</option>
              </select>
            </div>
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
import GanttChart from './GanttChart.vue';
import ToastNotification from './ToastNotification.vue';
import KeyboardShortcutsHelp from './KeyboardShortcutsHelp.vue';
import keyboardShortcuts from '@/services/keyboardShortcuts';

// Initialize the stores
const scheduleStore = useScheduleStore();
const notificationStore = useNotificationStore();
const {
  pendingSurgeries: storePendingSurgeries,
  scheduledSurgeries: storeScheduledSurgeries,
  selectedSurgeryId,
  isLoading
} = storeToRefs(scheduleStore);

// Component refs
const toastRef = ref(null);
const keyboardShortcutsRef = ref(null);

// --- State ---
const selectedSurgery = ref(null);
const selectedSurgerySource = ref(''); // 'pending' or 'scheduled'
const formMode = ref('view'); // 'view', 'edit', 'new'
const formErrors = ref({}); // To store validation errors
const formSubmitted = ref(false); // To track if form was submitted (for validation display)

const filters = ref({
  priority: '',
  specialty: '',
  status: '',
  surgeon: '',
  equipment: '',
  dateRange: {
    start: null,
    end: null
  },
  showAdvancedFilters: false
});

// Sorting options for pending surgeries list
const sortOptions = ref({
  field: 'priority', // Default sort field
  direction: 'desc' // 'asc' or 'desc'
});

const currentScheduleDateRange = ref('Today'); // Placeholder for date range display
const isGanttInitialized = ref(false); // To track if the Gantt library is loaded

// --- Data for Gantt Chart (to be passed as props or managed by the Gantt library wrapper) ---
const ganttTasks = ref([]); // Holds tasks formatted for the Gantt library
const ganttResources = ref([]); // Holds resources (ORs, Surgeons, Staff, Equipment)

// --- Computed Properties ---
const filteredPendingSurgeries = computed(() => {
  if (!storePendingSurgeries.value) return []; // Ensure pendingSurgeries is not null or undefined

  // First filter the surgeries
  const filtered = storePendingSurgeries.value.filter(surgery => {
    // Basic filters
    const matchesPriority = !filters.value.priority || surgery.priority === filters.value.priority;
    const matchesSpecialty = !filters.value.specialty ||
      (surgery.fullType && surgery.fullType.toLowerCase().includes(filters.value.specialty.toLowerCase()));
    const matchesStatus = !filters.value.status || surgery.status === filters.value.status;

    // Advanced filters
    const matchesSurgeon = !filters.value.surgeon ||
      (surgery.requiredSurgeons &&
        (Array.isArray(surgery.requiredSurgeons)
          ? surgery.requiredSurgeons.some(s => s.toLowerCase().includes(filters.value.surgeon.toLowerCase()))
          : surgery.requiredSurgeons.toLowerCase().includes(filters.value.surgeon.toLowerCase())));

    const matchesEquipment = !filters.value.equipment ||
      (surgery.requiredEquipment &&
        (Array.isArray(surgery.requiredEquipment)
          ? surgery.requiredEquipment.some(e => e.toLowerCase().includes(filters.value.equipment.toLowerCase()))
          : surgery.requiredEquipment.toLowerCase().includes(filters.value.equipment.toLowerCase())));

    // Date range filter
    let matchesDateRange = true;
    if (filters.value.dateRange.start && filters.value.dateRange.end) {
      const requestedDate = surgery.requestedDate ? new Date(surgery.requestedDate) : null;
      if (requestedDate) {
        const startDate = new Date(filters.value.dateRange.start);
        const endDate = new Date(filters.value.dateRange.end);
        // Set time to 00:00:00 for start and 23:59:59 for end to include the entire day
        startDate.setHours(0, 0, 0, 0);
        endDate.setHours(23, 59, 59, 999);
        matchesDateRange = requestedDate >= startDate && requestedDate <= endDate;
      }
    }

    return matchesPriority && matchesSpecialty && matchesStatus &&
           matchesSurgeon && matchesEquipment && matchesDateRange;
  });

  // Then sort the filtered surgeries
  return sortSurgeries(filtered, sortOptions.value.field, sortOptions.value.direction);
});

// Helper function to sort surgeries
const sortSurgeries = (surgeries, field, direction) => {
  return [...surgeries].sort((a, b) => {
    let comparison = 0;

    // Handle different field types
    switch (field) {
      case 'priority':
        // Convert priority to numeric value for sorting
        const priorityValues = { 'High': 3, 'Medium': 2, 'Low': 1 };
        comparison = priorityValues[a.priority] - priorityValues[b.priority];
        break;
      case 'estimatedDuration':
        comparison = a.estimatedDuration - b.estimatedDuration;
        break;
      case 'patientName':
        comparison = (a.patientName || a.patientId).localeCompare(b.patientName || b.patientId);
        break;
      case 'type':
        comparison = a.type.localeCompare(b.type);
        break;
      default:
        comparison = 0;
    }

    // Apply sort direction
    return direction === 'asc' ? comparison : -comparison;
  });
};

// Format the current date range for display
const currentGanttViewDateRange = computed(() => {
  const { currentDateRange, ganttViewMode } = scheduleStore;

  if (ganttViewMode === 'Day') {
    return currentDateRange.start.toLocaleDateString(undefined, {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  } else if (ganttViewMode === 'Week') {
    return `${currentDateRange.start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} -
            ${currentDateRange.end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
  }

  return 'Today';
});

// --- Methods ---

// Initialize data from the store
const initializeData = () => {
  // Load data from the store
  if (!scheduleStore.dataInitialized) {
    scheduleStore.loadInitialData();
  }

  // Set isGanttInitialized to true since we're using the actual GanttChart component
  // For testing purposes, we'll keep it false initially to show the placeholder
  // isGanttInitialized.value = true;
};

// Helper to transform surgery data to Gantt task format (example)
const transformSurgeryToGanttTask = (surgery, scheduledTime) => {
  // This is highly dependent on the chosen Gantt library's expected format
  return {
    id: surgery.id,
    text: `${surgery.patientId} - ${surgery.type}`,
    startDate: scheduledTime, // Ensure this is a valid date/time format for the library
    duration: surgery.estimatedDuration,
    durationUnit: 'minute', // Or 'hour', 'day' depending on library
    priority: surgery.priority,
    status: surgery.status,
    // Add other relevant fields: resourceId (OR, surgeon), dependencies, color, etc.
    ...surgery // Spread other surgery details that might be useful
  };
};

// Helper to transform scheduled surgeries (if fetched separately) to Gantt tasks
const transformScheduledSurgeriesToGanttTasks = () => {
  ganttTasks.value = storeScheduledSurgeries.value.map(surgery => {
    // Assuming surgery objects in scheduledSurgeries have a 'scheduledTime' and 'id'
    return transformSurgeryToGanttTask(surgery, surgery.startTime);
  });
  // TODO: Notify Gantt chart to refresh/load new tasks
};

// Watch for changes in storeScheduledSurgeries to update Gantt tasks
// This is a basic example; a real Gantt integration might handle this internally or via its API
watch(storeScheduledSurgeries, (newScheduledList) => {
  // transformScheduledSurgeriesToGanttTasks();
  console.log('Scheduled surgeries updated, Gantt tasks should refresh:', newScheduledList);
}, { deep: true });

const applyFilters = () => {
  // The computed property `filteredPendingSurgeries` will update automatically.
  // This function is here if any imperative logic is needed on filter change.
  console.log('Filters applied:', filters.value);
};

// Reset all filters to their default values
const resetFilters = () => {
  filters.value = {
    priority: '',
    specialty: '',
    status: '',
    surgeon: '',
    equipment: '',
    dateRange: {
      start: null,
      end: null
    },
    showAdvancedFilters: filters.value.showAdvancedFilters // Keep the advanced filters visibility state
  };
  console.log('Filters reset');
};

const selectSurgeryForDetails = (surgery, source) => {
  selectedSurgery.value = { ...surgery }; // Clone to avoid direct mutation if editing
  selectedSurgerySource.value = source;
  formMode.value = 'view';
  console.log(`Viewing ${source} surgery:`, surgery.id);

  // Also update the store's selected surgery
  if (source === 'scheduled') {
    scheduleStore.selectSurgery(surgery.id);
  }
};

const showCreateNewSurgeryForm = () => {
  // Reset form state
  formSubmitted.value = false;
  formErrors.value = {};

  selectedSurgery.value = {
    patientId: '',
    patientName: '',
    type: '',
    fullType: '',
    estimatedDuration: 60,
    duration: 60,
    priority: 'Medium',
    status: 'Pending',
    requiredSurgeons: [],
    requiredStaffRoles: [],
    requiredEquipment: []
  };
  selectedSurgerySource.value = 'new';
  formMode.value = 'new';
  console.log('Showing form to create new surgery');
};

// Validate the surgery form
const validateSurgeryForm = () => {
  formSubmitted.value = true;
  const errors = {};
  const surgery = selectedSurgery.value;

  // Required fields validation
  if (!surgery.patientId?.trim()) {
    errors.patientId = 'Patient ID is required';
  }

  if (!surgery.patientName?.trim()) {
    errors.patientName = 'Patient Name is required';
  }

  if (!surgery.type?.trim()) {
    errors.type = 'Surgery Type is required';
  }

  if (!surgery.fullType?.trim()) {
    errors.fullType = 'Full Type is required';
  }

  // Numeric validation
  if (!surgery.estimatedDuration || surgery.estimatedDuration <= 0) {
    errors.estimatedDuration = 'Duration must be greater than 0';
  }

  // Array fields validation (convert string to array if needed)
  if (typeof surgery.requiredSurgeons === 'string') {
    surgery.requiredSurgeons = surgery.requiredSurgeons.split(',').map(s => s.trim()).filter(Boolean);
  }

  if (typeof surgery.requiredStaffRoles === 'string') {
    surgery.requiredStaffRoles = surgery.requiredStaffRoles.split(',').map(s => s.trim()).filter(Boolean);
  }

  if (typeof surgery.requiredEquipment === 'string') {
    surgery.requiredEquipment = surgery.requiredEquipment.split(',').map(s => s.trim()).filter(Boolean);
  }

  formErrors.value = errors;
  return Object.keys(errors).length === 0;
};

const saveSurgeryDetails = async () => {
  if (!selectedSurgery.value) return;

  // Validate the form
  if (!validateSurgeryForm()) {
    console.error('Form validation failed:', formErrors.value);
    notificationStore.error('Please fix the validation errors before saving.');
    return;
  }

  console.log('Saving surgery details:', selectedSurgery.value);

  try {
    if (formMode.value === 'new') {
      // Add to pending list
      await scheduleStore.addPendingSurgery(selectedSurgery.value);
      notificationStore.success('New surgery added to pending list.', {
        title: 'Surgery Added',
        action: {
          label: 'Schedule Now',
          callback: () => scheduleSelectedSurgery(selectedSurgery.value)
        }
      });
    } else if (selectedSurgerySource.value === 'pending') {
      // Update pending surgery
      await scheduleStore.updatePendingSurgery(selectedSurgery.value);
      notificationStore.success('Pending surgery details updated.', {
        title: 'Surgery Updated'
      });
    } else if (selectedSurgerySource.value === 'scheduled') {
      // Update scheduled surgery
      await scheduleStore.updateScheduledSurgery(selectedSurgery.value);
      notificationStore.success('Scheduled surgery details updated.', {
        title: 'Surgery Updated'
      });
    }

    // Reset form state
    formMode.value = 'view';
    formSubmitted.value = false;
    formErrors.value = {};
  } catch (error) {
    console.error(`Error saving surgery: ${error.message}`);
    formErrors.value.general = `Error saving surgery: ${error.message}`;
    notificationStore.error(`Error saving surgery: ${error.message}`, {
      title: 'Save Failed'
    });
  }
};

// Helper to update the full type based on the selected surgery type
const updateFullType = () => {
  if (!selectedSurgery.value) return;

  const typeMap = {
    'CABG': 'Coronary Artery Bypass Graft',
    'KNEE': 'Total Knee Replacement',
    'APPEN': 'Appendectomy',
    'HERNI': 'Hernia Repair',
    'CATAR': 'Cataract Surgery',
    'HIPRE': 'Total Hip Replacement'
  };

  if (selectedSurgery.value.type && typeMap[selectedSurgery.value.type]) {
    selectedSurgery.value.fullType = typeMap[selectedSurgery.value.type];
  }
};

const clearSelectionOrCancel = () => {
  selectedSurgery.value = null;
  selectedSurgerySource.value = '';
  formMode.value = 'view';
  formSubmitted.value = false;
  formErrors.value = {};

  // Clear the store's selected surgery
  scheduleStore.clearSelectedSurgery();

  console.log('Selection cleared or form cancelled');
};

const scheduleSelectedSurgery = async () => {
  if (!selectedSurgery.value || selectedSurgerySource.value !== 'pending') return;

  try {
    // Schedule the surgery using the store
    const scheduledSurgery = await scheduleStore.schedulePendingSurgery(
      selectedSurgery.value.id,
      'OR1', // Default OR - in a real app, this would be selected by the user
      new Date() // Default time - in a real app, this would be selected by the user
    );

    notificationStore.success(`Surgery ${selectedSurgery.value.patientName || selectedSurgery.value.patientId} scheduled.`, {
      title: 'Surgery Scheduled',
      action: {
        label: 'View Schedule',
        callback: () => {
          // Scroll to the Gantt chart
          document.getElementById('gantt-chart-container')?.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });

    // View the newly scheduled surgery
    if (scheduledSurgery) {
      selectSurgeryForDetails(scheduledSurgery, 'scheduled');
    } else {
      clearSelectionOrCancel();
    }
  } catch (error) {
    notificationStore.error(`Error scheduling surgery: ${error.message}`, {
      title: 'Scheduling Failed'
    });
  }
};

// --- Drag and Drop Handlers ---
const draggedSurgery = ref(null);
const dragGhost = ref(null);
const dropTarget = ref({
  orId: null,
  time: null,
  isValid: true,
  message: ''
});

const handleDragStart = (surgery, event) => {
  console.log('Dragging surgery:', surgery.id);

  // Store the dragged surgery for reference
  draggedSurgery.value = surgery;

  // Set data for drop handling
  event.dataTransfer.setData('application/json', JSON.stringify(surgery));
  event.dataTransfer.effectAllowed = 'move';

  // Add visual feedback for dragging
  event.target.classList.add('dragging');

  // Create a custom drag image/ghost element
  const ghostElement = document.createElement('div');
  ghostElement.classList.add('surgery-drag-ghost');
  ghostElement.innerHTML = `
    <div class="ghost-priority ${surgery.priority.toLowerCase()}"></div>
    <div class="ghost-content">
      <div class="ghost-title">${surgery.patientName || surgery.patientId}</div>
      <div class="ghost-type">${surgery.type} - ${surgery.estimatedDuration} min</div>
    </div>
  `;

  // Add the ghost element to the document temporarily
  document.body.appendChild(ghostElement);
  dragGhost.value = ghostElement;

  // Set the custom drag image
  event.dataTransfer.setDragImage(ghostElement, 20, 20);

  // Hide the ghost element (it will still be used as drag image)
  setTimeout(() => {
    ghostElement.style.position = 'absolute';
    ghostElement.style.left = '-9999px';
  }, 0);
};

const handleDragEnd = (event) => {
  // Remove the dragging class
  event.target.classList.remove('dragging');

  // Clean up the ghost element
  if (dragGhost.value && dragGhost.value.parentNode) {
    dragGhost.value.parentNode.removeChild(dragGhost.value);
    dragGhost.value = null;
  }

  // Reset the dragged surgery
  draggedSurgery.value = null;

  // Reset drop target
  dropTarget.value = {
    orId: null,
    time: null,
    isValid: true,
    message: ''
  };
};

const handleDragOver = (event, orId) => {
  event.preventDefault();

  if (!draggedSurgery.value) return;

  // Calculate the time based on the mouse position
  // This is a simplified example - in a real app, you would calculate the exact time
  // based on the Gantt chart's time scale and the mouse position
  const rect = event.currentTarget.getBoundingClientRect();
  const relativeX = event.clientX - rect.left;
  const percentageX = relativeX / rect.width;

  // Get the current date range from the store
  const { start, end } = scheduleStore.currentDateRange;
  const totalMinutes = (end.getTime() - start.getTime()) / (60 * 1000);
  const minutesFromStart = totalMinutes * percentageX;

  // Calculate the target time
  const targetTime = new Date(start.getTime() + minutesFromStart * 60 * 1000);

  // Round to nearest 15 minutes for better UX
  const roundedMinutes = Math.round(targetTime.getMinutes() / 15) * 15;
  targetTime.setMinutes(roundedMinutes);
  targetTime.setSeconds(0);
  targetTime.setMilliseconds(0);

  // Update the drop target
  dropTarget.value = {
    orId,
    time: targetTime,
    isValid: true, // In a real app, you would check for conflicts here
    message: `Schedule in ${orId} at ${targetTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  };

  // Check for conflicts (simplified example)
  const conflictingSurgeries = scheduleStore.scheduledSurgeries.filter(s => {
    if (s.orId !== orId) return false;

    const surgeryStart = new Date(s.startTime);
    const surgeryEnd = new Date(s.endTime);
    const newSurgeryStart = targetTime;
    const newSurgeryEnd = new Date(targetTime.getTime() + draggedSurgery.value.estimatedDuration * 60 * 1000);

    return (newSurgeryStart < surgeryEnd && newSurgeryEnd > surgeryStart);
  });

  if (conflictingSurgeries.length > 0) {
    dropTarget.value.isValid = false;
    dropTarget.value.message = `Conflict with ${conflictingSurgeries[0].patientName}'s surgery`;
  }
};

const handleDropOnGantt = (event) => {
  event.preventDefault();
  const surgeryDataString = event.dataTransfer.getData('application/json');
  if (!surgeryDataString) return;

  const droppedSurgery = JSON.parse(surgeryDataString);
  console.log('Dropped pending surgery on Gantt chart:', droppedSurgery.id);

  // Check if we have a valid drop target
  if (!dropTarget.value.orId || !dropTarget.value.time) {
    console.warn('No valid drop target');
    return;
  }

  // Check if the drop target is valid (no conflicts)
  if (!dropTarget.value.isValid) {
    notificationStore.warning(`Cannot schedule surgery: ${dropTarget.value.message}`, {
      title: 'Scheduling Conflict'
    });
    return;
  }

  // Schedule the surgery using the store with the calculated OR and time
  scheduleStore.schedulePendingSurgery(
    droppedSurgery.id,
    dropTarget.value.orId,
    dropTarget.value.time
  ).then(scheduledSurgery => {
    if (scheduledSurgery) {
      const scheduledTime = dropTarget.value.time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      notificationStore.success(
        `Surgery ${droppedSurgery.patientName || droppedSurgery.patientId} scheduled in ${dropTarget.value.orId} at ${scheduledTime}`,
        {
          title: 'Surgery Scheduled',
          duration: 3000
        }
      );
      selectSurgeryForDetails(scheduledSurgery, 'scheduled');
    }
  }).catch(error => {
    notificationStore.error(`Error scheduling surgery: ${error.message}`, {
      title: 'Scheduling Failed'
    });
  });

  // Reset the drop target
  dropTarget.value = {
    orId: null,
    time: null,
    isValid: true,
    message: ''
  };
};

// Gantt Chart Navigation and Controls
const ganttNavigate = (direction) => {
  scheduleStore.navigateGanttDate(direction);
};

const ganttZoom = (level) => {
  // Adjust the zoom level
  if (level === 'in') {
    // Switch to day view
    scheduleStore.updateGanttViewMode('Day');
  } else if (level === 'out') {
    // Switch to week view
    scheduleStore.updateGanttViewMode('Week');
  }
};

// Initialize data on component mount
onMounted(() => {
  initializeData();

  // Set up the toast notification ref
  nextTick(() => {
    if (toastRef.value) {
      notificationStore.setToastRef(toastRef.value);
    }
  });

  // Register keyboard shortcuts
  registerKeyboardShortcuts();

  // Watch for changes in the store's selected surgery
  watch(() => selectedSurgeryId.value, (newId) => {
    if (newId) {
      // Find the surgery in the scheduled surgeries
      const surgery = storeScheduledSurgeries.value.find(s => s.id === newId);
      if (surgery) {
        selectSurgeryForDetails(surgery, 'scheduled');
      }
    }
  });
});

// Register keyboard shortcuts for the scheduling screen
const registerKeyboardShortcuts = () => {
  // Create new surgery (N)
  keyboardShortcuts.register('n', () => {
    showCreateNewSurgeryForm();
  }, {
    description: 'Create new surgery',
    scope: 'scheduling'
  });

  // Save surgery details (Ctrl+S)
  keyboardShortcuts.register('s', () => {
    if (selectedSurgery.value && formMode.value !== 'view') {
      saveSurgeryDetails();
    }
  }, {
    ctrlKey: true,
    description: 'Save surgery details',
    scope: 'scheduling'
  });

  // Cancel/close form (Escape)
  keyboardShortcuts.register('escape', () => {
    if (selectedSurgery.value) {
      clearSelectionOrCancel();
    }
  }, {
    description: 'Cancel/close form',
    scope: 'scheduling'
  });

  // Schedule selected surgery (Ctrl+Enter)
  keyboardShortcuts.register('enter', () => {
    if (selectedSurgery.value && selectedSurgerySource.value === 'pending') {
      scheduleSelectedSurgery();
    }
  }, {
    ctrlKey: true,
    description: 'Schedule selected surgery',
    scope: 'scheduling'
  });

  // Navigate Gantt chart (Arrow keys)
  keyboardShortcuts.register('arrowleft', () => {
    ganttNavigate('prev');
  }, {
    description: 'Previous day/week in schedule',
    scope: 'scheduling'
  });

  keyboardShortcuts.register('arrowright', () => {
    ganttNavigate('next');
  }, {
    description: 'Next day/week in schedule',
    scope: 'scheduling'
  });

  // Toggle advanced filters (F)
  keyboardShortcuts.register('f', () => {
    filters.value.showAdvancedFilters = !filters.value.showAdvancedFilters;
  }, {
    description: 'Toggle advanced filters',
    scope: 'scheduling'
  });

  // Show keyboard shortcuts help (?)
  keyboardShortcuts.register('?', () => {
    keyboardShortcutsRef.value?.toggle();
  }, {
    description: 'Show keyboard shortcuts help',
    scope: 'scheduling'
  });
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
    color: var(--text-color-secondary);
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
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.schedule-controls button:hover {
  background-color: var(--primary-color-dark);
}

.schedule-controls span {
    margin: 0 10px;
    font-weight: bold;
}

.gantt-chart-placeholder {
  flex-grow: 1;
  border: 2px dashed var(--border-color);
  display: flex;
  flex-direction: column; /* To stack p and ul */
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-color-secondary);
  border-radius: 4px;
  background-color: var(--background-color-light);
  min-height: 300px; /* Ensure it has some height */
  overflow-y: auto; /* If debug list gets long */
}

.gantt-chart-container {
  position: relative;
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

.scheduled-surgery-list-debug {
    list-style: none;
    padding: 0;
    margin-top: 10px;
    font-size: 0.9em;
}
.scheduled-surgery-list-debug li {
    padding: 5px;
    border-bottom: 1px solid var(--border-color-light);
    cursor: pointer;
}
.scheduled-surgery-list-debug li:hover {
    background-color: var(--hover-color);
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
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb, 0, 120, 212), 0.25);
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
  background-color: rgba(var(--color-error-rgb, 255, 0, 0), 0.1);
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
  flex-wrap: wrap; /* Allow buttons to wrap on smaller screens */
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

</style>