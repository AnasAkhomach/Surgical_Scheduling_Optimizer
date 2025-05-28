import { defineStore } from 'pinia';
import { operatingRoomAPI, surgeonAPI, staffAPI } from '../services/api.js';

export const useResourceStore = defineStore('resource', {
  state: () => ({
    isLoading: false,
    error: null,

    // Operating Rooms
    operatingRooms: [],

    // Staff
    staff: [
      { id: 'SG1', name: 'Dr. Jane Smith', role: 'Surgeon', specializations: ['Cardiac Surgery', 'Vascular Surgery'], status: 'Active' },
      { id: 'SG2', name: 'Dr. Bill Adams', role: 'Surgeon', specializations: ['Orthopedics', 'Sports Medicine'], status: 'Active' },
      { id: 'SG3', name: 'Dr. Sarah Chen', role: 'Surgeon', specializations: ['General Surgery'], status: 'Active' },
      { id: 'SG4', name: 'Dr. Michael Wong', role: 'Surgeon', specializations: ['Ophthalmology'], status: 'Active' },
      { id: 'AN1', name: 'Dr. Emily Carter', role: 'Anesthetist', specializations: [], status: 'Active' },
      { id: 'AN2', name: 'Dr. Robert Johnson', role: 'Anesthetist', specializations: [], status: 'On Leave' },
      { id: 'NR1', name: 'Nurse John Doe', role: 'Scrub Nurse', specializations: ['General Surgery'], status: 'Active' },
      { id: 'NR2', name: 'Nurse Maria Garcia', role: 'Circulating Nurse', specializations: ['Cardiac Surgery'], status: 'Active' },
    ],

    // Equipment
    equipment: [
      { id: 'EQ1', name: 'Heart-Lung Machine 1', type: 'Heart-Lung Machine', status: 'Available', location: 'Storage Room A' },
      { id: 'EQ2', name: 'Arthroscope Unit 2', type: 'Arthroscope', status: 'In Use', location: 'OR 2' },
      { id: 'EQ3', name: 'C-Arm Unit 1', type: 'C-Arm', status: 'Available', location: 'Storage Room A' },
      { id: 'EQ4', name: 'Anesthesia Machine B', type: 'Anesthesia Machine', status: 'In Use', location: 'OR 2' },
      { id: 'EQ5', name: 'Microscope Model X', type: 'Surgical Microscope', status: 'Available', location: 'Storage Room B' },
      { id: 'EQ6', name: 'Phacoemulsification Machine', type: 'Phacoemulsification Machine', status: 'Available', location: 'Storage Room C' },
      { id: 'EQ7', name: 'Orthopedic Power Tools Set', type: 'Orthopedic Power Tools', status: 'Available', location: 'Storage Room B' },
    ],

    // Resource availability (for scheduling)
    resourceAvailability: {
      // Key is date in ISO format, value is object with resource IDs and their availability
      '2023-10-27': {
        'OR1': { available: true, unavailablePeriods: [] },
        'OR2': { available: true, unavailablePeriods: [] },
        'OR3': { available: false, unavailablePeriods: [{ start: '00:00', end: '23:59', reason: 'Maintenance' }] },
        'SG1': { available: true, unavailablePeriods: [{ start: '12:00', end: '13:00', reason: 'Lunch' }] },
        'SG2': { available: true, unavailablePeriods: [{ start: '12:30', end: '13:30', reason: 'Lunch' }] },
      }
    }
  }),

  getters: {
    // Get all active operating rooms
    activeOperatingRooms: (state) => {
      return state.operatingRooms.filter(or => or.status === 'Active');
    },

    // Get all active staff
    activeStaff: (state) => {
      return state.staff.filter(s => s.status === 'Active');
    },

    // Get all available equipment
    availableEquipment: (state) => {
      return state.equipment.filter(eq => eq.status === 'Available');
    },

    // Get staff by role
    getStaffByRole: (state) => (role) => {
      return state.staff.filter(s => s.role === role && s.status === 'Active');
    },

    // Get surgeons by specialization
    getSurgeonsBySpecialization: (state) => (specialization) => {
      return state.staff.filter(s =>
        s.role === 'Surgeon' &&
        s.status === 'Active' &&
        s.specializations.includes(specialization)
      );
    },

    // Check if a resource is available at a specific time
    isResourceAvailable: (state) => (resourceId, date, startTime, endTime) => {
      const dateKey = new Date(date).toISOString().split('T')[0];
      const resourceAvailability = state.resourceAvailability[dateKey]?.[resourceId];

      if (!resourceAvailability || !resourceAvailability.available) {
        return false;
      }

      // Check if the resource is unavailable during any part of the requested time
      for (const period of resourceAvailability.unavailablePeriods) {
        if (
          (startTime >= period.start && startTime < period.end) || // Start time is within unavailable period
          (endTime > period.start && endTime <= period.end) || // End time is within unavailable period
          (startTime <= period.start && endTime >= period.end) // Requested time spans the unavailable period
        ) {
          return false;
        }
      }

      return true;
    }
  },

  actions: {
    // Load resources from API (simulated)
    async loadResources() {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        // In a real app, we would fetch data from the API here
        console.log('Resources loaded successfully');
      } catch (error) {
        this.error = 'Failed to load resources';
        console.error('Failed to load resources:', error);
      } finally {
        this.isLoading = false;
      }
    },

    // Load operating rooms from API
    async loadOperatingRooms() {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await operatingRoomAPI.getOperatingRooms();

        // Transform backend data to frontend format
        this.operatingRooms = response.map(room => ({
          id: room.room_id,
          name: `OR-${room.room_id}`,
          location: room.location,
          status: 'Available', // Default status
          primaryService: 'General' // Default service
        }));

        console.log('Operating rooms loaded successfully:', this.operatingRooms.length);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to load operating rooms';
        console.error('Failed to load operating rooms:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    // Operating Room actions
    async addOperatingRoom(orData) {
      this.isLoading = true;
      this.error = null;

      try {
        const payload = {
          location: orData.location
        };

        const response = await operatingRoomAPI.createOperatingRoom(payload);

        const newRoom = {
          id: response.room_id,
          name: `OR-${response.room_id}`,
          location: response.location,
          status: 'Available',
          primaryService: orData.primaryService || 'General'
        };

        this.operatingRooms.push(newRoom);

        console.log('Operating room added successfully:', response.room_id);
        return { success: true, data: newRoom };
      } catch (error) {
        this.error = 'Failed to add operating room';
        console.error('Failed to add operating room:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    async updateOperatingRoom(orId, orData) {
      this.isLoading = true;
      this.error = null;

      try {
        const payload = {
          location: orData.location
        };

        const response = await operatingRoomAPI.updateOperatingRoom(orId, payload);

        // Find and update the OR in state
        const index = this.operatingRooms.findIndex(or => or.id === orId);
        if (index !== -1) {
          this.operatingRooms[index] = {
            ...this.operatingRooms[index],
            location: response.location,
            name: `OR-${response.room_id}`,
            // Keep other frontend-specific fields
            primaryService: orData.primaryService || this.operatingRooms[index].primaryService
          };
        }

        console.log('Operating room updated successfully:', orId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to update operating room';
        console.error('Failed to update operating room:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteOperatingRoom(orId) {
      this.isLoading = true;
      this.error = null;

      try {
        await operatingRoomAPI.deleteOperatingRoom(orId);

        // Remove the OR from the state
        this.operatingRooms = this.operatingRooms.filter(or => or.id !== orId);

        console.log('Operating room deleted successfully:', orId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete operating room';
        console.error('Failed to delete operating room:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    // Surgeon actions (as part of Staff Management)
    async loadSurgeons() {
      this.isLoading = true;
      this.error = null;
      try {
        const backendSurgeons = await surgeonAPI.getSurgeons();
        const transformedSurgeons = backendSurgeons.map(surgeon => ({
          id: surgeon.surgeon_id.toString(), // Ensure ID is a string if components expect it
          name: surgeon.name,
          role: 'Surgeon',
          // Backend specialization is a string, frontend expects an array.
          // Split by comma if multiple, otherwise single item array.
          specializations: surgeon.specialization ? surgeon.specialization.split(',').map(s => s.trim()) : [],
          status: 'Active', // Default status, backend model might have 'availability'
          contact_info: surgeon.contact_info, // Keep original backend data if useful
          credentials: surgeon.credentials, // Keep original backend data if useful
          // availability: surgeon.availability // Consider how to map this to frontend 'status' or use directly
        }));

        // Filter out existing mock surgeons, keep other staff types
        const otherStaff = this.staff.filter(s => s.role !== 'Surgeon');
        this.staff = [...otherStaff, ...transformedSurgeons];

        console.log('Surgeons loaded and merged successfully:', transformedSurgeons.length);
        return { success: true, data: transformedSurgeons };
      } catch (error) {
        this.error = 'Failed to load surgeons';
        console.error('Failed to load surgeons:', error);
        // Potentially revert to mock data or clear surgeons if preferred
        // For now, just log error and keep existing state or partially loaded state.
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    // Staff actions
    async addStaff(staffMember) {
      // Simulate API call for non-surgeon roles or if API is not ready
      if (staffMember.role !== 'Surgeon') {
        console.warn('addStaff: Non-surgeon role, using mock data logic.');
        return new Promise((resolve) => {
          setTimeout(() => {
            const newStaff = { ...staffMember, id: Date.now().toString() }; // Ensure unique ID for mock
            this.staffList.push(newStaff);
            resolve(newStaff);
          }, 500);
        });
      }

      // Actual API call for Surgeons
      try {
        // Transform frontend staffMember to backend surgeon schema
        const surgeonPayload = {
          name: staffMember.name,
          specialty: staffMember.specialty || 'General Surgery', // Assuming specialty is a field
          phone_number: staffMember.contact,
          email: staffMember.email || `surgeon${Date.now()}@example.com`, // Ensure email if not provided
          // map other necessary fields from staffMember to surgeonPayload
          // availability: staffMember.availability, // This needs to be handled based on backend model
        };

        const response = await surgeonAPI.createSurgeon(surgeonPayload);
        // Transform backend response to frontend staffList format
        const newSurgeon = {
          id: response.id.toString(), // Ensure ID is a string
          name: response.name,
          role: 'Surgeon', // Explicitly set role
          specialty: response.specialty,
          contact: response.phone_number,
          email: response.email,
          availability: response.availability_schedule || [], // Adjust based on actual backend response
          // map other necessary fields from response to newSurgeon
        };
        this.staffList.push(newSurgeon);
        return newSurgeon;
      } catch (error) {
        console.error('Error adding surgeon:', error);
        // Optionally, re-throw the error or handle it by returning a specific error object
        // For now, let's fall back to mock behavior or throw to indicate failure
        // throw error; // Or handle as per application's error handling strategy
        // Fallback to mock for demo purposes if API fails, or remove this for production
        console.warn('addStaff: API call failed for surgeon, falling back to mock data logic (or throw error).');
        const mockNewStaff = { ...staffMember, id: `mock-${Date.now().toString()}` };
        this.staffList.push(mockNewStaff);
        return mockNewStaff;
      }
    },

    async updateStaff(staffId, staffData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Find the staff to update
        const index = this.staff.findIndex(s => s.id === staffId);

        if (index !== -1) {
          // Update the staff
          this.staff[index] = {
            ...this.staff[index],
            ...staffData
          };

          console.log('Staff updated successfully:', staffId);
          return { success: true };
        } else {
          throw new Error('Staff not found');
        }
      } catch (error) {
        this.error = 'Failed to update staff';
        console.error('Failed to update staff:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteStaff(staffId) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Remove the staff from the state
        this.staff = this.staff.filter(s => s.id !== staffId);

        console.log('Staff deleted successfully:', staffId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete staff';
        console.error('Failed to delete staff:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    // Equipment actions
    async addEquipment(equipmentData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Generate a unique ID
        const newId = `EQ${this.equipment.length + 1}`;

        // Add the new equipment to the state
        this.equipment.push({
          id: newId,
          ...equipmentData
        });

        console.log('Equipment added successfully:', newId);
        return { success: true, id: newId };
      } catch (error) {
        this.error = 'Failed to add equipment';
        console.error('Failed to add equipment:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async updateEquipment(equipmentId, equipmentData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Find the equipment to update
        const index = this.equipment.findIndex(eq => eq.id === equipmentId);

        if (index !== -1) {
          // Update the equipment
          this.equipment[index] = {
            ...this.equipment[index],
            ...equipmentData
          };

          console.log('Equipment updated successfully:', equipmentId);
          return { success: true };
        } else {
          throw new Error('Equipment not found');
        }
      } catch (error) {
        this.error = 'Failed to update equipment';
        console.error('Failed to update equipment:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteEquipment(equipmentId) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Remove the equipment from the state
        this.equipment = this.equipment.filter(eq => eq.id !== equipmentId);

        console.log('Equipment deleted successfully:', equipmentId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete equipment';
        console.error('Failed to delete equipment:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    // Resource availability actions
    async updateResourceAvailability(resourceId, date, availability) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Format date as ISO string (YYYY-MM-DD)
        const dateKey = new Date(date).toISOString().split('T')[0];

        // Ensure the date exists in the availability object
        if (!this.resourceAvailability[dateKey]) {
          this.resourceAvailability[dateKey] = {};
        }

        // Update the resource availability
        this.resourceAvailability[dateKey][resourceId] = availability;

        console.log('Resource availability updated successfully:', resourceId, dateKey);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to update resource availability';
        console.error('Failed to update resource availability:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async updateSurgeon(surgeonData) {
      if (!surgeonData || !surgeonData.id) {
        console.error('updateSurgeon: surgeonData with id is required.');
        return Promise.reject(new Error('Surgeon ID is missing.'));
      }
      try {
        // Transform frontend surgeonData to backend surgeon schema for update
        const surgeonPayload = {
          name: surgeonData.name,
          specialty: surgeonData.specialty,
          phone_number: surgeonData.contact,
          email: surgeonData.email,
          // availability_schedule: surgeonData.availability, // Ensure this matches backend expectations
        };

        const response = await surgeonAPI.updateSurgeon(surgeonData.id, surgeonPayload);
        // Transform backend response to frontend staffList format
        const updatedSurgeonFromAPI = {
          id: response.id.toString(),
          name: response.name,
          role: 'Surgeon',
          specialty: response.specialty,
          contact: response.phone_number,
          email: response.email,
          availability: response.availability_schedule || [],
        };

        const index = this.staffList.findIndex(s => s.id === updatedSurgeonFromAPI.id && s.role === 'Surgeon');
        if (index !== -1) {
          this.staffList.splice(index, 1, updatedSurgeonFromAPI);
        }
        return updatedSurgeonFromAPI;
      } catch (error) {
        console.error(`Error updating surgeon ${surgeonData.id}:`, error);
        throw error; // Re-throw to allow calling component to handle
      }
    },

    async deleteSurgeon(surgeonId) {
      if (!surgeonId) {
        console.error('deleteSurgeon: surgeonId is required.');
        return Promise.reject(new Error('Surgeon ID is missing.'));
      }
      try {
        await surgeonAPI.deleteSurgeon(surgeonId);
        this.staffList = this.staffList.filter(s => !(s.id === surgeonId && s.role === 'Surgeon'));
        return surgeonId; // Return the ID of the deleted surgeon
      } catch (error) {
        console.error(`Error deleting surgeon ${surgeonId}:`, error);
        throw error; // Re-throw to allow calling component to handle
      }
    },

    // Mock deleteStaff - can be removed or refactored if all staff types get API integration
    async deleteStaff(staffId) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Remove the staff from the state
        this.staff = this.staff.filter(s => s.id !== staffId);

        console.log('Staff deleted successfully:', staffId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete staff';
        console.error('Failed to delete staff:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    // Equipment actions
    async addEquipment(equipmentData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Generate a unique ID
        const newId = `EQ${this.equipment.length + 1}`;

        // Add the new equipment to the state
        this.equipment.push({
          id: newId,
          ...equipmentData
        });

        console.log('Equipment added successfully:', newId);
        return { success: true, id: newId };
      } catch (error) {
        this.error = 'Failed to add equipment';
        console.error('Failed to add equipment:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async updateEquipment(equipmentId, equipmentData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Find the equipment to update
        const index = this.equipment.findIndex(eq => eq.id === equipmentId);

        if (index !== -1) {
          // Update the equipment
          this.equipment[index] = {
            ...this.equipment[index],
            ...equipmentData
          };

          console.log('Equipment updated successfully:', equipmentId);
          return { success: true };
        } else {
          throw new Error('Equipment not found');
        }
      } catch (error) {
        this.error = 'Failed to update equipment';
        console.error('Failed to update equipment:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteEquipment(equipmentId) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Remove the equipment from the state
        this.equipment = this.equipment.filter(eq => eq.id !== equipmentId);

        console.log('Equipment deleted successfully:', equipmentId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete equipment';
        console.error('Failed to delete equipment:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    // Resource availability actions
    async updateResourceAvailability(resourceId, date, availability) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Format date as ISO string (YYYY-MM-DD)
        const dateKey = new Date(date).toISOString().split('T')[0];

        // Ensure the date exists in the availability object
        if (!this.resourceAvailability[dateKey]) {
          this.resourceAvailability[dateKey] = {};
        }

        // Update the resource availability
        this.resourceAvailability[dateKey][resourceId] = availability;

        console.log('Resource availability updated successfully:', resourceId, dateKey);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to update resource availability';
        console.error('Failed to update resource availability:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    }
  }
});
