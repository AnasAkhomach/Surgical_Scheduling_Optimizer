<template>
  <div class="optimization-suggestions">
    <div class="suggestions-header">
      <h3>🚀 Optimization Suggestions</h3>
      <div class="header-actions">
        <button
          v-if="!optimizationResults"
          @click="runQuickOptimization"
          :disabled="isOptimizing"
          class="quick-optimize-btn"
        >
          <span v-if="isOptimizing" class="spinner"></span>
          {{ isOptimizing ? 'Analyzing...' : 'Quick Optimize' }}
        </button>
        <router-link to="/optimization" class="view-all-link">
          View All
        </router-link>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isOptimizing" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Analyzing schedule for optimization opportunities...</p>
    </div>

    <!-- Suggestions List -->
    <div v-else-if="topSuggestions.length > 0" class="suggestions-list">
      <div
        v-for="suggestion in topSuggestions"
        :key="suggestion.id"
        class="suggestion-item"
        :class="`priority-${suggestion.priority.toLowerCase()}`"
      >
        <div class="suggestion-content">
          <div class="suggestion-header">
            <h4>{{ suggestion.title }}</h4>
            <div class="suggestion-meta">
              <span class="priority-badge" :class="`priority-${suggestion.priority.toLowerCase()}`">
                {{ suggestion.priority }}
              </span>
              <span class="impact">{{ suggestion.impact }} min</span>
            </div>
          </div>
          <p class="suggestion-description">{{ suggestion.description }}</p>
          <div class="suggestion-actions">
            <button
              @click="applySuggestion(suggestion.id)"
              class="apply-btn"
              :disabled="isApplying"
            >
              Apply
            </button>
            <span class="savings">{{ suggestion.estimatedSavings }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- No Suggestions State -->
    <div v-else-if="optimizationResults && topSuggestions.length === 0" class="no-suggestions">
      <div class="no-suggestions-content">
        <span class="success-icon">✅</span>
        <h4>Schedule Optimized!</h4>
        <p>Your current schedule is already well-optimized. No immediate improvements found.</p>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="initial-state">
      <div class="initial-content">
        <span class="optimize-icon">🎯</span>
        <h4>Ready to Optimize</h4>
        <p>Click "Quick Optimize" to get intelligent suggestions for improving your schedule.</p>
        <ul class="benefits-list">
          <li>Reduce SDST times</li>
          <li>Improve resource utilization</li>
          <li>Resolve conflicts</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useOptimizationStore } from '@/stores/optimizationStore';
import { storeToRefs } from 'pinia';

const optimizationStore = useOptimizationStore();
const {
  isOptimizing,
  optimizationResults,
  currentSuggestions
} = storeToRefs(optimizationStore);

// Local state
const isApplying = ref(false);

// Computed properties
const topSuggestions = computed(() => {
  return currentSuggestions.value.slice(0, 3); // Show top 3 suggestions
});

// Methods
const runQuickOptimization = async () => {
  try {
    await optimizationStore.runOptimization();
  } catch (error) {
    console.error('Quick optimization failed:', error);
  }
};

const applySuggestion = async (suggestionId) => {
  isApplying.value = true;
  try {
    await optimizationStore.applySuggestions([suggestionId]);
    console.log('Suggestion applied successfully');
  } catch (error) {
    console.error('Failed to apply suggestion:', error);
  } finally {
    isApplying.value = false;
  }
};
</script>

<style scoped>
.optimization-suggestions {
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.suggestions-header h3 {
  margin: 0;
  color: var(--color-text);
  font-size: var(--font-size-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.quick-optimize-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.quick-optimize-btn:disabled {
  background-color: var(--color-border);
  cursor: not-allowed;
}

.view-all-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.view-all-link:hover {
  text-decoration: underline;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: var(--spacing-xl);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(var(--color-primary-rgb), 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-md) auto;
}

.loading-state p {
  color: var(--color-text-secondary);
  margin: 0;
}

/* Suggestions List */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.suggestion-item {
  background-color: var(--color-background);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-border);
  padding: var(--spacing-md);
}

.suggestion-item.priority-high {
  border-left-color: var(--color-error);
}

.suggestion-item.priority-medium {
  border-left-color: var(--color-warning);
}

.suggestion-item.priority-low {
  border-left-color: var(--color-success);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-sm);
}

.suggestion-header h4 {
  margin: 0;
  color: var(--color-text);
  font-size: var(--font-size-md);
  flex: 1;
}

.suggestion-meta {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.priority-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
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

.impact {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background-color: var(--color-background-mute);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
}

.suggestion-description {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.suggestion-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.apply-btn {
  background-color: var(--color-success);
  color: white;
  border: none;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.apply-btn:disabled {
  background-color: var(--color-border);
  cursor: not-allowed;
}

.savings {
  font-size: var(--font-size-sm);
  color: var(--color-success);
  font-weight: var(--font-weight-medium);
}

/* No Suggestions State */
.no-suggestions {
  text-align: center;
  padding: var(--spacing-xl);
}

.no-suggestions-content {
  max-width: 300px;
  margin: 0 auto;
}

.success-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: var(--spacing-md);
}

.no-suggestions h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-success);
}

.no-suggestions p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* Initial State */
.initial-state {
  text-align: center;
  padding: var(--spacing-xl);
}

.initial-content {
  max-width: 300px;
  margin: 0 auto;
}

.optimize-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: var(--spacing-md);
}

.initial-state h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text);
}

.initial-state p {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.benefits-list {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
}

.benefits-list li {
  padding: var(--spacing-xs) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  position: relative;
  padding-left: var(--spacing-lg);
}

.benefits-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--color-success);
  font-weight: bold;
}

/* Responsive Design */
@media (max-width: 768px) {
  .suggestions-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-md);
  }

  .header-actions {
    justify-content: space-between;
  }

  .suggestion-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }

  .suggestion-meta {
    justify-content: flex-start;
  }

  .suggestion-actions {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }
}
</style>
