import { defineStore } from 'pinia';
import { scheduleAPI, operatingRoomAPI, staffAPI } from '../services/api.js';

export const useScheduleStore = defineStore('schedule', {
  state: () => ({
    // --- Core Schedule Data ---
    scheduledSurgeries: [],
    pendingSurgeries: [],

    // --- Resource Data ---
    operatingRooms: [],
    staff: [],
    equipment: [],

    // --- SDST Data ---
    surgeryTypes: {},
    sdsRules: {},
    initialSetupTimes: {},

    // --- UI State ---
    selectedSurgeryId: null,
    currentDateRange: {
      start: new Date('2023-10-27T07:00:00Z'),
      end: new Date('2023-10-27T19:00:00Z'),
    },
    ganttViewMode: 'Day',
    isLoading: false,
    error: null,

    // --- Optimization State ---
    isOptimizing: false,
    optimizationResults: null,
    optimizationError: null,
  }),
  getters: {
    visibleScheduledSurgeries: (state) => {
      const startTime = state.currentDateRange.start.getTime();
      const endTime = state.currentDateRange.end.getTime();
      return state.scheduledSurgeries.filter(surgery => {
        const surgeryStart = new Date(surgery.startTime).getTime();
        const surgeryEnd = new Date(surgery.endTime).getTime();
        return (
          (surgeryStart >= startTime && surgeryStart <= endTime) ||
          (surgeryEnd >= startTime && surgeryEnd <= endTime) ||
          (surgeryStart <= startTime && surgeryEnd >= endTime)
        );
      });
    },
    getSurgeriesForOR: (state) => (orId) => {
      return state.visibleScheduledSurgeries
        .filter(s => s.orId === orId)
        .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
    },
    getSurgeriesForDate: (state) => (targetDate) => {
      if (!targetDate) return state.scheduledSurgeries;
      const dateStr = typeof targetDate === 'string' ? targetDate : targetDate.toISOString().split('T')[0];
      return state.scheduledSurgeries.filter(surgery => {
        const surgeryDate = new Date(surgery.startTime).toISOString().split('T')[0];
        return surgeryDate === dateStr;
      });
    },
    selectedSurgery: (state) => {
      if (!state.selectedSurgeryId) return null;
      return (
        state.scheduledSurgeries.find((s) => s.id === state.selectedSurgeryId) ||
        state.pendingSurgeries.find((s) => s.id === state.selectedSurgeryId)
      );
    },
    availableOperatingRooms: (state) => {
      return state.operatingRooms.filter((or) => or.status !== 'Under Maintenance');
    },
  },
  actions: {
    async runOptimization(optimizationParameters) {
      this.isOptimizing = true;
      this.optimizationResults = null;
      this.optimizationError = null;

      try {
        const response = await scheduleAPI.optimizeSchedule(optimizationParameters);
        this.optimizationResults = response;
        console.log('Optimization results:', response);
        return { success: true, data: response };
      } catch (error) {
        this.optimizationError = 'Failed to run optimization: ' + error.message;
        console.error('Optimization error:', error);
        return { success: false, error: error.message };
      } finally {
        this.isOptimizing = false;
      }
    },

    async applyOptimizationResults(optimizedAssignments) {
      this.isLoading = true;
      this.error = null;

      try {
        // Transform assignments to match backend expected format
        const assignments = optimizedAssignments.map(assignment => ({
          surgery_id: assignment.surgery_id,
          room_id: assignment.room_id,
          start_time: assignment.start_time,
          end_time: assignment.end_time,
          surgeon_id: assignment.surgeon_id,
          patient_id: assignment.patient_id,
          duration_minutes: assignment.duration_minutes,
          surgery_type_id: assignment.surgery_type_id
        }));

        await scheduleAPI.applySchedule(assignments);

        // Reload the schedule to reflect changes
        await this.loadInitialData();

        console.log('Optimization results applied successfully.');
        return { success: true };
      } catch (error) {
        this.error = 'Failed to apply optimization results: ' + error.message;
        console.error('Apply optimization error:', error);
        return { success: false, error: error.message };
      } finally {
        this.isLoading = false;
      }
    },

    clearOptimizationResults() {
      this.optimizationResults = null;
      this.optimizationError = null;
    },

    async loadInitialData(date = null) { // Renamed and adapted from loadCurrentSchedule
      this.isLoading = true;
      this.error = null;
      try {
        const targetDate = date || this.currentDateRange.start.toISOString().split('T')[0];
        const scheduleResponse = await scheduleAPI.getCurrentSchedule(targetDate);

        // Transform backend data for frontend
        this.scheduledSurgeries = scheduleResponse.surgeries.map(surgery => ({
          id: surgery.surgery_id,
          patientName: surgery.patient_name,
          type: surgery.surgery_type,
          surgeon: surgery.surgeon_name, // Assuming surgeon_name is available
          surgeonId: surgery.surgeon_id, // Assuming surgeon_id is available for addSurgery
          startTime: surgery.start_time,
          endTime: surgery.end_time,
          duration: surgery.duration_minutes,
          operatingRoomId: surgery.operating_room_id,
          status: surgery.status,
          sdsTime: surgery.setup_time_minutes || 0
        }));
        // Update current date based on fetched schedule if needed, or keep as is
        // this.currentDateRange.start = new Date(scheduleResponse.date + 'T00:00:00Z');
        // this.currentDateRange.end = new Date(scheduleResponse.date + 'T23:59:59Z');

        // Load other resources in parallel as before
        const [operatingRoomsData, staffData, equipmentData, surgeryTypesData] = await Promise.all([
            operatingRoomAPI.getOperatingRooms(),
            staffAPI.getStaff(),
            scheduleAPI.fetchEquipment(), // Assuming this exists in your api service
            scheduleAPI.fetchSurgeryTypes() // Assuming this exists
        ]);

        this.operatingRooms = operatingRoomsData.map(room => ({
          id: room.room_id,
          name: `OR-${room.room_id}`,
          location: room.location,
          status: 'Available' // Default status, or fetch real status
        }));

        this.staff = staffData.map(staffMember => ({
          id: staffMember.staff_id,
          name: staffMember.name,
          role: staffMember.role,
          specializations: staffMember.specialization ? [staffMember.specialization] : [],
          status: 'Available' // Default status, or fetch real status
        }));

        this.equipment = equipmentData || [];
        this.surgeryTypes = surgeryTypesData || {};

        try {
          const [sdsRulesData, initialSetupTimesData] = await Promise.all([
            scheduleAPI.fetchSDSRules(), // Assuming this exists
            scheduleAPI.fetchInitialSetupTimes() // Assuming this exists
          ]);
          this.sdsRules = sdsRulesData || {};
          this.initialSetupTimes = initialSetupTimesData || {};
        } catch (sdstError) {
          console.warn('SDST data not available:', sdstError);
          this.sdsRules = {};
          this.initialSetupTimes = {};
        }

      } catch (err) {
        console.error('Data load failed:', err);
        this.error = 'Failed to load schedule: ' + err.message;
      } finally {
        this.isLoading = false;
      }
    },

    async addSurgery(surgeryData) {
      try {
        const payload = {
          patient_name: surgeryData.patientName,
          surgery_type: surgeryData.type,
          surgeon_id: surgeryData.surgeonId, // Ensure this ID is available in surgeryData
          start_time: surgeryData.startTime,
          duration_minutes: surgeryData.duration,
          operating_room_id: surgeryData.operatingRoomId,
          priority: surgeryData.priority || 'normal'
        };

        // Assuming surgeryAPI.createSurgery exists and is correctly imported/defined
        const response = await surgeryAPI.createSurgery(payload);
        await this.loadInitialData(); // Refresh schedule after adding
        return response; // Return the newly created surgery data from backend
      } catch (error) {
        this.error = 'Failed to add surgery: ' + error.message;
        console.error('Failed to add surgery:', error);
        throw new Error('Failed to add surgery: ' + error.message);
      }
    },

    processScheduleData() {
      const processedSurgeries = [];

      this.operatingRooms.forEach((or) => {
        const surgeriesInOR = this.scheduledSurgeries
          .filter((s) => s.orId === or.id)
          .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

        for (let i = 0; i < surgeriesInOR.length; i++) {
          const currentSurgery = surgeriesInOR[i];
          const precedingSurgery = i > 0 ? surgeriesInOR[i - 1] : null;
          const precedingType = precedingSurgery ? precedingSurgery.type : 'Initial';

          let sdsTime = 0;
          if (precedingType === 'Initial') {
            sdsTime = this.initialSetupTimes[currentSurgery.type] || 0;
          } else if (
            this.sdsRules[precedingType] &&
            this.sdsRules[precedingType][currentSurgery.type]
          ) {
            sdsTime = this.sdsRules[precedingType][currentSurgery.type];
          }
          sdsTime = Math.max(0, sdsTime);

          const conflicts = [];
          const surgeonConflicts = this.scheduledSurgeries.filter(
            (s) =>
              s.id !== currentSurgery.id &&
              s.surgeonId === currentSurgery.surgeonId &&
              (
                (new Date(currentSurgery.startTime) < new Date(s.endTime) &&
                  new Date(currentSurgery.endTime) > new Date(s.startTime)) ||
                (new Date(currentSurgery.startTime).getTime() - sdsTime * 60 * 1000 <
                  new Date(s.endTime).getTime() &&
                  new Date(currentSurgery.startTime) > new Date(s.startTime))
              )
          );
          if (surgeonConflicts.length > 0) {
            surgeonConflicts.forEach((conflict) => {
              conflicts.push(
                `Surgeon ${currentSurgery.surgeon} unavailable (scheduled in ${conflict.orName} at ${new Date(conflict.startTime).toLocaleTimeString()})`
              );
            });
          }

          if (precedingSurgery) {
            const gapBefore =
              (new Date(currentSurgery.startTime).getTime() -
                new Date(precedingSurgery.endTime).getTime()) / (1000 * 60);
            if (gapBefore < sdsTime) {
              conflicts.push(
                `SDST Violation: Requires ${sdsTime} min setup, only ${Math.max(0, Math.floor(gapBefore))} min available after ${precedingSurgery.patientName}.`
              );
            }
          }

          processedSurgeries.push({
            ...currentSurgery,
            sdsTime,
            precedingType,
            conflicts,
          });
        }
      });

      this.scheduledSurgeries = processedSurgeries;
    },

    selectSurgery(surgeryId) {
      this.selectedSurgeryId = surgeryId;
    },

    clearSelectedSurgery() {
      this.selectedSurgeryId = null;
    },

    async rescheduleSurgery(surgeryId, targetORId, newStartTime) {
      this.isLoading = true;
      this.error = null;
      try {
        console.log(
          `Attempting to reschedule surgery ${surgeryId} to OR ${targetORId} at ${newStartTime.toISOString()}`
        );

        const surgeryToMove = this.scheduledSurgeries.find(
          (s) => s.id === surgeryId
        );

        if (!surgeryToMove) {
          console.warn(`Surgery ${surgeryId} not found in scheduled list.`);
          this.error = `Surgery not found: ${surgeryId}`;
          this.isLoading = false;
          return;
        }

        const newStartTimeISO = newStartTime.toISOString();
        const durationMinutes = surgeryToMove.durationMinutes;
        const newEndTime = new Date(newStartTime.getTime() + durationMinutes * 60000);
        const newEndTimeISO = newEndTime.toISOString();

        // API Call to persist the change
        const response = await axios.put(`/api/surgeries/${surgeryId}/reschedule`, {
          or_id: targetORId,
          start_time: newStartTimeISO,
          end_time: newEndTimeISO, // Ensure backend expects/handles this
        });

        if (response.status === 200) {
          // Update local store on successful API call
          const surgeryIndex = this.scheduledSurgeries.findIndex(
            (s) => s.id === surgeryId
          );
          // Ensure surgery is still in the list (it should be, as we found it earlier)
          if (surgeryIndex !== -1) {
            this.scheduledSurgeries.splice(surgeryIndex, 1); // Remove old instance

            surgeryToMove.orId = targetORId;
            surgeryToMove.orName =
              this.operatingRooms.find((or) => or.id === targetORId)?.name || 'Unknown OR';
            surgeryToMove.startTime = newStartTimeISO;
            surgeryToMove.endTime = newEndTimeISO; // Update endTime as well

            this.scheduledSurgeries.push(surgeryToMove); // Add updated instance
            this.processScheduleData(); // Re-process to update conflicts, etc.
            console.log(`Successfully rescheduled surgery ${surgeryId} via API.`);
          } else {
            // This case should ideally not happen if logic is correct
            console.error(`Surgery ${surgeryId} disappeared from list during reschedule.`);
            this.error = 'An unexpected error occurred during reschedule.';
            // Potentially reload data or handle error more gracefully
            await this.loadInitialData(); // Fallback: reload all data
          }
        } else {
          // Handle non-200 success responses if necessary, or treat as error
          this.error = `Failed to reschedule surgery. API responded with ${response.status}`;
          console.error('API reschedule failed:', response.data);
          // Optionally, revert optimistic update or re-fetch data
        }
      } catch (err) {
        this.error = 'Failed to reschedule surgery. Network or server error.';
        console.error('Reschedule API call failed:', err.response ? err.response.data : err.message);
        // Optionally, revert optimistic update or re-fetch data
      } finally {
        this.isLoading = false;
      }
    },

    async addSurgeryFromPending(pendingSurgeryId, targetORId, startTime) {
      this.isLoading = true;
      this.error = null;
      try {
        console.log(
          `Attempting to schedule pending surgery ${pendingSurgeryId} in OR ${targetORId} at ${startTime.toISOString()}`
        );

        const pendingIndex = this.pendingSurgeries.findIndex(
          (p) => p.id === pendingSurgeryId
        );
        if (pendingIndex !== -1) {
          const [surgeryToSchedule] = this.pendingSurgeries.splice(pendingIndex, 1);

          surgeryToSchedule.id = 's-' + Math.random().toString(36).substr(2, 9);
          surgeryToSchedule.orId = targetORId;
          surgeryToSchedule.orName =
            this.operatingRooms.find((or) => or.id === targetORId)?.name || 'Unknown OR';
          surgeryToSchedule.startTime = startTime.toISOString();
          surgeryToSchedule.status = 'Scheduled';

          this.scheduledSurgeries.push(surgeryToSchedule);

          this.processScheduleData();

          console.log(`Simulated successful scheduling of pending surgery ${pendingSurgeryId}`);
        } else {
          console.warn(`Pending surgery ${pendingSurgeryId} not found.`);
          this.error = `Pending surgery not found: ${pendingSurgeryId}`;
        }
      } catch (err) {
        this.error = 'Failed to schedule pending surgery.';
        console.error('Simulated scheduling failed:', err);
      } finally {
        this.isLoading = false;
      }
    },

    updateDateRange(newStartDate, newEndDate) {
      this.currentDateRange.start = newStartDate;
      this.currentDateRange.end = newEndDate;
    },

    updateGanttViewMode(mode) {
      this.ganttViewMode = mode;

      const currentDate = new Date();

      if (mode === 'Day') {
        const start = new Date(currentDate);
        start.setHours(7, 0, 0, 0);

        const end = new Date(currentDate);
        end.setHours(19, 0, 0, 0);

        this.currentDateRange = { start, end };
      } else if (mode === 'Week') {
        const start = new Date(currentDate);
        const day = start.getDay();
        const diff = start.getDate() - day + (day === 0 ? -6 : 1);

        start.setDate(diff);
        start.setHours(0, 0, 0, 0);

        const end = new Date(start);
        end.setDate(start.getDate() + 6);
        end.setHours(23, 59, 59, 999);

        this.currentDateRange = { start, end };
      }

      this.loadInitialData();
    },

    navigateGanttDate(direction) {
      const { start, end } = this.currentDateRange;
      let newStart, newEnd;

      if (this.ganttViewMode === 'Day') {
        const dayOffset = direction === 'prev' ? -1 : 1;
        newStart = new Date(start);
        newStart.setDate(start.getDate() + dayOffset);

        newEnd = new Date(end);
        newEnd.setDate(end.getDate() + dayOffset);
      } else if (this.ganttViewMode === 'Week') {
        const weekOffset = direction === 'prev' ? -7 : 7;
        newStart = new Date(start);
        newStart.setDate(start.getDate() + weekOffset);

        newEnd = new Date(end);
        newEnd.setDate(end.getDate() + weekOffset);
      }

      this.currentDateRange = { start: newStart, end: newEnd };
      this.loadInitialData();
    },

    resetGanttToToday() {
      this.updateGanttViewMode(this.ganttViewMode);
    },

    async editSurgery(surgeryId, updatedData) {
      this.isLoading = true;
      this.error = null;
      console.log(`Schedule Store: Simulating editing surgery ${surgeryId} with data:`, updatedData);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        const index = this.scheduledSurgeries.findIndex((s) => s.id === surgeryId);
        if (index !== -1) {
          const updatedSurgery = { ...this.scheduledSurgeries[index], ...updatedData };
          updatedSurgery.endTime =
            new Date(
              new Date(updatedSurgery.startTime).getTime() +
                updatedSurgery.duration * 60 * 1000 +
                updatedSurgery.sdsTime * 60 * 1000
            ).toISOString();

          this.scheduledSurgeries.splice(index, 1, updatedSurgery);

          this.processScheduleData();

          console.log(`Schedule Store: Simulated edit successful for surgery ${surgeryId}`);
        } else {
          console.warn(`Schedule Store: Surgery ${surgeryId} not found for editing.`);
          this.error = `Surgery not found for editing: ${surgeryId}`;
        }
      } catch (err) {
        this.error = 'Failed to edit surgery.';
        console.error('Schedule Store: Simulated edit failed:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async cancelSurgery(surgeryId) {
      this.isLoading = true;
      this.error = null;
      console.log(`Schedule Store: Simulating canceling surgery ${surgeryId}`);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        const index = this.scheduledSurgeries.findIndex((s) => s.id === surgeryId);
        if (index !== -1) {
          this.scheduledSurgeries[index].status = 'Cancelled';

          this.processScheduleData();

          console.log(`Schedule Store: Simulated cancel successful for surgery ${surgeryId}`);
        } else {
          console.warn(`Schedule Store: Surgery ${surgeryId} not found for canceling.`);
          this.error = `Surgery not found for canceling: ${surgeryId}`;
        }
      } catch (err) {
        this.error = 'Failed to cancel surgery.';
        console.error('Schedule Store: Simulated cancel failed:', err);
      } finally {
        this.isLoading = false;
      }
    },

    updateSDSTValue(fromType, toType, value) {
      this.isLoading = true;
      this.error = null;

      try {
        console.log(`Updating SDST value from ${fromType} to ${toType}: ${value} minutes`);

        setTimeout(() => {
          if (!this.sdsRules[fromType]) {
            this.sdsRules[fromType] = {};
          }

          this.sdsRules[fromType][toType] = value;

          this.processScheduleData();

          this.isLoading = false;
          console.log(`SDST value updated successfully`);
        }, 300);
      } catch (err) {
        this.error = 'Failed to update SDST value.';
        console.error('SDST update failed:', err);
        this.isLoading = false;
      }
    },

    updateInitialSetupTime(surgeryType, value) {
      this.isLoading = true;
      this.error = null;

      try {
        console.log(`Updating initial setup time for ${surgeryType}: ${value} minutes`);

        setTimeout(() => {
          this.initialSetupTimes[surgeryType] = value;

          this.processScheduleData();

          this.isLoading = false;
          console.log(`Initial setup time updated successfully`);
        }, 300);
      } catch (err) {
        this.error = 'Failed to update initial setup time.';
        console.error('Initial setup time update failed:', err);
        this.isLoading = false;
      }
    },

    addNewSurgeryType(code, fullName, initialSetupTime) {
      this.isLoading = true;
      this.error = null;

      try {
        console.log(`Adding new surgery type: ${code} - ${fullName}`);

        setTimeout(() => {
          this.surgeryTypes[code] = {
            fullName: fullName,
            code: code,
          };

          this.initialSetupTimes[code] = initialSetupTime;

          this.sdsRules[code] = {};

          Object.keys(this.sdsRules).forEach((existingType) => {
            if (existingType !== code) {
              this.sdsRules[code][existingType] = 30;

              this.sdsRules[existingType][code] = 30;
            }
          });

          this.isLoading = false;
          console.log(`New surgery type added successfully`);
        }, 500);
      } catch (err) {
        this.error = 'Failed to add new surgery type.';
        console.error('Adding surgery type failed:', err);
        this.isLoading = false;
      }
    },

    deleteSurgeryType(code) {
      this.isLoading = true;
      this.error = null;

      try {
        console.log(`Deleting surgery type: ${code}`);

        setTimeout(() => {
          delete this.surgeryTypes[code];

          delete this.initialSetupTimes[code];

          delete this.sdsRules[code];

          Object.keys(this.sdsRules).forEach((existingType) => {
            if (this.sdsRules[existingType][code]) {
              delete this.sdsRules[existingType][code];
            }
          });

          this.isLoading = false;
          console.log(`Surgery type deleted successfully`);
        }, 500);
      } catch (err) {
        this.error = 'Failed to delete surgery type.';
        console.error('Deleting surgery type failed:', err);
        this.isLoading = false;
      }
    },

    calculateSDSTForPosition(surgery, targetORId, proposedStartTime) {
      const conflicts = [];
      let sdsTime = 0;

      const surgeriesInOR =
        this.scheduledSurgeries.filter((s) => s.orId === targetORId && s.id !== surgery.id)
          .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

      const precedingSurgery = surgeriesInOR
        .filter((s) => new Date(s.endTime) <= proposedStartTime)
        .pop();

      if (precedingSurgery) {
        const precedingType = precedingSurgery.type;
        sdsTime = this.sdsRules[precedingType]?.[surgery.type] || 0;
      } else {
        sdsTime = this.initialSetupTimes[surgery.type] || 0;
      }

      if (precedingSurgery) {
        const gapBefore =
          (proposedStartTime.getTime() - new Date(precedingSurgery.endTime).getTime()) / (1000 * 60);
        if (gapBefore < sdsTime) {
          conflicts.push(
            `SDST Violation: Requires ${sdsTime} min setup, only ${Math.max(0, Math.floor(gapBefore))} min available`
          );
        }
      }

      const proposedEndTime =
        new Date(proposedStartTime.getTime() + (surgery.estimatedDuration + sdsTime) * 60 * 1000);

      surgeriesInOR.forEach((existingSurgery) => {
        const existingStart = new Date(existingSurgery.startTime);
        const existingEnd = new Date(existingSurgery.endTime);

        if (proposedStartTime < existingEnd && proposedEndTime > existingStart) {
          conflicts.push(
            `Time conflict with ${existingSurgery.patientName} (${existingStart.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${existingEnd.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})`
          );
        }
      });

      const surgeonConflicts = this.scheduledSurgeries.filter(
        (s) =>
          s.id !== surgery.id &&
          s.surgeonId === surgery.surgeonId &&
          proposedStartTime < new Date(s.endTime) &&
          proposedEndTime > new Date(s.startTime)
      );

      surgeonConflicts.forEach((conflict) => {
        conflicts.push(
          `Surgeon ${surgery.requiredSurgeons?.[0] || 'conflict'} unavailable (scheduled in ${conflict.orName})`
        );
      });

      return { sdsTime, conflicts };
    },
  },
});