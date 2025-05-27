<template>
  <div class="add-or-form">
    <h3>{{ formTitle }}</h3>
    <form @submit.prevent="handleSubmit">
      <div class="input-group">
        <label for="or-name">Name/ID</label>
        <input type="text" id="or-name" v-model="orData.name" @input="clearError('name')">
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <div class="input-group">
        <label for="or-location">Location</label>
        <input type="text" id="or-location" v-model="orData.location">
        <!-- No validation for location in this example, but can be added -->
      </div>

      <div class="input-group">
        <label for="or-status">Status</label>
        <select id="or-status" v-model="orData.status" @change="clearError('status')">
          <option value="">Select Status</option>
          <option value="Active">Active</option>
          <option value="Under Maintenance">Under Maintenance</option>
          <option value="Inactive">Inactive</option>
        </select>
        <span v-if="errors.status" class="error-message">{{ errors.status }}</span>
      </div>

      <div class="input-group">
        <label for="or-service">Primary Service</label>
        <input type="text" id="or-service" v-model="orData.primaryService">
        <!-- No validation for primary service in this example, but can be added -->
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

const props = defineProps({
  orToEdit: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['save', 'cancel']);

const orData = ref({
  id: null,
  name: '',
  location: '',
  status: '',
  primaryService: '',
});

const errors = ref({ // Added for validation errors
  name: '',
  status: ''
});

// Functions to clear errors
const clearError = (field) => {
  if (errors.value[field]) {
    errors.value[field] = '';
  }
};

const clearAllErrors = () => {
  errors.value = { name: '', status: '' };
};

const isEditMode = computed(() => !!props.orToEdit);
const formTitle = computed(() => isEditMode.value ? 'Edit Operating Room' : 'Add New Operating Room');
const submitButtonText = computed(() => isEditMode.value ? 'Update OR' : 'Save OR');

watch(() => props.orToEdit, (newOr) => {
  if (newOr) {
    orData.value = { ...newOr };
  } else {
    orData.value = { id: null, name: '', location: '', status: '', primaryService: '' };
  }
  clearAllErrors(); // Clear errors when form data changes (e.g. switching to add/edit)
}, { immediate: true });

const validateForm = () => {
  let isValid = true;
  errors.value = { name: '', status: '' }; // Reset errors

  if (!orData.value.name.trim()) {
    errors.value.name = 'Name/ID is required.';
    isValid = false;
  }
  if (!orData.value.status) {
    errors.value.status = 'Status is required.';
    isValid = false;
  }
  return isValid;
};

const handleSubmit = () => {
  if (!validateForm()) {
    return; // Stop submission if validation fails
  }

  if (isEditMode.value) {
    console.log('Updating OR data:', orData.value);
    emit('save', { ...orData.value, isUpdate: true });
  } else {
    console.log('Submitting new OR data:', orData.value);
    const newOrPayload = { ...orData.value, id: orData.value.id || Date.now().toString() };
    emit('save', newOrPayload);
  }
  clearAllErrors(); // Clear errors on successful submission
};

const handleCancel = () => {
  console.log('Cancelling OR form');
  orData.value = { id: null, name: '', location: '', status: '', primaryService: '' };
  clearAllErrors(); // Clear errors on cancel
  emit('cancel');
};

</script>

<style scoped>
.add-or-form {
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

.add-or-form h3 {
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
  display: block;
  color: var(--color-danger);
  font-size: 0.8em;
  margin-top: 4px;
}

.input-group input.invalid,
.input-group select.invalid {
  border-color: var(--color-danger);
}

.input-group input:focus,
.input-group select:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
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