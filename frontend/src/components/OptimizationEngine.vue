<template>
  <div class="optimization-engine">
    <h1>Schedule Optimization Engine</h1>

    <!-- Optimization Controls -->
    <div class="optimization-controls">
      <div class="control-section">
        <h3>Optimization Settings</h3>
        <div class="settings-grid">
          <div class="setting-item">
            <label>
              <input
                type="checkbox"
                v-model="optimizationSettings.prioritizeSDST"
                @change="updateSettings"
              >
              Prioritize SDST Reduction
            </label>
          </div>
          <div class="setting-item">
            <label>
              <input
                type="checkbox"
                v-model="optimizationSettings.prioritizeUrgency"
                @change="updateSettings"
              >
              Respect Surgery Urgency
            </label>
          </div>
          <div class="setting-item">
            <label>
              <input
                type="checkbox"
                v-model="optimizationSettings.prioritizeResourceUtilization"
                @change="updateSettings"
              >
              Optimize Resource Utilization
            </label>
          </div>
          <div class="setting-item">
            <label>
              <input
                type="checkbox"
                v-model="optimizationSettings.allowMinorDelays"
                @change="updateSettings"
              >
              Allow Minor Delays (≤{{ optimizationSettings.maxDelayMinutes }} min)
            </label>
          </div>
        </div>

        <div class="action-buttons">
          <button
            class="run-optimization-btn"
            @click="runOptimization"
            :disabled="!canOptimize || isOptimizing"
          >
            <span v-if="isOptimizing" class="spinner"></span>
            {{ isOptimizing ? 'Analyzing Schedule...' : 'Run Optimization' }}
          </button>

          <button
            v-if="optimizationResults"
            class="clear-results-btn"
            @click="clearResults"
          >
            Clear Results
          </button>
        </div>
      </div>
    </div>

    <!-- Optimization Results -->
    <div v-if="optimizationResults" class="optimization-results">
      <!-- Results Summary -->
      <div class="results-summary">
        <h3>Optimization Results</h3>
        <div class="summary-cards">
          <div class="summary-card">
            <h4>Total Suggestions</h4>
            <div class="metric-value">{{ optimizationSummary.totalSuggestions }}</div>
          </div>
          <div class="summary-card">
            <h4>High Priority</h4>
            <div class="metric-value priority-high">{{ optimizationSummary.highPriority }}</div>
          </div>
          <div class="summary-card">
            <h4>Potential SDST Savings</h4>
            <div class="metric-value">{{ potentialSavings.sdstReduction }} min</div>
          </div>
          <div class="summary-card">
            <h4>Overall Impact</h4>
            <div class="metric-value" :class="`impact-${optimizationSummary.estimatedImpact.toLowerCase()}`">
              {{ optimizationSummary.estimatedImpact }}
            </div>
          </div>
        </div>
      </div>

      <!-- Suggestions List -->
      <div class="suggestions-section">
        <div class="suggestions-header">
          <h3>Optimization Suggestions</h3>
          <div class="suggestions-actions">
            <button @click="selectAllSuggestions" class="select-all-btn">
              Select All
            </button>
            <button @click="clearAllSelections" class="clear-selection-btn">
              Clear Selection
            </button>
            <button
              @click="applySelectedSuggestions"
              :disabled="selectedSuggestions.length === 0"
              class="apply-suggestions-btn"
            >
              Apply Selected ({{ selectedSuggestions.length }})
            </button>
          </div>
        </div>

        <div class="suggestions-list">
          <div
            v-for="suggestion in currentSuggestions"
            :key="suggestion.id"
            class="suggestion-card"
            :class="[
              `priority-${suggestion.priority.toLowerCase()}`,
              { 'selected': selectedSuggestions.includes(suggestion.id) }
            ]"
          >
            <div class="suggestion-header">
              <div class="suggestion-checkbox">
                <input
                  type="checkbox"
                  :checked="selectedSuggestions.includes(suggestion.id)"
                  @change="toggleSuggestionSelection(suggestion.id)"
                >
              </div>
              <div class="suggestion-info">
                <h4>{{ suggestion.title }}</h4>
                <div class="suggestion-meta">
                  <span class="category">{{ suggestion.category }}</span>
                  <span class="priority-badge" :class="`priority-${suggestion.priority.toLowerCase()}`">
                    {{ suggestion.priority }}
                  </span>
                  <span class="impact">Impact: {{ suggestion.impact }} min</span>
                  <span class="effort">Effort: {{ suggestion.effort }}</span>
                </div>
              </div>
            </div>

            <div class="suggestion-content">
              <p class="suggestion-description">{{ suggestion.description }}</p>

              <div class="suggestion-details">
                <div class="detail-item">
                  <strong>Estimated Savings:</strong> {{ suggestion.estimatedSavings }}
                </div>
                <div v-if="suggestion.risks && suggestion.risks.length > 0" class="detail-item">
                  <strong>Risks:</strong>
                  <ul class="risk-list">
                    <li v-for="risk in suggestion.risks" :key="risk">{{ risk }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results State -->
    <div v-else-if="!isOptimizing" class="no-results">
      <div class="no-results-content">
        <h3>Ready to Optimize</h3>
        <p>Click "Run Optimization" to analyze your current schedule and get intelligent suggestions for improvement.</p>
        <div class="optimization-benefits">
          <h4>Optimization Benefits:</h4>
          <ul>
            <li>Reduce Surgery-to-Surgery Transition (SDST) times</li>
            <li>Improve operating room utilization</li>
            <li>Resolve scheduling conflicts automatically</li>
            <li>Balance workload across resources</li>
            <li>Minimize patient wait times</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isOptimizing" class="optimization-loading">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <h3>Analyzing Your Schedule</h3>
        <p>Our optimization engine is analyzing your current schedule to identify improvement opportunities...</p>
        <div class="analysis-steps">
          <div class="step">✓ Analyzing SDST patterns</div>
          <div class="step">✓ Evaluating resource utilization</div>
          <div class="step">✓ Detecting scheduling conflicts</div>
          <div class="step">⏳ Generating optimization suggestions</div>
        </div>
      </div>
    </div>

    <!-- Optimization History -->
    <div v-if="optimizationHistory.length > 0" class="optimization-history">
      <h3>Recent Optimizations</h3>
      <div class="history-list">
        <div
          v-for="entry in optimizationHistory.slice(0, 5)"
          :key="entry.id"
          class="history-item"
          :class="{ 'applied': entry.applied }"
        >
          <div class="history-info">
            <div class="history-date">{{ formatDate(entry.timestamp) }}</div>
            <div class="history-details">
              {{ entry.suggestionsCount }} suggestions • {{ entry.potentialSavings }} min savings
            </div>
          </div>
          <div class="history-status">
            <span v-if="entry.applied" class="status-applied">Applied</span>
            <span v-else class="status-pending">Pending</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';

const scheduleStore = useScheduleStore();
const {
  isOptimizing,
  optimizationResults,
  selectedSuggestions,
  optimizationSettings,
  optimizationHistory,
  currentSuggestions,
  potentialSavings,
  optimizationSummary,
  canOptimize
} = storeToRefs(scheduleStore);

// Local reactive data
const showAdvancedSettings = ref(false);

// Methods
const runOptimization = async () => {
  try {
    await scheduleStore.runOptimization();
  } catch (error) {
    console.error('Optimization failed:', error);
    // Could show a toast notification here
  }
};

const clearResults = () => {
  scheduleStore.clearOptimizationResults();
};

const updateSettings = () => {
  scheduleStore.updateOptimizationSettings(optimizationSettings.value);
};

const toggleSuggestionSelection = (suggestionId) => {
  scheduleStore.toggleSuggestionSelection(suggestionId);
};

const selectAllSuggestions = () => {
  scheduleStore.selectAllSuggestions();
};

const clearAllSelections = () => {
  scheduleStore.clearAllSelections();
};

const applySelectedSuggestions = async () => {
  if (selectedSuggestions.value.length === 0) return;

  try {
    await scheduleStore.applyOptimizationResults([...selectedSuggestions.value]);
    // Could show success notification
    console.log('Suggestions applied successfully');
  } catch (error) {
    console.error('Failed to apply suggestions:', error);
    // Could show error notification
  }
};

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};

// Initialize component
onMounted(() => {
  // Could load any initial data here
});
</script>

<style scoped>
.optimization-engine {
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
}

/* Optimization Controls */
.optimization-controls {
  background-color: var(--color-background-soft);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.control-section h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.setting-item label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.setting-item input[type="checkbox"] {
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: var(--spacing-md);
}

.run-optimization-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.run-optimization-btn:disabled {
  background-color: var(--color-border);
  cursor: not-allowed;
}

.clear-results-btn {
  background-color: var(--color-background-mute);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Results Summary */
.results-summary {
  background-color: var(--color-background-soft);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.summary-card {
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-sm);
  text-align: center;
}

.summary-card h4 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.metric-value {
  font-size: 1.5rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.metric-value.priority-high {
  color: var(--color-error);
}

.metric-value.impact-high {
  color: var(--color-success);
}

.metric-value.impact-medium {
  color: var(--color-warning);
}

.metric-value.impact-low {
  color: var(--color-text-secondary);
}

/* Suggestions Section */
.suggestions-section {
  background-color: var(--color-background-soft);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-lg);
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.suggestions-header h3 {
  margin: 0;
}

.suggestions-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.suggestions-actions button {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-border);
  background-color: var(--color-background);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.apply-suggestions-btn {
  background-color: var(--color-success) !important;
  color: white !important;
  border-color: var(--color-success) !important;
}

.apply-suggestions-btn:disabled {
  background-color: var(--color-border) !important;
  color: var(--color-text-secondary) !important;
  cursor: not-allowed;
}

/* Suggestion Cards */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.suggestion-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-border);
  padding: var(--spacing-md);
  transition: all 0.2s ease;
}

.suggestion-card.priority-high {
  border-left-color: var(--color-error);
}

.suggestion-card.priority-medium {
  border-left-color: var(--color-warning);
}

.suggestion-card.priority-low {
  border-left-color: var(--color-success);
}

.suggestion-card.selected {
  background-color: rgba(var(--color-primary-rgb), 0.05);
  border-color: var(--color-primary);
}

.suggestion-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.suggestion-checkbox input {
  margin: 0;
}

.suggestion-info {
  flex: 1;
}

.suggestion-info h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text);
}

.suggestion-meta {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.suggestion-meta span {
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background-mute);
}

.priority-badge.priority-high {
  background-color: rgba(var(--color-error-rgb), 0.1);
  color: var(--color-error);
}

.priority-badge.priority-medium {
  background-color: rgba(var(--color-warning-rgb), 0.1);
  color: var(--color-warning);
}

.priority-badge.priority-low {
  background-color: rgba(var(--color-success-rgb), 0.1);
  color: var(--color-success);
}

.suggestion-description {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.suggestion-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.detail-item {
  font-size: var(--font-size-sm);
}

.risk-list {
  margin: var(--spacing-xs) 0 0 var(--spacing-md);
  padding: 0;
}

.risk-list li {
  color: var(--color-warning);
  margin-bottom: var(--spacing-xs);
}

/* No Results State */
.no-results {
  background-color: var(--color-background-soft);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-md);
  text-align: center;
}

.no-results-content h3 {
  margin-top: 0;
  color: var(--color-text);
}

.optimization-benefits {
  margin-top: var(--spacing-lg);
  text-align: left;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.optimization-benefits h4 {
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
}

.optimization-benefits ul {
  list-style-type: none;
  padding: 0;
}

.optimization-benefits li {
  padding: var(--spacing-xs) 0;
  position: relative;
  padding-left: var(--spacing-lg);
}

.optimization-benefits li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--color-success);
  font-weight: bold;
}

/* Loading State */
.optimization-loading {
  background-color: var(--color-background-soft);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-md);
  text-align: center;
}

.loading-content h3 {
  margin: var(--spacing-lg) 0 var(--spacing-md) 0;
  color: var(--color-text);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(var(--color-primary-rgb), 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

.analysis-steps {
  margin-top: var(--spacing-lg);
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.step {
  padding: var(--spacing-sm) 0;
  color: var(--color-text-secondary);
}

/* Optimization History */
.optimization-history {
  background-color: var(--color-background-soft);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
}

.optimization-history h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
}

.history-item.applied {
  border-left: 4px solid var(--color-success);
}

.history-date {
  font-weight: var(--font-weight-medium);
  color: var(--color-text);
}

.history-details {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.status-applied {
  color: var(--color-success);
  font-weight: var(--font-weight-medium);
}

.status-pending {
  color: var(--color-warning);
  font-weight: var(--font-weight-medium);
}

/* Responsive Design */
@media (max-width: 768px) {
  .suggestions-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-md);
  }

  .suggestions-actions {
    justify-content: stretch;
  }

  .suggestions-actions button {
    flex: 1;
  }

  .suggestion-meta {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
