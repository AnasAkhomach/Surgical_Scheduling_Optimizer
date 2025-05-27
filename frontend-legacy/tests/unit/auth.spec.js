import { createStore } from 'vuex'
import auth from '@/store/modules/auth'
import axios from 'axios'
import jwtDecode from 'jwt-decode'

// Mock axios
jest.mock('axios')

// Mock jwt-decode
jest.mock('jwt-decode', () => jest.fn())

describe('Auth Store Module', () => {
  let store

  beforeEach(() => {
    // Create a fresh store before each test
    store = createStore({
      modules: {
        auth: {
          ...auth,
          namespaced: true
        }
      },
      state: {
        loading: false,
        error: null
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
        }
      }
    })

    // Clear all mocks
    jest.clearAllMocks()
  })

  describe('getters', () => {
    it('isAuthenticated returns true when token exists', () => {
      store.replaceState({
        auth: {
          token: 'test-token',
          user: null
        },
        loading: false,
        error: null
      })

      expect(store.getters['auth/isAuthenticated']).toBe(true)
    })

    it('isAuthenticated returns false when token does not exist', () => {
      store.replaceState({
        auth: {
          token: null,
          user: null
        },
        loading: false,
        error: null
      })

      expect(store.getters['auth/isAuthenticated']).toBe(false)
    })

    it('currentUser returns the user object', () => {
      const user = { id: 1, username: 'testuser' }
      store.replaceState({
        auth: {
          token: 'test-token',
          user
        },
        loading: false,
        error: null
      })

      expect(store.getters['auth/currentUser']).toEqual(user)
    })

    it('isAdmin returns true when user role is admin', () => {
      store.replaceState({
        auth: {
          token: 'test-token',
          user: { id: 1, username: 'testuser', role: 'admin' }
        },
        loading: false,
        error: null
      })

      expect(store.getters['auth/isAdmin']).toBe(true)
    })

    it('isAdmin returns false when user role is not admin', () => {
      store.replaceState({
        auth: {
          token: 'test-token',
          user: { id: 1, username: 'testuser', role: 'user' }
        },
        loading: false,
        error: null
      })

      expect(store.getters['auth/isAdmin']).toBe(false)
    })

    it('isAdmin returns false when user is null', () => {
      store.replaceState({
        auth: {
          token: 'test-token',
          user: null
        },
        loading: false,
        error: null
      })

      expect(store.getters['auth/isAdmin']).toBe(false)
    })
  })

  describe('actions', () => {
    it('login action sets auth state on successful login', async () => {
      // Mock successful login response
      const token = 'test-token'
      const user = { id: 1, username: 'testuser', role: 'admin' }
      
      axios.post.mockResolvedValueOnce({ data: { access_token: token } })
      axios.get.mockResolvedValueOnce({ data: user })
      jwtDecode.mockReturnValueOnce({ sub: 'testuser', role: 'admin' })

      // Call login action
      const result = await store.dispatch('auth/login', {
        username: 'testuser',
        password: 'password'
      })

      // Verify axios was called with correct parameters
      expect(axios.post).toHaveBeenCalledWith(
        '/api/auth/token',
        expect.any(URLSearchParams),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/x-www-form-urlencoded'
          })
        })
      )

      // Verify user details were fetched
      expect(axios.get).toHaveBeenCalledWith('/api/users/me')

      // Verify state was updated
      expect(store.state.auth.token).toBe(token)
      expect(store.state.auth.user).toEqual(user)

      // Verify action returned success
      expect(result).toBe(true)
    })

    it('login action handles login failure', async () => {
      // Mock failed login response
      const error = { response: { data: { detail: 'Invalid credentials' } } }
      axios.post.mockRejectedValueOnce(error)

      // Call login action
      const result = await store.dispatch('auth/login', {
        username: 'testuser',
        password: 'wrong-password'
      })

      // Verify error was set
      expect(store.state.error).toBe('Invalid credentials')

      // Verify state was not updated
      expect(store.state.auth.token).toBeNull()
      expect(store.state.auth.user).toBeNull()

      // Verify action returned failure
      expect(result).toBe(false)
    })

    it('logout action clears auth state', async () => {
      // Set initial state
      store.replaceState({
        auth: {
          token: 'test-token',
          user: { id: 1, username: 'testuser' }
        },
        loading: false,
        error: null
      })

      // Call logout action
      await store.dispatch('auth/logout')

      // Verify state was cleared
      expect(store.state.auth.token).toBeNull()
      expect(store.state.auth.user).toBeNull()
    })

    it('checkAuth action returns true when token is valid', async () => {
      // Set initial state with token
      localStorage.setItem('token', 'test-token')
      
      // Mock successful user fetch
      const user = { id: 1, username: 'testuser', role: 'admin' }
      axios.get.mockResolvedValueOnce({ data: user })

      // Call checkAuth action
      const result = await store.dispatch('auth/checkAuth')

      // Verify user details were fetched
      expect(axios.get).toHaveBeenCalledWith('/api/users/me')

      // Verify state was updated
      expect(store.state.auth.token).toBe('test-token')
      expect(store.state.auth.user).toEqual(user)

      // Verify action returned success
      expect(result).toBe(true)

      // Clean up
      localStorage.removeItem('token')
    })

    it('checkAuth action returns false when token is invalid', async () => {
      // Set initial state with token
      localStorage.setItem('token', 'invalid-token')
      
      // Mock failed user fetch
      axios.get.mockRejectedValueOnce(new Error('Invalid token'))

      // Call checkAuth action
      const result = await store.dispatch('auth/checkAuth')

      // Verify state was not updated
      expect(store.state.auth.token).toBeNull()
      expect(store.state.auth.user).toBeNull()

      // Verify action returned failure
      expect(result).toBe(false)

      // Clean up
      localStorage.removeItem('token')
    })

    it('checkAuth action returns false when no token exists', async () => {
      // Ensure no token in localStorage
      localStorage.removeItem('token')

      // Call checkAuth action
      const result = await store.dispatch('auth/checkAuth')

      // Verify axios was not called
      expect(axios.get).not.toHaveBeenCalled()

      // Verify state was not updated
      expect(store.state.auth.token).toBeNull()
      expect(store.state.auth.user).toBeNull()

      // Verify action returned failure
      expect(result).toBe(false)
    })
  })
})
