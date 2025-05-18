import { createStore } from 'vuex'
import storeConfig from '@/store/index'

describe('Vuex Store', () => {
  let store

  beforeEach(() => {
    // Create a fresh store before each test
    store = createStore(storeConfig)
  })

  it('has the expected modules', () => {
    // Check that all expected modules are registered
    expect(store.state.auth).toBeDefined()
    expect(store.state.surgeries).toBeDefined()
    expect(store.state.operatingRooms).toBeDefined()
    expect(store.state.surgeons).toBeDefined()
    expect(store.state.patients).toBeDefined()
    expect(store.state.staff).toBeDefined()
    expect(store.state.appointments).toBeDefined()
    expect(store.state.schedule).toBeDefined()
    expect(store.state.users).toBeDefined()
  })

  it('has the expected root state', () => {
    // Check that the root state has the expected properties
    expect(store.state.loading).toBe(false)
    expect(store.state.error).toBeNull()
  })

  it('has the expected root getters', () => {
    // Check that the root getters return the expected values
    expect(store.getters.isLoading).toBe(false)
    expect(store.getters.hasError).toBe(false)
    expect(store.getters.errorMessage).toBeNull()
  })

  it('setLoading mutation updates loading state', () => {
    // Check that the setLoading mutation updates the loading state
    store.commit('SET_LOADING', true)
    expect(store.state.loading).toBe(true)
    expect(store.getters.isLoading).toBe(true)
    
    store.commit('SET_LOADING', false)
    expect(store.state.loading).toBe(false)
    expect(store.getters.isLoading).toBe(false)
  })

  it('setError mutation updates error state', () => {
    // Check that the setError mutation updates the error state
    const error = 'Test error'
    store.commit('SET_ERROR', error)
    expect(store.state.error).toBe(error)
    expect(store.getters.hasError).toBe(true)
    expect(store.getters.errorMessage).toBe(error)
  })

  it('clearError mutation clears error state', () => {
    // Set an error first
    store.commit('SET_ERROR', 'Test error')
    
    // Check that the clearError mutation clears the error state
    store.commit('CLEAR_ERROR')
    expect(store.state.error).toBeNull()
    expect(store.getters.hasError).toBe(false)
    expect(store.getters.errorMessage).toBeNull()
  })

  it('setLoading action commits SET_LOADING mutation', () => {
    // Mock commit
    const commit = jest.fn()
    
    // Call setLoading action
    storeConfig.actions.setLoading({ commit }, true)
    
    // Check that commit was called with the right arguments
    expect(commit).toHaveBeenCalledWith('SET_LOADING', true)
  })

  it('setError action commits SET_ERROR mutation', () => {
    // Mock commit
    const commit = jest.fn()
    
    // Call setError action
    const error = 'Test error'
    storeConfig.actions.setError({ commit }, error)
    
    // Check that commit was called with the right arguments
    expect(commit).toHaveBeenCalledWith('SET_ERROR', error)
  })

  it('clearError action commits CLEAR_ERROR mutation', () => {
    // Mock commit
    const commit = jest.fn()
    
    // Call clearError action
    storeConfig.actions.clearError({ commit })
    
    // Check that commit was called with the right arguments
    expect(commit).toHaveBeenCalledWith('CLEAR_ERROR')
  })
})
