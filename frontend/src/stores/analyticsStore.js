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
      sdstPatterns: null,
      resourceOptimization: null,
      schedulingEfficiency: null,
      conflictAnalysis: null,
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

    // Get SDST patterns data
    sdstPatterns: (state) => {
      if (state.cachedData.sdstPatterns) {
        return state.cachedData.sdstPatterns;
      }
      return null;
    },

    // Get resource optimization data
    resourceOptimization: (state) => {
      if (state.cachedData.resourceOptimization) {
        return state.cachedData.resourceOptimization;
      }
      return null;
    },

    // Get scheduling efficiency data
    schedulingEfficiency: (state) => {
      if (state.cachedData.schedulingEfficiency) {
        return state.cachedData.schedulingEfficiency;
      }
      return null;
    },

    // Get conflict analysis data
    conflictAnalysis: (state) => {
      if (state.cachedData.conflictAnalysis) {
        return state.cachedData.conflictAnalysis;
      }
      return null;
    },

    // Get key performance indicators
    keyPerformanceIndicators: (state) => {
      const orUtil = state.cachedData.orUtilization;
      const schedEff = state.cachedData.schedulingEfficiency;
      const sdstEff = state.cachedData.sdstEfficiency;

      if (!orUtil || !schedEff || !sdstEff) return null;

      return {
        averageORUtilization: orUtil.reduce((sum, or) => sum + or.utilizationRate, 0) / orUtil.length,
        onTimeStartRate: schedEff.onTimeStartRate?.overall || 0,
        averageSDST: sdstEff.averageSDST || 0,
        conflictRate: state.cachedData.conflictAnalysis?.conflictFrequency?.daily || 0,
      };
    },

    // Get optimization opportunities
    optimizationOpportunities: (state) => {
      const opportunities = [];

      if (state.cachedData.sdstPatterns?.optimizationOpportunities) {
        opportunities.push(...state.cachedData.sdstPatterns.optimizationOpportunities);
      }

      if (state.cachedData.resourceOptimization?.recommendations) {
        opportunities.push(...state.cachedData.resourceOptimization.recommendations.map(rec => ({
          type: rec.category,
          description: rec.recommendation,
          potentialSavings: rec.impact,
          priority: rec.priority,
        })));
      }

      return opportunities.sort((a, b) => {
        const priorityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      });
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
        sdstPatterns: null,
        resourceOptimization: null,
        schedulingEfficiency: null,
        conflictAnalysis: null,
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
        await this.simulateLoadSDSTPatterns();
        await this.simulateLoadResourceOptimization();
        await this.simulateLoadSchedulingEfficiency();
        await this.simulateLoadConflictAnalysis();

        console.log('Enhanced analytics data loaded successfully');
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

    // Simulate loading SDST patterns data
    async simulateLoadSDSTPatterns() {
      await new Promise(resolve => setTimeout(resolve, 300));

      try {
        const scheduleStore = useScheduleStore();
        const surgeries = scheduleStore.scheduledSurgeries || [];

        // Analyze SDST patterns
        const sdstPatterns = {
          transitionMatrix: this.calculateSDSTTransitionMatrix(surgeries),
          timeOfDayPatterns: this.calculateTimeOfDaySDSTPatterns(surgeries),
          orSpecificPatterns: this.calculateORSpecificSDSTPatterns(surgeries),
          optimizationOpportunities: this.identifySDSTOptimizationOpportunities(surgeries),
        };

        this.cachedData.sdstPatterns = sdstPatterns;
      } catch (error) {
        console.warn('Failed to load SDST patterns:', error);
        // Provide fallback data
        this.cachedData.sdstPatterns = {
          transitionMatrix: {},
          timeOfDayPatterns: {},
          orSpecificPatterns: {},
          optimizationOpportunities: [],
        };
      }
    },

    // Simulate loading resource optimization data
    async simulateLoadResourceOptimization() {
      await new Promise(resolve => setTimeout(resolve, 300));

      try {
        const scheduleStore = useScheduleStore();
        const resourceStore = useResourceStore();

        const resourceOptimization = {
          underutilizedResources: this.identifyUnderutilizedResources(),
          bottleneckAnalysis: this.analyzeResourceBottlenecks(),
          staffWorkloadBalance: this.analyzeStaffWorkloadBalance(),
          equipmentUtilization: this.analyzeEquipmentUtilization(),
          recommendations: this.generateResourceOptimizationRecommendations(),
        };

        this.cachedData.resourceOptimization = resourceOptimization;
      } catch (error) {
        console.warn('Failed to load resource optimization data:', error);
        this.cachedData.resourceOptimization = {
          underutilizedResources: [],
          bottleneckAnalysis: [],
          staffWorkloadBalance: { balanced: 0.75, overloaded: 0.15, underutilized: 0.10, recommendations: [] },
          equipmentUtilization: { highUtilization: [], mediumUtilization: [], lowUtilization: [], maintenanceSchedule: 'Optimal' },
          recommendations: [],
        };
      }
    },

    // Simulate loading scheduling efficiency data
    async simulateLoadSchedulingEfficiency() {
      await new Promise(resolve => setTimeout(resolve, 300));

      const scheduleStore = useScheduleStore();

      const schedulingEfficiency = {
        onTimeStartRate: this.calculateOnTimeStartRate(),
        averageTurnaroundTime: this.calculateAverageTurnaroundTime(),
        scheduleAdherence: this.calculateScheduleAdherence(),
        emergencyCaseImpact: this.analyzeEmergencyCaseImpact(),
        cancellationRate: this.calculateCancellationRate(),
        efficiencyTrends: this.calculateEfficiencyTrends(),
      };

      this.cachedData.schedulingEfficiency = schedulingEfficiency;
    },

    // Simulate loading conflict analysis data
    async simulateLoadConflictAnalysis() {
      await new Promise(resolve => setTimeout(resolve, 300));

      const scheduleStore = useScheduleStore();

      const conflictAnalysis = {
        conflictFrequency: this.analyzeConflictFrequency(),
        conflictTypes: this.categorizeConflictTypes(),
        resolutionTimes: this.analyzeConflictResolutionTimes(),
        preventableConflicts: this.identifyPreventableConflicts(),
        conflictTrends: this.analyzeConflictTrends(),
      };

      this.cachedData.conflictAnalysis = conflictAnalysis;
    },

    // Helper methods for enhanced analytics calculations
    calculateSDSTTransitionMatrix(surgeries) {
      const transitions = {};

      // Group surgeries by OR and date
      const orSchedules = {};
      surgeries.forEach(surgery => {
        const key = `${surgery.orId}-${surgery.startTime.split('T')[0]}`;
        if (!orSchedules[key]) orSchedules[key] = [];
        orSchedules[key].push(surgery);
      });

      // Analyze transitions within each OR schedule
      Object.values(orSchedules).forEach(schedule => {
        schedule.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

        for (let i = 1; i < schedule.length; i++) {
          const from = schedule[i - 1].type;
          const to = schedule[i].type;
          const key = `${from}->${to}`;

          if (!transitions[key]) {
            transitions[key] = { count: 0, totalTime: 0, avgTime: 0 };
          }

          transitions[key].count++;
          transitions[key].totalTime += schedule[i].sdsTime || 0;
          transitions[key].avgTime = transitions[key].totalTime / transitions[key].count;
        }
      });

      return transitions;
    },

    calculateTimeOfDaySDSTPatterns(surgeries) {
      const patterns = {
        morning: { count: 0, avgSDST: 0, totalSDST: 0 },
        afternoon: { count: 0, avgSDST: 0, totalSDST: 0 },
        evening: { count: 0, avgSDST: 0, totalSDST: 0 },
      };

      surgeries.forEach(surgery => {
        const hour = new Date(surgery.startTime).getHours();
        let period;

        if (hour < 12) period = 'morning';
        else if (hour < 17) period = 'afternoon';
        else period = 'evening';

        patterns[period].count++;
        patterns[period].totalSDST += surgery.sdsTime || 0;
        patterns[period].avgSDST = patterns[period].totalSDST / patterns[period].count;
      });

      return patterns;
    },

    calculateORSpecificSDSTPatterns(surgeries) {
      const orPatterns = {};

      surgeries.forEach(surgery => {
        if (!orPatterns[surgery.orId]) {
          orPatterns[surgery.orId] = {
            orName: surgery.orName,
            totalSDST: 0,
            surgeryCount: 0,
            avgSDST: 0,
            maxSDST: 0,
            minSDST: Infinity,
          };
        }

        const pattern = orPatterns[surgery.orId];
        const sdst = surgery.sdsTime || 0;

        pattern.totalSDST += sdst;
        pattern.surgeryCount++;
        pattern.avgSDST = pattern.totalSDST / pattern.surgeryCount;
        pattern.maxSDST = Math.max(pattern.maxSDST, sdst);
        pattern.minSDST = Math.min(pattern.minSDST, sdst);
      });

      return orPatterns;
    },

    identifySDSTOptimizationOpportunities(surgeries) {
      return [
        {
          type: 'Surgery Sequencing',
          description: 'Reorder surgeries to minimize SDST transitions',
          potentialSavings: '45 minutes/day',
          priority: 'High',
        },
        {
          type: 'OR Specialization',
          description: 'Dedicate specific ORs to surgery types with high SDST',
          potentialSavings: '30 minutes/day',
          priority: 'Medium',
        },
        {
          type: 'Equipment Pre-positioning',
          description: 'Pre-position equipment for known surgery sequences',
          potentialSavings: '20 minutes/day',
          priority: 'Medium',
        },
      ];
    },

    identifyUnderutilizedResources() {
      return [
        { type: 'OR', name: 'OR 5', utilization: 0.65, recommendation: 'Consider scheduling more cases' },
        { type: 'Staff', name: 'Dr. Johnson', utilization: 0.70, recommendation: 'Available for additional surgeries' },
        { type: 'Equipment', name: 'C-Arm Unit 3', utilization: 0.45, recommendation: 'Underutilized, consider reallocation' },
      ];
    },

    analyzeResourceBottlenecks() {
      return [
        { resource: 'Anesthesia Team', impact: 'High', description: 'Limited availability causing delays' },
        { resource: 'Cardiac OR', impact: 'Medium', description: 'High demand for specialized procedures' },
        { resource: 'Sterilization', impact: 'Low', description: 'Occasional delays in instrument processing' },
      ];
    },

    analyzeStaffWorkloadBalance() {
      return {
        balanced: 0.75,
        overloaded: 0.15,
        underutilized: 0.10,
        recommendations: [
          'Redistribute cases from Dr. Smith to Dr. Johnson',
          'Consider cross-training nurses for multiple specialties',
        ],
      };
    },

    analyzeEquipmentUtilization() {
      return {
        highUtilization: ['Phacoemulsification Machine', 'Cardiac Monitor'],
        mediumUtilization: ['C-Arm Unit 1', 'Laser System'],
        lowUtilization: ['C-Arm Unit 3', 'Microscope 2'],
        maintenanceSchedule: 'Optimal',
      };
    },

    generateResourceOptimizationRecommendations() {
      return [
        {
          priority: 'High',
          category: 'Staffing',
          recommendation: 'Add one additional anesthesia team for peak hours',
          impact: 'Reduce delays by 25%',
        },
        {
          priority: 'Medium',
          category: 'Equipment',
          recommendation: 'Relocate underutilized C-Arm to high-demand OR',
          impact: 'Improve equipment utilization by 15%',
        },
        {
          priority: 'Low',
          category: 'Scheduling',
          recommendation: 'Implement block scheduling for cardiac procedures',
          impact: 'Reduce SDST by 10%',
        },
      ];
    },

    calculateOnTimeStartRate() {
      return {
        overall: 0.82,
        byOR: {
          'OR1': 0.85,
          'OR2': 0.78,
          'OR3': 0.84,
          'OR4': 0.80,
          'OR5': 0.83,
        },
        trend: 'improving',
        target: 0.90,
      };
    },

    calculateAverageTurnaroundTime() {
      return {
        overall: 24.5, // minutes
        byType: {
          'APPEN': 18,
          'KNEE': 22,
          'CABG': 35,
          'CATAR': 15,
          'HIPRE': 28,
        },
        target: 20,
        trend: 'stable',
      };
    },

    calculateScheduleAdherence() {
      return {
        onTime: 0.75,
        delayed: 0.20,
        early: 0.05,
        averageDelay: 12, // minutes
        majorDelays: 0.03, // >30 minutes
      };
    },

    analyzeEmergencyCaseImpact() {
      return {
        frequency: 2.3, // per day
        averageDelay: 45, // minutes to scheduled cases
        cancellationRate: 0.05,
        resourceReallocation: 'Moderate',
        recommendations: [
          'Reserve OR capacity for emergencies',
          'Implement emergency case protocols',
        ],
      };
    },

    calculateCancellationRate() {
      return {
        overall: 0.08,
        byReason: {
          'Patient condition': 0.03,
          'Equipment failure': 0.02,
          'Staff unavailability': 0.02,
          'Emergency priority': 0.01,
        },
        trend: 'decreasing',
        target: 0.05,
      };
    },

    calculateEfficiencyTrends() {
      const days = 30;
      const trends = [];

      for (let i = 0; i < days; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);

        trends.unshift({
          date: date.toISOString().split('T')[0],
          efficiency: 0.75 + Math.random() * 0.2, // 75-95%
          onTimeStarts: 0.80 + Math.random() * 0.15, // 80-95%
          utilization: 0.70 + Math.random() * 0.25, // 70-95%
        });
      }

      return trends;
    },

    analyzeConflictFrequency() {
      return {
        daily: 3.2,
        weekly: 22.4,
        monthly: 96.8,
        trend: 'decreasing',
        peakTimes: ['Monday morning', 'Friday afternoon'],
      };
    },

    categorizeConflictTypes() {
      return {
        'Resource conflicts': 0.45,
        'SDST violations': 0.25,
        'Staff unavailability': 0.20,
        'Equipment conflicts': 0.10,
      };
    },

    analyzeConflictResolutionTimes() {
      return {
        average: 8.5, // minutes
        byType: {
          'Resource conflicts': 12,
          'SDST violations': 6,
          'Staff unavailability': 15,
          'Equipment conflicts': 5,
        },
        target: 5,
      };
    },

    identifyPreventableConflicts() {
      return {
        percentage: 0.65,
        causes: [
          'Inadequate advance planning',
          'Lack of real-time resource visibility',
          'Manual scheduling errors',
          'Emergency case disruptions',
        ],
        solutions: [
          'Implement automated conflict detection',
          'Improve resource tracking systems',
          'Enhanced staff training',
        ],
      };
    },

    analyzeConflictTrends() {
      const days = 30;
      const trends = [];

      for (let i = 0; i < days; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);

        trends.unshift({
          date: date.toISOString().split('T')[0],
          conflicts: Math.floor(Math.random() * 6) + 1, // 1-6 conflicts per day
          resolved: Math.floor(Math.random() * 5) + 1, // 1-5 resolved
          avgResolutionTime: Math.floor(Math.random() * 10) + 5, // 5-15 minutes
        });
      }

      return trends;
    },
  }
});
