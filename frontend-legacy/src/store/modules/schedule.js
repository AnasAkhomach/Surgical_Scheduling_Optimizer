import axios from 'axios'

const state = {
  currentSchedule: [],
  optimizedSchedule: [],
  optimizationResult: null,
  loading: false,
  error: null
}

const getters = {
  currentSchedule: state => state.currentSchedule,
  optimizedSchedule: state => state.optimizedSchedule,
  optimizationResult: state => state.optimizationResult,
  isLoading: state => state.loading,
  hasError: state => !!state.error,
  errorMessage: state => state.error
}

const actions = {
  async fetchCurrentSchedule({ commit, dispatch }, date) {
    try {
      commit('SET_LOADING', true)
      
      // In a real application, this would be an API call
      // const response = await axios.get('/api/schedules/current', { params: { date } })
      
      // Mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockSchedule = [
        { surgery_id: 101, room_id: 1, room: 'OR-1', surgeon_id: 1, surgeon: 'Dr. Smith', surgery_type_id: 1, surgery_type: 'Appendectomy', start_time: '2023-05-18T08:00:00', end_time: '2023-05-18T09:30:00', duration_minutes: 90 },
        { surgery_id: 102, room_id: 2, room: 'OR-2', surgeon_id: 2, surgeon: 'Dr. Johnson', surgery_type_id: 2, surgery_type: 'Hernia Repair', start_time: '2023-05-18T09:45:00', end_time: '2023-05-18T11:15:00', duration_minutes: 90 },
        { surgery_id: 103, room_id: 3, room: 'OR-3', surgeon_id: 3, surgeon: 'Dr. Williams', surgery_type_id: 3, surgery_type: 'Gallbladder Removal', start_time: '2023-05-18T10:00:00', end_time: '2023-05-18T12:30:00', duration_minutes: 150 },
        { surgery_id: 104, room_id: 1, room: 'OR-1', surgeon_id: 4, surgeon: 'Dr. Brown', surgery_type_id: 4, surgery_type: 'Hip Replacement', start_time: '2023-05-18T13:00:00', end_time: '2023-05-18T15:00:00', duration_minutes: 120 },
        { surgery_id: 105, room_id: 4, room: 'OR-4', surgeon_id: 5, surgeon: 'Dr. Davis', surgery_type_id: 5, surgery_type: 'Cataract Surgery', start_time: '2023-05-18T14:30:00', end_time: '2023-05-18T16:00:00', duration_minutes: 90 }
      ]
      
      commit('SET_CURRENT_SCHEDULE', mockSchedule)
      return mockSchedule
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch schedule')
      return []
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async optimizeSchedule({ commit, dispatch }, params) {
    try {
      commit('SET_LOADING', true)
      
      // In a real application, this would be an API call
      // const response = await axios.post('/api/schedules/optimize', params)
      
      // Mock response for demonstration
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const mockResponse = {
        assignments: [
          { surgery_id: 101, room_id: 2, room: 'OR-2', surgeon_id: 1, surgeon: 'Dr. Smith', surgery_type_id: 1, surgery_type: 'Appendectomy', start_time: '2023-05-18T08:00:00', end_time: '2023-05-18T09:30:00', duration_minutes: 90 },
          { surgery_id: 104, room_id: 1, room: 'OR-1', surgeon_id: 4, surgeon: 'Dr. Brown', surgery_type_id: 4, surgery_type: 'Hip Replacement', start_time: '2023-05-18T08:00:00', end_time: '2023-05-18T10:00:00', duration_minutes: 120 },
          { surgery_id: 102, room_id: 3, room: 'OR-3', surgeon_id: 2, surgeon: 'Dr. Johnson', surgery_type_id: 2, surgery_type: 'Hernia Repair', start_time: '2023-05-18T09:45:00', end_time: '2023-05-18T11:15:00', duration_minutes: 90 },
          { surgery_id: 105, room_id: 2, room: 'OR-2', surgeon_id: 5, surgeon: 'Dr. Davis', surgery_type_id: 5, surgery_type: 'Cataract Surgery', start_time: '2023-05-18T10:15:00', end_time: '2023-05-18T11:45:00', duration_minutes: 90 },
          { surgery_id: 103, room_id: 1, room: 'OR-1', surgeon_id: 3, surgeon: 'Dr. Williams', surgery_type_id: 3, surgery_type: 'Gallbladder Removal', start_time: '2023-05-18T10:30:00', end_time: '2023-05-18T13:00:00', duration_minutes: 150 }
        ],
        score: 87.5,
        metrics: {
          or_utilization: 0.92,
          setup_times: 0.85,
          surgeon_preferences: 0.78,
          workload_balance: 0.88,
          patient_wait_time: 0.75,
          emergency_priority: 0.95,
          operational_costs: 0.82,
          staff_overtime: 0.90
        },
        iteration_count: 78,
        execution_time_seconds: 2.34
      }
      
      commit('SET_OPTIMIZED_SCHEDULE', mockResponse.assignments)
      commit('SET_OPTIMIZATION_RESULT', mockResponse)
      
      return mockResponse
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to optimize schedule')
      return null
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async applySchedule({ commit, dispatch }, assignments) {
    try {
      commit('SET_LOADING', true)
      
      // In a real application, this would be an API call
      // await axios.post('/api/schedules/apply', { assignments })
      
      // Mock response for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      commit('SET_CURRENT_SCHEDULE', assignments)
      commit('CLEAR_OPTIMIZED_SCHEDULE')
      
      return true
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to apply schedule')
      return false
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  clearOptimizedSchedule({ commit }) {
    commit('CLEAR_OPTIMIZED_SCHEDULE')
  }
}

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_CURRENT_SCHEDULE(state, schedule) {
    state.currentSchedule = schedule
  },
  SET_OPTIMIZED_SCHEDULE(state, schedule) {
    state.optimizedSchedule = schedule
  },
  SET_OPTIMIZATION_RESULT(state, result) {
    state.optimizationResult = result
  },
  CLEAR_OPTIMIZED_SCHEDULE(state) {
    state.optimizedSchedule = []
    state.optimizationResult = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
