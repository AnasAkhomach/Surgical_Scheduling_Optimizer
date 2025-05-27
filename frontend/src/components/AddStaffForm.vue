<template>
  <div class="add-staff-form">
    <h3>{{ formTitle }}</h3>
    <form @submit.prevent="handleSubmit">
      <div class="input-group">
        <label for="staff-name">Name</label>
        <input type="text" id="staff-name" v-model="staffData.name" @input="clearError('name')">
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <div class="input-group">
        <label for="staff-role">Role</label>
         <select id="staff-role" v-model="staffData.role" @change="clearError('role')">
          <option value="">Select Role</option>
          <option value="Surgeon">Surgeon</option>
          <option value="Nurse">Nurse</option>
          <option value="Anesthetist">Anesthetist</option>
          <option value="Other">Other</option>
        </select>
        <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
      </div>

      <div class="input-group">
        <label for="staff-specializations">Specialization(s)</label>
        <input type="text" id="staff-specializations" v-model="staffData.specializationsString">
        <small>Enter specializations separated by commas (e.g., Orthopedics, Sports Medicine)</small>
        <!-- Basic validation for specializations can be added if it becomes a strict requirement -->
      </div>

       <div class="input-group">
        <label for="staff-status">Status</label>
        <select id="staff-status" v-model="staffData.status" @change="clearError('status')">
          <option value="">Select Status</option>
          <option value="Active">Active</option>
          <option value="On Leave">On Leave</option>
          <option value="Inactive">Inactive</option>
        </select>
        <span v-if="errors.status" class="error-message">{{ errors.status }}</span>
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
  staffToEdit: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['save', 'cancel']);

const initialStaffData = () => ({
  id: null,
  name: '',
  role: '',
  specializations: [],
  specializationsString: '',
  status: '',
});

const staffData = ref(initialStaffData());
const errors = ref({}); // Added for validation errors

const isEditMode = computed(() => !!props.staffToEdit);
const formTitle = computed(() => isEditMode.value ? 'Edit Staff Member' : 'Add New Staff Member');
const submitButtonText = computed(() => isEditMode.value ? 'Update Staff' : 'Save Staff');

const clearError = (field) => {
  if (errors.value[field]) {
    errors.value[field] = '';
  }
};

const clearAllErrors = () => {
  errors.value = {};
};

// Watch for changes in staffToEdit prop to pre-fill form
watch(() => props.staffToEdit, (newStaff) => {
  clearAllErrors(); // Clear errors when staffToEdit changes
  if (newStaff) {
    staffData.value = {
      ...newStaff,
      specializationsString: newStaff.specializations ? newStaff.specializations.join(', ') : ''
    };
  } else {
    staffData.value = initialStaffData();
  }
}, { immediate: true });

// Watch the string input and update the array
watch(() => staffData.value.specializationsString, (newValue) => {
    staffData.value.specializations = newValue.split(',').map(s => s.trim()).filter(s => s);
});


const validateForm = () => {
  clearAllErrors();
  let isValid = true;
  if (!staffData.value.name.trim()) {
    errors.value.name = 'Name is required.';
    isValid = false;
  }
  if (!staffData.value.role) {
    errors.value.role = 'Role is required.';
    isValid = false;
  }
  if (!staffData.value.status) {
    errors.value.status = 'Status is required.';
    isValid = false;
  }
  return isValid;
};

const handleSubmit = () => {
  if (!validateForm()) {
    return; // Stop submission if validation fails
  }

  const payload = { ...staffData.value };
  delete payload.specializationsString;

  if (isEditMode.value) {
    console.log('Updating Staff data:', payload);
    emit('save', { ...payload, isUpdate: true });
  } else {
    console.log('Submitting new Staff data:', payload);
    emit('save', payload);
  }
  staffData.value = initialStaffData(); // Reset form after successful submission
  clearAllErrors(); // Clear errors on successful submission
};

const handleCancel = () => {
  console.log('Cancelling Staff form');
  staffData.value = initialStaffData(); // Reset form
  clearAllErrors(); // Clear errors on cancel
  emit('cancel');
};

</script>

<style scoped>
.add-staff-form {
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

.add-staff-form h3 {
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