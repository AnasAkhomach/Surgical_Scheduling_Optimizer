// src/stores/authStore.js
import { defineStore } from 'pinia';
import router from '@/router'; // Import the router instance

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: localStorage.getItem('isAuthenticated') === 'true', // Load initial state from local storage
    user: JSON.parse(localStorage.getItem('user') || 'null'), // Load user info from local storage
    isLoading: false,
    error: null,
  }),
  getters: {
    // isAuthenticated: (state) => state.isAuthenticated, // Can be a simple state property
    // user: (state) => state.user,
  },
  actions: {
    async login(username, password) {
      this.isLoading = true;
      this.error = null;

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      try {
        // Mocked login logic
        if (username === 'test@example.com' && password === 'password') {
          const mockUser = { id: 1, username: 'test@example.com', name: 'Test User' };
          this.isAuthenticated = true;
          this.user = mockUser;
          localStorage.setItem('isAuthenticated', 'true');
          localStorage.setItem('user', JSON.stringify(mockUser));
          router.push({ name: 'Dashboard' });
        } else {
          throw new Error('Invalid mock credentials');
        }
      } catch (error) {
        console.error('Mock Login error:', error);
        this.error = error.message;
        this.isAuthenticated = false;
        this.user = null;
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('user');
      } finally {
        this.isLoading = false;
      }
    },

    async register(username, password) {
      this.isLoading = true;
      this.error = null;
      let success = false;

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      try {
        // Mocked registration logic
        // For simplicity, let's assume registration is always successful for a new user
        // or fails if username is already 'test@example.com'
        if (username === 'test@example.com') {
          throw new Error('Mock: Username already exists.');
        }

        // You could add to a mock user list in localStorage if needed for more complex simulation
        // For now, just simulate success
        console.log('Mock Registration successful for:', username, '. Please log in.');
        success = true;
      } catch (error) {
        console.error('Mock Registration error:', error);
        this.error = error.message;
        success = false;
      } finally {
        this.isLoading = false;
      }
      return success;
    },

    logout() {
       console.log('Auth Store: Logging out.');
      // Clear auth state
      this.isAuthenticated = false;
      this.user = null;
      this.error = null; // Clear any lingering errors
      // Remove auth data from local storage
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('user');
      // localStorage.removeItem('authToken'); // Clear token if used

      // Redirect to login page
      router.push({ name: 'Login' }); // Use router instance
    }
  }
});
