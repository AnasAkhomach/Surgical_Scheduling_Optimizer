import { describe, it, expect, vi, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useScheduleStore } from '../scheduleStore';
import { scheduleAPI } from '../../services/api';

// Mock the API
vi.mock('../../services/api', () => ({
  scheduleAPI: {
    getCurrentSchedule: vi.fn(),
    fetchOperatingRooms: vi.fn(),
    fetchStaff: vi.fn(),
    fetchEquipment: vi.fn(),
    fetchSurgeryTypes: vi.fn(),
    fetchSDSRules: vi.fn(),
    fetchInitialSetupTimes: vi.fn(),
    optimizeSchedule: vi.fn(),
    applySchedule: vi.fn(),
  },
}));

describe('Schedule Store Integration Tests', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useScheduleStore();
    vi.clearAllMocks();
  });

  describe('loadInitialData', () => {
    it('should load and transform schedule data correctly', async () => {
      // Mock API responses
      const mockScheduleData = [
        {
          surgery_id: 1,
          patient_id: 101,
          patient_name: 'John Doe',
          surgery_type: 'Appendectomy',
          surgeon_id: 201,
          surgeon: 'Dr. Smith',
          room_id: 1,
          room: 'OR-1',
          start_time: '2023-10-27T08:00:00Z',
          end_time: '2023-10-27T09:30:00Z',
          duration_minutes: 90,
          status: 'Scheduled',
          urgency_level: 'normal'
        }
      ];

      const mockOperatingRooms = [
        { room_id: 1, location: 'Main Floor OR 1' },
        { room_id: 2, location: 'Main Floor OR 2' }
      ];

      const mockStaff = [
        { staff_id: 201, name: 'Dr. Smith', role: 'Surgeon', specialization: 'General Surgery' }
      ];

      const mockEquipment = [];
      const mockSurgeryTypes = {};

      scheduleAPI.getCurrentSchedule.mockResolvedValue(mockScheduleData);
      scheduleAPI.fetchOperatingRooms.mockResolvedValue(mockOperatingRooms);
      scheduleAPI.fetchStaff.mockResolvedValue(mockStaff);
      scheduleAPI.fetchEquipment.mockResolvedValue(mockEquipment);
      scheduleAPI.fetchSurgeryTypes.mockResolvedValue(mockSurgeryTypes);
      scheduleAPI.fetchSDSRules.mockResolvedValue({});
      scheduleAPI.fetchInitialSetupTimes.mockResolvedValue({});

      // Execute
      await store.loadInitialData();

      // Verify API calls
      expect(scheduleAPI.getCurrentSchedule).toHaveBeenCalledWith('2023-10-27');
      expect(scheduleAPI.fetchOperatingRooms).toHaveBeenCalled();
      expect(scheduleAPI.fetchStaff).toHaveBeenCalled();
      expect(scheduleAPI.fetchEquipment).toHaveBeenCalled();
      expect(scheduleAPI.fetchSurgeryTypes).toHaveBeenCalled();

      // Verify data transformation
      expect(store.scheduledSurgeries).toHaveLength(1);
      expect(store.scheduledSurgeries[0]).toMatchObject({
        id: 1,
        surgeryId: 1,
        patientName: 'John Doe',
        type: 'Appendectomy',
        surgeon: 'Dr. Smith',
        orName: 'OR-1',
        duration: 90,
        status: 'Scheduled'
      });

      expect(store.operatingRooms).toHaveLength(2);
      expect(store.operatingRooms[0]).toMatchObject({
        id: 1,
        name: 'OR-1',
        location: 'Main Floor OR 1',
        status: 'Available'
      });

      expect(store.staff).toHaveLength(1);
      expect(store.staff[0]).toMatchObject({
        id: 201,
        name: 'Dr. Smith',
        role: 'Surgeon',
        specializations: ['General Surgery']
      });

      expect(store.isLoading).toBe(false);
      expect(store.error).toBe(null);
    });

    it('should handle API errors gracefully', async () => {
      scheduleAPI.getCurrentSchedule.mockRejectedValue(new Error('API Error'));

      await store.loadInitialData();

      expect(store.error).toContain('Failed to load schedule data: API Error');
      expect(store.isLoading).toBe(false);
    });

    it('should handle SDST data errors gracefully', async () => {
      scheduleAPI.getCurrentSchedule.mockResolvedValue([]);
      scheduleAPI.fetchOperatingRooms.mockResolvedValue([]);
      scheduleAPI.fetchStaff.mockResolvedValue([]);
      scheduleAPI.fetchEquipment.mockResolvedValue([]);
      scheduleAPI.fetchSurgeryTypes.mockResolvedValue({});
      scheduleAPI.fetchSDSRules.mockRejectedValue(new Error('SDST Error'));
      scheduleAPI.fetchInitialSetupTimes.mockRejectedValue(new Error('Setup Time Error'));

      await store.loadInitialData();

      expect(store.sdsRules).toEqual({});
      expect(store.initialSetupTimes).toEqual({});
      expect(store.error).toBe(null); // Should not fail overall
    });
  });

  describe('runOptimization', () => {
    it('should call optimization API and handle response', async () => {
      const mockOptimizationResult = {
        assignments: [
          {
            surgery_id: 1,
            room_id: 1,
            start_time: '2023-10-27T08:00:00Z',
            end_time: '2023-10-27T09:30:00Z',
            surgeon_id: 201,
            patient_id: 101,
            duration_minutes: 90,
            surgery_type_id: 1
          }
        ],
        score: 85.5,
        metrics: { utilization: 0.85 },
        iteration_count: 50,
        execution_time_seconds: 2.5
      };

      scheduleAPI.optimizeSchedule.mockResolvedValue(mockOptimizationResult);

      const parameters = {
        schedule_date: '2023-10-27',
        max_iterations: 100,
        time_limit_seconds: 30
      };

      const result = await store.runOptimization(parameters);

      expect(scheduleAPI.optimizeSchedule).toHaveBeenCalledWith(parameters);
      expect(result.success).toBe(true);
      expect(store.optimizationResults).toEqual(mockOptimizationResult);
      expect(store.isOptimizing).toBe(false);
    });

    it('should handle optimization errors', async () => {
      scheduleAPI.optimizeSchedule.mockRejectedValue(new Error('Optimization failed'));

      const result = await store.runOptimization({});

      expect(result.success).toBe(false);
      expect(result.error).toBe('Optimization failed');
      expect(store.optimizationError).toContain('Failed to run optimization');
      expect(store.isOptimizing).toBe(false);
    });
  });

  describe('applyOptimizationResults', () => {
    it('should apply optimization results and reload data', async () => {
      const mockAssignments = [
        {
          surgery_id: 1,
          room_id: 1,
          start_time: '2023-10-27T08:00:00Z',
          end_time: '2023-10-27T09:30:00Z',
          surgeon_id: 201,
          patient_id: 101,
          duration_minutes: 90,
          surgery_type_id: 1
        }
      ];

      scheduleAPI.applySchedule.mockResolvedValue({ message: 'Success' });
      scheduleAPI.getCurrentSchedule.mockResolvedValue([]);
      scheduleAPI.fetchOperatingRooms.mockResolvedValue([]);
      scheduleAPI.fetchStaff.mockResolvedValue([]);
      scheduleAPI.fetchEquipment.mockResolvedValue([]);
      scheduleAPI.fetchSurgeryTypes.mockResolvedValue({});
      scheduleAPI.fetchSDSRules.mockResolvedValue({});
      scheduleAPI.fetchInitialSetupTimes.mockResolvedValue({});

      const result = await store.applyOptimizationResults(mockAssignments);

      expect(scheduleAPI.applySchedule).toHaveBeenCalledWith(mockAssignments);
      expect(scheduleAPI.getCurrentSchedule).toHaveBeenCalled(); // Should reload data
      expect(result.success).toBe(true);
    });

    it('should handle apply errors', async () => {
      scheduleAPI.applySchedule.mockRejectedValue(new Error('Apply failed'));

      const result = await store.applyOptimizationResults([]);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Apply failed');
      expect(store.error).toContain('Failed to apply optimization results');
    });
  });

  describe('getters', () => {
    beforeEach(() => {
      store.scheduledSurgeries = [
        {
          id: 1,
          orId: 1,
          startTime: '2023-10-27T08:00:00Z',
          endTime: '2023-10-27T09:30:00Z'
        },
        {
          id: 2,
          orId: 1,
          startTime: '2023-10-27T10:00:00Z',
          endTime: '2023-10-27T11:30:00Z'
        },
        {
          id: 3,
          orId: 2,
          startTime: '2023-10-27T08:30:00Z',
          endTime: '2023-10-27T10:00:00Z'
        }
      ];

      store.operatingRooms = [
        { id: 1, status: 'Available' },
        { id: 2, status: 'Under Maintenance' }
      ];
    });

    it('should filter surgeries by OR correctly', () => {
      const or1Surgeries = store.getSurgeriesForOR(1);
      expect(or1Surgeries).toHaveLength(2);
      expect(or1Surgeries.map(s => s.id)).toEqual([1, 2]);
    });

    it('should filter available operating rooms', () => {
      const availableRooms = store.availableOperatingRooms;
      expect(availableRooms).toHaveLength(1);
      expect(availableRooms[0].id).toBe(1);
    });
  });
});
