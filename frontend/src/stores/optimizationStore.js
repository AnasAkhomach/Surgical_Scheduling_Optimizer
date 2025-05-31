import { defineStore } from 'pinia';
import { useScheduleStore } from './scheduleStore';
import { useResourceStore } from './resourceStore';
import { useAnalyticsStore } from './analyticsStore';
import { scheduleAPI } from '@/services/api';

export const useOptimizationStore = defineStore('optimization', {
  state: () => ({
    // Optimization state
    isOptimizing: false,
    optimizationResults: null,
    selectedSuggestions: [],

    // Optimization settings
    optimizationSettings: {
      prioritizeSDST: true,
      prioritizeUrgency: true,
      prioritizeResourceUtilization: true,
      allowMinorDelays: true,
      maxDelayMinutes: 30,
      preserveEmergencies: true,
    },

    // Cached optimization data
    cachedOptimizations: {},

    // Optimization history
    optimizationHistory: [],

    // Performance metrics
    optimizationMetrics: {
      totalSuggestionsGenerated: 0,
      suggestionsApplied: 0,
      averageSDSTImprovement: 0,
      averageUtilizationImprovement: 0,
    },
  }),

  getters: {
    // Get current optimization suggestions
    currentSuggestions: (state) => {
      return state.optimizationResults?.suggestions || [];
    },

    // Get high priority suggestions
    highPrioritySuggestions: (state) => {
      return state.optimizationResults?.suggestions?.filter(s => s.priority === 'High') || [];
    },

    // Get potential savings
    potentialSavings: (state) => {
      if (!state.optimizationResults) return null;

      return {
        sdstReduction: state.optimizationResults.metrics?.sdstReduction || 0,
        utilizationImprovement: state.optimizationResults.metrics?.utilizationImprovement || 0,
        conflictReduction: state.optimizationResults.metrics?.conflictReduction || 0,
        timesSaved: state.optimizationResults.metrics?.timesSaved || 0,
      };
    },

    // Get optimization summary
    optimizationSummary: (state) => {
      if (!state.optimizationResults) return null;

      const suggestions = state.optimizationResults.suggestions || [];
      return {
        totalSuggestions: suggestions.length,
        highPriority: suggestions.filter(s => s.priority === 'High').length,
        mediumPriority: suggestions.filter(s => s.priority === 'Medium').length,
        lowPriority: suggestions.filter(s => s.priority === 'Low').length,
        estimatedImpact: state.optimizationResults.metrics?.overallImpact || 'Low',
      };
    },

    // Check if optimization is available
    canOptimize: (state) => {
      const scheduleStore = useScheduleStore();
      return !state.isOptimizing && scheduleStore.scheduledSurgeries.length > 0;
    },
  },

  actions: {
    // Run optimization analysis
    async runOptimization(targetDate = null) {
      if (this.isOptimizing) return;

      this.isOptimizing = true;

      try {
        const scheduleStore = useScheduleStore();

        // Get current schedule data
        const surgeries = targetDate
          ? scheduleStore.getSurgeriesForDate(targetDate)
          : scheduleStore.scheduledSurgeries;

        if (surgeries.length === 0) {
          throw new Error('No surgeries found for optimization');
        }

        // Prepare optimization parameters
        const optimizationParams = {
          schedule_date: targetDate || new Date().toISOString().split('T')[0],
          max_iterations: 100,
          tabu_tenure: 10,
          max_no_improvement: 20,
          time_limit_seconds: 300,
          weights: {
            sdst_weight: this.optimizationSettings.prioritizeSDST ? 0.4 : 0.1,
            urgency_weight: this.optimizationSettings.prioritizeUrgency ? 0.3 : 0.1,
            utilization_weight: this.optimizationSettings.prioritizeResourceUtilization ? 0.3 : 0.1
          }
        };

        // Call the backend optimization API
        const response = await scheduleAPI.optimizeSchedule(optimizationParams);

        // Transform backend response to frontend format
        const suggestions = this.transformOptimizationResults(response, surgeries);

        // Calculate optimization metrics
        const metrics = this.calculateOptimizationMetrics(surgeries, suggestions);

        // Store results
        this.optimizationResults = {
          timestamp: new Date().toISOString(),
          targetDate: targetDate || new Date().toISOString().split('T')[0],
          suggestions,
          metrics,
          originalSchedule: [...surgeries],
          backendResults: response, // Store original backend response
        };

        // Update metrics
        this.optimizationMetrics.totalSuggestionsGenerated += suggestions.length;

        // Add to history
        this.optimizationHistory.unshift({
          id: Date.now(),
          timestamp: new Date().toISOString(),
          suggestionsCount: suggestions.length,
          potentialSavings: metrics.sdstReduction,
          applied: false,
        });

        // Keep only last 10 optimization runs
        if (this.optimizationHistory.length > 10) {
          this.optimizationHistory = this.optimizationHistory.slice(0, 10);
        }

        console.log('Optimization completed:', this.optimizationResults);

      } catch (error) {
        console.error('Optimization failed:', error);
        throw error;
      } finally {
        this.isOptimizing = false;
      }
    },

    // Transform backend optimization results to frontend suggestions format
    transformOptimizationResults(backendResponse, originalSurgeries) {
      const suggestions = [];

      if (!backendResponse.assignments || backendResponse.assignments.length === 0) {
        return suggestions;
      }

      // Compare original schedule with optimized assignments
      const originalMap = new Map(originalSurgeries.map(s => [s.id, s]));

      backendResponse.assignments.forEach((assignment, index) => {
        const originalSurgery = originalMap.get(assignment.surgery_id?.toString());

        if (originalSurgery) {
          // Check if surgery was moved to different OR
          if (originalSurgery.orId !== `OR${assignment.room_id}`) {
            suggestions.push({
              id: `move-or-${assignment.surgery_id}`,
              type: 'relocate',
              category: 'Resource Optimization',
              priority: 'Medium',
              title: `Move surgery to different OR`,
              description: `Move ${originalSurgery.type} surgery (${originalSurgery.patientName}) from ${originalSurgery.orId} to OR${assignment.room_id}`,
              impact: 15,
              effort: 'Medium',
              surgeryIds: [originalSurgery.id],
              fromOR: originalSurgery.orId,
              toOR: `OR${assignment.room_id}`,
              estimatedSavings: 'Improved resource utilization',
              risks: ['Requires staff coordination'],
            });
          }

          // Check if surgery time was changed significantly
          const originalStart = new Date(originalSurgery.startTime);
          const newStart = new Date(assignment.start_time);
          const timeDiff = Math.abs(newStart - originalStart) / (1000 * 60); // minutes

          if (timeDiff > 30) {
            suggestions.push({
              id: `reschedule-${assignment.surgery_id}`,
              type: 'reschedule',
              category: 'Schedule Optimization',
              priority: timeDiff > 120 ? 'High' : 'Medium',
              title: `Reschedule surgery for better optimization`,
              description: `Reschedule ${originalSurgery.type} surgery (${originalSurgery.patientName}) to ${newStart.toLocaleTimeString()}`,
              impact: Math.min(timeDiff / 2, 30),
              effort: 'High',
              surgeryIds: [originalSurgery.id],
              originalTime: originalSurgery.startTime,
              suggestedTime: assignment.start_time,
              estimatedSavings: `${Math.round(timeDiff / 2)} minutes optimization`,
              risks: ['Patient notification required'],
            });
          }
        }
      });

      // Add overall optimization suggestion based on backend metrics
      if (backendResponse.score && backendResponse.metrics) {
        suggestions.push({
          id: `overall-optimization-${Date.now()}`,
          type: 'apply_all',
          category: 'Overall Optimization',
          priority: 'High',
          title: `Apply complete optimization solution`,
          description: `Apply the full optimization solution with score ${backendResponse.score.toFixed(2)}`,
          impact: backendResponse.metrics.total_score || 50,
          effort: 'High',
          surgeryIds: backendResponse.assignments.map(a => a.surgery_id?.toString()).filter(Boolean),
          estimatedSavings: `Complete schedule optimization`,
          risks: ['Significant schedule changes', 'Multiple patient notifications'],
          backendData: backendResponse,
        });
      }

      return suggestions;
    },

    // Generate optimization suggestions
    async generateOptimizationSuggestions(surgeries) {
      const suggestions = [];

      // 1. SDST Optimization Suggestions
      const sdstSuggestions = this.generateSDSTOptimizationSuggestions(surgeries);
      suggestions.push(...sdstSuggestions);

      // 2. Resource Utilization Suggestions
      const resourceSuggestions = this.generateResourceOptimizationSuggestions(surgeries);
      suggestions.push(...resourceSuggestions);

      // 3. Conflict Resolution Suggestions
      const conflictSuggestions = this.generateConflictResolutionSuggestions(surgeries);
      suggestions.push(...conflictSuggestions);

      // 4. Schedule Balancing Suggestions
      const balancingSuggestions = this.generateScheduleBalancingSuggestions(surgeries);
      suggestions.push(...balancingSuggestions);

      // Sort by priority and impact
      return suggestions.sort((a, b) => {
        const priorityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
        if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        }
        return b.impact - a.impact;
      });
    },

    // Generate SDST optimization suggestions
    generateSDSTOptimizationSuggestions(surgeries) {
      const suggestions = [];

      // Group surgeries by OR
      const orGroups = {};
      surgeries.forEach(surgery => {
        if (!orGroups[surgery.orId]) orGroups[surgery.orId] = [];
        orGroups[surgery.orId].push(surgery);
      });

      // Analyze each OR for SDST optimization opportunities
      Object.entries(orGroups).forEach(([orId, orSurgeries]) => {
        if (orSurgeries.length < 2) return;

        // Sort by start time
        orSurgeries.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

        // Find inefficient transitions
        for (let i = 1; i < orSurgeries.length; i++) {
          const prev = orSurgeries[i - 1];
          const current = orSurgeries[i];

          // Check if reordering could reduce SDST
          const currentSDST = this.getSDSTBetweenTypes(prev.type, current.type);

          // Look for better alternatives
          const alternatives = orSurgeries.slice(i).filter(s =>
            this.getSDSTBetweenTypes(prev.type, s.type) < currentSDST - 10
          );

          if (alternatives.length > 0) {
            const bestAlternative = alternatives[0];
            const savings = currentSDST - this.getSDSTBetweenTypes(prev.type, bestAlternative.type);

            suggestions.push({
              id: `sdst-${Date.now()}-${i}`,
              type: 'reorder',
              category: 'SDST Optimization',
              priority: savings > 20 ? 'High' : savings > 10 ? 'Medium' : 'Low',
              title: `Reorder surgeries in ${orId} to reduce SDST`,
              description: `Move ${bestAlternative.type} surgery (${bestAlternative.patientName}) before ${current.type} surgery (${current.patientName}) to save ${savings} minutes of setup time`,
              impact: savings,
              effort: 'Low',
              surgeryIds: [current.id, bestAlternative.id],
              originalOrder: [current.id, bestAlternative.id],
              suggestedOrder: [bestAlternative.id, current.id],
              estimatedSavings: `${savings} minutes SDST reduction`,
              risks: savings > 15 ? [] : ['Minor schedule disruption'],
            });
          }
        }
      });

      return suggestions;
    },

    // Generate resource optimization suggestions
    generateResourceOptimizationSuggestions(surgeries) {
      const suggestions = [];
      const resourceStore = useResourceStore();

      // Analyze resource conflicts and underutilization
      const resourceUsage = this.analyzeResourceUsage(surgeries);

      // Suggest moving surgeries to underutilized ORs
      Object.entries(resourceUsage.orUtilization).forEach(([orId, utilization]) => {
        if (utilization < 0.6) {
          const overutilizedORs = Object.entries(resourceUsage.orUtilization)
            .filter(([id, util]) => util > 0.9 && id !== orId);

          if (overutilizedORs.length > 0) {
            const [overutilizedOR] = overutilizedORs[0];
            const movableSurgeries = surgeries.filter(s =>
              s.orId === overutilizedOR && s.priority !== 'Emergency'
            );

            if (movableSurgeries.length > 0) {
              const surgery = movableSurgeries[0];
              suggestions.push({
                id: `resource-${Date.now()}-${orId}`,
                type: 'relocate',
                category: 'Resource Optimization',
                priority: 'Medium',
                title: `Move surgery to underutilized OR`,
                description: `Move ${surgery.type} surgery (${surgery.patientName}) from ${overutilizedOR} to ${orId} to balance resource utilization`,
                impact: 15,
                effort: 'Medium',
                surgeryIds: [surgery.id],
                fromOR: overutilizedOR,
                toOR: orId,
                estimatedSavings: 'Improved resource balance',
                risks: ['Requires staff coordination'],
              });
            }
          }
        }
      });

      return suggestions;
    },

    // Generate conflict resolution suggestions
    generateConflictResolutionSuggestions(surgeries) {
      const suggestions = [];

      // Find surgeries with conflicts
      const conflictedSurgeries = surgeries.filter(s => s.conflicts && s.conflicts.length > 0);

      conflictedSurgeries.forEach(surgery => {
        surgery.conflicts.forEach(conflict => {
          if (conflict.includes('SDST Violation')) {
            suggestions.push({
              id: `conflict-${Date.now()}-${surgery.id}`,
              type: 'reschedule',
              category: 'Conflict Resolution',
              priority: 'High',
              title: `Resolve SDST conflict for ${surgery.type} surgery`,
              description: `Reschedule ${surgery.patientName}'s surgery to allow adequate setup time`,
              impact: 25,
              effort: 'High',
              surgeryIds: [surgery.id],
              conflictType: 'SDST Violation',
              estimatedSavings: 'Eliminates scheduling conflict',
              risks: ['Patient notification required', 'Schedule disruption'],
            });
          }
        });
      });

      return suggestions;
    },

    // Generate schedule balancing suggestions
    generateScheduleBalancingSuggestions(surgeries) {
      const suggestions = [];

      // Analyze daily workload distribution
      const dailyWorkload = {};
      surgeries.forEach(surgery => {
        const date = surgery.startTime.split('T')[0];
        if (!dailyWorkload[date]) dailyWorkload[date] = { count: 0, duration: 0 };
        dailyWorkload[date].count++;
        dailyWorkload[date].duration += surgery.duration;
      });

      // Find imbalanced days
      const avgWorkload = Object.values(dailyWorkload).reduce((sum, day) => sum + day.duration, 0) / Object.keys(dailyWorkload).length;

      Object.entries(dailyWorkload).forEach(([date, workload]) => {
        if (workload.duration > avgWorkload * 1.3) {
          suggestions.push({
            id: `balance-${Date.now()}-${date}`,
            type: 'redistribute',
            category: 'Schedule Balancing',
            priority: 'Medium',
            title: `Redistribute workload for ${date}`,
            description: `Move non-urgent surgeries from overloaded day to balance schedule`,
            impact: 20,
            effort: 'Medium',
            targetDate: date,
            estimatedSavings: 'Better workload distribution',
            risks: ['Requires patient coordination'],
          });
        }
      });

      return suggestions;
    },

    // Helper method to get SDST between surgery types
    getSDSTBetweenTypes(fromType, toType) {
      // This would normally come from the SDST matrix
      const sdstMatrix = {
        'APPEN->KNEE': 15,
        'KNEE->HIPRE': 15,
        'CABG->APPEN': 45,
        'CABG->CATAR': 45,
        'HIPRE->CABG': 45,
        'CATAR->HIPRE': 30,
        // Add more transitions as needed
      };

      const key = `${fromType}->${toType}`;
      return sdstMatrix[key] || 25; // Default SDST
    },

    // Analyze resource usage
    analyzeResourceUsage(surgeries) {
      const orUtilization = {};
      const staffUtilization = {};
      const equipmentUtilization = {};

      // Calculate OR utilization (simplified)
      surgeries.forEach(surgery => {
        if (!orUtilization[surgery.orId]) orUtilization[surgery.orId] = 0;
        orUtilization[surgery.orId] += surgery.duration / (8 * 60); // Assuming 8-hour days
      });

      return {
        orUtilization,
        staffUtilization,
        equipmentUtilization,
      };
    },

    // Calculate optimization metrics
    calculateOptimizationMetrics(originalSurgeries, suggestions) {
      const sdstReduction = suggestions
        .filter(s => s.category === 'SDST Optimization')
        .reduce((sum, s) => sum + s.impact, 0);

      const conflictReduction = suggestions
        .filter(s => s.category === 'Conflict Resolution')
        .length;

      const utilizationImprovement = suggestions
        .filter(s => s.category === 'Resource Optimization')
        .length * 5; // Simplified calculation

      return {
        sdstReduction,
        utilizationImprovement,
        conflictReduction,
        timesSaved: sdstReduction + utilizationImprovement,
        overallImpact: sdstReduction > 60 ? 'High' : sdstReduction > 30 ? 'Medium' : 'Low',
      };
    },

    // Apply selected suggestions
    async applySuggestions(suggestionIds) {
      const scheduleStore = useScheduleStore();
      const applicableSuggestions = this.currentSuggestions.filter(s =>
        suggestionIds.includes(s.id)
      );

      for (const suggestion of applicableSuggestions) {
        try {
          await this.applySingleSuggestion(suggestion);
          this.optimizationMetrics.suggestionsApplied++;
        } catch (error) {
          console.error('Failed to apply suggestion:', suggestion.id, error);
        }
      }

      // Update optimization history
      const historyEntry = this.optimizationHistory[0];
      if (historyEntry) {
        historyEntry.applied = true;
        historyEntry.appliedCount = suggestionIds.length;
      }

      // Recalculate metrics
      await this.updateOptimizationMetrics();
    },

    // Apply a single suggestion
    async applySingleSuggestion(suggestion) {
      const scheduleStore = useScheduleStore();

      switch (suggestion.type) {
        case 'reorder':
          await this.applySurgeryReorder(suggestion);
          break;
        case 'relocate':
          await this.applySurgeryRelocation(suggestion);
          break;
        case 'reschedule':
          await this.applySurgeryReschedule(suggestion);
          break;
        default:
          console.warn('Unknown suggestion type:', suggestion.type);
      }
    },

    // Apply surgery reorder
    async applySurgeryReorder(suggestion) {
      const scheduleStore = useScheduleStore();
      const [firstId, secondId] = suggestion.suggestedOrder;

      // Get the surgeries
      const firstSurgery = scheduleStore.scheduledSurgeries.find(s => s.id === firstId);
      const secondSurgery = scheduleStore.scheduledSurgeries.find(s => s.id === secondId);

      if (firstSurgery && secondSurgery) {
        // Swap their start times
        const tempStartTime = firstSurgery.startTime;
        firstSurgery.startTime = secondSurgery.startTime;
        secondSurgery.startTime = tempStartTime;

        // Update end times
        firstSurgery.endTime = new Date(new Date(firstSurgery.startTime).getTime() + firstSurgery.duration * 60000).toISOString();
        secondSurgery.endTime = new Date(new Date(secondSurgery.startTime).getTime() + secondSurgery.duration * 60000).toISOString();

        console.log('Applied surgery reorder:', suggestion.title);
      }
    },

    // Apply surgery relocation
    async applySurgeryRelocation(suggestion) {
      const scheduleStore = useScheduleStore();
      const surgery = scheduleStore.scheduledSurgeries.find(s => s.id === suggestion.surgeryIds[0]);

      if (surgery) {
        surgery.orId = suggestion.toOR;
        surgery.orName = `Operating Room ${suggestion.toOR.replace('OR', '')}`;
        console.log('Applied surgery relocation:', suggestion.title);
      }
    },

    // Apply surgery reschedule
    async applySurgeryReschedule(suggestion) {
      // This would involve more complex logic to find a new time slot
      console.log('Surgery reschedule would be applied:', suggestion.title);
    },

    // Update optimization metrics
    async updateOptimizationMetrics() {
      // Recalculate average improvements
      const history = this.optimizationHistory.filter(h => h.applied);
      if (history.length > 0) {
        this.optimizationMetrics.averageSDSTImprovement =
          history.reduce((sum, h) => sum + h.potentialSavings, 0) / history.length;
      }
    },

    // Clear optimization results
    clearOptimizationResults() {
      this.optimizationResults = null;
      this.selectedSuggestions = [];
    },

    // Update optimization settings
    updateOptimizationSettings(newSettings) {
      this.optimizationSettings = { ...this.optimizationSettings, ...newSettings };
    },

    // Toggle suggestion selection
    toggleSuggestionSelection(suggestionId) {
      const index = this.selectedSuggestions.indexOf(suggestionId);
      if (index > -1) {
        this.selectedSuggestions.splice(index, 1);
      } else {
        this.selectedSuggestions.push(suggestionId);
      }
    },

    // Select all suggestions
    selectAllSuggestions() {
      this.selectedSuggestions = this.currentSuggestions.map(s => s.id);
    },

    // Clear all selections
    clearAllSelections() {
      this.selectedSuggestions = [];
    },
  },
});
