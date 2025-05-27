
<template>
  <div class="pending-surgeries-list">
    <h4>Pending Surgeries</h4>
    <!-- Add filter/sort controls here later -->
    <div class="pending-items">
      <div
        v-for="surgery in pendingSurgeries"
        :key="surgery.id"
        class="pending-surgery-item"
        draggable="true"
        @dragstart="onDragStart($event, surgery)"
        @dragend="onDragEnd($event)" <!-- Add dragend handler -->
        @click="selectSurgery(surgery)"
        :aria-label="`Pending Surgery: ${surgery.fullType} for ${surgery.patientName}. Estimated duration: ${surgery.estimatedDuration} minutes. Priority: ${surgery.priority}.`"
        tabindex="0"
      >
        <div class="item-info">
          <strong>{{ surgery.patientName }}</strong> - {{ surgery.type }}
        </div>
        <div class="item-details">
          Duration: {{ surgery.estimatedDuration }} min | Priority: {{ surgery.priority }}
        </div>
        <!-- Add quick action buttons like "Schedule Now" or details icon if needed -->
      </div>
      <p v-if="pendingSurgeries.length === 0" class="empty-list-message">
          No pending surgeries at this time.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';

const store = useScheduleStore();
const { pendingSurgeries } = storeToRefs(store);

// --- Drag and Drop Logic ---
const onDragStart = (event, surgery) => {
  // Store data to be transferred (e.g., surgery ID)
  // The drop target (GanttChart) expects 'text/plain' with the surgery ID
  event.dataTransfer.setData('text/plain', surgery.id);
  event.dataTransfer.effectAllowed = 'move'; // Indicate that the element can be moved

  // Add a class for visual feedback while dragging
   // Use setTimeout to ensure the class is added after the browser takes the screenshot for the drag image
   setTimeout(() => {
      event.target.classList.add('is-dragging');
   }, 0);
};

const onDragEnd = (event) => {
    // Clean up the dragging class when the drag operation ends (success or cancel)
    event.target.classList.remove('is-dragging');
    // Note: Removing the surgery from the pending list happens in the store action (addSurgeryFromPending)
    // triggered by a successful drop in the GanttChart.
};

// --- Interaction Logic ---
const selectSurgery = (surgery) => {
  store.selectSurgery(surgery.id); // Select the surgery in the store for details panel
};

</script>

<style scoped>
.pending-surgeries-list {
  padding: var(--spacing-md); /* Use global spacing variable */
  border-right: 1px solid var(--color-border); /* Use global border variable */
  overflow-y: auto;
  height: 100%;
  flex-shrink: 0;
  width: 250px;
  background-color: var(--color-background-soft); /* Use global background variable */
}

.pending-surgeries-list h4 {
  margin-top: 0;
  margin-bottom: var(--spacing-md); /* Use global spacing variable */
  color: var(--color-text); /* Use global text color variable */
  border-bottom: 1px solid var(--color-border-soft); /* Use global border variable */
  padding-bottom: var(--spacing-xs); /* Use global spacing variable */
}

.pending-items {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm); /* Use global spacing variable */
}

.pending-surgery-item {
  border: 1px solid var(--color-border); /* Use global border variable */
  border-radius: var(--border-radius-sm); /* Use global border radius variable */
  padding: var(--spacing-sm); /* Use global spacing variable */
  cursor: grab; /* Indicate draggable item */
  background-color: var(--color-background); /* Use global background variable */
  transition: background-color 0.2s ease, border-color 0.2s ease; /* Add transition */
   outline-offset: 2px; /* Ensure outline doesn't overlap border */
    color: var(--color-text); /* Use global text color variable */
}

.pending-surgery-item:hover {
  background-color: var(--color-background-mute); /* Use global background variable */
  border-color: var(--color-primary); /* Use global primary color variable */
}

.pending-surgery-item:active {
    cursor: grabbing; /* Indicate being grabbed */
}

.pending-surgery-item.is-dragging {
    opacity: 0.4;
    border: 2px dashed var(--color-accent); /* Use global accent variable */
    background-color: var(--color-background-mute); /* Use global background variable */
}

.item-info strong {
    color: inherit; /* Inherit color from parent */
}

.item-details {
    font-size: var(--font-size-sm); /* Use global font size variable */
    color: var(--color-text-secondary); /* Use global text color variable */
    margin-top: var(--spacing-xs); /* Use global spacing variable */
}

.empty-list-message {
    color: var(--color-text-secondary); /* Use global text color variable */
    text-align: center;
    font-style: italic;
    margin-top: var(--spacing-md); /* Use global spacing variable */
}
</style>
