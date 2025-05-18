<template>
  <div class="notification-center">
    <Button 
      icon="pi pi-bell" 
      class="p-button-rounded p-button-text" 
      @click="toggleNotifications"
      :badge="unreadCount > 0 ? unreadCount.toString() : undefined"
      badge-class="p-badge-danger"
    />
    
    <OverlayPanel ref="notificationPanel" :style="{ width: '350px' }">
      <template #header>
        <div class="flex justify-content-between align-items-center">
          <h3 class="m-0">Notifications</h3>
          <div>
            <Button 
              v-if="hasUnread" 
              label="Mark All Read" 
              class="p-button-text p-button-sm" 
              @click="markAllAsRead" 
            />
            <Button 
              v-if="notifications.length > 0" 
              label="Clear All" 
              class="p-button-text p-button-sm p-button-danger" 
              @click="clearNotifications" 
            />
          </div>
        </div>
      </template>
      
      <div class="notification-list" v-if="notifications.length > 0">
        <div 
          v-for="notification in notifications" 
          :key="notification.id" 
          class="notification-item p-3 mb-2" 
          :class="{ 'unread': !notification.read }"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-header flex align-items-center mb-2">
            <i 
              class="notification-icon mr-2" 
              :class="getNotificationIcon(notification.type)"
            ></i>
            <span class="notification-title font-bold">{{ notification.title }}</span>
            <small class="notification-time ml-auto">{{ formatTime(notification.timestamp) }}</small>
          </div>
          <div class="notification-message">{{ notification.message }}</div>
        </div>
      </div>
      
      <div v-else class="p-3 text-center">
        <i class="pi pi-inbox text-5xl text-color-secondary mb-3"></i>
        <p>No notifications</p>
      </div>
    </OverlayPanel>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import moment from 'moment';

export default {
  name: 'NotificationCenter',
  setup() {
    const store = useStore();
    const notificationPanel = ref(null);
    
    const notifications = computed(() => store.getters['notifications/notifications']);
    const unreadCount = computed(() => store.getters['notifications/unreadCount']);
    const hasUnread = computed(() => store.getters['notifications/hasUnread']);
    
    const toggleNotifications = (event) => {
      notificationPanel.value.toggle(event);
    };
    
    const markAsRead = (id) => {
      store.dispatch('notifications/markAsRead', id);
    };
    
    const markAllAsRead = () => {
      store.dispatch('notifications/markAllAsRead');
    };
    
    const clearNotifications = () => {
      store.dispatch('notifications/clearNotifications');
    };
    
    const getNotificationIcon = (type) => {
      switch (type) {
        case 'success':
          return 'pi pi-check-circle text-green-500';
        case 'info':
          return 'pi pi-info-circle text-blue-500';
        case 'warning':
          return 'pi pi-exclamation-triangle text-orange-500';
        case 'error':
          return 'pi pi-times-circle text-red-500';
        default:
          return 'pi pi-info-circle text-blue-500';
      }
    };
    
    const formatTime = (timestamp) => {
      return moment(timestamp).fromNow();
    };
    
    // Add some mock notifications for demonstration
    onMounted(() => {
      // Only add mock notifications if there are none
      if (notifications.value.length === 0) {
        store.dispatch('notifications/addNotification', {
          type: 'info',
          title: 'Welcome',
          message: 'Welcome to the Surgery Scheduling Application',
          timestamp: new Date()
        });
        
        store.dispatch('notifications/addNotification', {
          type: 'success',
          title: 'Schedule Optimized',
          message: 'The schedule has been optimized successfully',
          timestamp: new Date(Date.now() - 1000 * 60 * 5) // 5 minutes ago
        });
        
        store.dispatch('notifications/addNotification', {
          type: 'warning',
          title: 'Surgeon Availability',
          message: 'Dr. Smith is not available on Friday',
          timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30 minutes ago
        });
      }
    });
    
    return {
      notificationPanel,
      notifications,
      unreadCount,
      hasUnread,
      toggleNotifications,
      markAsRead,
      markAllAsRead,
      clearNotifications,
      getNotificationIcon,
      formatTime
    };
  }
}
</script>

<style scoped>
.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  border-radius: 4px;
  background-color: #f8f9fa;
  transition: background-color 0.2s;
  cursor: pointer;
}

.notification-item:hover {
  background-color: #e9ecef;
}

.notification-item.unread {
  background-color: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.notification-item.unread:hover {
  background-color: #bbdefb;
}

.notification-icon {
  font-size: 1.2rem;
}

.notification-time {
  font-size: 0.8rem;
  color: #6c757d;
}

.notification-message {
  color: #495057;
}
</style>
