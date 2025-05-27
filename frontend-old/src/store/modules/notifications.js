const state = {
  notifications: [],
  unreadCount: 0,
  maxNotifications: 50 // Maximum number of notifications to keep
}

const getters = {
  notifications: state => state.notifications,
  unreadCount: state => state.unreadCount,
  hasUnread: state => state.unreadCount > 0
}

const actions = {
  /**
   * Add a notification to the store
   * @param {Object} context - Vuex context
   * @param {Object} notification - The notification to add
   * @param {string} notification.type - The notification type (success, info, warning, error)
   * @param {string} notification.title - The notification title
   * @param {string} notification.message - The notification message
   * @param {Date} notification.timestamp - The notification timestamp
   */
  addNotification({ commit }, notification) {
    // Generate a unique ID for the notification
    const id = Date.now() + Math.random().toString(36).substr(2, 5);
    
    // Add default values if not provided
    const newNotification = {
      id,
      read: false,
      type: notification.type || 'info',
      title: notification.title || 'Notification',
      message: notification.message || '',
      timestamp: notification.timestamp || new Date()
    };
    
    commit('ADD_NOTIFICATION', newNotification);
    
    // Play sound for important notifications
    if (notification.type === 'error' || notification.type === 'warning') {
      const audio = new Audio('/notification-sound.mp3');
      audio.play().catch(e => console.warn('Could not play notification sound', e));
    }
    
    return id;
  },
  
  /**
   * Mark a notification as read
   * @param {Object} context - Vuex context
   * @param {string} id - The notification ID
   */
  markAsRead({ commit }, id) {
    commit('MARK_AS_READ', id);
  },
  
  /**
   * Mark all notifications as read
   * @param {Object} context - Vuex context
   */
  markAllAsRead({ commit }) {
    commit('MARK_ALL_AS_READ');
  },
  
  /**
   * Remove a notification
   * @param {Object} context - Vuex context
   * @param {string} id - The notification ID
   */
  removeNotification({ commit }, id) {
    commit('REMOVE_NOTIFICATION', id);
  },
  
  /**
   * Clear all notifications
   * @param {Object} context - Vuex context
   */
  clearNotifications({ commit }) {
    commit('CLEAR_NOTIFICATIONS');
  }
}

const mutations = {
  ADD_NOTIFICATION(state, notification) {
    // Add the notification to the beginning of the array
    state.notifications.unshift(notification);
    
    // Increment the unread count
    state.unreadCount++;
    
    // Limit the number of notifications
    if (state.notifications.length > state.maxNotifications) {
      state.notifications = state.notifications.slice(0, state.maxNotifications);
    }
  },
  
  MARK_AS_READ(state, id) {
    const notification = state.notifications.find(n => n.id === id);
    if (notification && !notification.read) {
      notification.read = true;
      state.unreadCount--;
    }
  },
  
  MARK_ALL_AS_READ(state) {
    state.notifications.forEach(notification => {
      notification.read = true;
    });
    state.unreadCount = 0;
  },
  
  REMOVE_NOTIFICATION(state, id) {
    const index = state.notifications.findIndex(n => n.id === id);
    if (index !== -1) {
      const notification = state.notifications[index];
      if (!notification.read) {
        state.unreadCount--;
      }
      state.notifications.splice(index, 1);
    }
  },
  
  CLEAR_NOTIFICATIONS(state) {
    state.notifications = [];
    state.unreadCount = 0;
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
