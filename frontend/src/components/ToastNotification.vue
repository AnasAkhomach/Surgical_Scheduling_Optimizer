<template>
  <Teleport to="body">
    <div class="toast-container" data-testid="toast-notification">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="[`toast-${toast.type}`, { 'with-action': toast.action }]"
          role="alert"
          aria-live="assertive"
        >
          <div class="toast-icon" aria-hidden="true">
            <span v-if="toast.type === 'success'">✓</span>
            <span v-else-if="toast.type === 'error'">✕</span>
            <span v-else-if="toast.type === 'warning'">⚠</span>
            <span v-else>ℹ</span>
          </div>
          <div class="toast-content">
            <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
            <div class="toast-message">{{ toast.message }}</div>
          </div>
          <button
            v-if="toast.action"
            class="toast-action"
            @click="toast.action.callback"
            :aria-label="toast.action.label"
          >
            {{ toast.action.label }}
          </button>
          <button
            class="toast-close"
            @click="dismissToast(toast.id)"
            aria-label="Close notification"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// Toast data structure
// {
//   id: string,
//   type: 'success' | 'error' | 'warning' | 'info',
//   message: string,
//   title?: string,
//   duration?: number,
//   action?: { label: string, callback: Function }
// }

const toasts = ref([]);
const toastTimeouts = ref({});

// Add a new toast notification
const addToast = (toast) => {
  const id = `toast-${Date.now()}`;
  const newToast = {
    id,
    type: toast.type || 'info',
    message: toast.message,
    title: toast.title || null,
    duration: toast.duration !== undefined ? toast.duration : 5000, // Default 5 seconds
    action: toast.action || null
  };

  toasts.value.push(newToast);

  // Auto-dismiss after duration
  if (newToast.duration > 0) {
    toastTimeouts.value[id] = setTimeout(() => {
      dismissToast(id);
    }, newToast.duration);
  }

  return id;
};

// Dismiss a toast by ID
const dismissToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id);
  if (index !== -1) {
    toasts.value.splice(index, 1);

    // Clear the timeout
    if (toastTimeouts.value[id]) {
      clearTimeout(toastTimeouts.value[id]);
      delete toastTimeouts.value[id];
    }
  }
};

// Expose methods to parent components
defineExpose({
  addToast,
  dismissToast
});

// Clean up timeouts on component unmount
onUnmounted(() => {
  Object.values(toastTimeouts.value).forEach(timeout => {
    clearTimeout(timeout);
  });
});
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  max-width: 400px;
  width: calc(100% - 40px);
}

.toast {
  display: flex;
  align-items: flex-start;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  background-color: var(--color-background);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: var(--spacing-sm);
  animation: slide-in 0.3s ease-out;
  border-left: 4px solid var(--color-primary);
}

.toast-success {
  border-left-color: var(--color-success, #10b981);
}

.toast-error {
  border-left-color: var(--color-error, #ef4444);
}

.toast-warning {
  border-left-color: var(--color-warning, #f59e0b);
}

.toast-info {
  border-left-color: var(--color-primary);
}

.toast-icon {
  margin-right: var(--spacing-sm);
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
}

.toast-success .toast-icon {
  color: var(--color-success, #10b981);
}

.toast-error .toast-icon {
  color: var(--color-error, #ef4444);
}

.toast-warning .toast-icon {
  color: var(--color-warning, #f59e0b);
}

.toast-info .toast-icon {
  color: var(--color-primary);
}

.toast-content {
  flex-grow: 1;
  margin-right: var(--spacing-sm);
}

.toast-title {
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-xs);
}

.toast-message {
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.toast-close {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  padding: var(--spacing-xs);
  margin: calc(-1 * var(--spacing-xs));
  border-radius: var(--border-radius-sm);
}

.toast-close:hover {
  color: var(--color-text);
  background-color: var(--color-background-mute);
}

.toast-action {
  margin-right: var(--spacing-sm);
  background-color: transparent;
  border: 1px solid currentColor;
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
  cursor: pointer;
  color: inherit;
}

.toast-success .toast-action {
  color: var(--color-success, #10b981);
}

.toast-error .toast-action {
  color: var(--color-error, #ef4444);
}

.toast-warning .toast-action {
  color: var(--color-warning, #f59e0b);
}

.toast-info .toast-action {
  color: var(--color-primary);
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

@keyframes slide-in {
  from {
    transform: translateX(30px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .toast-container {
    top: auto;
    bottom: 20px;
    left: 20px;
    right: 20px;
    max-width: none;
    width: calc(100% - 40px);
  }
}
</style>
