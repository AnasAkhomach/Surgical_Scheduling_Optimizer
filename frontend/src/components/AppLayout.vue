<template>
  <div :class="['app-layout', {
    'sidebar-collapsed': isSidebarCollapsed,
    'mobile-nav-open': isMobileNavOpen,
    'is-mobile': isMobile
  }]">
    <header class="top-nav-bar">
      <div class="app-brand">
         <button
           @click="toggleSidebar"
           class="icon-button toggle-sidebar-button btn-touch"
           aria-label="Toggle Sidebar"
           :class="{ 'mobile-hamburger': isMobile }"
         >
             <!-- Mobile hamburger menu or desktop arrow -->
             <span v-if="isMobile" class="hamburger-icon">
               <span class="hamburger-line"></span>
               <span class="hamburger-line"></span>
               <span class="hamburger-line"></span>
             </span>
             <span v-else-if="isSidebarCollapsed">&#x25BA;</span> <!-- Right arrow -->
             <span v-else>&#x25C4;</span> <!-- Left arrow -->
         </button>
        <!-- App Logo/Name -->
        <img src="/vite.svg" alt="App Logo" class="app-logo-small">
        <span v-if="!isSidebarCollapsed || !isMobile" class="app-title">Surgery Scheduler</span>
      </div>
      <div class="global-search" :class="{ 'mobile-hidden': isMobile && !showMobileSearch }">
        <!-- Global Search Bar -->
        <input
          type="text"
          placeholder="Search..."
          v-model="searchTerm"
          @input="handleSearch"
          aria-label="Search"
          class="form-control-mobile"
        >
      </div>
      <div class="user-utilities">
        <!-- Mobile Search Toggle -->
        <button
          v-if="isMobile"
          @click="toggleMobileSearch"
          class="icon-button btn-touch mobile-search-toggle"
          aria-label="Toggle Search"
        >
          🔍
        </button>
        <!-- Notification Icon -->
        <button class="icon-button btn-touch" aria-label="Notifications">
          <span class="notification-icon">🔔</span>
          <span v-if="notificationCount > 0" class="notification-badge">{{ notificationCount }}</span>
        </button>
        <!-- User Profile Dropdown -->
        <div class="user-profile" aria-haspopup="true" aria-expanded="false">
          <span class="user-name" :class="{ 'mobile-hidden': isMobile }">{{ authStore.user?.username || 'User Name' }}</span>
          <span class="user-profile-dropdown-icon">▼</span>
        </div>
      </div>
    </header>

    <!-- Mobile Search Overlay -->
    <div v-if="isMobile && showMobileSearch" class="mobile-search-overlay">
      <div class="mobile-search-container">
        <input
          type="text"
          placeholder="Search surgeries, patients, staff..."
          v-model="searchTerm"
          @input="handleSearch"
          aria-label="Mobile Search"
          class="mobile-search-input form-control-mobile"
          ref="mobileSearchInput"
        >
        <button @click="toggleMobileSearch" class="mobile-search-close btn-touch">✕</button>
      </div>
    </div>

    <!-- Mobile Navigation Overlay -->
    <div v-if="isMobile && isMobileNavOpen" class="mobile-nav-overlay" @click="closeMobileNav"></div>

    <aside class="left-sidebar" :class="{ 'mobile-sidebar': isMobile }">
      <!-- Navigation Links -->
      <nav aria-label="Main Navigation">
        <ul>
          <li>
            <router-link to="/dashboard" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">🏠</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Dashboard</span>
            </router-link>
          </li>
          <li>
            <router-link to="/scheduling" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">📅</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Surgery Scheduling</span>
            </router-link>
          </li>
          <li>
            <router-link to="/master-schedule" @click="handleNavClick" class="nav-link nav-link-prominent">
              <span class="nav-icon" aria-hidden="true">📊</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Master Schedule (Gantt)</span>
            </router-link>
          </li>
          <li>
            <router-link to="/resource-management" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">🛠️</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Resource Management</span>
            </router-link>
          </li>
          <li>
            <router-link to="/sdst-data-management" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">📊</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">SDST Data Management</span>
            </router-link>
          </li>
          <li>
            <router-link to="/reporting-analytics" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">📈</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Reporting & Analytics</span>
            </router-link>
          </li>
          <li>
            <router-link to="/optimization" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">🚀</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Optimization Engine</span>
            </router-link>
          </li>
          <li>
            <router-link to="/notifications" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">🔔</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Notifications</span>
            </router-link>
          </li>
          <li>
            <router-link to="/administration" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">⚙️</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Administration</span>
            </router-link>
          </li>
          <li>
            <router-link to="/patient-management" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">👨‍⚕️</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Patient Management</span>
            </router-link>
          </li>
          <li>
            <router-link to="/my-profile-settings" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">👤</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">My Profile / Settings</span>
            </router-link>
          </li>
          <li>
            <router-link to="/help-documentation" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">❓</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Help / Documentation</span>
            </router-link>
          </li>
          <li>
            <router-link to="/mobile-test" @click="handleNavClick" class="nav-link">
              <span class="nav-icon" aria-hidden="true">📱</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Mobile Test</span>
            </router-link>
          </li>
          <li class="logout-item">
            <button @click="handleLogout" class="logout-button nav-link">
              <span class="nav-icon" aria-hidden="true">🚪</span>
              <span v-if="!isSidebarCollapsed || isMobile" class="nav-text">Logout</span>
            </button>
          </li>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

// Import the authentication store
import { useAuthStore } from '@/stores/authStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const authStore = useAuthStore();

// Use storeToRefs for reactive state from the store if needed in template directly
const { isAuthenticated, user, isLoading, error } = storeToRefs(authStore);

// Mobile responsiveness state
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value < 768);
const isTablet = computed(() => windowWidth.value >= 768 && windowWidth.value < 1024);

// Navigation state
const isSidebarCollapsed = ref(false);
const isMobileNavOpen = ref(false);
const showMobileSearch = ref(false);
const searchTerm = ref('');

// Notification state
const notificationCount = ref(3); // Mock notification count

// Refs for mobile functionality
const mobileSearchInput = ref(null);

// Handle window resize for responsive behavior
const handleResize = () => {
  windowWidth.value = window.innerWidth;

  // Auto-close mobile nav when switching to desktop
  if (!isMobile.value && isMobileNavOpen.value) {
    isMobileNavOpen.value = false;
  }

  // Auto-close mobile search when switching to desktop
  if (!isMobile.value && showMobileSearch.value) {
    showMobileSearch.value = false;
  }
};

// Toggle sidebar/mobile navigation
const toggleSidebar = () => {
  if (isMobile.value) {
    isMobileNavOpen.value = !isMobileNavOpen.value;
    // Prevent body scroll when mobile nav is open
    document.body.style.overflow = isMobileNavOpen.value ? 'hidden' : '';
  } else {
    isSidebarCollapsed.value = !isSidebarCollapsed.value;
  }
};

// Close mobile navigation
const closeMobileNav = () => {
  isMobileNavOpen.value = false;
  document.body.style.overflow = '';
};

// Handle navigation click (close mobile nav on mobile)
const handleNavClick = () => {
  if (isMobile.value) {
    closeMobileNav();
  }
};

// Toggle mobile search
const toggleMobileSearch = async () => {
  showMobileSearch.value = !showMobileSearch.value;

  if (showMobileSearch.value) {
    // Focus the search input after the overlay is rendered
    await nextTick();
    if (mobileSearchInput.value) {
      mobileSearchInput.value.focus();
    }
  }
};

// Handle logout
const handleLogout = () => {
  console.log('AppLayout: Handling logout click.');
  authStore.logout();
  // Close mobile nav if open
  if (isMobile.value) {
    closeMobileNav();
  }
};

// Handle search
const handleSearch = () => {
  console.log('Searching for:', searchTerm.value);
  // In a real app, this would trigger a search action
  // Close mobile search after search on mobile
  if (isMobile.value && showMobileSearch.value) {
    showMobileSearch.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  window.addEventListener('resize', handleResize);

  // Set initial sidebar state based on screen size
  if (isMobile.value) {
    isSidebarCollapsed.value = true;
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  // Clean up body overflow style
  document.body.style.overflow = '';
});

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

/* Mobile layout adjustments */
.app-layout.is-mobile {
  grid-template-columns: 1fr; /* Single column on mobile */
  grid-template-rows: var(--top-nav-height) 1fr;
}

.app-layout.is-mobile.mobile-nav-open {
  overflow: hidden;
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

/* Mobile hamburger menu styles */
.mobile-hamburger {
  position: relative;
  padding: 12px;
}

.hamburger-icon {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 20px;
  height: 16px;
}

.hamburger-line {
  width: 100%;
  height: 2px;
  background-color: var(--color-text-secondary);
  transition: all 0.3s ease;
}

.mobile-nav-open .hamburger-line:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.mobile-nav-open .hamburger-line:nth-child(2) {
  opacity: 0;
}

.mobile-nav-open .hamburger-line:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -6px);
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
    position: relative;
}

.icon-button:hover {
    background-color: #e9ecef;
    color: var(--color-primary);
}

/* Notification badge */
.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: var(--color-danger);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7em;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
}

/* Mobile search overlay */
.mobile-search-overlay {
  position: fixed;
  top: var(--top-nav-height);
  left: 0;
  right: 0;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  z-index: var(--z-index-mobile-nav);
  padding: var(--spacing-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mobile-search-container {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.mobile-search-input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
}

.mobile-search-close {
  background-color: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  width: var(--touch-target-comfortable);
  height: var(--touch-target-comfortable);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
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

/* Mobile sidebar styles */
.left-sidebar.mobile-sidebar {
  position: fixed;
  top: var(--top-nav-height);
  left: 0;
  bottom: 0;
  width: 280px;
  z-index: var(--z-index-mobile-nav);
  transform: translateX(-100%);
  transition: transform 0.3s ease-in-out;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.app-layout.mobile-nav-open .left-sidebar.mobile-sidebar {
  transform: translateX(0);
}

/* Mobile navigation overlay */
.mobile-nav-overlay {
  position: fixed;
  top: var(--top-nav-height);
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: calc(var(--z-index-mobile-nav) - 1);
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
.left-sidebar nav .logout-button,
.nav-link {
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
  min-height: var(--touch-target-min);
}

/* Mobile navigation link styles */
.mobile-sidebar .nav-link {
  padding: 16px 20px;
  font-size: 1rem;
  min-height: var(--touch-target-comfortable);
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

/* Prominent navigation link styling for Master Schedule */
.nav-link-prominent {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white !important;
  font-weight: 600;
  border-left: 3px solid var(--color-primary-dark);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-link-prominent:hover {
  background: linear-gradient(135deg, var(--color-primary-dark) 0%, var(--color-primary) 100%);
  color: white !important;
  transform: translateX(2px);
}

.nav-link-prominent.router-link-exact-active {
  background: linear-gradient(135deg, var(--color-primary-dark) 0%, var(--color-primary) 100%);
  color: white !important;
  border-left-color: white;
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

/* Mobile main content styles */
.app-layout.is-mobile .main-content {
  grid-column: 1;
  padding: var(--spacing-md);
  padding-bottom: calc(var(--spacing-md) + env(safe-area-inset-bottom, 0px));
}

/* Responsive breakpoints for AppLayout */
@media (max-width: 767px) {
  .app-brand .app-title {
    font-size: var(--font-size-base);
  }

  .global-search {
    display: none;
  }

  .user-utilities .user-name {
    display: none;
  }

  .icon-button {
    margin-left: var(--spacing-sm);
    padding: var(--spacing-sm);
  }
}

@media (max-width: 480px) {
  .top-nav-bar {
    padding: 0 var(--spacing-sm);
  }

  .app-brand .app-title {
    display: none;
  }

  .main-content {
    padding: var(--spacing-sm);
  }
}

/* Landscape orientation adjustments for mobile */
@media (max-height: 500px) and (orientation: landscape) {
  .mobile-sidebar .nav-link {
    padding: 12px 20px;
    min-height: 40px;
  }
}
</style>
