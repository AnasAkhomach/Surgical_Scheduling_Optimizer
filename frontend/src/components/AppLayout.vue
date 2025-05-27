<template>
  <div :class="['app-layout', { 'sidebar-collapsed': isSidebarCollapsed }]">
    <header class="top-nav-bar">
      <div class="app-brand">
         <button @click="toggleSidebar" class="icon-button toggle-sidebar-button" aria-label="Toggle Sidebar">
             <!-- Hamburger or arrow icon -->
             <span v-if="isSidebarCollapsed">&#x25BA;</span> <!-- Right arrow -->
             <span v-else>&#x25C4;</span> <!-- Left arrow -->
         </button>
        <!-- App Logo/Name -->
        <img src="/vite.svg" alt="App Logo" class="app-logo-small"> <!-- Assuming vite.svg is in public folder -->
        <span v-if="!isSidebarCollapsed">Surgery Scheduler</span>
      </div>
      <div class="global-search">
        <!-- Global Search Bar -->
        <input type="text" placeholder="Search..." v-model="searchTerm" @input="handleSearch" aria-label="Search">
      </div>
      <div class="user-utilities">
        <!-- Notification Icon -->
        <button class="icon-button" aria-label="Notifications">🔔</button>
        <!-- User Profile Dropdown -->
        <div class="user-profile" aria-haspopup="true" aria-expanded="false"> <!-- Add ARIA for dropdown -->
          <span>{{ authStore.user?.username || 'User Name' }}</span> <!-- Display dynamic username -->
          <!-- Dropdown icon/button here -->
           <span class="user-profile-dropdown-icon">▼</span> <!-- Simple dropdown arrow -->
        </div>
      </div>
    </header>

    <aside class="left-sidebar">
      <!-- Navigation Links -->
      <nav aria-label="Main Navigation">
        <ul>
          <li><router-link to="/dashboard"><span class="nav-icon" aria-hidden="true">🏠</span><span v-if="!isSidebarCollapsed" class="nav-text">Dashboard</span></router-link></li>
          <li><router-link to="/scheduling"><span class="nav-icon" aria-hidden="true">📅</span><span v-if="!isSidebarCollapsed" class="nav-text">Scheduling</span></router-link></li>
          <li><router-link to="/resource-management"><span class="nav-icon" aria-hidden="true">🛠️</span><span v-if="!isSidebarCollapsed" class="nav-text">Resource Management</span></router-link></li>
          <li><router-link to="/sdst-data-management"><span class="nav-icon" aria-hidden="true">📊</span><span v-if="!isSidebarCollapsed" class="nav-text">SDST Data Management</span></router-link></li>
          <li><router-link to="/reporting-analytics"><span class="nav-icon" aria-hidden="true">📈</span><span v-if="!isSidebarCollapsed" class="nav-text">Reporting & Analytics</span></router-link></li>
          <li><router-link to="/notifications"><span class="nav-icon" aria-hidden="true">🔔</span><span v-if="!isSidebarCollapsed" class="nav-text">Notifications</span></router-link></li>
          <li><router-link to="/administration"><span class="nav-icon" aria-hidden="true">⚙️</span><span v-if="!isSidebarCollapsed" class="nav-text">Administration</span></router-link></li>
          <li><router-link to="/patient-management"><span class="nav-icon" aria-hidden="true">👨‍⚕️</span><span v-if="!isSidebarCollapsed" class="nav-text">Patient Management</span></router-link></li>
          <li><router-link to="/my-profile-settings"><span class="nav-icon" aria-hidden="true">👤</span><span v-if="!isSidebarCollapsed" class="nav-text">My Profile / Settings</span></router-link></li>
          <li><router-link to="/help-documentation"><span class="nav-icon" aria-hidden="true">❓</span><span v-if="!isSidebarCollapsed" class="nav-text">Help / Documentation</span></router-link></li>
          <li class="logout-item"><button @click="handleLogout" class="logout-button"><span class="nav-icon" aria-hidden="true">🚪</span><span v-if="!isSidebarCollapsed" class="nav-text">Logout</span></button></li>
        </ul>
      </nav>
    </aside>

    <main class="main-content">
      <!-- Router View renders the specific page component -->
      <router-view />
    </main>
    <!-- Toast notifications are typically triggered programmatically, not placed as a component here -->
    <!-- Toasts will be rendered by the plugin at the root level -->
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// import { setAuthenticated } from '../router'; // REMOVED
import { useToast } from 'vue-toastification'; // Assuming you use this for notifications

// Import the authentication store
import { useAuthStore } from '@/stores/authStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const authStore = useAuthStore(); // Get store instance

// Use storeToRefs for reactive state from the store if needed in template directly
const { isAuthenticated, user, isLoading, error } = storeToRefs(authStore);

const isSidebarCollapsed = ref(false); // State for sidebar collapse
const searchTerm = ref(''); // State for global search input

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const handleLogout = () => {
  console.log('AppLayout: Handling logout click.');
  authStore.logout(); // Call the logout action from the auth store
  // The auth store will handle clearing state and redirecting
};

const handleSearch = () => {
  // Placeholder for actual search logic
  console.log('Searching for:', searchTerm.value);
  // In a real app, this would trigger a search action,
  // potentially navigating to a search results page or filtering data.
};

// Optional: Check auth state on mount to ensure consistency (though router guard should handle initial check)
// onMounted(() => {
//    if (!authStore.isAuthenticated && router.currentRoute.value.meta.requiresAuth) {
//        router.push({ name: 'Login' });
//    }
// });

</script>

<style scoped>
/* Basic Variables (Consider moving to a global CSS file or :root) */
/* These variables should ideally be in a global file like src/style.css */
/* Duplicated here for demonstration, but avoid in production */
:root {
  --color-primary: #4A90E2; /* Example Primary Color */
  --color-primary-dark: #357ABD;
  --color-background: #f4f7f6; /* Light grayish background */
  --color-surface: #ffffff; /* For cards, modals, sidebars */
  --color-text-primary: #333333;
  --color-text-secondary: #555555;
  --color-border: #e0e0e0;
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 60px;
  --top-nav-height: 60px;

  /* Ensure using the variables from src/style.css */
  /* Example: */
  /* --color-primary: var(--color-primary); */
  /* --color-background: var(--color-background); */
  /* etc. */
}

.app-layout {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr; /* Default: Wider Sidebar */
  grid-template-rows: var(--top-nav-height) 1fr; /* Top nav fixed height */
  height: 100vh; /* Full viewport height */
  background-color: var(--color-background);
  overflow: hidden; /* Prevent scrollbars on layout itself */
  transition: grid-template-columns 0.3s ease-in-out; /* Smooth transition for collapse */
}

.app-layout.sidebar-collapsed {
    grid-template-columns: var(--sidebar-width-collapsed) 1fr; /* Collapsed: Narrower Sidebar */
}

.top-nav-bar {
  grid-column: 1 / 3; /* Span across both columns */
  grid-row: 1;
  background-color: var(--color-surface);
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  height: var(--top-nav-height);
}

.app-brand {
  display: flex;
  align-items: center;
  font-size: 1.25em;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
}

.toggle-sidebar-button {
    margin-right: 15px;
    font-size: 1.2em;
    padding: 8px;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: color 0.2s ease, transform 0.3s ease;
}

.toggle-sidebar-button:hover {
    color: var(--color-primary);
}

.app-logo-small {
    height: 32px;
    margin-right: 10px;
    transition: margin-right 0.3s ease-in-out;
}

.app-layout.sidebar-collapsed .app-brand span {
    display: none;
}

.app-layout.sidebar-collapsed .app-logo-small {
     margin-right: 0;
}

.global-search input[type="text"] {
    padding: 9px 15px;
    border: 1px solid var(--color-border);
    border-radius: 18px;
    font-size: 0.9em;
    width: 280px;
    background-color: #f0f2f5;
    color: var(--color-text-primary);
    transition: width 0.3s ease-in-out, background-color 0.2s ease;
}

.global-search input[type="text"]:focus {
    background-color: var(--color-surface);
    border-color: var(--color-primary);
    outline: none;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.user-utilities {
    display: flex;
    align-items: center;
}

.icon-button {
    background: none;
    border: none;
    font-size: 1.4em;
    cursor: pointer;
    margin-left: 15px;
    padding: 8px;
    color: var(--color-text-secondary);
    border-radius: 50%;
    transition: background-color 0.2s ease, color 0.2s ease;
}

.icon-button:hover {
    background-color: #e9ecef;
    color: var(--color-primary);
}

.user-profile {
    display: flex;
    align-items: center;
    cursor: pointer;
    margin-left: 15px;
    padding: 5px 10px;
    border-radius: 15px;
    transition: background-color 0.2s ease;
}

.user-profile:hover {
    background-color: #e9ecef;
}

.user-profile span {
    margin-right: 8px;
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 0.9em;
}

.user-profile-dropdown-icon {
     font-size: 0.7em;
     color: var(--color-text-secondary);
}


.left-sidebar {
  grid-column: 1;
  grid-row: 2;
  background-color: var(--color-surface);
  padding-top: 15px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.3s ease-in-out;
  border-right: 1px solid var(--color-border);
}

.left-sidebar nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.left-sidebar nav li {
  margin-bottom: 2px;
}

.left-sidebar nav a,
.left-sidebar nav .logout-button {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  text-decoration: none;
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: 0.95em;
  transition: background-color 0.2s ease, color 0.2s ease, padding-left 0.3s ease-in-out;
  white-space: nowrap;
  overflow: hidden;
  border-left: 3px solid transparent;
}

.app-layout.sidebar-collapsed .left-sidebar nav a,
.app-layout.sidebar-collapsed .left-sidebar nav .logout-button {
    padding-left: calc((var(--sidebar-width-collapsed) - 24px - 6px) / 2);
    justify-content: center;
}

.app-layout.sidebar-collapsed .left-sidebar nav .nav-text {
    display: none;
}

.left-sidebar nav a:hover,
.left-sidebar nav .logout-button:hover {
  background-color: #e9ecef;
  color: var(--color-primary);
}

.left-sidebar nav a.router-link-exact-active {
  color: var(--color-primary);
  background-color: #e7f3ff;
  border-left-color: var(--color-primary);
}

.nav-icon {
    margin-right: 12px;
    font-size: 1.2em;
    width: 24px;
    text-align: center;
    transition: margin-right 0.3s ease-in-out;
}

.app-layout.sidebar-collapsed .left-sidebar nav .nav-icon {
    margin-right: 0;
}

.logout-item {
    margin-top: auto;
    padding-top: 20px;
    border-top: 1px solid var(--color-border);
}

.logout-button {
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
   /* Use danger color for the button */
    color: var(--color-danger);
    font-weight: var(--font-weight-medium);
}

.logout-button:hover {
     background-color: #e9ecef; /* Light hover */
     color: var(--color-danger-dark); /* Consider adding a danger-dark variable */
}

.main-content {
  grid-column: 2;
  grid-row: 2;
  padding: 25px;
  overflow-y: auto;
  background-color: var(--color-background);
}

/* Scrollbar styling (optional, for a more polished look) */
.left-sidebar::-webkit-scrollbar,
.main-content::-webkit-scrollbar {
  width: 6px;
}

.left-sidebar::-webkit-scrollbar-thumb,
.main-content::-webkit-scrollbar-thumb {
  background-color: #cccccc;
  border-radius: 3px;
}

.left-sidebar::-webkit-scrollbar-thumb:hover,
.main-content::-webkit-scrollbar-thumb:hover {
  background-color: #aaaaaa;
}

.left-sidebar::-webkit-scrollbar-track,
.main-content::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>
