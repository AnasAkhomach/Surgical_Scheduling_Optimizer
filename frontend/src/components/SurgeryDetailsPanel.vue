
<template>
  <aside class="details-panel" v-if="selectedSurgery">
    <h3>Surgery Details</h3>
    <div class="detail-section">
      <h4>Patient Information</h4>
      <p><strong>Patient ID:</strong> {{ selectedSurgery.patientId }}</p>
      <p><strong>Patient Name:</strong> {{ selectedSurgery.patientName }}</p>
      <!-- Add EHR integration link/info here if applicable -->
      <!-- As per guide.txt 8.1.1: Link to patient's EHR record -->
      <!-- <p v-if="selectedSurgery.ehrLink"><a :href="selectedSurgery.ehrLink" target="_blank">View in EHR</a></p> -->
    </div>

    <div class="detail-section">
      <h4>Surgery Information</h4>
      <p><strong>Surgery Type:</strong> {{ selectedSurgery.fullType }}</p>
      <p><strong>Estimated Duration:</strong> {{ selectedSurgery.estimatedDuration }} minutes</p>
      <p><strong>Priority:</strong> {{ selectedSurgery.priority }}</p>
      <p><strong>Scheduled Time:</strong> {{ formatDateTime(selectedSurgery.startTime) }}</p>
      <p><strong>Operating Room:</strong> {{ selectedSurgery.orName }}</p>
       <!-- Display actual duration if different from estimated -->
       <p v-if="selectedSurgery.duration !== selectedSurgery.estimatedDuration">
           <strong>Actual Duration:</strong> {{ selectedSurgery.duration }} minutes
       </p>
       <p v-if="selectedSurgery.status"><strong>Status:</strong> {{ selectedSurgery.status }}</p>
    </div>

    <div class="detail-section">
      <h4>Required Resources</h4>
      <p><strong>Surgeon(s):</strong> {{ selectedSurgery.requiredSurgeons.join(', ') }}</p>
      <p><strong>Staff Roles:</strong> {{ selectedSurgery.requiredStaffRoles.join(', ') }}</p>
      <p><strong>Equipment:</strong> {{ selectedSurgery.requiredEquipment.join(', ') }}</p>
       <!-- Display resource availability status for the scheduled time -->
       <!-- This would require fetching/calculating resource availability for the surgery's time slot -->
       <!-- <div v-if="selectedSurgery.resourceStatus">
         <p><strong>Resource Status:</strong></p>
          <div v-for="(status, resource) in selectedSurgery.resourceStatus" :key="resource">
              <span :class="{'status-available': status === 'Available', 'status-unavailable': status !== 'Available'}">●</span>
              {{ resource }}: {{ status }}
          </div>
       </div> -->
    </div>

    <div class="detail-section">
      <h4>Sequence-Dependent Setup Time (SDST)</h4>
      <p>
         <strong>Calculated SDST:</strong>
         <span class="sdst-value">{{ selectedSurgery.sdsTime }}</span> minutes
      </p>
      <p class="sdst-explanation">
         (Required between <strong>{{ selectedSurgery.precedingType }}</strong> and <strong>{{ selectedSurgery.type }}</strong>)
      </p>
       <!-- Link to SDST matrix entry if needed (guide.txt 7.1) -->
       <!-- <p><a href="#">View SDST Rule Details</a></p> -->
    </div>

    <!-- Display Conflict Alerts (guide.txt 7.2) -->
    <div class="detail-section conflicts" v-if="selectedSurgery.conflicts && selectedSurgery.conflicts.length">
        <h4>Alerts / Conflicts</h4>
        <ul>
            <li v-for="(conflict, index) in selectedSurgery.conflicts" :key="index" class="conflict-alert">
                <span class="alert-icon" aria-hidden="true">⚠️</span> {{ conflict }}
            </li>
        </ul>
    </div>


    <!-- Action buttons (Edit, Cancel) -->
    <div class="action-buttons">
      <!-- Disable buttons if surgery is cancelled or in progress -->
      <button class="btn btn-secondary" @click="handleEditSurgery" :disabled="!isEditable">Edit Surgery</button>
      <button class="btn btn-danger" @click="handleCancelSurgery" :disabled="!isCancellable">Cancel Surgery</button>
    </div>

     <!-- Placeholder Confirmation Modal (visually hidden or handled by a global component) -->
     <!-- In a real app, this would be a dedicated modal component -->
     <div v-if="showCancelConfirmation" class="confirmation-modal-placeholder">
         <p>Are you sure you want to cancel the surgery for {{ selectedSurgery.patientName }}?</p>
         <button @click="confirmCancel">Yes, Cancel</button>
         <button @click="cancelCancel">No, Keep Surgery</button>
     </div>

  </aside>
  <aside class="details-panel empty" v-else>
      <p>Select a surgery from the schedule or pending list to view details.</p>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';

const store = useScheduleStore();
// Use the getter from the store to get the full selected surgery object
const { selectedSurgery } = storeToRefs(store);

const showCancelConfirmation = ref(false); // State to control confirmation modal

// Computed property to determine if the surgery is editable
const isEditable = computed(() => {
    // A surgery is editable if it exists and its status is not 'Completed' or 'Cancelled'
    return selectedSurgery.value && selectedSurgery.value.status !== 'Completed' && selectedSurgery.value.status !== 'Cancelled';
});

// Computed property to determine if the surgery is cancellable
const isCancellable = computed(() => {
     // A surgery is cancellable if it exists and its status is not 'Completed' or 'Cancelled'
    return selectedSurgery.value && selectedSurgery.value.status !== 'Completed' && selectedSurgery.value.status !== 'Cancelled';
});


const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    // Format date and time clearly
    return date.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
};

// --- Action Handlers ---

const handleEditSurgery = () => {
    console.log('Details Panel: Edit Surgery clicked for', selectedSurgery.value.id);
    // In a real app, this would typically emit an event to the parent
    // to open a modal or navigate to a surgery edit form,
    // passing the selectedSurgery.value as data.
    // Example: emit('edit-surgery', selectedSurgery.value);

    // Placeholder: Log the action
    alert(`Simulating Edit for Surgery: ${selectedSurgery.value.patientName}`);
    // After editing and saving (in modal/form), you would dispatch store.editSurgery(surgeryId, updatedData)
};

const handleCancelSurgery = () => {
    console.log('Details Panel: Cancel Surgery clicked for', selectedSurgery.value.id);
    // Show confirmation modal before canceling
    showCancelConfirmation.value = true;
};

const confirmCancel = async () => {
    console.log('Details Panel: Confirm Cancel clicked for', selectedSurgery.value.id);
    showCancelConfirmation.value = false; // Close modal
    if (selectedSurgery.value) {
        // Dispatch the cancel action to the store
        await store.cancelSurgery(selectedSurgery.value.id);
        // The store will handle updating the state and showing loading/error if needed
        // After successful cancellation, you might want to clear the selected surgery
         if (!store.error) { // Check for error in store state after action
             store.clearSelectedSurgery();
         }
    }
};

const cancelCancel = () => {
    console.log('Details Panel: Cancel action aborted.');
    showCancelConfirmation.value = false; // Close modal without canceling
};

</script>

<style scoped>
.details-panel {
  width: 300px; /* Fixed width for the panel */
  border-left: 1px solid var(--color-border);
  padding: var(--spacing-md);
  overflow-y: auto; /* Allow scrolling if content overflows */
  background-color: var(--color-background-soft);
  flex-shrink: 0;
  height: 100%; /* Ensure panel takes full height of its container */
  display: flex;
  flex-direction: column;
}

.details-panel.empty {
    align-items: center;
    justify-content: center;
    color: var(--color-text-secondary);
    text-align: center;
}

.details-panel h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
}

.details-panel h4 {
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border-soft);
  padding-bottom: var(--spacing-xs);
}

.detail-section {
  margin-bottom: var(--spacing-md);
}

.detail-section p {
  margin-bottom: var(--spacing-xs);
  line-height: 1.4;
  font-size: var(--font-size-base);
   color: var(--color-text);
}

.detail-section p strong {
    color: var(--color-text);
}


.sdst-value {
    font-weight: bold;
    color: var(--color-accent); /* Highlight SDST value */
}

.sdst-explanation {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
  font-style: italic;
}

.conflicts h4 {
    color: var(--color-error); /* Red color for conflict header */
    border-color: var(--color-error); /* Red border */
}

.conflict-alert {
    color: var(--color-error); /* Red color for conflict text */
    font-size: var(--font-size-base);
    margin-bottom: var(--spacing-xs);
    list-style: none; /* Remove default list styling */
    padding-left: 0;
    display: flex;
    align-items: center;
    font-weight: var(--font-weight-medium); /* Make alerts slightly bolder */
}

.alert-icon {
    margin-right: var(--spacing-xs);
    font-size: var(--font-size-lg); /* Slightly larger icon */
     /* Color is inherited from parent .conflict-alert */
}


.action-buttons {
  margin-top: auto; /* Push buttons to the bottom */
  display: flex;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md); /* Add some space above buttons */
  border-top: 1px solid var(--color-border-soft); /* Separator line */
}

.btn {
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    font-size: var(--font-size-base);
    transition: background-color 0.2s ease, opacity 0.2s ease;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-secondary {
    background-color: var(--color-background-mute);
    color: var(--color-text);
    border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
    background-color: rgba(0, 0, 0, 0.05); /* Use rgba for darkening effect */
}

.btn-danger {
    background-color: var(--color-error);
    color: var(--color-text-inverted);
}

.btn-danger:hover:not(:disabled) {
    background-color: rgba(0, 0, 0, 0.1); /* Use rgba for darkening effect */
}

/* Placeholder Confirmation Modal Styling */
.confirmation-modal-placeholder {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: var(--color-white);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius-md);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    z-index: var(--z-index-modal);
    text-align: center;
    max-width: 400px;
    width: 90%;
    border: 1px solid var(--color-border);
}

.confirmation-modal-placeholder button {
    margin: var(--spacing-sm);
}

</style>
