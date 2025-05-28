<template>
  <div class="gantt-container">
    <div class="gantt-header">
      <div class="gantt-title">
        <h3>Operating Room Schedule</h3>
        <span class="view-mode-indicator">{{ scheduleStore.ganttViewMode }} View</span>
      </div>
      <div class="view-controls">
        <div class="date-navigation">
          <button class="btn btn-icon" @click="navigateDateRange('prev')" aria-label="Previous day">
            <span aria-hidden="true">◀</span>
          </button>
          <span class="current-date-display">{{ formattedDateRange }}</span>
          <button class="btn btn-icon" @click="navigateDateRange('next')" aria-label="Next day">
            <span aria-hidden="true">▶</span>
          </button>
        </div>
        <div class="view-mode-buttons">
          <button
            class="btn"
            :class="{'btn-primary': scheduleStore.ganttViewMode === 'Day', 'btn-secondary': scheduleStore.ganttViewMode !== 'Day'}"
            @click="changeViewMode('Day')">
            Day
          </button>
          <button
            class="btn"
            :class="{'btn-primary': scheduleStore.ganttViewMode === 'Week', 'btn-secondary': scheduleStore.ganttViewMode !== 'Week'}"
            @click="changeViewMode('Week')">
            Week
          </button>
          <button class="btn btn-secondary" @click="resetToToday()">Today</button>
        </div>
      </div>
    </div>

    <!-- SDST Legend -->
    <div class="sdst-legend">
      <div class="legend-title">SDST Color Coding:</div>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-color sdst-low"></div>
          <div class="legend-label">Short (≤15 min)</div>
        </div>
        <div class="legend-item">
          <div class="legend-color sdst-medium"></div>
          <div class="legend-label">Medium (16-30 min)</div>
        </div>
        <div class="legend-item">
          <div class="legend-color sdst-high"></div>
          <div class="legend-label">Long (>30 min)</div>
        </div>
        <div class="legend-item">
          <div class="legend-icon">→</div>
          <div class="legend-label">Surgery Type Transition</div>
        </div>
      </div>
    </div>

    <div class="gantt-grid" ref="ganttGrid">
      <div class="gantt-time-axis">
        <!-- Hourly markers (adjust based on view mode) -->
        <div
          v-for="hour in hours"
          :key="hour"
          class="time-marker"
          :style="getTimeMarkerStyle(hour)"
        >
          {{ formatHourMarker(hour) }}
        </div>
      </div>
      <div class="gantt-or-rows">
        <div
          v-for="or in availableOperatingRooms"
          :key="or.id"
          class="gantt-or-row"
          :class="{'drop-target': currentDropTarget === or.id}"
          @dragover.prevent="onDragOver($event, or.id)"
          @dragenter.prevent="onDragEnter($event, or.id)"
          @dragleave="onDragLeave($event, or.id)"
          @drop="onDrop($event, or.id)"
          :aria-label="`Operating Room: ${or.name}`"
        >
          <div class="or-label">{{ or.name }}</div>
          <div class="or-timeline">
            <!-- Surgery blocks positioned here -->
            <div
              v-for="surgery in getSurgeriesForOR(or.id)"
              :key="surgery.id"
              :style="getSurgeryBlockStyle(surgery)"
              :class="{
                'surgery-block': true,
                'has-conflict': surgery.conflicts && surgery.conflicts.length > 0,
                'is-selected': isSelected(surgery),
                'is-dragging': isDragging(surgery)
              }"
              @mouseover="showTooltip($event, surgery)"
              @mouseleave="hideTooltip"
              @click="selectSurgery(surgery)"
              draggable="true"
              @dragstart="onDragStart($event, surgery)"
              @dragend="onDragEnd"
              :aria-label="getSurgeryAccessibleLabel(surgery)"
              :aria-invalid="surgery.conflicts && surgery.conflicts.length > 0 ? 'true' : null"
              tabindex="0"
            >
              <div
                v-if="surgery.sdsTime > 0"
                class="sdst-segment"
                :class="{
                  'sdst-low': surgery.sdsTime <= 15,
                  'sdst-medium': surgery.sdsTime > 15 && surgery.sdsTime <= 30,
                  'sdst-high': surgery.sdsTime > 30
                }"
                :style="getSDSTSegmentStyle(surgery)"
              >
                <span class="sdst-label" v-if="surgery.sdsTime >= 10 && pixelsPerMinute.value > 1">
                  {{ surgery.sdsTime }}m
                </span>
                <div class="sdst-transition-icon" :title="`${surgery.precedingType || 'Initial'} → ${surgery.type}`">
                  →
                </div>
              </div>
              <div class="surgery-info">
                {{ surgery.patientName }} - {{ surgery.type }}
              </div>
              <!-- Conflict Indicator Icon (WCAG 1.4.1 - not relying on color alone) -->
              <span v-if="surgery.conflicts && surgery.conflicts.length > 0" class="conflict-indicator" aria-hidden="true">⚠️</span>
            </div>

            <!-- Current time indicator (vertical line) -->
            <div v-if="isCurrentTimeVisible" class="current-time-indicator" :style="currentTimeIndicatorStyle"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced tooltip component -->
    <div v-if="tooltip.visible" class="surgery-tooltip" :style="tooltip.style" role="tooltip">
      <div class="tooltip-header">
        <strong>{{ tooltip.surgery?.patientName }}</strong>
      </div>
      <div class="tooltip-body">
        <p><strong>Type:</strong> {{ tooltip.surgery?.fullType }}</p>
        <p><strong>Surgeon:</strong> {{ tooltip.surgery?.surgeon }}</p>
        <p><strong>Time:</strong> {{ formatTime(tooltip.surgery?.startTime) }} - {{ formatTime(tooltip.surgery?.endTime) }}</p>
        <p><strong>Duration:</strong> {{ tooltip.surgery?.duration }} min</p>
        <div class="tooltip-sdst-section">
          <p><strong>SDST:</strong> {{ tooltip.surgery?.sdsTime }} min</p>
          <div class="tooltip-sdst-detail">
            <div class="sdst-transition">
              <span class="sdst-from">{{ tooltip.surgery?.precedingType || 'Initial' }}</span>
              <span class="sdst-arrow">→</span>
              <span class="sdst-to">{{ tooltip.surgery?.type }}</span>
            </div>
            <div
              class="sdst-indicator"
              :class="{
                'sdst-low': tooltip.surgery?.sdsTime <= 15,
                'sdst-medium': tooltip.surgery?.sdsTime > 15 && tooltip.surgery?.sdsTime <= 30,
                'sdst-high': tooltip.surgery?.sdsTime > 30
              }"
            ></div>
            <div class="sdst-explanation">
              {{ getSDSTExplanation(tooltip.surgery) }}
            </div>
          </div>
        </div>
        <div v-if="tooltip.surgery?.conflicts && tooltip.surgery.conflicts.length > 0" class="tooltip-conflicts">
          <strong>Conflicts:</strong>
          <ul>
            <li v-for="(c, idx) in tooltip.surgery.conflicts" :key="idx">{{ c }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Accessible Table View (Visually Hidden) -->
    <GanttAccessibleTable />

    <!-- Loading Indicator -->
    <div v-if="scheduleStore.isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>Loading Schedule...</span>
    </div>

    <!-- Ghost element for drag preview -->
    <div v-if="dragGhost.visible" class="drag-ghost" :style="dragGhost.style">
      <div class="sdst-segment" :style="dragGhost.sdstStyle"></div>
      <div class="ghost-info">{{ dragGhost.text }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';
import GanttAccessibleTable from './GanttAccessibleTable.vue';

const scheduleStore = useScheduleStore();
// Use storeToRefs to get reactive state and getters from the store
const {
  visibleScheduledSurgeries,
  availableOperatingRooms,
  currentDateRange,
  isLoading,
  selectedSurgeryId
} = storeToRefs(scheduleStore);

// Tooltip state
const tooltip = ref({
  visible: false,
  surgery: null,
  style: {}
});

// Drag ghost element state
const dragGhost = ref({
  visible: false,
  style: {},
  sdstStyle: {},
  text: ''
});

// Track current drop target for visual feedback
const currentDropTarget = ref(null);

// Current time indicator
const isCurrentTimeVisible = computed(() => {
  if (!currentDateRange || !currentDateRange.start || !currentDateRange.end) {
    return false;
  }
  const now = new Date();
  return now >= currentDateRange.start && now <= currentDateRange.end;
});

const currentTimeIndicatorStyle = computed(() => {
  if (!isCurrentTimeVisible.value || !currentDateRange || !currentDateRange.start) return {};

  const now = new Date();
  const minutesFromViewStart = (now.getTime() - currentDateRange.start.getTime()) / (1000 * 60);
  const leftPosition = minutesFromViewStart * pixelsPerMinute.value;

  return {
    left: `${leftPosition}px`
  };
});

// Format the date range for display
const formattedDateRange = computed(() => {
  if (!currentDateRange || !currentDateRange.start || !currentDateRange.end) {
    return 'Loading...';
  }

  const start = currentDateRange.start;
  const end = currentDateRange.end;

  if (scheduleStore.ganttViewMode === 'Day') {
    return start.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  } else if (scheduleStore.ganttViewMode === 'Week') {
    return `${start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
  }
  return '';
});

// Computed property for generating hourly time markers based on current view range
const hours = computed(() => {
  if (!currentDateRange || !currentDateRange.start || !currentDateRange.end) {
    return [];
  }

  const start = currentDateRange.start;
  const end = currentDateRange.end;

  if (scheduleStore.ganttViewMode === 'Day') {
    // For day view, show hours from 7:00 to 19:00 (7am to 7pm)
    const hoursArray = [];
    const startHour = 7; // 7am
    const endHour = 19; // 7pm

    for (let h = startHour; h <= endHour; h++) {
      hoursArray.push(h);
    }
    return hoursArray;
  } else if (scheduleStore.ganttViewMode === 'Week') {
    // For week view, show days of the week with key hours
    const daysArray = [];
    const dayCount = 7; // 7 days in a week
    const startDate = new Date(start);

    for (let d = 0; d < dayCount; d++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + d);
      daysArray.push(currentDate);
    }
    return daysArray;
  }

  return [];
});

// Format hour markers based on view mode
const formatHourMarker = (hour) => {
  if (scheduleStore.ganttViewMode === 'Day') {
    // Format as 24-hour time for day view
    return `${String(hour).padStart(2, '0')}:00`;
  } else if (scheduleStore.ganttViewMode === 'Week') {
    // Format as day name for week view
    return hour.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' });
  }
  return '';
};

// Calculate time marker positioning
const getTimeMarkerStyle = (hour) => {
  if (!currentDateRange || !currentDateRange.start) {
    return { left: '0px', width: '100px' };
  }

  if (scheduleStore.ganttViewMode === 'Day') {
    // For day view, position based on hour
    const viewStartHour = currentDateRange.start.getHours();
    const hourOffset = hour - viewStartHour;
    const leftPosition = hourOffset * 60 * pixelsPerMinute.value; // 60 minutes per hour

    return {
      left: `${leftPosition}px`,
      width: `${60 * pixelsPerMinute.value}px`, // Width of one hour
      minWidth: '60px'
    };
  } else if (scheduleStore.ganttViewMode === 'Week') {
    // For week view, position based on day
    const daysDiff = Math.floor((hour.getTime() - currentDateRange.start.getTime()) / (1000 * 60 * 60 * 24));
    const leftPosition = daysDiff * 24 * 60 * pixelsPerMinute.value; // 24 hours per day

    return {
      left: `${leftPosition}px`,
      width: `${24 * 60 * pixelsPerMinute.value}px`, // Width of one day
      minWidth: '100px'
    };
  }

  return { left: '0px', width: '100px' };
};

// Get surgeries for a specific OR within the current view, sorted by time
const getSurgeriesForOR = (orId) => {
  return scheduleStore.getSurgeriesForOR(orId);
};

// Define a scale (pixels per minute) for the Gantt chart based on the view mode
const pixelsPerMinute = computed(() => {
  if (scheduleStore.ganttViewMode === 'Day') {
    return 2; // 2px per minute = 120px per hour
  } else if (scheduleStore.ganttViewMode === 'Week') {
    return 0.3; // 0.3px per minute = 18px per hour, 432px per day
  }
  return 1; // Default fallback
});

// Calculate surgery block position and size
const getSurgeryBlockStyle = (surgery) => {
  if (!currentDateRange || !currentDateRange.start || !surgery) {
    return {
      left: '0px',
      width: '100px',
      backgroundColor: 'var(--color-primary)',
    };
  }

  const startTime = new Date(surgery.startTime);
  const endTime = new Date(surgery.endTime);
  const durationWithSDST = (endTime.getTime() - startTime.getTime()) / (1000 * 60);

  const viewStartTime = currentDateRange.start;
  const startMinutesFromViewStart = (startTime.getTime() - viewStartTime.getTime()) / (1000 * 60);

  const leftPosition = startMinutesFromViewStart * pixelsPerMinute.value;
  const width = durationWithSDST * pixelsPerMinute.value;

  // Get surgery type color from CSS variables
  const surgeryTypeColorVar = `--color-surgery-${surgery.type?.toLowerCase() || 'default'}`;
  const element = document.documentElement;
  const surgeryColor = getComputedStyle(element).getPropertyValue(surgeryTypeColorVar).trim() || 'var(--color-primary)';

  return {
    left: `${leftPosition}px`,
    width: `${width}px`,
    backgroundColor: surgeryColor,
  };
};

// Calculate SDST segment style with color coding based on duration
const getSDSTSegmentStyle = (surgery) => {
  if (!surgery || surgery.sdsTime === undefined || surgery.sdsTime === null) {
    return {
      width: '0px',
      backgroundColor: 'transparent',
      borderRight: 'none',
      flexShrink: 0,
      position: 'relative',
    };
  }

  const sdstWidth = surgery.sdsTime * pixelsPerMinute.value;

  // Color coding based on SDST duration
  let backgroundColor = 'var(--color-sdst-low, rgba(40, 167, 69, 0.4))'; // Default: green for short setup
  let borderColor = 'var(--color-sdst-low-border, rgba(40, 167, 69, 0.8))';

  if (surgery.sdsTime > 30) {
    // Red for long setup times
    backgroundColor = 'var(--color-sdst-high, rgba(220, 53, 69, 0.4))';
    borderColor = 'var(--color-sdst-high-border, rgba(220, 53, 69, 0.8))';
  } else if (surgery.sdsTime > 15) {
    // Yellow for medium setup times
    backgroundColor = 'var(--color-sdst-medium, rgba(255, 193, 7, 0.4))';
    borderColor = 'var(--color-sdst-medium-border, rgba(255, 193, 7, 0.8))';
  }

  return {
    width: `${sdstWidth}px`,
    backgroundColor: backgroundColor,
    borderRight: `2px dashed ${borderColor}`,
    flexShrink: 0,
    position: 'relative',
  };
};

// Check if a surgery is currently selected
const isSelected = (surgery) => {
  return surgery.id === selectedSurgeryId.value;
};

// Check if a surgery is currently being dragged
const isDragging = (surgery) => {
  return surgery.id === draggedSurgeryId.value;
};

// Interaction Logic
const selectSurgery = (surgery) => {
  scheduleStore.selectSurgery(surgery.id);
};

// Show tooltip with surgery details
const showTooltip = (event, surgery) => {
  tooltip.value.surgery = surgery;
  tooltip.value.visible = true;

  // Position tooltip near the element
  const rect = event.target.getBoundingClientRect();

  // Calculate position to avoid going off-screen
  const viewportWidth = window.innerWidth;
  let left = rect.left + rect.width / 2;

  // Adjust if tooltip would go off right edge
  const tooltipWidth = 300; // Approximate width
  if (left + tooltipWidth / 2 > viewportWidth) {
    left = viewportWidth - tooltipWidth / 2 - 10;
  }

  // Adjust if tooltip would go off left edge
  if (left - tooltipWidth / 2 < 0) {
    left = tooltipWidth / 2 + 10;
  }

  tooltip.value.style = {
    top: `${rect.bottom + 10}px`,
    left: `${left}px`,
    transform: 'translateX(-50%)',
  };
};

const hideTooltip = () => {
  tooltip.value.visible = false;
};

// Format time for display
const formatTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Get SDST explanation for tooltip
const getSDSTExplanation = (surgery) => {
  if (!surgery || !surgery.sdsTime) return 'No setup time required';

  const precedingType = surgery.precedingType || 'Initial';
  const currentType = surgery.type;

  if (precedingType === 'Initial') {
    return `Initial setup for ${currentType} surgery`;
  } else {
    return `Transition from ${precedingType} to ${currentType} surgery`;
  }
};

// Get accessible label for surgery blocks
const getSurgeryAccessibleLabel = (surgery) => {
  const conflicts = surgery.conflicts && surgery.conflicts.length > 0
    ? ` Warning: ${surgery.conflicts.length} conflict(s)`
    : '';

  return `Surgery: ${surgery.patientName}, Type: ${surgery.fullType}, Time: ${formatTime(surgery.startTime)} to ${formatTime(surgery.endTime)}, SDST: ${surgery.sdsTime} minutes${conflicts}`;
};

// Real-time SDST calculation and conflict detection using store method
const calculateSDSTAndConflicts = (surgery, targetORId, proposedStartTime) => {
  return scheduleStore.calculateSDSTForPosition(surgery, targetORId, proposedStartTime);
};

// Navigation and view controls
const navigateDateRange = (direction) => {
  scheduleStore.navigateGanttDate(direction);
};

const changeViewMode = (mode) => {
  scheduleStore.updateGanttViewMode(mode);
};

const resetToToday = () => {
  scheduleStore.resetGanttToToday();
};

// Drag and Drop Logic
let draggedSurgeryId = ref(null);

const onDragStart = (event, surgery) => {
  draggedSurgeryId.value = surgery.id;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', surgery.id);

  // Create custom drag image
  dragGhost.value = {
    visible: true,
    text: `${surgery.patientName} - ${surgery.type}`,
    style: {
      width: `${surgery.duration * pixelsPerMinute.value}px`,
      backgroundColor: getSurgeryBlockStyle(surgery).backgroundColor,
    },
    sdstStyle: getSDSTSegmentStyle(surgery)
  };
};

const onDragEnd = () => {
  draggedSurgeryId.value = null;
  dragGhost.value.visible = false;
  currentDropTarget.value = null;
};

const onDragOver = (event, orId) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'move';

  // Update ghost position and calculate real-time SDST during drag
  if (dragGhost.value.visible) {
    const ganttTimeline = event.target.closest('.or-timeline');
    if (ganttTimeline) {
      const timelineRect = ganttTimeline.getBoundingClientRect();
      const clickX = event.clientX - timelineRect.left;

      // Calculate proposed time based on cursor position
      const minutesFromViewStart = clickX / pixelsPerMinute.value;
      const proposedStartTime = new Date(currentDateRange.start.getTime() + minutesFromViewStart * 60 * 1000);

      // Get the dragged surgery data
      const draggedSurgeryId = event.dataTransfer.getData('text/plain');
      const draggedSurgery = scheduleStore.scheduledSurgeries.find(s => s.id === draggedSurgeryId) ||
                            scheduleStore.pendingSurgeries.find(s => s.id === draggedSurgeryId);

      if (draggedSurgery) {
        // Calculate SDST for this position
        const { sdsTime, conflicts } = calculateSDSTAndConflicts(draggedSurgery, orId, proposedStartTime);

        // Update ghost with real-time feedback
        dragGhost.value.sdstStyle = {
          width: `${sdsTime * pixelsPerMinute.value}px`,
          backgroundColor: sdsTime <= 15 ? 'var(--color-sdst-low, rgba(40, 167, 69, 0.4))' :
                          sdsTime <= 30 ? 'var(--color-sdst-medium, rgba(255, 193, 7, 0.4))' :
                          'var(--color-sdst-high, rgba(220, 53, 69, 0.4))'
        };

        // Update text with conflict information
        const conflictText = conflicts.length > 0 ? ` (${conflicts.length} conflicts)` : '';
        dragGhost.value.text = `${draggedSurgery.patientName} - ${draggedSurgery.type} | SDST: ${sdsTime}min${conflictText}`;
      }
    }
  }
};

const onDragEnter = (event, orId) => {
  event.preventDefault();
  currentDropTarget.value = orId;
};

const onDragLeave = (event, orId) => {
  if (currentDropTarget.value === orId) {
    currentDropTarget.value = null;
  }
};

const onDrop = (event, targetORId) => {
  event.preventDefault();
  currentDropTarget.value = null;

  const surgeryId = event.dataTransfer.getData('text/plain');
  if (!surgeryId || !currentDateRange || !currentDateRange.start) return;

  // Calculate drop time
  const ganttTimeline = event.target.closest('.or-timeline');
  if (!ganttTimeline) return;

  const timelineRect = ganttTimeline.getBoundingClientRect();
  const clickX = event.clientX - timelineRect.left;
  const scrollX = ganttTimeline.parentElement.parentElement.scrollLeft || 0;
  const totalX = clickX + scrollX;

  const minutesFromViewStart = totalX / pixelsPerMinute.value;
  const newStartTime = new Date(currentDateRange.start.getTime() + minutesFromViewStart * 60 * 1000);

  // Snap to 15-minute intervals
  const minutes = newStartTime.getMinutes();
  newStartTime.setMinutes(Math.round(minutes / 15) * 15, 0, 0);

  // Get the surgery being dropped
  const surgery = scheduleStore.scheduledSurgeries.find(s => s.id === surgeryId) ||
                 scheduleStore.pendingSurgeries.find(s => s.id === surgeryId);

  if (surgery) {
    // Perform final conflict check before dropping
    const { sdsTime, conflicts } = calculateSDSTAndConflicts(surgery, targetORId, newStartTime);

    // Show conflicts to user if any exist
    if (conflicts.length > 0) {
      const confirmDrop = confirm(
        `Warning: This placement has ${conflicts.length} conflict(s):\n\n${conflicts.join('\n')}\n\nDo you want to proceed anyway?`
      );

      if (!confirmDrop) {
        draggedSurgeryId.value = null;
        dragGhost.value.visible = false;
        return;
      }
    }

    console.log(`Dropping surgery ${surgeryId} in OR ${targetORId} at ${newStartTime.toISOString()} with SDST: ${sdsTime}min`);

    // Check if this is a pending surgery (schedule it) or existing surgery (reschedule it)
    const isPendingSurgery = scheduleStore.pendingSurgeries.some(p => p.id === surgeryId);

    if (isPendingSurgery) {
      scheduleStore.addSurgeryFromPending(surgeryId, targetORId, newStartTime);
    } else {
      scheduleStore.rescheduleSurgery(surgeryId, targetORId, newStartTime);
    }
  }

  draggedSurgeryId.value = null;
  dragGhost.value.visible = false;
};



// Update current time indicator periodically
let currentTimeInterval = null;

// Lifecycle hooks
onMounted(() => {
  // Load initial data
  scheduleStore.loadInitialData();

  // Set up interval to update current time indicator
  currentTimeInterval = setInterval(() => {
    // Force re-computation of current time indicator
    if (isCurrentTimeVisible.value) {
      // This is a trick to force Vue to re-render the computed property
      currentTimeIndicatorStyle.value;
    }
  }, 60000); // Update every minute
});

onUnmounted(() => {
  // Clean up interval
  if (currentTimeInterval) {
    clearInterval(currentTimeInterval);
  }
});

</script>

<style scoped>
/* Gantt Chart Container */
.gantt-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  position: relative;
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Header Section */
.gantt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-background);
  flex-shrink: 0;
}

.gantt-title {
  display: flex;
  flex-direction: column;
}

.gantt-title h3 {
  margin: 0;
  color: var(--color-text);
  font-weight: var(--font-weight-bold);
}

.view-mode-indicator {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.view-controls {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-right: var(--spacing-md);
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-sm);
}

.current-date-display {
  font-weight: var(--font-weight-medium);
  padding: 0 var(--spacing-sm);
  min-width: 150px;
  text-align: center;
}

.view-mode-buttons {
  display: flex;
  gap: var(--spacing-xs);
}

.btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-border);
  background-color: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: all 0.2s ease;
}

.btn:hover {
  background-color: var(--color-background-mute);
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverted);
  border-color: var(--color-primary);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark, var(--color-primary));
  opacity: 0.9;
}

.btn-secondary {
  background-color: var(--color-background-soft);
}

.btn-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

/* Gantt Grid */
.gantt-grid {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: auto;
  position: relative;
}

.gantt-time-axis {
  display: flex;
  padding-left: 120px; /* Width of OR label column */
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-background-soft);
  position: sticky;
  top: 0;
  z-index: 2;
}

.time-marker {
  width: 120px; /* Width per hour */
  flex-shrink: 0;
  text-align: center;
  padding: var(--spacing-xs) 0;
  border-right: 1px solid var(--color-border-soft);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.gantt-or-rows {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  min-width: calc(120px * 13); /* 13 hours (7am to 7pm) */
}

.gantt-or-row {
  display: flex;
  border-bottom: 1px solid var(--color-border-soft);
  min-height: 60px;
  position: relative;
  transition: background-color 0.2s ease;
  width: 100%;
}

.gantt-or-row:hover {
  background-color: var(--color-background-hover, rgba(0, 0, 0, 0.02));
}

.gantt-or-row.drop-target {
  background-color: var(--color-background-active, rgba(0, 0, 0, 0.05));
  border: 2px dashed var(--color-primary);
}

.or-label {
  width: 120px; /* Width of OR label column */
  flex-shrink: 0;
  padding: var(--spacing-sm);
  background-color: var(--color-background-soft);
  border-right: 1px solid var(--color-border);
  font-weight: var(--font-weight-bold);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  position: sticky;
  left: 0;
  z-index: 1;
}

.or-timeline {
  flex-grow: 1;
  position: relative;
  min-height: 60px;
  background-color: var(--color-background);
  /* Add subtle grid lines for hours */
  background-image: repeating-linear-gradient(
    to right,
    var(--color-border-soft) 0px,
    var(--color-border-soft) 1px,
    transparent 1px,
    transparent 120px /* Width per hour */
  );
}

/* Current time indicator */
.current-time-indicator {
  position: absolute;
  top: 0;
  height: 100%;
  width: 2px;
  background-color: var(--color-accent, red);
  z-index: 3;
  pointer-events: none;
}

/* Surgery Blocks */
.surgery-block {
  position: absolute;
  top: 5px; /* Small margin from top of row */
  height: calc(100% - 10px); /* Height with margins */
  border-radius: var(--border-radius-sm);
  display: flex;
  flex-direction: row;
  align-items: center;
  overflow: hidden;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease, transform 0.1s ease;
  color: var(--color-text-inverted, #fff); /* Default to white text, can be overridden */
  z-index: 1; /* Above the timeline grid */
  padding: var(--spacing-xs);
}

.surgery-block:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  z-index: 2; /* Bring to front when hovered */
}

.surgery-block:active {
  cursor: grabbing;
}

.surgery-block.is-dragging {
  opacity: 0.6;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.surgery-block.is-selected {
  border: 2px solid var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb, 0, 120, 212), 0.3);
  z-index: 3; /* Above other blocks */
}

.surgery-info {
  padding: 0 var(--spacing-xs);
  font-size: var(--font-size-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

/* SDST Segment */
.sdst-segment {
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: visible;
}

/* SDST color coding */
.sdst-low {
  background-color: rgba(40, 167, 69, 0.4) !important; /* Green with opacity */
  border-right: 2px dashed rgba(40, 167, 69, 0.8) !important;
}

.sdst-medium {
  background-color: rgba(255, 193, 7, 0.4) !important; /* Yellow with opacity */
  border-right: 2px dashed rgba(255, 193, 7, 0.8) !important;
}

.sdst-high {
  background-color: rgba(220, 53, 69, 0.4) !important; /* Red with opacity */
  border-right: 2px dashed rgba(220, 53, 69, 0.8) !important;
}

/* SDST duration label */
.sdst-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  background-color: rgba(255, 255, 255, 0.8);
  padding: 1px 3px;
  border-radius: 2px;
  white-space: nowrap;
  z-index: 1;
}

/* Transition icon */
.sdst-transition-icon {
  position: absolute;
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  cursor: help;
}

/* Conflict Styling */
.surgery-block.has-conflict {
  border: 2px solid var(--color-error);
  animation: pulse 2s infinite;
}

.conflict-indicator {
  margin-right: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--color-error-rgb, 255, 0, 0), 0.4);
  }
  70% {
    box-shadow: 0 0 0 5px rgba(var(--color-error-rgb, 255, 0, 0), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--color-error-rgb, 255, 0, 0), 0);
  }
}

/* Enhanced Tooltip */
.surgery-tooltip {
  position: fixed;
  z-index: 1000;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: var(--font-size-sm);
  max-width: 300px;
  pointer-events: none; /* Allow clicking through the tooltip */
  overflow: hidden;
}

.tooltip-header {
  background-color: var(--color-background-soft);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-bottom: 1px solid var(--color-border-soft);
  font-weight: var(--font-weight-bold);
}

.tooltip-body {
  padding: var(--spacing-sm);
}

.tooltip-body p {
  margin: var(--spacing-xs) 0;
}

.tooltip-sdst-section {
  margin-bottom: var(--spacing-sm);
  border: 1px solid var(--color-border-soft);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-xs);
  background-color: var(--color-background-soft);
}

.tooltip-sdst-detail {
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
}

.sdst-transition {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-xs);
}

.sdst-from, .sdst-to {
  font-weight: var(--font-weight-bold);
  padding: 2px 4px;
  border-radius: 3px;
  background-color: var(--color-background);
}

.sdst-arrow {
  color: var(--color-text-secondary);
}

.sdst-indicator {
  height: 8px;
  border-radius: 4px;
  margin: var(--spacing-xs) 0;
}

.sdst-explanation {
  font-style: italic;
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.tooltip-conflicts {
  margin-top: var(--spacing-xs);
  padding-top: var(--spacing-xs);
  border-top: 1px solid var(--color-border-soft);
  color: var(--color-error);
}

.tooltip-conflicts ul {
  margin: var(--spacing-xs) 0 0;
  padding-left: var(--spacing-md);
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  z-index: 10;
  font-size: var(--font-size-lg);
  color: var(--color-primary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(var(--color-primary-rgb, 0, 120, 212), 0.2);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Drag Ghost */
.drag-ghost {
  position: fixed;
  height: 50px;
  border-radius: var(--border-radius-sm);
  display: flex;
  flex-direction: row;
  align-items: center;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: var(--color-text-inverted, #fff);
  z-index: 1000;
  pointer-events: none;
  opacity: 0.8;
}

.ghost-info {
  padding: 0 var(--spacing-xs);
  font-size: var(--font-size-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

/* SDST Legend */
.sdst-legend {
  padding: var(--spacing-xs) var(--spacing-md);
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.legend-title {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
  color: var(--color-text);
  white-space: nowrap;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.legend-color {
  width: 20px;
  height: 10px;
  border-radius: 2px;
}

.legend-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  font-size: var(--font-size-xs);
}

.legend-label {
  white-space: nowrap;
}

/* Enhanced Mobile Responsive Design */

/* Tablet adjustments (768px - 1024px) */
@media (max-width: 1024px) {
  .gantt-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
  }

  .view-controls {
    width: 100%;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .view-controls select,
  .view-controls button {
    min-height: var(--touch-target-min);
    padding: var(--spacing-sm) var(--spacing-md);
  }
}

/* Mobile adjustments (up to 768px) */
@media (max-width: 768px) {
  .gantt-chart {
    font-size: var(--font-size-sm);
  }

  .gantt-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
  }

  .view-controls {
    width: 100%;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .view-controls select,
  .view-controls button {
    width: 100%;
    min-height: var(--touch-target-comfortable);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-base);
  }

  .or-label, .time-marker {
    width: 60px; /* Smaller width on mobile */
    font-size: var(--font-size-xs);
    padding: var(--spacing-xs);
  }

  .or-timeline {
    background-image: repeating-linear-gradient(
      to right,
      var(--color-border-soft) 0px,
      var(--color-border-soft) 1px,
      transparent 1px,
      transparent 60px /* Smaller width per hour on mobile */
    );
  }

  .surgery-block {
    min-height: 40px; /* Larger touch targets */
    font-size: var(--font-size-xs);
    padding: var(--spacing-xs);
  }

  .surgery-block .surgery-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .surgery-block .surgery-title {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
  }

  .surgery-block .surgery-details {
    font-size: 10px;
    opacity: 0.8;
  }

  .sdst-legend {
    padding: var(--spacing-xs);
    flex-direction: column;
    align-items: flex-start;
  }

  .legend-items {
    margin-top: var(--spacing-xs);
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }

  .legend-item {
    margin-right: 0;
    margin-bottom: var(--spacing-xs);
    font-size: var(--font-size-xs);
  }

  .sdst-label {
    display: none; /* Hide SDST labels on mobile */
  }

  /* Mobile-specific gantt container */
  .gantt-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  /* Simplified mobile view */
  .mobile-simplified .surgery-block .surgery-details {
    display: none;
  }

  .mobile-simplified .sdst-indicator {
    display: none;
  }
}

/* Small mobile adjustments (up to 480px) */
@media (max-width: 480px) {
  .gantt-header {
    padding: var(--spacing-xs);
  }

  .or-label, .time-marker {
    width: 50px;
    font-size: 10px;
  }

  .or-timeline {
    background-image: repeating-linear-gradient(
      to right,
      var(--color-border-soft) 0px,
      var(--color-border-soft) 1px,
      transparent 1px,
      transparent 50px
    );
  }

  .surgery-block {
    min-height: 36px;
    font-size: 10px;
  }

  .surgery-block .surgery-title {
    font-size: 10px;
  }

  .legend-item {
    font-size: 10px;
  }

  .legend-color {
    width: 16px;
    height: 8px;
  }

  .legend-icon {
    width: 14px;
    height: 14px;
    font-size: 8px;
  }
}

/* Touch-specific enhancements */
@media (hover: none) and (pointer: coarse) {
  .surgery-block {
    min-height: var(--touch-target-comfortable);
    cursor: default;
  }

  .surgery-block:hover {
    transform: none; /* Disable hover transforms on touch devices */
  }

  .surgery-block:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }

  .view-controls button:active {
    transform: scale(0.95);
  }
}

/* Landscape orientation for mobile */
@media (max-height: 500px) and (orientation: landscape) {
  .gantt-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-xs) var(--spacing-sm);
  }

  .view-controls {
    flex-direction: row;
    width: auto;
  }

  .view-controls select,
  .view-controls button {
    width: auto;
    min-height: 36px;
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-sm);
  }

  .surgery-block {
    min-height: 32px;
  }
}

/* Accessibility Enhancements */
.surgery-block:focus {
  outline: 2px solid var(--color-focus, var(--color-primary));
  outline-offset: 2px;
  z-index: 3; /* Bring to front when focused */
}

/* Visually hidden but accessible to screen readers */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
