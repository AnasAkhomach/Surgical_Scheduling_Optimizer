<template>
  <div class="resource-management-container">
    <h1>Resource Management</h1>

    <div class="tabs">
      <button
        :class="{ active: activeTab === 'ors' }"
        @click="activeTab = 'ors'"
      >Operating Rooms</button>
      <button
        :class="{ active: activeTab === 'staff' }"
        @click="activeTab = 'staff'"
      >Staff</button>
      <button
        :class="{ active: activeTab === 'equipment' }"
        @click="activeTab = 'equipment'"
      >Equipment</button>
    </div>

    <div class="tab-content">
      <!-- Operating Rooms Section -->
      <div v-if="activeTab === 'ors'" class="resource-section">
        <h2>Operating Rooms List</h2>
        <button class="button-primary" @click="openOrFormForAdd" v-if="!showAddOrForm">Add New OR</button>
        <AddOrForm
          v-if="showAddOrForm"
          :or-to-edit="currentOrToEdit"
          @cancel="handleCancelOrForm"
          @save="handleSaveOr"
        />
        <div v-if="isLoading" class="loading-indicator">
          <div class="spinner"></div>
          <p>Loading operating rooms...</p>
        </div>
        <table v-else>
          <thead>
            <tr>
              <th scope="col">Name/ID</th>
              <th scope="col">Location</th>
              <th scope="col">Status</th>
              <th scope="col">Primary Service</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="or in operatingRooms" :key="or.id">
              <td>{{ or.name }}</td>
              <td>{{ or.location }}</td>
              <td :class="'status-' + or.status.toLowerCase().replace(' ', '-')">{{ or.status }}</td>
              <td>{{ or.primaryService }}</td>
              <td>
                <button class="button-small" @click="openOrFormForEdit(or)">View/Edit</button>
                <button class="button-small button-danger" @click="deleteOr(or)">Delete</button>
              </td>
            </tr>
            <tr v-if="operatingRooms.length === 0">
              <td colspan="5" class="no-items">No operating rooms found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Staff Section -->
      <div v-if="activeTab === 'staff'" class="resource-section">
        <h2>Staff List</h2>
        <button class="button-primary" @click="openStaffFormForAdd" v-if="!showAddStaffForm">Add New Staff</button>
        <AddStaffForm
          v-if="showAddStaffForm"
          :staff-to-edit="currentStaffToEdit"
          @cancel="handleCancelStaffForm"
          @save="handleSaveStaff"
        />
        <div v-if="isLoading" class="loading-indicator">
          <div class="spinner"></div>
          <p>Loading staff data...</p>
        </div>
        <table v-else>
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Role</th>
              <th scope="col">Specialization(s)</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="person in staff" :key="person.id">
              <td>{{ person.name }}</td>
              <td>{{ person.role }}</td>
              <td>{{ person.specializations.join(', ') }}</td>
              <td :class="'status-' + person.status.toLowerCase().replace(' ', '-')">{{ person.status }}</td>
              <td>
                <button class="button-small" @click="openStaffFormForEdit(person)">View/Edit</button>
                <button class="button-small button-danger" @click="deleteStaff(person)">Delete</button>
              </td>
            </tr>
            <tr v-if="staff.length === 0">
              <td colspan="5" class="no-items">No staff found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Equipment Section -->
      <div v-if="activeTab === 'equipment'" class="resource-section">
        <h2>Equipment List</h2>
        <button class="button-primary" @click="openEquipmentFormForAdd" v-if="!showAddEquipmentForm">Add New Equipment</button>
        <AddEquipmentForm
          v-if="showAddEquipmentForm"
          :equipment-to-edit="currentEquipmentToEdit"
          @cancel="handleCancelEquipmentForm"
          @save="handleSaveEquipment"
        />
        <div v-if="isLoading" class="loading-indicator">
          <div class="spinner"></div>
          <p>Loading equipment data...</p>
        </div>
        <table v-else>
          <thead>
            <tr>
              <th scope="col">Name/ID</th>
              <th scope="col">Type</th>
              <th scope="col">Status</th>
              <th scope="col">Location</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in equipment" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.type }}</td>
              <td :class="'status-' + item.status.toLowerCase().replace(' ', '-')">{{ item.status }}</td>
              <td>{{ item.location }}</td>
              <td>
                <button class="button-small" @click="openEquipmentFormForEdit(item)">View/Edit</button>
                <button class="button-small button-danger" @click="deleteEquipment(item)">Delete</button>
              </td>
            </tr>
            <tr v-if="equipment.length === 0">
              <td colspan="5" class="no-items">No equipment found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="showConfirmationModal"
      :title="confirmationTitle"
      :message="confirmationMessage"
      @confirm="handleConfirmDelete"
      @cancel="handleCancelDelete"
    />

    <!-- Resource Availability Calendar Modal -->
    <div v-if="showAvailabilityModal" class="modal-overlay">
      <div class="modal-content availability-modal">
        <div class="modal-header">
          <h3>Resource Availability</h3>
          <button class="close-button" @click="closeAvailabilityModal">✕</button>
        </div>
        <div class="modal-body">
          <ResourceAvailabilityCalendar
            v-if="selectedResourceForAvailability"
            :resource="selectedResourceForAvailability"
            :resourceType="selectedResourceType"
            @update="handleAvailabilityUpdate"
            @close="closeAvailabilityModal"
          />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'vue-toastification';
import { useResourceStore } from '@/stores/resourceStore';
import { storeToRefs } from 'pinia';
import AddOrForm from './AddOrForm.vue';
import AddStaffForm from './AddStaffForm.vue';
import AddEquipmentForm from './AddEquipmentForm.vue';
import ConfirmationModal from './ConfirmationModal.vue';
import ResourceAvailabilityCalendar from './ResourceAvailabilityCalendar.vue';

const toast = useToast();
const activeTab = ref('ors'); // Default active tab

// Initialize the resource store
const resourceStore = useResourceStore();
const { isLoading, error, operatingRooms, staff, equipment } = storeToRefs(resourceStore);

// Load resources when component is mounted
onMounted(async () => {
  await resourceStore.loadOperatingRooms();
  // TODO: Add loadStaff() and loadEquipment() when implemented
});

// --- Resource Availability Calendar State & Logic ---
const showAvailabilityModal = ref(false);
const selectedResourceForAvailability = ref(null);
const selectedResourceType = ref('');

const openAvailabilityCalendar = (resource, type) => {
  selectedResourceForAvailability.value = resource;
  selectedResourceType.value = type;
  showAvailabilityModal.value = true;
};

const closeAvailabilityModal = () => {
  showAvailabilityModal.value = false;
  selectedResourceForAvailability.value = null;
  selectedResourceType.value = '';
};

const handleAvailabilityUpdate = () => {
  toast.success('Resource availability updated successfully!');
  // No need to close the modal here, let the user continue editing if needed
};

// --- Confirmation Modal State & Logic ---
const showConfirmationModal = ref(false);
const itemToDelete = ref(null);
const itemTypeToDelete = ref(''); // 'or', 'staff', 'equipment'
const confirmationTitle = ref('Confirm Deletion');
const confirmationMessage = ref('Are you sure you want to delete this item? This action cannot be undone.');

const openConfirmationModal = (item, type, title, message) => {
  itemToDelete.value = item;
  itemTypeToDelete.value = type;
  confirmationTitle.value = title || 'Confirm Deletion';
  confirmationMessage.value = message || 'Are you sure you want to delete this item? This action cannot be undone.';
  showConfirmationModal.value = true;
};

const handleConfirmDelete = async () => {
  if (!itemToDelete.value || !itemTypeToDelete.value) return;

  const item = itemToDelete.value;
  const type = itemTypeToDelete.value;
  const itemName = item.name;
  const itemTypeDisplay = type.charAt(0).toUpperCase() + type.slice(1);

  try {
    let result;

    // Call the appropriate store method based on the item type
    if (type === 'or') {
      result = await resourceStore.deleteOperatingRoom(item.id);
    } else if (type === 'staff') {
      result = await resourceStore.deleteStaff(item.id);
    } else if (type === 'equipment') {
      result = await resourceStore.deleteEquipment(item.id);
    }

    if (result.success) {
      console.log(`Deleted ${type}:`, item);
      toast.success(`${itemTypeDisplay} '${itemName}' deleted successfully!`);
    } else {
      throw new Error(result.error || 'Unknown error');
    }
  } catch (error) {
    console.error(`Failed to delete ${type}:`, item, error);
    toast.error(`Failed to delete ${itemTypeDisplay} '${itemName}': ${error.message}`);
  }

  handleCancelDelete(); // Close modal and reset state regardless of outcome
};

const handleCancelDelete = () => {
  showConfirmationModal.value = false;
  itemToDelete.value = null;
  itemTypeToDelete.value = '';
  confirmationTitle.value = 'Confirm Deletion'; // Reset to default
  confirmationMessage.value = 'Are you sure you want to delete this item? This action cannot be undone.'; // Reset to default
};

// --- OR Management State & Logic ---
const showAddOrForm = ref(false);
const currentOrToEdit = ref(null);

// Computed property for active operating rooms
const activeOperatingRooms = computed(() => resourceStore.activeOperatingRooms);

const openOrFormForAdd = () => {
  currentOrToEdit.value = null;
  showAddOrForm.value = true;
};

const openOrFormForEdit = (or) => {
  currentOrToEdit.value = { ...or };
  showAddOrForm.value = true;
};

const handleCancelOrForm = () => {
  showAddOrForm.value = false;
  currentOrToEdit.value = null;
};

const handleSaveOr = async (orData) => {
  if (isLoading.value) return; // Prevent multiple submissions

  try {
    if (currentOrToEdit.value) {
      // Editing existing OR
      const result = await resourceStore.updateOperatingRoom(orData.id, orData);
      if (result.success) {
        toast.success(`Operating Room '${orData.name}' updated successfully!`);
      } else {
        toast.error(`Failed to update Operating Room: ${result.error}`);
      }
    } else {
      // Adding new OR
      const result = await resourceStore.addOperatingRoom(orData);
      if (result.success) {
        toast.success(`Operating Room '${orData.name}' added successfully!`);
      } else {
        toast.error(`Failed to add Operating Room: ${result.error}`);
      }
    }
    showAddOrForm.value = false;
    currentOrToEdit.value = null;
  } catch (err) {
    toast.error(`An error occurred: ${err.message}`);
  }
};

const viewOrAvailability = (orItem) => {
  openAvailabilityCalendar(orItem, 'operatingRoom');
};

const deleteOr = (orItem) => {
  openConfirmationModal(
    orItem,
    'or',
    'Delete Operating Room?',
    `Are you sure you want to delete the operating room "${orItem.name}"? This action cannot be undone.`
  );
};

// --- Staff Management State & Logic ---
const showAddStaffForm = ref(false);
const currentStaffToEdit = ref(null);

// Computed property for active staff
const activeStaff = computed(() => resourceStore.activeStaff);

const openStaffFormForAdd = () => {
  currentStaffToEdit.value = null;
  showAddStaffForm.value = true;
};

const openStaffFormForEdit = (staffMember) => {
  currentStaffToEdit.value = { ...staffMember };
  showAddStaffForm.value = true;
};

const handleCancelStaffForm = () => {
  showAddStaffForm.value = false;
  currentStaffToEdit.value = null;
};

const handleSaveStaff = async (staffData) => {
  if (isLoading.value) return; // Prevent multiple submissions

  try {
    if (currentStaffToEdit.value) {
      // Editing existing staff
      const result = await resourceStore.updateStaff(staffData.id, staffData);
      if (result.success) {
        toast.success(`Staff member '${staffData.name}' updated successfully!`);
      } else {
        toast.error(`Failed to update staff member: ${result.error}`);
      }
    } else {
      // Adding new staff
      const result = await resourceStore.addStaff(staffData);
      if (result.success) {
        toast.success(`Staff member '${staffData.name}' added successfully!`);
      } else {
        toast.error(`Failed to add staff member: ${result.error}`);
      }
    }
    showAddStaffForm.value = false;
    currentStaffToEdit.value = null;
  } catch (err) {
    toast.error(`An error occurred: ${err.message}`);
  }
};

const viewStaffAvailability = (staffItem) => {
  openAvailabilityCalendar(staffItem, 'staff');
};

const deleteStaff = (staffItem) => {
  openConfirmationModal(
    staffItem,
    'staff',
    'Delete Staff Member?',
    `Are you sure you want to delete staff member "${staffItem.name}"? This action cannot be undone.`
  );
};

// --- Equipment Management State & Logic ---
const showAddEquipmentForm = ref(false);
const currentEquipmentToEdit = ref(null);

// Computed property for available equipment
const availableEquipment = computed(() => resourceStore.availableEquipment);

const openEquipmentFormForAdd = () => {
  currentEquipmentToEdit.value = null;
  showAddEquipmentForm.value = true;
};

const openEquipmentFormForEdit = (equipmentItem) => {
  currentEquipmentToEdit.value = { ...equipmentItem };
  showAddEquipmentForm.value = true;
};

const handleCancelEquipmentForm = () => {
  showAddEquipmentForm.value = false;
  currentEquipmentToEdit.value = null;
};

const handleSaveEquipment = async (equipmentData) => {
  if (isLoading.value) return; // Prevent multiple submissions

  try {
    if (currentEquipmentToEdit.value) {
      // Editing existing equipment
      const result = await resourceStore.updateEquipment(equipmentData.id, equipmentData);
      if (result.success) {
        toast.success(`Equipment '${equipmentData.name}' updated successfully!`);
      } else {
        toast.error(`Failed to update equipment: ${result.error}`);
      }
    } else {
      // Adding new equipment
      const result = await resourceStore.addEquipment(equipmentData);
      if (result.success) {
        toast.success(`Equipment '${equipmentData.name}' added successfully!`);
      } else {
        toast.error(`Failed to add equipment: ${result.error}`);
      }
    }
    showAddEquipmentForm.value = false;
    currentEquipmentToEdit.value = null;
  } catch (err) {
    toast.error(`An error occurred: ${err.message}`);
  }
};

const viewEquipmentAvailability = (equipmentItem) => {
  openAvailabilityCalendar(equipmentItem, 'equipment');
};

const deleteEquipment = (equipmentItem) => {
  openConfirmationModal(
    equipmentItem,
    'equipment',
    'Delete Equipment?',
    `Are you sure you want to delete equipment "${equipmentItem.name}"? This action cannot be undone.`
  );
};

// Removed duplicate deleteEquipment function

// TODO: Add backend integration for all CRUD operations
// TODO: Add form validation to all forms
// TODO: Improve UI/UX (e.g., loading states, success/error notifications)

</script>

<style scoped>
.resource-management-container {
  padding: 20px;
  font-family: sans-serif;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ccc;
}

.tabs button {
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  background-color: transparent;
  font-size: 16px;
  border-bottom: 3px solid transparent; /* For active state */
  margin-bottom: -1px; /* Align with container's border */
}

.tabs button.active {
  border-bottom: 3px solid #007bff;
  color: #007bff;
  font-weight: bold;
}

.tab-content .resource-section {
  margin-bottom: 30px;
}

.resource-section h2 {
  margin-bottom: 15px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.button-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 15px; /* Space before the table or form */
}

.button-primary:hover {
  background-color: #0056b3;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

th, td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}

th {
  background-color: #e9ecef;
  color: #495057;
  font-weight: bold;
}

.button-small {
  padding: 5px 10px;
  font-size: 12px;
  margin-right: 5px;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid #ccc;
  background-color: #f8f9fa;
}

.button-small:hover {
  background-color: #e2e6ea;
}

.button-danger {
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
}

.button-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
}

.no-items {
    text-align: center;
    color: #6c757d;
    padding: 20px;
    font-style: italic;
}

/* Status-specific styling */
.status-active,
.status-available {
  color: #28a745; /* Green */
  font-weight: bold;
}

.status-under-maintenance {
  color: #ffc107; /* Yellow */
  font-weight: bold;
}

.status-inactive,
.status-on-leave,
.status-retired {
  color: #dc3545; /* Red */
  font-weight: bold;
}

.status-in-use {
    color: #fd7e14; /* Orange */
    font-weight: bold;
}

/* Loading indicator styles */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: var(--color-dark-gray);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 123, 255, 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.availability-modal {
  padding: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.close-button:hover {
  color: #333;
}

.modal-body {
  padding: 0;
}

</style>