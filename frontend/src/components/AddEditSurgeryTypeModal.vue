<template>
  <div class="modal-overlay" v-if="show" @click.self="handleCancel">
    <div class="modal-content">
      <h3>{{ isEditing ? 'Edit Surgery Type' : 'Add New Surgery Type' }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <label for="type-name">Name</label>
          <input type="text" id="type-name" v-model="formData.name" required>
        </div>

        <div class="input-group">
          <label for="type-code">Code (e.g., CABG, TKR)</label>
          <input type="text" id="type-code" v-model="formData.code">
        </div>

        <div class="input-group">
          <label for="type-description">Description</label>
          <textarea id="type-description" v-model="formData.description"></textarea>
        </div>

        <div class="form-actions">
          <button type="submit" class="button-primary">{{ isEditing ? 'Save Changes' : 'Add Type' }}</button>
          <button type="button" class="button-secondary" @click="handleCancel">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// Define props to receive initial data for editing and a flag for edit mode
const props = defineProps({
  show: { type: Boolean, default: false }, // Added show prop
  initialData: { type: Object, default: null }, // Data for the type being edited
  isEditing: { type: Boolean, default: false },
});

// Define emits to communicate with parent (e.g., SDSTDataManagementScreen)
const emit = defineEmits(['save', 'cancel']);

// Initialize form data
const formData = ref({
  id: null, // Include ID for editing
  name: '',
  code: '',
  description: '',
});

// Watch for changes in initialData prop to populate form when editing
watch(() => props.initialData, (newData) => {
  if (newData) {
    formData.value = { ...newData }; // Populate form for editing
  } else {
    // Reset form when not editing (e.g., adding new)
     formData.value = { id: null, name: '', code: '', description: '' };
  }
}, { immediate: true }); // Run immediately to set initial state


const handleSubmit = () => {
  console.log('Submitting Surgery Type data:', formData.value);
  // Emit the form data to the parent component
  emit('save', formData.value);
  // Reset form (handled by watch effect when parent closes modal/clears initialData)
};

const handleCancel = () => {
  console.log('Cancelling Surgery Type form');
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

.input-group input[type="text"],
.input-group textarea {
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
.input-group textarea:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Example focus style */
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