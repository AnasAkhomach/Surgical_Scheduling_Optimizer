// src/services/api.js
// API service for communicating with FastAPI backend
import { getCacheBustingHeaders, addCacheBuster } from '../utils/cacheManager.js';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Generic API request function
 * @param {string} endpoint - API endpoint (without /api prefix)
 * @param {object} options - Fetch options
 * @returns {Promise} - Response data
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  // Check if we're sending FormData (for file uploads or OAuth2 form data)
  const isFormData = options.body instanceof FormData;

  const defaultOptions = {
    headers: {},
  };

  // Only set Content-Type for JSON requests, let browser handle FormData
  if (!isFormData) {
    defaultOptions.headers['Content-Type'] = 'application/json';
  }

  // Add cache-busting headers for API requests
  const cacheBustingHeaders = getCacheBustingHeaders();
  Object.assign(defaultOptions.headers, cacheBustingHeaders);

  // Add authentication token if available
  const token = localStorage.getItem('authToken');
  console.log('🔑 Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'null');
  if (token) {
    defaultOptions.headers.Authorization = `Bearer ${token}`;
    console.log('✅ Authorization header added');
  } else {
    console.log('❌ No token found in localStorage');
  }

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    console.log(`🔍 API Request: ${config.method || 'GET'} ${url}`);
    console.log('📤 Request config:', {
      headers: config.headers,
      body: config.body instanceof FormData ? 'FormData' : config.body
    });

    const response = await fetch(url, config);

    console.log(`📥 Response: ${response.status} ${response.statusText}`);

    // Handle non-JSON responses (like 204 No Content)
    if (response.status === 204) {
      console.log('✅ 204 No Content response');
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      console.error('❌ API Error Response:', data);

      // Log detailed field errors for debugging
      if (data.field_errors) {
        console.error('🔍 Field Validation Errors:', data.field_errors);
      }

      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }

    console.log('✅ API Success:', data);
    return data;
  } catch (error) {
    console.error(`💥 API request failed: ${endpoint}`, error);
    throw error;
  }
}

// Authentication API
export const authAPI = {
  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', 'password'); // Required by OAuth2PasswordRequestForm

    return apiRequest('/auth/token', {
      method: 'POST',
      // Don't set headers - let apiRequest detect FormData and handle Content-Type automatically
      body: formData,
    });
  },

  async register(userData) {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  async getCurrentUser() {
    return apiRequest('/auth/me');
  },

  async refreshToken() {
    return apiRequest('/auth/refresh', {
      method: 'POST',
    });
  },
};

// Surgery API
export const surgeryAPI = {
  async getSurgeries() {
    return apiRequest('/surgeries');
  },

  async getSurgery(id) {
    return apiRequest(`/surgeries/${id}`);
  },

  async createSurgery(surgeryData) {
    return apiRequest('/surgeries', {
      method: 'POST',
      body: JSON.stringify(surgeryData),
    });
  },

  async updateSurgery(id, surgeryData) {
    return apiRequest(`/surgeries/${id}`, {
      method: 'PUT',
      body: JSON.stringify(surgeryData),
    });
  },

  async deleteSurgery(id) {
    return apiRequest(`/surgeries/${id}`, {
      method: 'DELETE',
    });
  },
};

// Schedule API
export const scheduleAPI = {
  async getSchedules(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/schedules?${queryString}` : '/schedules';
    return apiRequest(endpoint);
  },

  async optimizeSchedule(optimizationData) {
    return apiRequest('/schedules/optimize', {
      method: 'POST',
      body: JSON.stringify(optimizationData),
    });
  },

  async getOptimizationStatus(taskId) {
    return apiRequest(`/schedules/optimization-status/${taskId}`);
  },
};

// Operating Rooms API
export const operatingRoomAPI = {
  async getOperatingRooms() {
    return apiRequest('/operating-rooms');
  },

  async getOperatingRoom(id) {
    return apiRequest(`/operating-rooms/${id}`);
  },

  async createOperatingRoom(roomData) {
    return apiRequest('/operating-rooms', {
      method: 'POST',
      body: JSON.stringify(roomData),
    });
  },

  async updateOperatingRoom(id, roomData) {
    return apiRequest(`/operating-rooms/${id}`, {
      method: 'PUT',
      body: JSON.stringify(roomData),
    });
  },

  async deleteOperatingRoom(id) {
    return apiRequest(`/operating-rooms/${id}`, {
      method: 'DELETE',
    });
  },
};

// Surgeons API
export const surgeonAPI = {
  async getSurgeons() {
    return apiRequest('/surgeons');
  },

  async getSurgeon(id) {
    return apiRequest(`/surgeons/${id}`);
  },

  async createSurgeon(surgeonData) {
    return apiRequest('/surgeons', {
      method: 'POST',
      body: JSON.stringify(surgeonData),
    });
  },

  async updateSurgeon(id, surgeonData) {
    return apiRequest(`/surgeons/${id}`, {
      method: 'PUT',
      body: JSON.stringify(surgeonData),
    });
  },

  async deleteSurgeon(id) {
    return apiRequest(`/surgeons/${id}`, {
      method: 'DELETE',
    });
  },
};

// Patients API
export const patientAPI = {
  async getPatients() {
    return apiRequest('/patients');
  },

  async getPatient(id) {
    return apiRequest(`/patients/${id}`);
  },

  async createPatient(patientData) {
    return apiRequest('/patients', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  },

  async updatePatient(id, patientData) {
    return apiRequest(`/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(patientData),
    });
  },

  async deletePatient(id) {
    return apiRequest(`/patients/${id}`, {
      method: 'DELETE',
    });
  },
};

// Staff API
export const staffAPI = {
  async getStaff() {
    return apiRequest('/staff');
  },

  async getStaffMember(id) {
    return apiRequest(`/staff/${id}`);
  },

  async createStaffMember(staffData) {
    return apiRequest('/staff', {
      method: 'POST',
      body: JSON.stringify(staffData),
    });
  },

  async updateStaffMember(id, staffData) {
    return apiRequest(`/staff/${id}`, {
      method: 'PUT',
      body: JSON.stringify(staffData),
    });
  },

  async deleteStaffMember(id) {
    return apiRequest(`/staff/${id}`, {
      method: 'DELETE',
    });
  },
};

// SDST API
export const sdstAPI = {
  async getSDSTData() {
    return apiRequest('/sdst');
  },

  async updateSDSTData(sdstData) {
    return apiRequest('/sdst', {
      method: 'PUT',
      body: JSON.stringify(sdstData),
    });
  },

  async getSurgeryTypes() {
    return apiRequest('/surgery-types');
  },
};

// Health check
export const healthAPI = {
  async checkHealth() {
    return apiRequest('/health');
  },
};

// Export default API object
export default {
  auth: authAPI,
  surgery: surgeryAPI,
  schedule: scheduleAPI,
  operatingRoom: operatingRoomAPI,
  surgeon: surgeonAPI,
  patient: patientAPI,
  staff: staffAPI,
  sdst: sdstAPI,
  health: healthAPI,
};
