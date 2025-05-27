<template>
  <div class="add-equipment-form">
    <h3>{{ formTitle }}</h3>
    <form @submit.prevent="handleSubmit">
      <div class="input-group">
        <label for="equipment-name">Name/ID</label>
        <input type="text" id="equipment-name" v-model="equipmentData.name" @input="clearError('name')">
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <div class="input-group">
        <label for="equipment-type">Type</label>
        <input type="text" id="equipment-type" v-model="equipmentData.type" @input="clearError('type')">
        <span v-if="errors.type" class="error-message">{{ errors.type }}</span>
      </div>

      <div class="input-group">
        <label for="equipment-status">Status</label>
        <select id="equipment-status" v-model="equipmentData.status" @change="clearError('status')">
          <option value="">Select Status</option>
          <option value="Available">Available</option>
          <option value="In Use">In Use</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Retired">Retired</option>
        </select>
        <span v-if="errors.status" class="error-message">{{ errors.status }}</span>
      </div>

       <div class="input-group">
        <label for="equipment-location">Location</label>
        <input type="text" id="equipment-location" v-model="equipmentData.location">
         <small>E.g., OR 5, Storage Room B</small>
         <!-- Location is optional, so no specific validation message for being empty -->
      </div>

      <div class="form-actions">
        <button type="submit" class="button-primary">{{ submitButtonText }}</button>
        <button type="button" class="button-secondary" @click="handleCancel">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

// Props definition
const props = defineProps({
  equipmentToEdit: {
    type: Object,
    default: null
  }
});

// Define initial form data structure
const initialEquipmentData = () => ({
  id: null,
  name: '',
  type: '',
  status: '',
  location: '',
});

const equipmentData = ref(initialEquipmentData());
const errors = ref({}); // Added for validation errors

// Functions to clear errors
const clearError = (field) => {
  if (errors.value[field]) {
    errors.value[field] = '';
  }
};

const clearAllErrors = () => {
  errors.value = {};
};

// Define emits to communicate with parent
const emit = defineEmits(['save', 'cancel']);

// Computed properties for dynamic UI elements
const isEditMode = computed(() => !!props.equipmentToEdit);
const formTitle = computed(() => isEditMode.value ? 'Edit Equipment' : 'Add New Equipment');
const submitButtonText = computed(() => isEditMode.value ? 'Update Equipment' : 'Save Equipment');

// Watch for changes in equipmentToEdit prop to pre-fill or reset the form
watch(() => props.equipmentToEdit, (newVal) => {
  clearAllErrors(); // Clear errors when equipmentToEdit changes
  if (newVal) {
    // Pre-fill form for editing
    equipmentData.value = { ...newVal };
  } else {
    // Reset form for adding or after cancellation
    equipmentData.value = initialEquipmentData();
  }
}, { immediate: true }); // immediate: true to run on component mount if prop is initially set

const validateForm = () => {
  clearAllErrors();
  let isValid = true;
  if (!equipmentData.value.name.trim()) {
    errors.value.name = 'Name/ID is required.';
    isValid = false;
  }
  if (!equipmentData.value.type.trim()) {
    errors.value.type = 'Type is required.';
    isValid = false;
  }
  if (!equipmentData.value.status) {
    errors.value.status = 'Status is required.';
    isValid = false;
  }
  return isValid;
};

const handleSubmit = () => {
  if (!validateForm()) {
    return; // Stop submission if validation fails
  }

  const dataToSave = { ...equipmentData.value };
  if (isEditMode.value) {
    dataToSave.isUpdate = true; // Add a flag to indicate an update operation
  }
  console.log('Submitting Equipment data:', dataToSave);
  emit('save', dataToSave);
  equipmentData.value = initialEquipmentData(); // Reset form after emitting save
  clearAllErrors(); // Clear errors on successful submission
};

const handleCancel = () => {
  console.log('Cancelling Equipment form');
  equipmentData.value = initialEquipmentData();
  clearAllErrors(); // Clear errors on cancel
  emit('cancel');
};

</script>

<style scoped>
.add-equipment-form {
  background-color: var(--color-white);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-mid-light-gray);
  margin-top: 20px; /* Space above the form */
  max-width: 600px; /* Limit form width */
  margin-left: auto;
  margin-right: auto; /* Center the form */
}

.add-equipment-form h3 {
    font-size: 1.1em;
    margin-top: 0;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--color-mid-light-gray);
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
.input-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-gray);
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1em;
  color: var(--color-very-dark-gray);
  background-color: var(--color-white);
}

.error-message {
  color: var(--color-error);
  font-size: 0.8em;
  margin-top: 4px;
  display: block;
}

.input-group input.invalid,
.input-group select.invalid {
  border-color: var(--color-error);
}

.input-group input:focus,
.input-group select:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.input-group small {
    display: block;
    margin-top: 5px;
    color: var(--color-dark-gray);
    font-size: 0.85em;
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