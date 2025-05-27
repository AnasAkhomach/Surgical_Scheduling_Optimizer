<template>
  <div class="modal-overlay" v-if="show" @click.self="handleCancel">
    <div class="modal-content">
      <h3>{{ title || 'Confirm Action' }}</h3>
      <div class="modal-body">
        <p>{{ message || 'Are you sure you want to perform this action?' }}</p>
      </div>
      
      <div class="form-actions">
        <button type="button" class="button-danger" @click="handleConfirm">Confirm</button>
        <button type="button" class="button-secondary" @click="handleCancel">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  show: { type: Boolean, default: false }, // Added show prop
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure you want to perform this action?' },
});

const emit = defineEmits(['confirm', 'cancel']);

const handleConfirm = () => {
  emit('confirm');
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); /* Darker overlay */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000; /* Ensure it's above other modals */
}

.modal-content {
  background-color: var(--color-white);
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
  max-width: 400px; /* Smaller modal for confirmation */
  width: 90%;
  text-align: center; /* Center content */
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: var(--color-very-dark-gray);
  font-size: 1.4em;
}

.modal-body p {
    font-size: 1em;
    color: var(--color-dark-gray);
    margin-bottom: 20px;
    line-height: 1.5;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center; /* Center buttons */
  gap: 15px; /* Space between buttons */
}

.form-actions button {
    padding: 10px 20px;
    font-size: 1em;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease;
    border: none;
}

.button-danger {
    background-color: var(--color-danger);
    color: var(--color-white);
}

.button-danger:hover {
    background-color: #c82333; /* Darker red */
}

.button-secondary {
     background-color: var(--color-secondary);
     color: var(--color-white);
}

.button-secondary:hover {
     background-color: #5a6268;
}

</style>
