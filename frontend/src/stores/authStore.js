// src/stores/authStore.js
import { defineStore } from 'pinia';
import router from '@/router'; // Import the router instance
import { authAPI } from '@/services/api'; // Import API service

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: localStorage.getItem('isAuthenticated') === 'true', // Load initial state from local storage
    user: JSON.parse(localStorage.getItem('user') || 'null'), // Load user info from local storage
    token: localStorage.getItem('authToken') || null, // Store auth token
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

      try {
        // Call real API
        const response = await authAPI.login(username, password);

        // Store authentication data
        this.token = response.access_token;
        this.isAuthenticated = true;

        // Get user info
        const userInfo = await authAPI.getCurrentUser();
        this.user = userInfo;

        // Store in localStorage
        localStorage.setItem('authToken', this.token);
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('user', JSON.stringify(this.user));

        // Navigate to dashboard
        router.push({ name: 'Dashboard' });
      } catch (error) {
        console.error('Login error:', error);
        this.error = error.message || 'Login failed';
        this.isAuthenticated = false;
        this.user = null;
        this.token = null;
        localStorage.removeItem('authToken');
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

      try {
        // Call real API
        await authAPI.register({
          username,
          password,
          email: username, // Assuming username is email
        });

        console.log('Registration successful for:', username, '. Please log in.');
        success = true;
      } catch (error) {
        console.error('Registration error:', error);
        this.error = error.message || 'Registration failed';
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
      this.token = null;
      this.error = null; // Clear any lingering errors
      // Remove auth data from local storage
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');

      // Redirect to login page
      router.push({ name: 'Login' }); // Use router instance
    }
  }
});
