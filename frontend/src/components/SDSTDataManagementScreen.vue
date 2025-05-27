<template>
  <div class="sdst-management-container">
    <h1>SDST Data Management</h1>

    <div class="tabs">
      <button
        :class="{ active: activeTab === 'surgeryTypes' }"
        @click="activeTab = 'surgeryTypes'"
      >
        Manage Surgery Types
      </button>
      <button
        :class="{ active: activeTab === 'sdstMatrix' }"
        @click="activeTab = 'sdstMatrix'"
      >
        Manage SDST Matrix
      </button>
      <button
        :class="{ active: activeTab === 'initialSetup' }"
        @click="activeTab = 'initialSetup'"
      >
        Manage Initial Setup Times
      </button>
      <!-- Optional Tab for OR-Specific SDST could be added here -->
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'surgeryTypes'">
        <h2>Manage Surgery Types</h2>
        <p>Manage the distinct types of surgeries used for SDST calculations.</p>

        <button class="add-button" @click="addSurgeryType">Add New Surgery Type</button>

        <table class="data-table">
          <thead>
            <tr>
              <th>Surgery Type Name</th>
              <th>Code</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <!-- Bind to surgeryTypes data -->
            <tr v-for="type in surgeryTypes" :key="type.id">
              <td>{{ type.name }}</td>
              <td>{{ type.code }}</td>
              <td>{{ type.description }}</td>
              <td>
                <button class="action-button edit-button" @click="editSurgeryType(type)">Edit</button>
                <button class="action-button delete-button" @click="deleteSurgeryType(type.id)">Delete</button>
              </td>
            </tr>
             <tr v-if="surgeryTypes.length === 0">
                <td colspan="4" class="no-items">No surgery types defined.</td>
            </tr>
          </tbody>
        </table>

      </div>

      <div v-if="activeTab === 'sdstMatrix'">
        <h2>Manage SDST Matrix</h2>
        <p>Define the setup time required when transitioning between different surgery types in an OR. Times are in minutes.</p>
         <p>Needs input validation and potentially color-coding for durations.</p>
         <!-- Placeholder for SDST Matrix Grid/Input -->
         <div class="sdst-matrix-container">
            <table class="sdst-matrix-table data-table">
                <thead>
                    <tr>
                        <th>From \ To</th>
                         <th v-for="toType in surgeryTypes" :key="'to-'+toType.id">{{ toType.name }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="fromType in surgeryTypes" :key="'from-'+fromType.id">
                         <th>{{ fromType.name }}</th>
                         <td v-for="toType in surgeryTypes" :key="'sdst-'+fromType.id+'-'+toType.id">
                             <!-- Bind input to sdstMatrix data -->
                             <input type="number" v-model.number="sdstMatrix[fromType.id][toType.id]" min="0">
                         </td>
                    </tr>
                    <tr v-if="surgeryTypes.length === 0">
                        <td :colspan="surgeryTypes.length + 1" class="no-items">Define Surgery Types first to manage the matrix.</td>
                    </tr>
                </tbody>
            </table>
         </div>
          <button class="save-matrix-button action-button edit-button" @click="saveMatrixChanges">Save Matrix Changes</button>

      </div>

      <div v-if="activeTab === 'initialSetup'">
        <h2>Manage Initial Setup Times</h2>
        <p>Define the initial setup time for the first surgery of a specific type in an OR for the day.</p>
         <table class="data-table">
          <thead>
            <tr>
              <th>Surgery Type Name</th>
              <th>Initial Setup Time (minutes)</th>
               <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <!-- Bind to initialSetupTimes data -->
            <tr v-for="setupTime in initialSetupTimes" :key="'initial-'+setupTime.typeId">
              <td>{{ getSurgeryTypeName(setupTime.typeId) }}</td>
              <td><input type="number" v-model.number="setupTime.time" min="0"></td>
               <td>
                <button class="action-button edit-button" @click="editInitialSetup(setupTime)">Edit</button>
                <button class="action-button delete-button" @click="deleteInitialSetup(setupTime.typeId)">Delete</button>
              </td>
            </tr>
             <tr v-if="initialSetupTimes.length === 0">
                <td colspan="3" class="no-items">No initial setup times defined.</td>
            </tr>
          </tbody>
        </table>
        <button class="add-button" @click="addInitialSetup">Add Initial Setup Time</button>
      </div>
    </div>

     <div class="action-buttons">
      <!-- Placeholder data management actions - may move into tabs later -->
      <button>Import Data</button>
      <button>Export Data</button>
      <button>Settings</button>
       <button @click="validateDataIntegrity">Validate Data Integrity</button> <!-- Based on FR-SDSTDATA-006 -->
    </div>

    <!-- Add/Edit Surgery Type Modal -->
    <AddEditSurgeryTypeModal
      v-if="showSurgeryTypeModal"
      :initialData="surgeryTypeToEdit"
      :isEditing="!!surgeryTypeToEdit"
      @save="handleSaveSurgeryType"
      @cancel="handleCancelSurgeryType"
    />

    <!-- Add/Edit Initial Setup Time Modal -->
     <AddEditInitialSetupModal
        v-if="showInitialSetupModal"
        :initialData="initialSetupToEdit"
        :isEditing="!!initialSetupToEdit"
        :surgeryTypes="surgeryTypes"
        @save="handleSaveInitialSetup"
        @cancel="handleCancelInitialSetup"
     />

  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import AddEditSurgeryTypeModal from './AddEditSurgeryTypeModal.vue';
import AddEditInitialSetupModal from './AddEditInitialSetupModal.vue';

const activeTab = ref('surgeryTypes'); // Default active tab

// --- State for Add/Edit Surgery Type Modal ---
const showSurgeryTypeModal = ref(false);
const surgeryTypeToEdit = ref(null); // Holds data of the type being edited, null for adding
// ---------------------------------------------

// --- State for Add/Edit Initial Setup Time Modal ---
const showInitialSetupModal = ref(false);
const initialSetupToEdit = ref(null); // Holds data of the initial setup time being edited, null for adding
// ---------------------------------------------------

// --- Simulated Data for Surgery Types ---
const surgeryTypes = ref([
    { id: 1, name: 'Cardiac - CABG', code: 'CABG', description: 'Coronary Artery Bypass Grafting' },
    { id: 2, name: 'Orthopedic - Knee Replacement', code: 'TKR', description: 'Total Knee Replacement' },
    { id: 3, name: 'General - Appendectomy', code: 'APP', description: 'Surgical removal of the appendix' },
]);
// ----------------------------------------

// --- Simulated Data for Initial Setup Times ---
// In a real app, this data would link to surgery types by ID
const initialSetupTimes = ref([
    { typeId: 1, time: 60 }, // CABG
    { typeId: 2, time: 45 }, // TKR
    { typeId: 3, time: 30 }, // Appendectomy
]);
// ----------------------------------------------

// --- Simulated Data for SDST Matrix ---
// Represent as a nested object: { fromTypeId: { toTypeId: setupTime, ... }, ...}
const sdstMatrix = ref({});

// Initialize matrix when surgery types change (or on component mount)
watch(surgeryTypes, (newTypes) => {
    console.log('Surgery types changed. Initializing/updating SDST matrix.');
    const newMatrix = {};
    const oldMatrix = sdstMatrix.value; // Preserve old matrix data

    newTypes.forEach(fromType => {
        newMatrix[fromType.id] = {};
        newTypes.forEach(toType => {
            // Preserve existing value if available, otherwise use a default
            const existingTime = oldMatrix[fromType.id]?.[toType.id];
             newMatrix[fromType.id][toType.id] = existingTime !== undefined ? existingTime : (fromType.id === toType.id) ? 0 : 15; // Preserve existing or set default
        });
    });
    sdstMatrix.value = newMatrix;
    console.log('SDST matrix initialized/updated:', sdstMatrix.value);
}, { immediate: true, deep: true }); // Run immediately and watch deeply for nested changes
// -------------------------------------


// --- Helper to get Surgery Type Name by ID ---
const getSurgeryTypeName = (typeId) => {
    const type = surgeryTypes.value.find(t => t.id === typeId);
    return type ? type.name : 'Unknown Type';
};
// ---------------------------------------------

// --- Surgery Type Management Logic ---
const addSurgeryType = () => {
    console.log('Add New Surgery Type clicked');
    surgeryTypeToEdit.value = null; // Clear any previous data
    showSurgeryTypeModal.value = true; // Show the modal for adding
};

const editSurgeryType = (type) => {
    console.log('Edit Surgery Type clicked:', type);
    surgeryTypeToEdit.value = { ...type }; // Set the data to be edited (create a copy)
    showSurgeryTypeModal.value = true; // Show the modal for editing
};

const deleteSurgeryType = (typeId) => {
    console.log('Attempting to delete Surgery Type with ID:', typeId);
    // In a real app, show a confirmation dialog first (e.g., using a confirmation modal)
    const confirmDelete = confirm('Are you sure you want to delete this Surgery Type? This will also remove associated SDST matrix entries and initial setup times.');

    if (confirmDelete) {
         // Simulate deletion from the list
         surgeryTypes.value = surgeryTypes.value.filter(type => type.id !== typeId);
         // Note: Deleting a surgery type would also require updating the SDST matrix and initial setup times
         // The watch effect on surgeryTypes will handle matrix update logic (re-initializes with remaining types)
         initialSetupTimes.value = initialSetupTimes.value.filter(item => item.typeId !== typeId);
         console.log('Surgery Type deleted.');
         // Show a success message
    } else {
         console.log('Surgery Type deletion cancelled.');
    }
};

const handleSaveSurgeryType = (savedType) => {
    console.log('Saving Surgery Type:', savedType);
    if (savedType.id) {
        // Editing existing type
        const index = surgeryTypes.value.findIndex(type => type.id === savedType.id);
        if (index !== -1) {
            surgeryTypes.value[index] = savedType;
             console.log('Surgery Type updated.', savedType);
            // Show a success message
        }
    } else {
        // Adding new type
        const newId = surgeryTypes.value.length > 0 ? Math.max(...surgeryTypes.value.map(type => type.id)) + 1 : 1;
        surgeryTypes.value.push({ ...savedType, id: newId });
         console.log('New Surgery Type added.', { ...savedType, id: newId });
        // Show a success message
    }
    handleCancelSurgeryType(); // Close modal after save
};

const handleCancelSurgeryType = () => {
    console.log('Cancelling Surgery Type modal');
    showSurgeryTypeModal.value = false;
    surgeryTypeToEdit.value = null; // Clear editing data
};
// -----------------------------------------------------

// --- Initial Setup Time Management Logic ---
const addInitialSetup = () => {
    console.log('Add Initial Setup Time clicked');
    initialSetupToEdit.value = null; // Clear any previous data
    showInitialSetupModal.value = true; // Show the modal for adding
};

const editInitialSetup = (setupTime) => {
    console.log('Edit Initial Setup Time clicked:', setupTime);
    initialSetupToEdit.value = { ...setupTime }; // Set the data to be edited (create a copy)
    showInitialSetupModal.value = true; // Show the modal for editing
};

const deleteInitialSetup = (typeId) => {
    console.log('Attempting to delete Initial Setup Time for type ID:', typeId);
    // In a real app, show a confirmation dialog first
    const confirmDelete = confirm('Are you sure you want to delete this Initial Setup Time entry?');

    if (confirmDelete) {
         // Simulate deletion from the list
         initialSetupTimes.value = initialSetupTimes.value.filter(item => item.typeId !== typeId);
         console.log('Initial Setup Time deleted for type ID:', typeId);
         // Show a success message
    } else {
         console.log('Initial Setup Time deletion cancelled.');
    }
};

const handleSaveInitialSetup = (savedSetupTime) => {
     console.log('Saving Initial Setup Time:', savedSetupTime);
     const index = initialSetupTimes.value.findIndex(item => item.typeId === savedSetupTime.typeId);

    if (index !== -1) {
        // Editing existing initial setup time
        initialSetupTimes.value[index] = savedSetupTime;
         console.log('Initial Setup Time updated.', savedSetupTime);
        // Show a success message
    } else {
        // Adding new initial setup time
        // Check if a setup time for this type already exists
        const existing = initialSetupTimes.value.find(item => item.typeId === savedSetupTime.typeId);
        if (existing) {
             console.warn('Initial Setup Time for this Surgery Type already exists. Updating instead of adding.');
            existing.time = savedSetupTime.time;
             console.log('Initial Setup Time updated (via add form).', existing);
            // Show a success message
        } else {
            // Ensure the surgery type exists before adding setup time
            const typeExists = surgeryTypes.value.some(type => type.id === savedSetupTime.typeId);
            if (typeExists) {
                 initialSetupTimes.value.push({ ...savedSetupTime });
                 console.log('New Initial Setup Time added.', { ...savedSetupTime });
                // Show a success message
            } else {
                 console.error('Cannot add Initial Setup Time: Surgery Type not found.', savedSetupTime.typeId);
                // In a real app, show an error message to the user
            }
        }
    }
     handleCancelInitialSetup(); // Close modal after save
};

const handleCancelInitialSetup = () => {
    console.log('Cancelling Initial Setup Time modal');
    showInitialSetupModal.value = false;
    initialSetupToEdit.value = null; // Clear editing data
};
// ----------------------------------------------------------

// --- SDST Matrix Management Logic ---
const saveMatrixChanges = () => {
    console.log('Attempting to save SDST Matrix changes.');

    // First, validate the data integrity (e.g., check for negative values, required entries)
    const validationResult = validateDataIntegrity(); // Call the validation method, it returns object

    if (validationResult.isValid) {
         console.log('SDST Matrix data is valid.', sdstMatrix.value);
         // Confirmation step before saving significant changes (Section 4.4)
         const confirmSave = confirm('Are you sure you want to save changes to the SDST Matrix? This affects all future scheduling.');

         if (confirmSave) {
             console.log('User confirmed save. Simulating save:', sdstMatrix.value);
            // Placeholder for sending the updated matrix data to the backend (FR-SDSTDATA-005)
            // In a real app, you would send sdstMatrix.value to your API
            // Show a success message (e.g., using a notification system)
         } else {
              console.log('SDST Matrix save cancelled by user.');
             // Show a cancelled message
         }

    } else {
         console.warn('SDST Matrix data is invalid. Cannot save. Errors:', validationResult.errors);
        // Show validation error messages to the user (implementation needed using a notification system or inline errors)
    }

};

// --- Data Integrity Validation (Placeholder) ---
// Returns an object { isValid: boolean, errors: string[] }
const validateDataIntegrity = () => {
     console.log('Running Data Integrity Validation for SDST Data...');

     let isValid = true;
     let validationErrors = [];

    // Validation: Check for negative setup times in the matrix
    console.log('Validating SDST Matrix values...');
    for (const fromTypeId in sdstMatrix.value) {
        for (const toTypeId in sdstMatrix.value[fromTypeId]) {
            const time = sdstMatrix.value[fromTypeId][toTypeId];
            // Check if time is a number, not null/undefined, and is negative
            if (typeof time === 'number' && time !== null && time !== undefined && time < 0) {
                validationErrors.push(`SDST from ${getSurgeryTypeName(parseInt(fromTypeId))} to ${getSurgeryTypeName(parseInt(toTypeId))} cannot be negative.`);
                isValid = false;
            }
             // Add other matrix validation rules here (e.g., check if all combinations are filled if required)
        }
    }

     // Validation: Check if all current surgery types have a corresponding initial setup time entry
     console.log('Validating Initial Setup Times presence for all Surgery Types...');
     const definedInitialSetupTypes = initialSetupTimes.value.map(item => item.typeId);
     surgeryTypes.value.forEach(type => {
         if (!definedInitialSetupTypes.includes(type.id)) {
             validationErrors.push(`Initial Setup Time is missing for Surgery Type: ${type.name}`);
             isValid = false;
         }
     });

    // Add other data integrity validation rules here (e.g., check for duplicate surgery codes, ensure type IDs in setupTimes/matrix match existing surgeryTypes)
    console.log('Validation complete.');

     return { isValid, errors: validationErrors };
};
// -----------------------------------------------

</script>

<style scoped>
.sdst-management-container {
  padding: 20px;
  background-color: var(--color-white); /* Match layout background */
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h1 {
    color: var(--color-very-dark-gray);
    margin-bottom: 20px;
}

.tabs {
  margin-bottom: 20px;
  border-bottom: 1px solid var(--color-gray);
}

.tabs button {
  background-color: transparent;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
  font-size: 1em;
  color: var(--color-dark-gray);
  transition: color 0.25s ease, border-bottom-color 0.25s ease;
  margin-right: 5px; /* Space between buttons */
  border-bottom: 2px solid transparent; /* Underline effect */
}

.tabs button.active {
  color: var(--color-primary);
  font-weight: 600;
  border-bottom-color: var(--color-primary); /* Highlight active tab */
}

.tabs button:hover:not(.active) {
    color: var(--color-primary-dark); /* Darker on hover */
}

.tab-content {
  padding: 20px 0;
}

.tab-content h2 {
    color: var(--color-very-dark-gray);
    margin-bottom: 15px;
    font-size: 1.4em;
}

/* --- Table Styles --- */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.data-table th,
.data-table td {
  border: 1px solid var(--color-mid-light-gray);
  padding: 10px 12px;
  text-align: left;
}

.data-table th {
  background-color: var(--color-light-gray);
  font-weight: 600;
  color: var(--color-very-dark-gray);
}

.data-table tbody tr:nth-child(even) {
  background-color: var(--color-background); /* Zebrabar-striping */
}

.data-table tbody tr:hover {
  background-color: var(--color-hover-gray); /* Highlight row on hover */
}

.action-button {
    padding: 5px 10px;
    margin-right: 5px;
    border: 1px solid;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
}

.edit-button {
    background-color: var(--color-primary-light);
    color: var(--color-primary-dark);
    border-color: var(--color-primary);
}

.edit-button:hover {
    background-color: var(--color-primary);
    color: var(--color-white);
}

.delete-button {
    background-color: var(--color-danger-light);
    color: var(--color-danger-dark);
    border-color: var(--color-danger);
}

.delete-button:hover {
    background-color: var(--color-danger);
    color: var(--color-white);
}

.add-button {
   padding: 8px 15px;
   background-color: var(--color-success);
   color: var(--color-white);
   border: none;
   border-radius: 4px;
   cursor: pointer;
   margin-bottom: 15px; /* Space below add button */
   transition: background-color 0.25s ease;
}

.add-button:hover {
    background-color: var(--color-success-dark);
}
/* --- End Table Styles --- */

/* --- SDST Matrix Styles --- */
.sdst-matrix-container {
    overflow-x: auto; /* Add horizontal scroll for wide matrices */
    margin-bottom: 20px;
}

.sdst-matrix-table {
    min-width: 600px; /* Ensure some minimum width */
}

.sdst-matrix-table th:first-child {
    position: sticky;
    left: 0;
    background-color: var(--color-light-gray); /* Sticky header background */
    z-index: 2; /* Ensure it's above scrolling cells */
}

.sdst-matrix-table tbody tr th {
     position: sticky;
    left: 0;
     background-color: var(--color-light-gray); /* Sticky header background */
     z-index: 1; /* Ensure it's above scrolling cells */
}

.sdst-matrix-table td input[type="number"] {
    width: 80px; /* Fixed width for input cells */
    padding: 5px;
    border: 1px solid var(--color-gray);
    border-radius: 4px;
    text-align: center; /* Center numbers */
}

.save-matrix-button {
    margin-top: 10px; /* Space above save button */
}

/* --- End SDST Matrix Styles --- */


.action-buttons button {
    padding: 8px 15px;
    margin-left: 10px; /* Space between buttons */
    border: 1px solid var(--color-primary);
    border-radius: 4px;
    background-color: var(--color-primary);
    color: var(--color-white);
    cursor: pointer;
    transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease;
}

.action-buttons button:hover {
    background-color: var(--color-primary-dark);
     border-color: var(--color-primary-dark);
}

/* Style for secondary buttons if needed, e.g., Import/Export */
.action-buttons button:nth-child(-n+2) { /* Apply to first two buttons */
   background-color: var(--color-light-gray);
   color: var(--color-very-dark-gray);
   border-color: var(--color-gray);
}

.action-buttons button:nth-child(-n+2):hover {
    background-color: var(--color-gray);
     color: var(--color-very-dark-gray);
}

/* Specific style for Validate Data Integrity button */
.action-buttons button:last-child {
    background-color: var(--color-secondary);
     border-color: var(--color-secondary);
     color: var(--color-white);
}

.action-buttons button:last-child:hover {
    background-color: #5a6268;
     border-color: #5a6268;
}

</style>