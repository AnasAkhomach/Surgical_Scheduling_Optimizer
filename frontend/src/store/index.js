import { createStore } from 'vuex'
import auth from './modules/auth'
import surgeries from './modules/surgeries'
import operatingRooms from './modules/operatingRooms'
import surgeons from './modules/surgeons'
import patients from './modules/patients'
import staff from './modules/staff'
import appointments from './modules/appointments'
import schedule from './modules/schedule'
import users from './modules/users'
import notifications from './modules/notifications'

export default createStore({
  state: {
    loading: false,
    error: null,
    webSocketConnected: false
  },
  getters: {
    isLoading: state => state.loading,
    hasError: state => !!state.error,
    errorMessage: state => state.error,
    isWebSocketConnected: state => state.webSocketConnected
  },
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    },
    SET_WEBSOCKET_CONNECTED(state, connected) {
      state.webSocketConnected = connected
    }
  },
  actions: {
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    },
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    },
    setWebSocketConnected({ commit }, connected) {
      commit('SET_WEBSOCKET_CONNECTED', connected)
    }
  },
  modules: {
    auth,
    surgeries,
    operatingRooms,
    surgeons,
    patients,
    staff,
    appointments,
    schedule,
    users,
    notifications
  }
})
