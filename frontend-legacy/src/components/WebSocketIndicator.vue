<template>
  <div class="websocket-indicator">
    <i 
      class="pi" 
      :class="isConnected ? 'pi-wifi text-green-500' : 'pi-wifi-off text-red-500'"
      :title="isConnected ? 'Connected to real-time updates' : 'Disconnected from real-time updates'"
    ></i>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'WebSocketIndicator',
  setup() {
    const store = useStore();
    
    const isConnected = computed(() => store.getters.isWebSocketConnected);
    
    return {
      isConnected
    };
  }
}
</script>

<style scoped>
.websocket-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.5rem;
}

.websocket-indicator i {
  font-size: 1.2rem;
}
</style>
