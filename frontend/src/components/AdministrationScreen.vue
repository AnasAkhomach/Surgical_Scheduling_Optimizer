<template>
  <div class="administration-screen">
    <h1>Administration</h1>
    <div class="admin-navigation">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        @click="activeTab = tab.name"
        :class="['nav-button', { active: activeTab === tab.name }]"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="admin-content">
      <!-- Content for each tab will be rendered here -->
      <div v-if="activeTab === 'userManagement'">
        <p>User Management Content (Placeholder)</p>
      </div>
      <div v-if="activeTab === 'roleManagement'">
        <p>Role Management Content (Placeholder)</p>
      </div>
      <div v-if="activeTab === 'systemSettings'">
        <p>System Settings Content (Placeholder)</p>
      </div>
      <div v-if="activeTab === 'auditLogs'">
        <p>Audit Logs Content (Placeholder)</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const activeTab = ref('userManagement'); // Default active tab

const tabs = [
  { name: 'userManagement', label: 'User Management' },
  { name: 'roleManagement', label: 'Role Management' },
  { name: 'systemSettings', label: 'System Settings' },
  { name: 'auditLogs', label: 'Audit Logs' },
];

// Later, we will import and use actual components for each tab:
// import UserManagement from './UserManagement.vue';
// import RoleManagement from './RoleManagement.vue';
// import SystemConfiguration from './SystemConfiguration.vue';
// import AuditLogViewer from './AuditLogViewer.vue';
</script>

<style scoped>
.administration-screen {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.administration-screen h1 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.admin-navigation {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ccc;
}

.nav-button {
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  background-color: transparent;
  font-size: 16px;
  color: #555;
  margin-right: 5px; /* Spacing between buttons */
  border-bottom: 3px solid transparent; /* For active state indicator */
  transition: color 0.3s ease, border-bottom-color 0.3s ease;
}

.nav-button:hover {
  color: #007bff;
}

.nav-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: bold;
}

.admin-content {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  min-height: 300px; /* Give some space for content */
}

.admin-content p {
  font-size: 1.1em;
  color: #666;
}
</style>