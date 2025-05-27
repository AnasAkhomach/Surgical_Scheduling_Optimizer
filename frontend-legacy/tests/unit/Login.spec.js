import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import Login from '@/components/Login.vue'

// Mock PrimeVue components
jest.mock('primevue/card', () => ({
  name: 'Card',
  render: h => h('div', { class: 'p-card' }, [
    h('div', { class: 'p-card-title' }, h('slot', { name: 'title' })),
    h('div', { class: 'p-card-content' }, h('slot', { name: 'content' }))
  ])
}))

jest.mock('primevue/inputtext', () => ({
  name: 'InputText',
  render: h => h('input', { class: 'p-inputtext' })
}))

jest.mock('primevue/button', () => ({
  name: 'Button',
  render: h => h('button', { class: 'p-button' })
}))

describe('Login.vue', () => {
  let store
  let wrapper

  beforeEach(() => {
    // Create a fresh store before each test
    store = createStore({
      state: {
        loading: false,
        error: null
      },
      getters: {
        isLoading: state => state.loading,
        errorMessage: state => state.error
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
      },
      modules: {
        auth: {
          namespaced: true,
          actions: {
            login: jest.fn()
          }
        }
      }
    })

    // Mount the component
    wrapper = mount(Login, {
      global: {
        plugins: [store],
        stubs: ['Card', 'InputText', 'Button']
      }
    })
  })

  it('renders the login form', () => {
    // Check that the component renders
    expect(wrapper.exists()).toBe(true)

    // Check that the form elements are present
    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('#username').exists()).toBe(true)
    expect(wrapper.find('#password').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('updates username and password on input', async () => {
    // Get the input elements
    const usernameInput = wrapper.find('#username')
    const passwordInput = wrapper.find('#password')

    // Set values
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password')

    // Check that the component data is updated
    expect(wrapper.vm.username).toBe('testuser')
    expect(wrapper.vm.password).toBe('password')
  })

  it('validates form on submit', async () => {
    // Submit the form without entering credentials
    await wrapper.find('form').trigger('submit')

    // Check that submitted flag is set
    expect(wrapper.vm.submitted).toBe(true)

    // Check that error messages are displayed
    expect(wrapper.find('#username-error').exists()).toBe(true)
    expect(wrapper.find('#password-error').exists()).toBe(true)

    // Check that login action was not dispatched
    expect(store.modules.auth.actions.login).not.toHaveBeenCalled()
  })

  it('dispatches login action on valid form submit', async () => {
    // Mock successful login
    store.modules.auth.actions.login.mockResolvedValue(true)

    // Set form values
    await wrapper.find('#username').setValue('testuser')
    await wrapper.find('#password').setValue('password')

    // Submit the form
    await wrapper.find('form').trigger('submit')

    // Check that login action was dispatched with correct credentials
    expect(store.modules.auth.actions.login).toHaveBeenCalledWith(
      expect.any(Object),
      {
        username: 'testuser',
        password: 'password'
      },
      undefined
    )
  })

  it('emits login-success event on successful login', async () => {
    // Mock successful login
    store.modules.auth.actions.login.mockResolvedValue(true)

    // Set form values
    await wrapper.find('#username').setValue('testuser')
    await wrapper.find('#password').setValue('password')

    // Submit the form
    await wrapper.find('form').trigger('submit')

    // Check that login-success event was emitted
    expect(wrapper.emitted('login-success')).toBeTruthy()
    expect(wrapper.emitted('login-success').length).toBe(1)
  })

  it('does not emit login-success event on failed login', async () => {
    // Mock failed login
    store.modules.auth.actions.login.mockResolvedValue(false)

    // Set form values
    await wrapper.find('#username').setValue('testuser')
    await wrapper.find('#password').setValue('wrong-password')

    // Submit the form
    await wrapper.find('form').trigger('submit')

    // Check that login-success event was not emitted
    expect(wrapper.emitted('login-success')).toBeFalsy()
  })

  it('displays error message on login failure', async () => {
    // Set error in store
    store.state.error = 'Invalid credentials'

    // Force re-render
    await wrapper.vm.$nextTick()

    // Check that error message is displayed
    expect(wrapper.find('.p-error').text()).toBe('Invalid credentials')
  })

  it('clears previous errors before login attempt', async () => {
    // Mock clearError action
    const clearErrorSpy = jest.spyOn(store, 'dispatch')

    // Set form values
    await wrapper.find('#username').setValue('testuser')
    await wrapper.find('#password').setValue('password')

    // Submit the form
    await wrapper.find('form').trigger('submit')

    // Check that clearError action was dispatched
    expect(clearErrorSpy).toHaveBeenCalledWith('clearError')
  })
})
