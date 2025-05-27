<template>
  <div class="patient-management-container">
    <div v-if="!isLoading">
      <h1>Patient Management</h1>
      <!-- Placeholder for patient list or table -->
      <button class="button-primary" @click="addNewPatient">Add New Patient</button>
      <ul v-if="patients.length > 0">
        <li v-for="patient in patients" :key="patient.id">
          {{ patient.name }} (MRN: {{ patient.mrn }}) - DOB: {{ patient.dob }}
        </li>
      </ul>
      <p v-if="patients.length === 0">No patients found.</p>
    </div>

    <div v-if="isLoading" class="loading-message">Loading patient data...</div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// Script logic will be added here later

const isLoading = ref(true);

const fetchPatientsData = async () => {
  // Simulate data fetching delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  // In a real app, fetch data from backend and populate `patients.value`
  isLoading.value = false;
};

onMounted(() => {
  fetchPatientsData();
});

const addNewPatient = () => {
  console.log('Add New Patient button clicked');
  // TODO: Navigate to patient creation form or open a modal
};

const patients = ref([
    { id: 1, name: 'Alice Smith', dob: '1990-05-15', mrn: 'MRN12345' },
    { id: 2, name: 'Bob Johnson', dob: '1985-11-20', mrn: 'MRN67890' },
    { id: 3, name: 'Charlie Brown', dob: '2000-01-01', mrn: 'MRN11223' },
]);
</script>

<style scoped>
.patient-management-container {
  padding: 20px;
}
.loading-message {
  text-align: center;
  color: gray;
  margin-top: 20px;
}
</style>