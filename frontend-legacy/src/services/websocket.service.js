// Mock WebSocket service for demonstration
import store from '@/store';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3 seconds
    this.mockEventListeners = {};
  }

  /**
   * Initialize the WebSocket connection
   * @param {string} url - The WebSocket server URL
   * @param {string} token - The authentication token
   */
  init(url, token) {
    console.log(`Initializing WebSocket connection to ${url} with token ${token}`);

    if (this.socket) {
      this.disconnect();
    }

    // Simulate connection
    setTimeout(() => {
      this.connected = true;
      store.dispatch('setWebSocketConnected', true);
      console.log('WebSocket connected');

      // Simulate receiving notifications periodically
      this.simulateNotifications();
    }, 1000);
  }

  /**
   * Simulate receiving notifications periodically
   */
  simulateNotifications() {
    // Simulate a schedule update after 10 seconds
    setTimeout(() => {
      if (this.connected) {
        console.log('Simulating schedule update notification');
        store.dispatch('notifications/addNotification', {
          type: 'info',
          title: 'Schedule Updated',
          message: 'The schedule has been updated',
          timestamp: new Date()
        });
      }
    }, 10000);

    // Simulate a surgery creation after 20 seconds
    setTimeout(() => {
      if (this.connected) {
        console.log('Simulating surgery creation notification');
        store.dispatch('notifications/addNotification', {
          type: 'success',
          title: 'Surgery Created',
          message: 'Surgery #123 has been created',
          timestamp: new Date()
        });
      }
    }, 20000);

    // Simulate a random notification every 30 seconds
    setInterval(() => {
      if (this.connected) {
        const types = ['info', 'success', 'warning'];
        const titles = ['System Update', 'Reminder', 'Alert'];
        const messages = [
          'System maintenance scheduled for tonight',
          'Don\'t forget to complete your reports',
          'New surgeon availability has been added',
          'Operating room OR-3 will be unavailable tomorrow'
        ];

        const type = types[Math.floor(Math.random() * types.length)];
        const title = titles[Math.floor(Math.random() * titles.length)];
        const message = messages[Math.floor(Math.random() * messages.length)];

        console.log(`Simulating random notification: ${title} - ${message}`);
        store.dispatch('notifications/addNotification', {
          type,
          title,
          message,
          timestamp: new Date()
        });
      }
    }, 30000);
  }

  /**
   * Disconnect the WebSocket
   */
  disconnect() {
    console.log('Disconnecting WebSocket');
    this.connected = false;
    store.dispatch('setWebSocketConnected', false);
  }

  /**
   * Check if the WebSocket is connected
   * @returns {boolean} True if connected, false otherwise
   */
  isConnected() {
    return this.connected;
  }

  /**
   * Send a message to the server (mock implementation)
   * @param {string} event - The event name
   * @param {any} data - The data to send
   */
  emit(event, data) {
    if (this.connected) {
      console.log(`Emitting event: ${event}`, data);
    } else {
      console.warn('Cannot emit event, WebSocket not connected');
    }
  }
}

export default new WebSocketService();
