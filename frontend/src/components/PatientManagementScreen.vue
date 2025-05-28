<template>
  <div class="patient-management-screen">
    <h1>Patient Management</h1>

    <div class="toolbar">
      <input type="text" placeholder="Search Patients (Name, MRN)..." v-model="searchTerm" class="search-input">
      <button class="button-primary" @click="openAddPatientModal">Add New Patient</button>
    </div>

    <div v-if="isLoading" class="loading-indicator">
      <p>Loading patient data...</p>
      <!-- Consider adding a spinner component here -->
    </div>

    <div v-else-if="filteredPatients.length > 0" class="patient-table-container">
      <table class="patient-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>MRN</th>
            <th>Date of Birth</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="patient in filteredPatients" :key="patient.id">
            <td>{{ patient.name }}</td>
            <td>{{ patient.mrn }}</td>
            <td>{{ formatDate(patient.dob) }}</td>
            <td>
              <button class="button-icon button-edit" @click="editPatient(patient)" title="Edit Patient">✏️</button>
              <button class="button-icon button-delete" @click="confirmDeletePatient(patient)" title="Delete Patient">🗑️</button>
              <!-- Add more actions like 'View Details' -->
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="!isLoading && searchTerm && filteredPatients.length === 0" class="no-results">
      <p>No patients found matching your search criteria "{{ searchTerm }}".</p>
    </div>

    <div v-else class="no-patients">
      <p>No patients found. Click "Add New Patient" to get started.</p>
    </div>

    <!-- Modals for Add/Edit and Confirmation -->
    <!-- <AddEditPatientModal v-if="showAddEditModal" :patient="selectedPatient" @close="closeAddEditModal" @save="handleSavePatient" /> -->
    <!-- <ConfirmationModal v-if="showDeleteConfirmModal" @confirm="deletePatientConfirmed" @cancel="closeDeleteConfirmModal" title="Confirm Deletion"> -->
      <!-- <p>Are you sure you want to delete patient {{ patientToDelete?.name }}?</p> -->
    <!-- </ConfirmationModal> -->

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
// import AddEditPatientModal from './modals/AddEditPatientModal.vue'; // Placeholder for modal component
// import ConfirmationModal from './modals/ConfirmationModal.vue'; // Placeholder for modal component

const isLoading = ref(true);
const patients = ref([]);
const searchTerm = ref('');

// const showAddEditModal = ref(false);
// const selectedPatient = ref(null);
// const showDeleteConfirmModal = ref(false);
// const patientToDelete = ref(null);

// Simulate fetching patient data
const fetchPatientsData = async () => {
  isLoading.value = true;
  await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
  patients.value = [
    { id: 1, name: 'Alice Wonderland Smith', dob: '1990-05-15', mrn: 'MRN12345', gender: 'Female', contact: '555-1234', address: '123 Fantasy Lane' },
    { id: 2, name: 'Robert "Bob" Johnson Jr.', dob: '1985-11-20', mrn: 'MRN67890', gender: 'Male', contact: '555-5678', address: '456 Reality Ave' },
    { id: 3, name: 'Charles "Charlie" Brown III', dob: '2000-01-01', mrn: 'MRN11223', gender: 'Male', contact: '555-9012', address: '789 Comic Strip' },
    { id: 4, name: 'Diana Prince', dob: '1975-03-22', mrn: 'MRN44556', gender: 'Female', contact: '555-3456', address: 'Themyscira Island' },
  ];
  isLoading.value = false;
};

onMounted(() => {
  fetchPatientsData();
});

const filteredPatients = computed(() => {
  if (!searchTerm.value) {
    return patients.value;
  }
  const lowerSearchTerm = searchTerm.value.toLowerCase();
  return patients.value.filter(patient =>
    patient.name.toLowerCase().includes(lowerSearchTerm) ||
    patient.mrn.toLowerCase().includes(lowerSearchTerm)
  );
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const openAddPatientModal = () => {
  // selectedPatient.value = null; // For a new patient
  // showAddEditModal.value = true;
  console.log('Open Add Patient Modal');
  // TODO: Implement actual modal opening
};

const editPatient = (patient) => {
  // selectedPatient.value = { ...patient }; // Pass a copy to avoid direct mutation
  // showAddEditModal.value = true;
  console.log('Edit patient:', patient);
  // TODO: Implement actual modal opening for editing
};

const confirmDeletePatient = (patient) => {
  // patientToDelete.value = patient;
  // showDeleteConfirmModal.value = true;
  console.log('Confirm delete patient:', patient);
  // TODO: Implement actual confirmation modal
};

// const closeAddEditModal = () => {
//   showAddEditModal.value = false;
//   selectedPatient.value = null;
// };

// const handleSavePatient = (savedPatient) => {
//   if (savedPatient.id) { // Existing patient
//     const index = patients.value.findIndex(p => p.id === savedPatient.id);
//     if (index !== -1) patients.value.splice(index, 1, savedPatient);
//   } else { // New patient
//     savedPatient.id = Date.now(); // Simple ID generation for demo
//     patients.value.push(savedPatient);
//   }
//   closeAddEditModal();
//   // TODO: Add API call to save patient to backend
//   console.log('Patient saved:', savedPatient);
// };

// const deletePatientConfirmed = () => {
//   if (patientToDelete.value) {
//     patients.value = patients.value.filter(p => p.id !== patientToDelete.value.id);
//     // TODO: Add API call to delete patient from backend
//     console.log('Patient deleted:', patientToDelete.value);
//   }
//   closeDeleteConfirmModal();
// };

// const closeDeleteConfirmModal = () => {
//   showDeleteConfirmModal.value = false;
//   patientToDelete.value = null;
// };

</script>

<style scoped>
.patient-management-screen {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.patient-management-screen h1 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  width: 300px; /* Adjust as needed */
}

.button-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.button-primary:hover {
  background-color: #0056b3;
}

.loading-indicator,
.no-results,
.no-patients {
  text-align: center;
  color: #666;
  margin-top: 30px;
  font-size: 1.1em;
}

.patient-table-container {
  overflow-x: auto; /* For responsiveness on smaller screens */
}

.patient-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.patient-table th,
.patient-table td {
  border: 1px solid #ddd;
  padding: 10px 12px;
  text-align: left;
  font-size: 14px;
}

.patient-table th {
  background-color: #f8f9fa;
  color: #333;
  font-weight: bold;
}

.patient-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.patient-table tbody tr:hover {
  background-color: #f1f1f1;
}

.button-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px; /* Adjust icon size */
  padding: 5px;
  margin-right: 8px;
  color: #007bff;
  transition: color 0.2s ease;
}

.button-icon:hover {
  color: #0056b3;
}

.button-delete:hover {
  color: #dc3545; /* Red for delete actions */
}

/* Add styles for modals if/when implemented */

</style>