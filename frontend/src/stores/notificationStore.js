import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([]);
  const toastRef = ref(null);

  // Set the toast component reference
  const setToastRef = (ref) => {
    toastRef.value = ref;
  };

  // Show a success notification
  const success = (message, options = {}) => {
    return showNotification({
      type: 'success',
      message,
      ...options
    });
  };

  // Show an error notification
  const error = (message, options = {}) => {
    return showNotification({
      type: 'error',
      message,
      ...options
    });
  };

  // Show a warning notification
  const warning = (message, options = {}) => {
    return showNotification({
      type: 'warning',
      message,
      ...options
    });
  };

  // Show an info notification
  const info = (message, options = {}) => {
    return showNotification({
      type: 'info',
      message,
      ...options
    });
  };

  // Generic method to show a notification
  const showNotification = (notification) => {
    if (toastRef.value) {
      return toastRef.value.addToast(notification);
    } else {
      console.warn('Toast component reference not set. Falling back to alert.');
      alert(`${notification.type.toUpperCase()}: ${notification.message}`);
      return null;
    }
  };

  // Dismiss a notification by ID
  const dismiss = (id) => {
    if (toastRef.value) {
      toastRef.value.dismissToast(id);
    }
  };

  return {
    notifications,
    setToastRef,
    success,
    error,
    warning,
    info,
    showNotification,
    dismiss
  };
});
