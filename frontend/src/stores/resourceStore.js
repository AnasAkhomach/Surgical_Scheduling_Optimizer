import { defineStore } from 'pinia';
import { operatingRoomAPI, surgeonAPI, staffAPI } from '../services/api.js';

export const useResourceStore = defineStore('resource', {
  state: () => ({
    isLoading: false,
    error: null,

    // Operating Rooms
    operatingRooms: [],

    // Staff
    staff: [],

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
          id: room.room_id || room.id,
          name: room.name,
          location: room.location,
          status: room.status,
          primaryService: room.primary_service || room.primaryService
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
          name: orData.name,
          location: orData.location,
          status: orData.status || 'Active',
          primaryService: orData.primaryService
        };

        const response = await operatingRoomAPI.createOperatingRoom(payload);

        const newRoom = {
          id: response.room_id || response.id,
          name: response.name,
          location: response.location,
          status: response.status,
          primaryService: response.primary_service || response.primaryService
        };

        this.operatingRooms.push(newRoom);

        console.log('Operating room added successfully:', response.room_id || response.id);
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
          name: orData.name,
          location: orData.location,
          status: orData.status,
          primaryService: orData.primaryService
        };

        const response = await operatingRoomAPI.updateOperatingRoom(orId, payload);

        // Find and update the OR in state
        const index = this.operatingRooms.findIndex(or => or.id === orId);
        if (index !== -1) {
          this.operatingRooms[index] = {
            id: response.room_id || response.id,
            name: response.name,
            location: response.location,
            status: response.status,
            primaryService: response.primary_service || response.primaryService
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
          id: surgeon.surgeon_id || surgeon.id,
          name: surgeon.name,
          role: 'Surgeon',
          specializations: surgeon.specialization ? surgeon.specialization.split(',').map(s => s.trim()) : [],
          status: surgeon.availability ? 'Active' : 'Inactive',
          contact_info: surgeon.contact_info,
          credentials: surgeon.credentials,
          availability: surgeon.availability
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
    async addStaff(staffData) {
      this.isLoading = true;
      this.error = null;

      try {
        const payload = {
          name: staffData.name,
          role: staffData.role,
          specializations: staffData.specializations || [],
          status: staffData.status || 'Active'
        };

        const response = await staffAPI.createStaff(payload);

        const newStaff = {
          id: response.staff_id || response.id,
          name: response.name,
          role: response.role,
          specializations: response.specializations || [],
          status: response.status || 'Active'
        };

        this.staff.push(newStaff);

        console.log('Staff added successfully:', response.staff_id);
        return { success: true, data: newStaff };
      } catch (error) {
        this.error = 'Failed to add staff';
        console.error('Failed to add staff:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    async updateStaff(staffId, staffData) {
      this.isLoading = true;
      this.error = null;

      try {
        const payload = {
          name: staffData.name,
          role: staffData.role,
          specializations: staffData.specializations || [],
          status: staffData.status
        };

        const response = await staffAPI.updateStaff(staffId, payload);

        const index = this.staff.findIndex(s => s.id === staffId);
        if (index !== -1) {
          this.staff[index] = {
            id: response.staff_id || response.id,
            name: response.name,
            role: response.role,
            specializations: response.specializations || [],
            status: response.status
          };
        }

        console.log('Staff updated successfully:', response.staff_id || response.id);
        return { success: true, data: this.staff[index] };
      } catch (error) {
        this.error = 'Failed to update staff';
        console.error('Failed to update staff:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteStaff(staffId) {
      this.isLoading = true;
      this.error = null;

      try {
        await staffAPI.deleteStaff(staffId);

        this.staff = this.staff.filter(s => s.id !== staffId);

        console.log('Staff deleted successfully:', staffId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete staff';
        console.error('Failed to delete staff:', error);
        return { success: false, error: error.message };
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

    // Load staff (surgeons) from API
    async loadStaff() {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await staffAPI.getStaff();

        this.staff = response.map(s => ({
          id: s.staff_id || s.id,
          name: s.name,
          role: s.role,
          specializations: s.specializations || [],
          status: s.status || 'Active'
        }));

        console.log('Staff loaded successfully:', this.staff.length);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to load staff';
        console.error('Failed to load staff:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    }
  }
});
