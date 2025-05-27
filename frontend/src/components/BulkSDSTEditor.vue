<template>
  <div class="modal-overlay" v-if="show">
    <div class="modal-content bulk-edit-modal" role="dialog" aria-labelledby="bulk-edit-title">
      <h3 id="bulk-edit-title">Bulk Edit SDST Values</h3>
      
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="['tab-button', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <!-- Pattern-based editing -->
      <div v-if="activeTab === 'pattern'" class="tab-content">
        <p class="description">
          Apply a pattern to multiple SDST values at once. This is useful for setting up initial values or making bulk changes.
        </p>
        
        <div class="form-group">
          <label for="pattern-type">Pattern Type:</label>
          <select id="pattern-type" v-model="patternType" class="form-control">
            <option value="fixed">Fixed Value</option>
            <option value="percentage">Percentage Adjustment</option>
            <option value="increment">Increment/Decrement</option>
          </select>
        </div>
        
        <div class="form-group" v-if="patternType === 'fixed'">
          <label for="fixed-value">Set all selected values to:</label>
          <input 
            type="number" 
            id="fixed-value" 
            v-model.number="fixedValue" 
            min="0" 
            max="180"
            class="form-control"
          />
          <span class="input-hint">minutes</span>
        </div>
        
        <div class="form-group" v-if="patternType === 'percentage'">
          <label for="percentage-value">Adjust by percentage:</label>
          <div class="input-with-prefix">
            <select v-model="percentageDirection" class="form-control prefix">
              <option value="increase">Increase by</option>
              <option value="decrease">Decrease by</option>
            </select>
            <input 
              type="number" 
              id="percentage-value" 
              v-model.number="percentageValue" 
              min="1" 
              max="100"
              class="form-control"
            />
            <span class="input-hint">%</span>
          </div>
        </div>
        
        <div class="form-group" v-if="patternType === 'increment'">
          <label for="increment-value">Adjust by fixed amount:</label>
          <div class="input-with-prefix">
            <select v-model="incrementDirection" class="form-control prefix">
              <option value="increase">Increase by</option>
              <option value="decrease">Decrease by</option>
            </select>
            <input 
              type="number" 
              id="increment-value" 
              v-model.number="incrementValue" 
              min="1" 
              max="60"
              class="form-control"
            />
            <span class="input-hint">minutes</span>
          </div>
        </div>
        
        <div class="form-group">
          <label>Apply to:</label>
          <div class="checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="applyToAll" @change="handleApplyToAllChange" />
              All SDST values
            </label>
            <label class="checkbox-label" v-if="!applyToAll">
              <input type="checkbox" v-model="applyToLow" />
              Low values (≤ 15 min)
            </label>
            <label class="checkbox-label" v-if="!applyToAll">
              <input type="checkbox" v-model="applyToMedium" />
              Medium values (16-30 min)
            </label>
            <label class="checkbox-label" v-if="!applyToAll">
              <input type="checkbox" v-model="applyToHigh" />
              High values (> 30 min)
            </label>
          </div>
        </div>
      </div>
      
      <!-- CSV Import/Export -->
      <div v-if="activeTab === 'csv'" class="tab-content">
        <p class="description">
          Import or export SDST values as CSV for editing in spreadsheet software.
        </p>
        
        <div class="action-buttons">
          <button class="btn btn-secondary" @click="exportCSV">
            <span class="icon">📤</span> Export as CSV
          </button>
          <button class="btn btn-primary" @click="triggerFileInput">
            <span class="icon">📥</span> Import from CSV
          </button>
          <input 
            type="file" 
            ref="fileInput" 
            accept=".csv" 
            style="display: none;" 
            @change="handleFileUpload"
          />
        </div>
        
        <div class="csv-format-info">
          <h4>CSV Format</h4>
          <p>The CSV file should have the following format:</p>
          <pre>FromType,ToType,Minutes
CABG,KNEE,30
CABG,APPEN,45
...</pre>
          <p>The first row is a header row. Each subsequent row represents one SDST value.</p>
        </div>
      </div>
      
      <div class="preview-section" v-if="activeTab === 'pattern' && hasSelection">
        <h4>Preview of Changes</h4>
        <p>{{ getPreviewText() }}</p>
        <div class="affected-count">
          {{ getAffectedCount() }} values will be affected
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn btn-secondary" @click="cancel">Cancel</button>
        <button 
          class="btn btn-primary" 
          @click="applyChanges"
          :disabled="!isValid"
        >
          Apply Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['close', 'update']);

const store = useScheduleStore();

// Tabs
const tabs = [
  { id: 'pattern', label: 'Pattern-based Editing' },
  { id: 'csv', label: 'CSV Import/Export' }
];
const activeTab = ref('pattern');

// Pattern-based editing
const patternType = ref('fixed');
const fixedValue = ref(30);
const percentageDirection = ref('increase');
const percentageValue = ref(10);
const incrementDirection = ref('increase');
const incrementValue = ref(5);
const applyToAll = ref(true);
const applyToLow = ref(false);
const applyToMedium = ref(false);
const applyToHigh = ref(false);

// File input reference
const fileInput = ref(null);

// Handle apply to all checkbox
const handleApplyToAllChange = () => {
  if (applyToAll.value) {
    applyToLow.value = false;
    applyToMedium.value = false;
    applyToHigh.value = false;
  }
};

// Watch individual category checkboxes
watch([applyToLow, applyToMedium, applyToHigh], ([newLow, newMedium, newHigh]) => {
  if (newLow || newMedium || newHigh) {
    applyToAll.value = false;
  }
});

// Computed property to check if any selection is made
const hasSelection = computed(() => {
  return applyToAll.value || applyToLow.value || applyToMedium.value || applyToHigh.value;
});

// Computed property to check if the form is valid
const isValid = computed(() => {
  if (activeTab.value === 'pattern') {
    return hasSelection.value;
  }
  return true;
});

// Get preview text based on current settings
const getPreviewText = () => {
  if (patternType.value === 'fixed') {
    return `Set selected SDST values to ${fixedValue.value} minutes`;
  } else if (patternType.value === 'percentage') {
    return `${percentageDirection.value === 'increase' ? 'Increase' : 'Decrease'} selected SDST values by ${percentageValue.value}%`;
  } else if (patternType.value === 'increment') {
    return `${incrementDirection.value === 'increase' ? 'Increase' : 'Decrease'} selected SDST values by ${incrementValue.value} minutes`;
  }
  return '';
};

// Get count of affected values
const getAffectedCount = () => {
  let count = 0;
  const surgeryTypes = Object.keys(store.surgeryTypes);
  
  for (const fromType of surgeryTypes) {
    for (const toType of surgeryTypes) {
      if (fromType === toType) continue; // Skip same type
      
      const value = store.sdsRules[fromType]?.[toType];
      if (value === undefined) continue;
      
      if (applyToAll.value || 
          (applyToLow.value && value <= 15) ||
          (applyToMedium.value && value > 15 && value <= 30) ||
          (applyToHigh.value && value > 30)) {
        count++;
      }
    }
  }
  
  return count;
};

// Apply the pattern changes
const applyChanges = () => {
  if (activeTab.value === 'pattern') {
    applyPatternChanges();
  }
  emit('update');
  emit('close');
};

// Apply pattern-based changes
const applyPatternChanges = () => {
  const surgeryTypes = Object.keys(store.surgeryTypes);
  
  for (const fromType of surgeryTypes) {
    for (const toType of surgeryTypes) {
      if (fromType === toType) continue; // Skip same type
      
      const currentValue = store.sdsRules[fromType]?.[toType];
      if (currentValue === undefined) continue;
      
      // Check if this value should be updated
      if (applyToAll.value || 
          (applyToLow.value && currentValue <= 15) ||
          (applyToMedium.value && currentValue > 15 && currentValue <= 30) ||
          (applyToHigh.value && currentValue > 30)) {
        
        let newValue = currentValue;
        
        // Calculate new value based on pattern type
        if (patternType.value === 'fixed') {
          newValue = fixedValue.value;
        } else if (patternType.value === 'percentage') {
          if (percentageDirection.value === 'increase') {
            newValue = Math.round(currentValue * (1 + percentageValue.value / 100));
          } else {
            newValue = Math.round(currentValue * (1 - percentageValue.value / 100));
          }
        } else if (patternType.value === 'increment') {
          if (incrementDirection.value === 'increase') {
            newValue = currentValue + incrementValue.value;
          } else {
            newValue = Math.max(0, currentValue - incrementValue.value);
          }
        }
        
        // Update the value in the store
        store.updateSDSTValue(fromType, toType, newValue);
      }
    }
  }
};

// Trigger file input click
const triggerFileInput = () => {
  fileInput.value.click();
};

// Handle file upload
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    const contents = e.target.result;
    processCSV(contents);
  };
  reader.readAsText(file);
};

// Process CSV data
const processCSV = (csvData) => {
  const lines = csvData.split('\n');
  const headers = lines[0].split(',');
  
  // Validate headers
  if (headers.length < 3 || 
      !headers.includes('FromType') || 
      !headers.includes('ToType') || 
      !headers.includes('Minutes')) {
    alert('Invalid CSV format. Please ensure the CSV has FromType, ToType, and Minutes columns.');
    return;
  }
  
  const fromIndex = headers.indexOf('FromType');
  const toIndex = headers.indexOf('ToType');
  const minutesIndex = headers.indexOf('Minutes');
  
  let updatedCount = 0;
  
  // Process data rows
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    
    const values = lines[i].split(',');
    if (values.length < 3) continue;
    
    const fromType = values[fromIndex].trim();
    const toType = values[toIndex].trim();
    const minutes = parseInt(values[minutesIndex].trim(), 10);
    
    if (isNaN(minutes) || minutes < 0) continue;
    
    // Update the value in the store
    if (store.surgeryTypes[fromType] && store.surgeryTypes[toType] && fromType !== toType) {
      store.updateSDSTValue(fromType, toType, minutes);
      updatedCount++;
    }
  }
  
  alert(`Successfully updated ${updatedCount} SDST values.`);
  emit('update');
  emit('close');
};

// Export to CSV
const exportCSV = () => {
  const surgeryTypes = Object.keys(store.surgeryTypes);
  let csvContent = 'FromType,ToType,Minutes\n';
  
  for (const fromType of surgeryTypes) {
    for (const toType of surgeryTypes) {
      if (fromType === toType) continue; // Skip same type
      
      const value = store.sdsRules[fromType]?.[toType];
      if (value !== undefined) {
        csvContent += `${fromType},${toType},${value}\n`;
      }
    }
  }
  
  // Create a download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'sdst_values.csv');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Cancel and close
const cancel = () => {
  emit('close');
};
</script>

<style scoped>
.bulk-edit-modal {
  width: 600px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-md);
}

.tab-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  margin-bottom: var(--spacing-md);
}

.description {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-secondary);
}

.input-with-prefix {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.prefix {
  width: 130px;
  flex-shrink: 0;
}

.input-hint {
  margin-left: var(--spacing-xs);
  color: var(--color-text-secondary);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-xs);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  cursor: pointer;
}

.preview-section {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
}

.affected-count {
  margin-top: var(--spacing-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.icon {
  margin-right: var(--spacing-xs);
}

.csv-format-info {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
}

pre {
  background-color: var(--color-background);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  overflow-x: auto;
  font-family: monospace;
  margin: var(--spacing-sm) 0;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .input-with-prefix {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .prefix {
    width: 100%;
  }
}
</style>
