/**
 * Cache Management Utility
 * 
 * This utility provides functions to manage browser caching and ensure
 * users always see the latest version of the application.
 */

/**
 * Clear all browser caches
 */
export function clearAllCaches() {
  console.log('🧹 Starting cache clearing process...');
  
  // Clear localStorage
  const localStorageKeys = Object.keys(localStorage);
  localStorageKeys.forEach(key => {
    if (key.startsWith('vue-') || key.startsWith('app-cache-') || key.startsWith('pinia-')) {
      localStorage.removeItem(key);
    }
  });
  
  // Clear sessionStorage
  const sessionStorageKeys = Object.keys(sessionStorage);
  sessionStorageKeys.forEach(key => {
    if (key.startsWith('vue-') || key.startsWith('app-cache-') || key.startsWith('pinia-')) {
      sessionStorage.removeItem(key);
    }
  });
  
  console.log('✅ Application caches cleared');
}

/**
 * Force reload the page bypassing cache
 */
export function hardReload() {
  console.log('🔄 Performing hard reload...');
  
  // Clear caches first
  clearAllCaches();
  
  // Force reload bypassing cache
  if (window.location.reload) {
    window.location.reload(true); // Force reload from server
  } else {
    // Fallback for browsers that don't support the parameter
    window.location.href = window.location.href;
  }
}

/**
 * Check if the application version has changed
 */
export function checkVersionChange() {
  const currentVersion = document.querySelector('meta[name="app-version"]')?.content || '1.0.0';
  const storedVersion = localStorage.getItem('app-version');
  
  if (storedVersion && storedVersion !== currentVersion) {
    console.log(`📦 Version change detected: ${storedVersion} → ${currentVersion}`);
    return true;
  }
  
  return false;
}

/**
 * Update the stored application version
 */
export function updateStoredVersion() {
  const currentVersion = document.querySelector('meta[name="app-version"]')?.content || '1.0.0';
  localStorage.setItem('app-version', currentVersion);
  console.log(`📝 Updated stored version to: ${currentVersion}`);
}

/**
 * Add cache-busting query parameter to URLs
 */
export function addCacheBuster(url) {
  const separator = url.includes('?') ? '&' : '?';
  const timestamp = Date.now();
  return `${url}${separator}_cb=${timestamp}`;
}

/**
 * Create cache-busting headers for fetch requests
 */
export function getCacheBustingHeaders() {
  return {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    'X-Requested-With': 'XMLHttpRequest'
  };
}

/**
 * Initialize cache management
 */
export function initializeCacheManagement() {
  console.log('🚀 Initializing cache management...');
  
  // Check for version changes
  if (checkVersionChange()) {
    clearAllCaches();
    updateStoredVersion();
  } else {
    updateStoredVersion();
  }
  
  // Add global cache-busting for dynamic imports
  if (window.performance && window.performance.mark) {
    window.performance.mark('cache-management-initialized');
  }
  
  console.log('✅ Cache management initialized');
}

/**
 * Debug function to show current cache status
 */
export function debugCacheStatus() {
  console.group('🔍 Cache Status Debug');
  
  const currentVersion = document.querySelector('meta[name="app-version"]')?.content || '1.0.0';
  const storedVersion = localStorage.getItem('app-version');
  
  console.log('Current Version:', currentVersion);
  console.log('Stored Version:', storedVersion);
  console.log('Version Match:', currentVersion === storedVersion);
  
  console.log('LocalStorage Keys:', Object.keys(localStorage));
  console.log('SessionStorage Keys:', Object.keys(sessionStorage));
  
  console.groupEnd();
}

// Export default object with all functions
export default {
  clearAllCaches,
  hardReload,
  checkVersionChange,
  updateStoredVersion,
  addCacheBuster,
  getCacheBustingHeaders,
  initializeCacheManagement,
  debugCacheStatus
};
