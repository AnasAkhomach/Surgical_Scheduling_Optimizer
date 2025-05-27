<template>
  <div class="sdst-management-screen">
    <h2>SDST Management</h2>
    <p class="description">
      Manage Sequence-Dependent Setup Times (SDST) between different surgery types.
      SDST represents the time needed to prepare the OR when transitioning from one surgery type to another.
    </p>

    <!-- Controls Section -->
    <div class="controls-section">
      <div class="search-filter">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search surgery types..."
          class="search-input"
          aria-label="Search surgery types"
        />
      </div>
      <div class="action-buttons">
        <button class="btn btn-secondary" @click="showBulkEditModal = true">
          Bulk Edit SDST Values
        </button>
        <button class="btn btn-primary" @click="showAddSurgeryTypeModal = true">
          Add New Surgery Type
        </button>
      </div>
    </div>

    <!-- SDST Matrix -->
    <div class="sdst-matrix-container">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span>Loading SDST data...</span>
      </div>

      <table class="sdst-matrix" aria-label="SDST Matrix">
        <caption>SDST Matrix (minutes)</caption>
        <thead>
          <tr>
            <th scope="col">From \ To</th>
            <th v-for="toType in filteredSurgeryTypes" :key="`to-${toType}`" scope="col">
              <div class="surgery-type-header">
                <span>{{ toType }}</span>
                <button
                  class="delete-type-btn"
                  @click.stop="confirmDeleteSurgeryType(toType)"
                  title="Delete surgery type"
                >
                  ✕
                </button>
              </div>
              <div class="surgery-type-label">{{ getSurgeryTypeFullName(toType) }}</div>
            </th>
            <th scope="col">Initial Setup</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="fromType in filteredSurgeryTypes" :key="`from-${fromType}`">
            <th scope="row">
              <div class="surgery-type-header">
                <span>{{ fromType }}</span>
                <button
                  class="delete-type-btn"
                  @click.stop="confirmDeleteSurgeryType(fromType)"
                  title="Delete surgery type"
                >
                  ✕
                </button>
              </div>
              <div class="surgery-type-label">{{ getSurgeryTypeFullName(fromType) }}</div>
            </th>
            <td
              v-for="toType in filteredSurgeryTypes"
              :key="`${fromType}-to-${toType}`"
              :class="{
                'same-type': fromType === toType,
                'editable': fromType !== toType,
                'sdst-low': fromType !== toType && getSDSTValueNumber(fromType, toType) <= 15,
                'sdst-medium': fromType !== toType && getSDSTValueNumber(fromType, toType) > 15 && getSDSTValueNumber(fromType, toType) <= 30,
                'sdst-high': fromType !== toType && getSDSTValueNumber(fromType, toType) > 30
              }"
              @click="fromType !== toType && openEditModal(fromType, toType)"
            >
              <span v-if="fromType === toType">-</span>
              <span v-else>{{ getSDSTValue(fromType, toType) }}</span>
            </td>
            <td class="initial-setup">
              <!-- Not applicable for "from" types -->
              -
            </td>
          </tr>
          <tr>
            <th scope="row">Initial Setup</th>
            <td
              v-for="toType in filteredSurgeryTypes"
              :key="`initial-to-${toType}`"
              class="editable"
              @click="openEditInitialSetupModal(toType)"
            >
              {{ getInitialSetupTime(toType) }}
            </td>
            <td>-</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Legend -->
    <div class="legend">
      <div class="legend-item">
        <span class="legend-color" style="background-color: var(--color-background-mute);"></span>
        <span>Not applicable (same surgery type)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(40, 167, 69, 0.1);"></span>
        <span>Short setup time (≤ 15 min)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(255, 193, 7, 0.1);"></span>
        <span>Medium setup time (16-30 min)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(220, 53, 69, 0.1);"></span>
        <span>Long setup time (> 30 min)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: var(--color-background);"></span>
        <span>Click on a cell to edit SDST value</span>
      </div>
    </div>

    <!-- Edit SDST Modal -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-content" role="dialog" aria-labelledby="edit-sdst-title">
        <h3 id="edit-sdst-title">Edit SDST Value</h3>
        <p>
          Set the setup time required when transitioning from
          <strong>{{ editingFromType }}</strong> to <strong>{{ editingToType }}</strong>
        </p>
        <div class="form-group">
          <label for="sdst-value">Setup Time (minutes):</label>
          <input
            type="number"
            id="sdst-value"
            v-model.number="editingValue"
            min="0"
            max="180"
            class="form-control"
          />
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeEditModal">Cancel</button>
          <button class="btn btn-primary" @click="saveSDSTValue">Save</button>
        </div>
      </div>
    </div>

    <!-- Add Surgery Type Modal -->
    <div v-if="showAddSurgeryTypeModal" class="modal-overlay">
      <div class="modal-content" role="dialog" aria-labelledby="add-surgery-type-title">
        <h3 id="add-surgery-type-title">Add New Surgery Type</h3>
        <div class="form-group">
          <label for="surgery-code">Surgery Code (e.g., CABG):</label>
          <input
            type="text"
            id="surgery-code"
            v-model="newSurgeryType.code"
            class="form-control"
            maxlength="5"
            placeholder="Enter code (max 5 chars)"
          />
        </div>
        <div class="form-group">
          <label for="surgery-name">Full Name:</label>
          <input
            type="text"
            id="surgery-name"
            v-model="newSurgeryType.fullName"
            class="form-control"
            placeholder="e.g., Cardiac - Coronary Artery Bypass Graft"
          />
        </div>
        <div class="form-group">
          <label for="initial-setup">Initial Setup Time (minutes):</label>
          <input
            type="number"
            id="initial-setup"
            v-model.number="newSurgeryType.initialSetupTime"
            min="0"
            max="180"
            class="form-control"
          />
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showAddSurgeryTypeModal = false">Cancel</button>
          <button class="btn btn-primary" @click="addNewSurgeryType" :disabled="!isNewSurgeryTypeValid">Add</button>
        </div>
      </div>
    </div>

    <!-- Delete Surgery Type Confirmation Modal -->
    <div v-if="showDeleteConfirmModal" class="modal-overlay">
      <div class="modal-content" role="dialog" aria-labelledby="delete-surgery-type-title">
        <h3 id="delete-surgery-type-title" class="danger-text">Delete Surgery Type</h3>
        <p>
          Are you sure you want to delete the surgery type <strong>{{ typeToDelete }}</strong>?
        </p>
        <p class="warning-text">
          This will remove all SDST rules associated with this surgery type. This action cannot be undone.
        </p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteConfirmModal = false">Cancel</button>
          <button class="btn btn-danger" @click="deleteSurgeryType">Delete</button>
        </div>
      </div>
    </div>

    <!-- Bulk SDST Editor Modal -->
    <BulkSDSTEditor
      v-if="showBulkEditModal"
      :show="showBulkEditModal"
      @close="showBulkEditModal = false"
      @update="handleBulkUpdate"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import BulkSDSTEditor from './BulkSDSTEditor.vue';

const store = useScheduleStore();
const isLoading = ref(false);
const searchQuery = ref('');

// Edit modal state
const showEditModal = ref(false);
const editingFromType = ref('');
const editingToType = ref('');
const editingValue = ref(0);
const isInitialSetup = ref(false);

// Add surgery type modal state
const showAddSurgeryTypeModal = ref(false);
const newSurgeryType = ref({
  code: '',
  fullName: '',
  initialSetupTime: 30
});

// Delete surgery type modal state
const showDeleteConfirmModal = ref(false);
const typeToDelete = ref('');

// Bulk edit modal state
const showBulkEditModal = ref(false);

// Get surgery type full names from the store
const getSurgeryTypeFullName = (type) => {
  return store.surgeryTypes[type]?.fullName || type;
};

// Get all surgery types from the store
const surgeryTypes = computed(() => {
  // Get surgery types directly from the surgeryTypes object
  return Object.keys(store.surgeryTypes).sort();
});

// Filter surgery types based on search query
const filteredSurgeryTypes = computed(() => {
  if (!searchQuery.value) return surgeryTypes.value;

  return surgeryTypes.value.filter(type =>
    type.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    getSurgeryTypeFullName(type).toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Validate new surgery type
const isNewSurgeryTypeValid = computed(() => {
  const code = newSurgeryType.value.code.trim();
  const fullName = newSurgeryType.value.fullName.trim();

  return (
    code.length > 0 &&
    code.length <= 5 &&
    fullName.length > 0 &&
    !surgeryTypes.value.includes(code.toUpperCase())
  );
});

// This function is now defined above as a const arrow function

// Get SDST value between two surgery types
function getSDSTValue(fromType, toType) {
  if (fromType === toType) return '-';

  if (store.sdsRules[fromType] && store.sdsRules[fromType][toType] !== undefined) {
    return store.sdsRules[fromType][toType];
  }

  return 'N/A';
}

// Get SDST value as a number for color coding
function getSDSTValueNumber(fromType, toType) {
  if (fromType === toType) return 0;

  if (store.sdsRules[fromType] && store.sdsRules[fromType][toType] !== undefined) {
    return store.sdsRules[fromType][toType];
  }

  return 0; // Default for N/A
}

// Get initial setup time for a surgery type
function getInitialSetupTime(type) {
  return store.initialSetupTimes[type] !== undefined ? store.initialSetupTimes[type] : 'N/A';
}

// Open edit modal for SDST value
function openEditModal(fromType, toType) {
  editingFromType.value = fromType;
  editingToType.value = toType;
  editingValue.value = store.sdsRules[fromType]?.[toType] || 0;
  isInitialSetup.value = false;
  showEditModal.value = true;
}

// Open edit modal for initial setup time
function openEditInitialSetupModal(toType) {
  editingFromType.value = 'Initial';
  editingToType.value = toType;
  editingValue.value = store.initialSetupTimes[toType] || 0;
  isInitialSetup.value = true;
  showEditModal.value = true;
}

// Close edit modal
function closeEditModal() {
  showEditModal.value = false;
}

// Save SDST value
function saveSDSTValue() {
  if (isInitialSetup.value) {
    // Update initial setup time
    store.updateInitialSetupTime(editingToType.value, editingValue.value);
  } else {
    // Update SDST value
    store.updateSDSTValue(editingFromType.value, editingToType.value, editingValue.value);
  }

  closeEditModal();
}

// Add new surgery type
function addNewSurgeryType() {
  if (!isNewSurgeryTypeValid.value) return;

  const code = newSurgeryType.value.code.trim().toUpperCase();

  // Add to store (which now handles adding to surgeryTypes)
  store.addNewSurgeryType(
    code,
    newSurgeryType.value.fullName.trim(),
    newSurgeryType.value.initialSetupTime
  );

  // Reset form
  newSurgeryType.value = {
    code: '',
    fullName: '',
    initialSetupTime: 30
  };

  showAddSurgeryTypeModal.value = false;
}

// Confirm delete surgery type
function confirmDeleteSurgeryType(type) {
  typeToDelete.value = type;
  showDeleteConfirmModal.value = true;
}

// Delete surgery type
function deleteSurgeryType() {
  if (!typeToDelete.value) return;

  // Call store method to delete the surgery type
  store.deleteSurgeryType(typeToDelete.value);

  // Close the modal
  showDeleteConfirmModal.value = false;
  typeToDelete.value = '';
}

// Handle bulk update from the bulk editor
function handleBulkUpdate() {
  console.log('Bulk update completed');
  // No need to do anything here as the store is already updated by the bulk editor
}

// Load data
onMounted(async () => {
  isLoading.value = true;
  try {
    // In a real app, this would fetch SDST data from the backend
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
  } catch (error) {
    console.error('Failed to load SDST data:', error);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.sdst-management-screen {
  padding: var(--spacing-md);
  max-width: 1200px;
  margin: 0 auto;
}

.description {
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-secondary);
}

.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
}

.search-input {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  width: 300px;
}

.sdst-matrix-container {
  position: relative;
  overflow-x: auto;
  margin-bottom: var(--spacing-lg);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background-color: var(--color-background);
}

.sdst-matrix {
  width: 100%;
  border-collapse: collapse;
}

.sdst-matrix caption {
  padding: var(--spacing-sm);
  font-weight: var(--font-weight-bold);
  text-align: left;
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
}

.sdst-matrix th,
.sdst-matrix td {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border-soft);
  text-align: center;
  position: relative;
}

.sdst-matrix th {
  background-color: var(--color-background-soft);
  font-weight: var(--font-weight-bold);
  position: sticky;
  top: 0;
  z-index: 1;
}

.sdst-matrix th:first-child {
  left: 0;
  z-index: 2;
}

.surgery-type-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.delete-type-btn {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s ease;
}

.delete-type-btn:hover {
  background-color: var(--color-danger, #dc3545);
  color: white;
  opacity: 1;
}

.surgery-type-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.same-type {
  background-color: var(--color-background-mute);
}

.editable {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.editable:hover {
  background-color: var(--color-background-hover);
}

/* SDST value color coding */
.sdst-low {
  background-color: rgba(40, 167, 69, 0.1); /* Green with low opacity */
  color: #28a745;
}

.sdst-medium {
  background-color: rgba(255, 193, 7, 0.1); /* Yellow with low opacity */
  color: #d39e00;
}

.sdst-high {
  background-color: rgba(220, 53, 69, 0.1); /* Red with low opacity */
  color: #dc3545;
}

.sdst-low:hover, .sdst-medium:hover, .sdst-high:hover {
  opacity: 0.8;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  min-width: 200px;
  margin-bottom: var(--spacing-xs);
}

.legend-color {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
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
  z-index: var(--z-index-modal);
}

.modal-content {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

.form-control {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

/* Loading overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(var(--color-primary-rgb, 0, 120, 212), 0.2);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.danger-text {
  color: var(--color-danger, #dc3545);
}

.warning-text {
  color: var(--color-warning, #ffc107);
  font-weight: var(--font-weight-medium);
  background-color: rgba(255, 193, 7, 0.1);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  border-left: 3px solid var(--color-warning, #ffc107);
}

.btn-danger {
  background-color: var(--color-danger, #dc3545);
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: var(--color-danger-dark, #bd2130);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .controls-section {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }

  .search-input {
    width: 100%;
  }

  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-sm);
  }

  .legend {
    flex-direction: column;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm);
  }

  .legend-item {
    min-width: 100%;
  }
}
</style>
