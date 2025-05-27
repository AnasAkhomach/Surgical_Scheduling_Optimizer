import { defineStore } from 'pinia';
import { useScheduleStore } from './scheduleStore';
import { useResourceStore } from './resourceStore';

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    isLoading: false,
    error: null,
    
    // Date range for analytics
    dateRange: {
      start: new Date(new Date().setDate(new Date().getDate() - 30)), // Default to last 30 days
      end: new Date(),
    },
    
    // Cached analytics data
    cachedData: {
      orUtilization: null,
      surgeonUtilization: null,
      surgeryTypeDistribution: null,
      sdstEfficiency: null,
      dailyMetrics: null,
    },
    
    // Custom report configurations
    savedReports: [
      {
        id: 'report-1',
        name: 'Monthly OR Utilization',
        type: 'orUtilization',
        dateRange: { 
          start: new Date(new Date().setMonth(new Date().getMonth() - 1)), 
          end: new Date() 
        },
        filters: { orIds: ['OR1', 'OR2', 'OR3'] },
        metrics: ['utilizationRate', 'idleTime', 'overtimeRate'],
        chartType: 'bar',
      },
      {
        id: 'report-2',
        name: 'Surgeon Performance',
        type: 'surgeonUtilization',
        dateRange: { 
          start: new Date(new Date().setMonth(new Date().getMonth() - 3)), 
          end: new Date() 
        },
        filters: { surgeonIds: ['SG1', 'SG2', 'SG3'] },
        metrics: ['surgeryCount', 'averageDuration', 'onTimeStart'],
        chartType: 'line',
      },
    ],
  }),
  
  getters: {
    // Get the schedule and resource stores
    scheduleStore: () => useScheduleStore(),
    resourceStore: () => useResourceStore(),
    
    // Get OR utilization data
    orUtilization: (state) => {
      if (state.cachedData.orUtilization) {
        return state.cachedData.orUtilization;
      }
      
      // If not cached, calculate it (this would normally be fetched from an API)
      return null;
    },
    
    // Get surgeon utilization data
    surgeonUtilization: (state) => {
      if (state.cachedData.surgeonUtilization) {
        return state.cachedData.surgeonUtilization;
      }
      
      // If not cached, calculate it (this would normally be fetched from an API)
      return null;
    },
    
    // Get surgery type distribution data
    surgeryTypeDistribution: (state) => {
      if (state.cachedData.surgeryTypeDistribution) {
        return state.cachedData.surgeryTypeDistribution;
      }
      
      // If not cached, calculate it (this would normally be fetched from an API)
      return null;
    },
    
    // Get SDST efficiency data
    sdstEfficiency: (state) => {
      if (state.cachedData.sdstEfficiency) {
        return state.cachedData.sdstEfficiency;
      }
      
      // If not cached, calculate it (this would normally be fetched from an API)
      return null;
    },
    
    // Get daily metrics data
    dailyMetrics: (state) => {
      if (state.cachedData.dailyMetrics) {
        return state.cachedData.dailyMetrics;
      }
      
      // If not cached, calculate it (this would normally be fetched from an API)
      return null;
    },
  },
  
  actions: {
    // Set the date range for analytics
    setDateRange(start, end) {
      this.dateRange.start = start;
      this.dateRange.end = end;
      
      // Clear cached data when date range changes
      this.clearCachedData();
    },
    
    // Clear cached data
    clearCachedData() {
      this.cachedData = {
        orUtilization: null,
        surgeonUtilization: null,
        surgeryTypeDistribution: null,
        sdstEfficiency: null,
        dailyMetrics: null,
      };
    },
    
    // Load analytics data
    async loadAnalyticsData() {
      this.isLoading = true;
      this.error = null;
      
      try {
        // In a real app, this would fetch data from an API
        await this.simulateLoadORUtilization();
        await this.simulateLoadSurgeonUtilization();
        await this.simulateLoadSurgeryTypeDistribution();
        await this.simulateLoadSDSTEfficiency();
        await this.simulateLoadDailyMetrics();
        
        console.log('Analytics data loaded successfully');
      } catch (error) {
        this.error = 'Failed to load analytics data';
        console.error('Failed to load analytics data:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    // Simulate loading OR utilization data
    async simulateLoadORUtilization() {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate mock data
      const orUtilization = [];
      const scheduleStore = useScheduleStore();
      const resourceStore = useResourceStore();
      
      resourceStore.operatingRooms.forEach(or => {
        // Calculate utilization based on scheduled surgeries
        const surgeries = scheduleStore.scheduledSurgeries.filter(s => s.orId === or.id);
        const totalMinutes = surgeries.reduce((total, s) => total + s.duration, 0);
        const totalHours = totalMinutes / 60;
        
        // Assume 8-hour workday
        const workdayHours = 8;
        const utilizationRate = Math.min(totalHours / workdayHours, 1);
        
        orUtilization.push({
          orId: or.id,
          orName: or.name,
          utilizationRate: utilizationRate,
          scheduledHours: totalHours,
          availableHours: workdayHours,
          idleTime: Math.max(0, workdayHours - totalHours),
          overtimeRate: Math.max(0, (totalHours - workdayHours) / workdayHours),
        });
      });
      
      this.cachedData.orUtilization = orUtilization;
    },
    
    // Simulate loading surgeon utilization data
    async simulateLoadSurgeonUtilization() {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate mock data
      const surgeonUtilization = [];
      const scheduleStore = useScheduleStore();
      const resourceStore = useResourceStore();
      
      resourceStore.staff
        .filter(s => s.role === 'Surgeon')
        .forEach(surgeon => {
          // Calculate utilization based on scheduled surgeries
          const surgeries = scheduleStore.scheduledSurgeries.filter(s => s.surgeonId === surgeon.id);
          const totalMinutes = surgeries.reduce((total, s) => total + s.duration, 0);
          const totalHours = totalMinutes / 60;
          const surgeryCount = surgeries.length;
          
          // Calculate average duration
          const averageDuration = surgeryCount > 0 ? totalMinutes / surgeryCount : 0;
          
          // Simulate on-time start percentage (would be calculated from actual data)
          const onTimeStart = Math.random() * 0.3 + 0.7; // Random between 70% and 100%
          
          surgeonUtilization.push({
            surgeonId: surgeon.id,
            surgeonName: surgeon.name,
            surgeryCount,
            totalHours,
            averageDuration,
            onTimeStart,
          });
        });
      
      this.cachedData.surgeonUtilization = surgeonUtilization;
    },
    
    // Simulate loading surgery type distribution data
    async simulateLoadSurgeryTypeDistribution() {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate mock data
      const surgeryTypeDistribution = [];
      const scheduleStore = useScheduleStore();
      
      // Get unique surgery types
      const surgeryTypes = [...new Set(scheduleStore.scheduledSurgeries.map(s => s.type))];
      
      surgeryTypes.forEach(type => {
        const surgeries = scheduleStore.scheduledSurgeries.filter(s => s.type === type);
        const count = surgeries.length;
        const totalMinutes = surgeries.reduce((total, s) => total + s.duration, 0);
        
        surgeryTypeDistribution.push({
          type,
          count,
          totalMinutes,
          averageDuration: count > 0 ? totalMinutes / count : 0,
          percentage: count / scheduleStore.scheduledSurgeries.length,
        });
      });
      
      this.cachedData.surgeryTypeDistribution = surgeryTypeDistribution;
    },
    
    // Simulate loading SDST efficiency data
    async simulateLoadSDSTEfficiency() {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate mock data for SDST efficiency
      const sdstEfficiency = {
        averageSDST: 22.5, // minutes
        sdstPercentage: 0.12, // 12% of total OR time
        mostEfficientTransition: {
          from: 'APPEN',
          to: 'KNEE',
          averageTime: 15,
        },
        leastEfficientTransition: {
          from: 'CABG',
          to: 'APPEN',
          averageTime: 45,
        },
        potentialSavings: 120, // minutes per day
      };
      
      this.cachedData.sdstEfficiency = sdstEfficiency;
    },
    
    // Simulate loading daily metrics data
    async simulateLoadDailyMetrics() {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate mock data for daily metrics over the last 30 days
      const dailyMetrics = [];
      const startDate = new Date(this.dateRange.start);
      const endDate = new Date(this.dateRange.end);
      
      // Loop through each day in the date range
      for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        const date = new Date(d);
        
        // Generate random metrics for the day
        dailyMetrics.push({
          date: date.toISOString().split('T')[0],
          surgeryCount: Math.floor(Math.random() * 10) + 5,
          utilizationRate: Math.random() * 0.3 + 0.6, // 60-90%
          onTimeStart: Math.random() * 0.3 + 0.7, // 70-100%
          averageTurnaround: Math.floor(Math.random() * 10) + 20, // 20-30 minutes
        });
      }
      
      this.cachedData.dailyMetrics = dailyMetrics;
    },
    
    // Save a custom report configuration
    saveCustomReport(reportConfig) {
      // Generate a unique ID
      const newId = `report-${Date.now()}`;
      
      // Add the new report
      this.savedReports.push({
        id: newId,
        ...reportConfig,
      });
      
      return newId;
    },
    
    // Delete a custom report
    deleteCustomReport(reportId) {
      this.savedReports = this.savedReports.filter(r => r.id !== reportId);
    },
  }
});
