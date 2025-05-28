<template>
  <div class="notifications-container">
    <!-- Enhanced Header -->
    <div class="notifications-header">
      <div class="header-content">
        <h1>Notifications & Alerts</h1>
        <p class="header-subtitle">Stay informed about critical updates and system alerts</p>
      </div>
      <div class="header-actions">
        <button @click="markAllAsRead" class="btn btn-secondary" :disabled="unreadCount === 0">
          <span class="icon">✓</span> Mark All Read ({{ unreadCount }})
        </button>
        <button @click="clearAll" class="btn btn-outline">
          <span class="icon">🗑️</span> Clear All
        </button>
        <button @click="refreshNotifications" class="btn btn-primary">
          <span class="icon">🔄</span> Refresh
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="notification-filters">
      <button
        v-for="filter in filters"
        :key="filter.key"
        @click="activeFilter = filter.key"
        :class="['filter-tab', { active: activeFilter === filter.key }]"
      >
        <span class="filter-icon">{{ filter.icon }}</span>
        <span class="filter-label">{{ filter.label }}</span>
        <span v-if="filter.count > 0" class="filter-count">{{ filter.count }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-message">
      <div class="loading-spinner"></div>
      <p>Loading notifications...</p>
    </div>

    <!-- Notifications List -->
    <div v-else class="notifications-list">
      <div v-if="filteredNotifications.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No notifications</h3>
        <p>{{ getEmptyStateMessage() }}</p>
      </div>

      <div v-else class="notification-items">
        <div
          v-for="notification in filteredNotifications"
          :key="notification.id"
          :class="['notification-item', notification.type, { unread: !notification.read }]"
          @click="markAsRead(notification)"
        >
          <div class="notification-icon">
            <span>{{ getNotificationIcon(notification.type) }}</span>
          </div>
          <div class="notification-content">
            <div class="notification-header">
              <h4 class="notification-title">{{ notification.title }}</h4>
              <span class="notification-time">{{ formatTime(notification.timestamp) }}</span>
            </div>
            <p class="notification-message">{{ notification.message }}</p>
            <div v-if="notification.actions" class="notification-actions">
              <button
                v-for="action in notification.actions"
                :key="action.label"
                @click.stop="handleAction(action, notification)"
                :class="['action-btn', action.type]"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
          <div class="notification-controls">
            <button @click.stop="dismissNotification(notification)" class="dismiss-btn">
              <span>×</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Reactive state
const isLoading = ref(false);
const activeFilter = ref('all');
const notifications = ref([]);

// Sample notification data - in real app, this would come from an API/store
const sampleNotifications = [
  {
    id: 1,
    type: 'critical',
    title: 'Emergency Surgery Scheduled',
    message: 'Emergency appendectomy scheduled for OR 3 at 14:30. Immediate attention required.',
    timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    read: false,
    actions: [
      { label: 'View Details', type: 'primary', action: 'view-surgery' },
      { label: 'Acknowledge', type: 'secondary', action: 'acknowledge' }
    ]
  },
  {
    id: 2,
    type: 'warning',
    title: 'SDST Conflict Detected',
    message: 'Potential setup time conflict between surgeries in OR 2. Review scheduling.',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    read: false,
    actions: [
      { label: 'Resolve Conflict', type: 'primary', action: 'resolve-conflict' },
      { label: 'Ignore', type: 'secondary', action: 'ignore' }
    ]
  },
  {
    id: 3,
    type: 'info',
    title: 'Daily Schedule Optimized',
    message: 'Schedule optimization completed. 15% improvement in OR utilization achieved.',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
    read: true,
    actions: [
      { label: 'View Report', type: 'primary', action: 'view-report' }
    ]
  },
  {
    id: 4,
    type: 'success',
    title: 'Surgery Completed Successfully',
    message: 'Knee arthroscopy in OR 1 completed successfully. Patient transferred to recovery.',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
    read: true
  },
  {
    id: 5,
    type: 'warning',
    title: 'Equipment Maintenance Due',
    message: 'Anesthesia machine in OR 4 requires scheduled maintenance within 48 hours.',
    timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 hours ago
    read: false,
    actions: [
      { label: 'Schedule Maintenance', type: 'primary', action: 'schedule-maintenance' },
      { label: 'Postpone', type: 'secondary', action: 'postpone' }
    ]
  },
  {
    id: 6,
    type: 'info',
    title: 'New Staff Member Added',
    message: 'Dr. Sarah Johnson has been added to the surgical team for cardiovascular procedures.',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
    read: true
  }
];

// Filter definitions
const filters = computed(() => [
  {
    key: 'all',
    label: 'All',
    icon: '📋',
    count: notifications.value.length
  },
  {
    key: 'unread',
    label: 'Unread',
    icon: '🔴',
    count: notifications.value.filter(n => !n.read).length
  },
  {
    key: 'critical',
    label: 'Critical',
    icon: '🚨',
    count: notifications.value.filter(n => n.type === 'critical').length
  },
  {
    key: 'warning',
    label: 'Warnings',
    icon: '⚠️',
    count: notifications.value.filter(n => n.type === 'warning').length
  },
  {
    key: 'info',
    label: 'Info',
    icon: 'ℹ️',
    count: notifications.value.filter(n => n.type === 'info').length
  },
  {
    key: 'success',
    label: 'Success',
    icon: '✅',
    count: notifications.value.filter(n => n.type === 'success').length
  }
]);

// Computed properties
const filteredNotifications = computed(() => {
  let filtered = notifications.value;

  switch (activeFilter.value) {
    case 'unread':
      filtered = filtered.filter(n => !n.read);
      break;
    case 'critical':
    case 'warning':
    case 'info':
    case 'success':
      filtered = filtered.filter(n => n.type === activeFilter.value);
      break;
    default:
      // 'all' - no filtering
      break;
  }

  // Sort by timestamp (newest first)
  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
});

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length;
});

// Methods
const getNotificationIcon = (type) => {
  const icons = {
    critical: '🚨',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅'
  };
  return icons[type] || 'ℹ️';
};

const formatTime = (timestamp) => {
  const now = new Date();
  const diff = now - new Date(timestamp);
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (minutes < 60) {
    return `${minutes}m ago`;
  } else if (hours < 24) {
    return `${hours}h ago`;
  } else {
    return `${days}d ago`;
  }
};

const getEmptyStateMessage = () => {
  switch (activeFilter.value) {
    case 'unread':
      return 'All notifications have been read.';
    case 'critical':
      return 'No critical alerts at this time.';
    case 'warning':
      return 'No warnings to display.';
    case 'info':
      return 'No informational notifications.';
    case 'success':
      return 'No success notifications.';
    default:
      return 'No notifications available.';
  }
};

const markAsRead = (notification) => {
  if (!notification.read) {
    notification.read = true;
    console.log('Marked notification as read:', notification.title);
  }
};

const markAllAsRead = () => {
  notifications.value.forEach(n => {
    n.read = true;
  });
  console.log('Marked all notifications as read');
};

const dismissNotification = (notification) => {
  const index = notifications.value.findIndex(n => n.id === notification.id);
  if (index > -1) {
    notifications.value.splice(index, 1);
    console.log('Dismissed notification:', notification.title);
  }
};

const clearAll = () => {
  if (confirm('Are you sure you want to clear all notifications?')) {
    notifications.value = [];
    console.log('Cleared all notifications');
  }
};

const refreshNotifications = () => {
  isLoading.value = true;
  console.log('Refreshing notifications...');

  // Simulate API call
  setTimeout(() => {
    // In real app, this would fetch from API
    notifications.value = [...sampleNotifications];
    isLoading.value = false;
    console.log('Notifications refreshed');
  }, 1000);
};

const handleAction = (action, notification) => {
  console.log('Handling action:', action.action, 'for notification:', notification.title);

  switch (action.action) {
    case 'view-surgery':
      router.push({ name: 'Scheduling' });
      break;
    case 'resolve-conflict':
      router.push({ name: 'MasterSchedule' });
      break;
    case 'view-report':
      console.log('Navigate to reports');
      break;
    case 'schedule-maintenance':
      console.log('Navigate to maintenance scheduling');
      break;
    case 'acknowledge':
    case 'ignore':
    case 'postpone':
      markAsRead(notification);
      break;
    default:
      console.log('Unknown action:', action.action);
  }
};

// Initialize component
onMounted(() => {
  console.log('NotificationsScreen mounted');
  notifications.value = [...sampleNotifications];
});
</script>

<style scoped>
.notifications-container {
  padding: var(--spacing-lg);
  background-color: var(--color-background);
  min-height: 100vh;
}

/* Enhanced Header */
.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border-radius: var(--border-radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
}

.header-subtitle {
  margin: 0;
  font-size: var(--font-size-base);
  opacity: 0.9;
  font-weight: var(--font-weight-normal);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.header-actions .btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.header-actions .btn-primary {
  background-color: white;
  color: var(--color-primary);
  border-color: white;
}

.header-actions .btn-primary:hover {
  background-color: var(--color-primary-light);
  color: white;
  transform: translateY(-1px);
}

.header-actions .btn-secondary {
  background-color: transparent;
  color: white;
  border-color: white;
}

.header-actions .btn-secondary:hover:not(:disabled) {
  background-color: white;
  color: var(--color-primary);
  transform: translateY(-1px);
}

.header-actions .btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-actions .btn-outline {
  background-color: transparent;
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

.header-actions .btn-outline:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: white;
  transform: translateY(-1px);
}

/* Filter Tabs */
.notification-filters {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-lg);
  overflow-x: auto;
  padding-bottom: var(--spacing-xs);
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-1px);
}

.filter-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.filter-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  min-width: 20px;
  text-align: center;
}

.filter-tab:not(.active) .filter-count {
  background: var(--color-primary);
  color: white;
}

/* Loading State */
.loading-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-md);
}

.empty-state h3 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text);
}

.empty-state p {
  margin: 0;
  font-size: var(--font-size-base);
}

/* Notification Items */
.notification-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.notification-item {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-surface);
  border-radius: var(--border-radius-md);
  border-left: 4px solid var(--color-border);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.notification-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.notification-item.unread {
  background: linear-gradient(135deg, rgba(0, 117, 194, 0.02) 0%, rgba(0, 117, 194, 0.01) 100%);
  border-left-color: var(--color-primary);
}

.notification-item.critical {
  border-left-color: var(--color-danger);
}

.notification-item.critical.unread {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.05) 0%, rgba(220, 53, 69, 0.02) 100%);
}

.notification-item.warning {
  border-left-color: var(--color-warning);
}

.notification-item.warning.unread {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05) 0%, rgba(255, 193, 7, 0.02) 100%);
}

.notification-item.success {
  border-left-color: var(--color-success);
}

.notification-item.success.unread {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.05) 0%, rgba(40, 167, 69, 0.02) 100%);
}

.notification-item.info {
  border-left-color: var(--color-info);
}

.notification-item.info.unread {
  background: linear-gradient(135deg, rgba(23, 162, 184, 0.05) 0%, rgba(23, 162, 184, 0.02) 100%);
}

.notification-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--color-background);
  font-size: var(--font-size-lg);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xs);
  gap: var(--spacing-md);
}

.notification-title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  line-height: 1.4;
}

.notification-time {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
}

.notification-message {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.notification-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.action-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.primary {
  background: var(--color-primary);
  color: white;
}

.action-btn.primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.action-btn.secondary {
  background: var(--color-background);
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}

.action-btn.secondary:hover {
  background: var(--color-border);
  color: var(--color-text);
  transform: translateY(-1px);
}

.notification-controls {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
}

.dismiss-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: var(--font-size-lg);
}

.dismiss-btn:hover {
  background: var(--color-danger);
  color: white;
  transform: scale(1.1);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .notifications-container {
    padding: var(--spacing-md);
  }

  .notifications-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
    padding: var(--spacing-lg);
  }

  .header-content h1 {
    font-size: var(--font-size-xl);
  }

  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .notification-filters {
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }

  .notification-item {
    padding: var(--spacing-md);
  }

  .notification-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }

  .notification-time {
    align-self: flex-end;
  }

  .notification-actions {
    gap: var(--spacing-xs);
  }
}

@media (max-width: 480px) {
  .notifications-header {
    padding: var(--spacing-md);
  }

  .header-content h1 {
    font-size: var(--font-size-lg);
  }

  .header-subtitle {
    font-size: var(--font-size-sm);
  }

  .notification-item {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .notification-icon {
    align-self: flex-start;
  }

  .notification-controls {
    align-self: flex-end;
  }
}
</style>