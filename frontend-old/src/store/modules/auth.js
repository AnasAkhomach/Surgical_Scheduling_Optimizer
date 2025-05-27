import axios from 'axios'
import jwtDecode from 'jwt-decode'
import router from '../../router'
import websocketService from '../../services/websocket.service'

const state = {
  token: localStorage.getItem('token') || null,
  user: null
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  isAdmin: state => state.user && state.user.role === 'admin',
  token: state => state.token
}

const actions = {
  async login({ commit, dispatch }, credentials) {
    try {
      dispatch('setLoading', true, { root: true })

      const response = await axios.post('/api/auth/token', new URLSearchParams({
        username: credentials.username,
        password: credentials.password
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const token = response.data.access_token

      // Store token in localStorage
      localStorage.setItem('token', token)

      // Set token in axios headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

      // Decode token to get user info
      const decodedToken = jwtDecode(token)

      // Get user details
      const userResponse = await axios.get('/api/users/me')

      commit('SET_AUTH', { token, user: userResponse.data })

      // Initialize WebSocket connection
      websocketService.init(process.env.VUE_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws', token)

      return true
    } catch (error) {
      dispatch('setError', error.response?.data?.detail || 'Login failed', { root: true })
      return false
    } finally {
      dispatch('setLoading', false, { root: true })
    }
  },

  async logout({ commit }) {
    // Remove token from localStorage
    localStorage.removeItem('token')

    // Remove token from axios headers
    delete axios.defaults.headers.common['Authorization']

    // Disconnect WebSocket
    websocketService.disconnect()

    // Clear auth state
    commit('CLEAR_AUTH')

    // Redirect to login page
    router.push('/login')
  },

  async checkAuth({ commit, dispatch }) {
    const token = localStorage.getItem('token')

    if (!token) {
      return false
    }

    try {
      // Set token in axios headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

      // Get user details
      const userResponse = await axios.get('/api/users/me')

      commit('SET_AUTH', { token, user: userResponse.data })

      // Initialize WebSocket connection
      websocketService.init(process.env.VUE_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws', token)

      return true
    } catch (error) {
      // Token is invalid or expired
      dispatch('logout')
      return false
    }
  }
}

const mutations = {
  SET_AUTH(state, { token, user }) {
    state.token = token
    state.user = user
  },
  CLEAR_AUTH(state) {
    state.token = null
    state.user = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
