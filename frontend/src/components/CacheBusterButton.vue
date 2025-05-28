<template>
  <div class="cache-buster">
    <button 
      @click="clearCache" 
      :disabled="isClearing"
      class="cache-clear-btn"
      title="Clear application cache and reload"
    >
      <span v-if="!isClearing">🧹 Clear Cache</span>
      <span v-else>🔄 Clearing...</span>
    </button>
    
    <button 
      @click="hardReload" 
      :disabled="isClearing"
      class="hard-reload-btn"
      title="Force reload bypassing all caches"
    >
      <span v-if="!isClearing">🔄 Hard Reload</span>
      <span v-else>🔄 Reloading...</span>
    </button>
    
    <button 
      @click="showDebugInfo" 
      class="debug-btn"
      title="Show cache debug information"
    >
      🔍 Debug Cache
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { 
  clearAllCaches, 
  hardReload, 
  debugCacheStatus,
  updateStoredVersion 
} from '../utils/cacheManager.js';

const isClearing = ref(false);

const clearCache = async () => {
  isClearing.value = true;
  
  try {
    console.log('🧹 Manual cache clearing initiated...');
    clearAllCaches();
    updateStoredVersion();
    
    // Show success message
    console.log('✅ Cache cleared successfully');
    
    // Reload the page after a short delay
    setTimeout(() => {
      window.location.reload();
    }, 500);
    
  } catch (error) {
    console.error('❌ Error clearing cache:', error);
    isClearing.value = false;
  }
};

const performHardReload = async () => {
  isClearing.value = true;
  
  try {
    console.log('🔄 Manual hard reload initiated...');
    hardReload();
  } catch (error) {
    console.error('❌ Error performing hard reload:', error);
    isClearing.value = false;
  }
};

const showDebugInfo = () => {
  debugCacheStatus();
  
  // Also show in a more user-friendly way
  const currentVersion = document.querySelector('meta[name="app-version"]')?.content || '1.0.0';
  const storedVersion = localStorage.getItem('app-version');
  
  alert(`Cache Debug Info:
Current Version: ${currentVersion}
Stored Version: ${storedVersion}
Version Match: ${currentVersion === storedVersion}
LocalStorage Keys: ${Object.keys(localStorage).length}
SessionStorage Keys: ${Object.keys(sessionStorage).length}

Check console for detailed information.`);
};
</script>

<style scoped>
.cache-buster {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.cache-clear-btn,
.hard-reload-btn,
.debug-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f8f9fa;
  color: #333;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.cache-clear-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.hard-reload-btn:hover {
  background: #fff3cd;
  border-color: #ffeaa7;
}

.debug-btn:hover {
  background: #d1ecf1;
  border-color: #bee5eb;
}

.cache-clear-btn:disabled,
.hard-reload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .cache-buster {
    flex-direction: column;
    align-items: stretch;
  }
  
  .cache-clear-btn,
  .hard-reload-btn,
  .debug-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
