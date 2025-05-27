<template>
  <div class="modal-overlay" v-if="show" @click.self="handleCancel">
    <div class="modal-content">
      <h3>{{ isEditing ? 'Edit Initial Setup Time' : 'Add New Initial Setup Time' }}</h3>
      <form @submit.prevent="handleSubmit">

        <div class="input-group">
          <label for="setup-type">Surgery Type</label>
          <!-- Dropdown to select surgery type -->
          <!-- This dropdown should be populated by surgery types passed from the parent -->
          <select id="setup-type" v-model="formData.typeId" required :disabled="isEditing"> <!-- Disable type selection when editing -->
            <option value="">Select Surgery Type</option>
            <!-- Options will be populated via v-for on a prop -->
             <option v-for="type in surgeryTypes" :key="type.id" :value="type.id">{{ type.name }}</option>
          </select>
          <small v-if="isEditing">Cannot change Surgery Type when editing.</small>
        </div>

        <div class="input-group">
          <label for="setup-time">Initial Setup Time (minutes)</label>
          <input type="number" id="setup-time" v-model.number="formData.time" required min="0">
        </div>

        <div class="form-actions">
          <button type="submit" class="button-primary">{{ isEditing ? 'Save Changes' : 'Add Setup Time' }}</button>
          <button type="button" class="button-secondary" @click="handleCancel">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// Define props to receive initial data for editing, editing flag, and the list of surgery types
const props = defineProps({
  show: { type: Boolean, default: false }, // Added show prop
  initialData: { type: Object, default: null }, // Data for the setup time being edited
  isEditing: { type: Boolean, default: false },
  surgeryTypes: { type: Array, required: true }, // List of surgery types to populate dropdown
});

// Define emits to communicate with parent (e.g., SDSTDataManagementScreen)
const emit = defineEmits(['save', 'cancel']);

// Initialize form data
const formData = ref({
  typeId: null,
  time: 0,
});

// Watch for changes in initialData prop to populate form when editing
watch(() => props.initialData, (newData) => {
  if (newData) {
    // Ensure we don't overwrite typeId if editing
    formData.value = { ...newData };
  } else {
    // Reset form when not editing (e.g., adding new)
     formData.value = { typeId: null, time: 0 };
  }
}, { immediate: true, deep: true }); // Run immediately and watch deeply


const handleSubmit = () => {
  console.log('Submitting Initial Setup Time data:', formData.value);
   // Add validation here if needed (e.g., check if typeId is selected, time is non-negative)
  if (!formData.value.typeId) {
      alert('Please select a Surgery Type.'); // Basic alert, replace with better UI feedback
      return;
  }
   if (formData.value.time < 0) {
       alert('Setup time cannot be negative.'); // Basic alert
       return;
   }

  // Emit the form data to the parent component
  emit('save', formData.value);
  // Reset form (handled by watch effect when parent closes modal/clears initialData)
};

const handleCancel = () => {
  console.log('Cancelling Initial Setup Time form');
  // Emit cancel event to the parent component
  emit('cancel');
  // Reset form (handled by watch effect when parent closes modal/clears initialData)
};

</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent black background */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Ensure modal is on top */
}

.modal-content {
  background-color: var(--color-white);
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  max-width: 500px; /* Limit modal width */
  width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--color-very-dark-gray);
  border-bottom: 1px solid var(--color-mid-light-gray);
  padding-bottom: 10px;
}

.input-group {
  margin-bottom: 15px;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: var(--color-dark-gray);
  font-size: 0.9em;
}

.input-group input[type="number"],
.input-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-gray);
  border-radius: 4px;
  box-sizing: border-box; /* Include padding and border in element's total width */
  font-size: 1em;
  color: var(--color-very-dark-gray);
  background-color: var(--color-white);
}

.input-group input:focus,
.input-group select:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Example focus style */
}

.input-group small {
     display: block;
     margin-top: 5px;
     color: var(--color-dark-gray);
     font-size: 0.8em;
     font-style: italic;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end; /* Align buttons to the right */
  gap: 10px; /* Space between buttons */
}

.form-actions button {
    padding: 10px 20px;
    font-size: 1em;
}

.button-primary {
     background-color: var(--color-primary);
     color: var(--color-white);
     border: none;
}

.button-primary:hover {
    background-color: var(--color-primary-dark);
}

.button-secondary {
     background-color: var(--color-secondary);
     color: var(--color-white);
     border: none;
}

.button-secondary:hover {
     background-color: #5a6268;
}

</style>