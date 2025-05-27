import { defineStore } from 'pinia';

export const useResourceStore = defineStore('resource', {
  state: () => ({
    isLoading: false,
    error: null,

    // Operating Rooms
    operatingRooms: [
      { id: 'OR1', name: 'OR 1', location: 'Main Building, 2nd Floor', status: 'Active', primaryService: 'General Surgery' },
      { id: 'OR2', name: 'OR 2', location: 'Main Building, 2nd Floor', status: 'Active', primaryService: 'Orthopedics' },
      { id: 'OR3', name: 'OR 3', location: 'Main Building, 3rd Floor', status: 'Under Maintenance', primaryService: 'Cardiac Surgery' },
      { id: 'OR4', name: 'OR 4', location: 'East Wing, 1st Floor', status: 'Active', primaryService: 'Neurosurgery' },
      { id: 'OR5', name: 'OR 5', location: 'East Wing, 1st Floor', status: 'Active', primaryService: 'Ophthalmology' },
    ],

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

    // Operating Room actions
    async addOperatingRoom(orData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Generate a unique ID
        const newId = `OR${this.operatingRooms.length + 1}`;

        // Add the new OR to the state
        this.operatingRooms.push({
          id: newId,
          ...orData
        });

        console.log('Operating room added successfully:', newId);
        return { success: true, id: newId };
      } catch (error) {
        this.error = 'Failed to add operating room';
        console.error('Failed to add operating room:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async updateOperatingRoom(orId, orData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Find the OR to update
        const index = this.operatingRooms.findIndex(or => or.id === orId);

        if (index !== -1) {
          // Update the OR
          this.operatingRooms[index] = {
            ...this.operatingRooms[index],
            ...orData
          };

          console.log('Operating room updated successfully:', orId);
          return { success: true };
        } else {
          throw new Error('Operating room not found');
        }
      } catch (error) {
        this.error = 'Failed to update operating room';
        console.error('Failed to update operating room:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteOperatingRoom(orId) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Remove the OR from the state
        this.operatingRooms = this.operatingRooms.filter(or => or.id !== orId);

        console.log('Operating room deleted successfully:', orId);
        return { success: true };
      } catch (error) {
        this.error = 'Failed to delete operating room';
        console.error('Failed to delete operating room:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    // Staff actions
    async addStaff(staffData) {
      this.isLoading = true;
      this.error = null;

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Generate a unique ID based on role
        let prefix = 'ST'; // Default prefix
        if (staffData.role === 'Surgeon') prefix = 'SG';
        else if (staffData.role === 'Anesthetist') prefix = 'AN';
        else if (staffData.role === 'Nurse') prefix = 'NR';

        const newId = `${prefix}${this.staff.length + 1}`;

        // Add the new staff to the state
        this.staff.push({
          id: newId,
          ...staffData
        });

        console.log('Staff added successfully:', newId);
        return { success: true, id: newId };
      } catch (error) {
        this.error = 'Failed to add staff';
        console.error('Failed to add staff:', error);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
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
    }
  }
});
