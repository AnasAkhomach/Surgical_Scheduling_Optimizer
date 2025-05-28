import { createApp } from 'vue'
import { createPinia } from 'pinia' // Add Pinia import
import './style.css'
import App from './App.vue'
import router from './router' // Import the router instance
import 'vue-toastification/dist/index.css'; // Import the CSS FIRST
import Toast from 'vue-toastification'; // Import vue-toastification
import ganttastic from '@infectoone/vue-ganttastic'; // Import vue-ganttastic

import { initializeCacheManagement } from './utils/cacheManager.js'; // Import cache manager

// Filter out browser extension errors from console
const originalError = console.error;
console.error = function(...args) {
  const message = args.join(' ');

  // Filter out browser extension related errors
  if (message.includes('web_accessible_resources') ||
      message.includes('chrome-extension://invalid') ||
      message.includes('Denying load of') ||
      (message.includes('Failed to load resource: net::ERR_FAILED') && message.includes('chrome-extension'))) {
    // Silently ignore browser extension errors
    return;
  }

  // Log all other errors normally
  originalError.apply(console, args);
};

// Test app.provide directly
try {
  if (typeof app.provide === 'function') {
    console.log('app.provide is a function on the app instance created by createApp.');
    app.provide('myCustomTestProvide', 'testValueFromMainJs');
    console.log('Successfully called app.provide directly in main.js.');
  } else {
    console.error('CRITICAL: app.provide is NOT a function on the app instance in main.js.', app);
  }
} catch (e) {
  console.error('Error encountered while testing app.provide directly in main.js:', e);
}


// Cache busting utility
function clearApplicationCache() {
  // Clear localStorage cache if needed
  const cacheKeys = Object.keys(localStorage).filter(key =>
    key.startsWith('vue-') || key.startsWith('app-cache-')
  );
  cacheKeys.forEach(key => localStorage.removeItem(key));

  // Log cache clearing
  if (cacheKeys.length > 0) {
    console.log('🧹 Cleared application cache keys:', cacheKeys);
  }
}

// Check for app version changes and clear cache if needed
function checkAppVersion() {
  const currentVersion = document.querySelector('meta[name="app-version"]')?.content || '1.0.0';
  const storedVersion = localStorage.getItem('app-version');

  if (storedVersion && storedVersion !== currentVersion) {
    console.log(`📦 App version changed from ${storedVersion} to ${currentVersion}`);
    clearApplicationCache();
  }

  localStorage.setItem('app-version', currentVersion);
}

console.log('🚀 Surgery Scheduler Frontend Starting...');
console.log('🔧 Browser extension error filtering enabled');

// Initialize cache management system
initializeCacheManagement();

// Check app version and clear cache if needed (legacy support)
checkAppVersion();

const app = createApp(App);
const pinia = createPinia(); // Create Pinia instance

app.use(pinia); // Install Pinia BEFORE mounting
app.use(router); // Use the router
app.use(Toast); // Use vue-toastification
app.use(ganttastic); // Use vue-ganttastic


app.mount('#app');