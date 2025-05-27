import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import { createRouter, createWebHistory } from 'vue-router'
import App from '@/App.vue'

// Mock child components
jest.mock('@/components/Login.vue', () => ({
  name: 'Login',
  render: h => h('div', { class: 'mock-login' })
}))

// Mock PrimeVue components
jest.mock('primevue/menubar', () => ({
  name: 'Menubar',
  render: h => h('div', { class: 'p-menubar' }, [
    h('slot'),
    h('slot', { name: 'end' })
  ])
}))

jest.mock('primevue/button', () => ({
  name: 'Button',
  render: h => h('button', { class: 'p-button' })
}))

jest.mock('primevue/toast', () => ({
  name: 'Toast',
  render: h => h('div', { class: 'p-toast' })
}))

jest.mock('primevue/confirmdialog', () => ({
  name: 'ConfirmDialog',
  render: h => h('div', { class: 'p-confirmdialog' })
}))

describe('App.vue', () => {
  let store
  let router
  let wrapper

  beforeEach(() => {
    // Create a fresh store before each test
    store = createStore({
      modules: {
        auth: {
          namespaced: true,
          state: {
            token: null,
            user: null
          },
          getters: {
            isAuthenticated: state => !!state.token,
            isAdmin: state => state.user && state.user.role === 'admin',
            currentUser: state => state.user
          },
          actions: {
            logout: jest.fn()
          }
        }
      }
    })

    // Create a fresh router before each test
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { render: h => h('div') } },
        { path: '/login', name: 'Login', component: { render: h => h('div') } }
      ]
    })

    // Mount the component
    wrapper = mount(App, {
      global: {
        plugins: [store, router],
        stubs: ['router-view', 'Toast', 'ConfirmDialog', 'Menubar', 'Button', 'Login']
      }
    })
  })

  it('renders the app container', () => {
    // Check that the component renders
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.app-container').exists()).toBe(true)
  })

  it('renders Toast and ConfirmDialog components', () => {
    // Check that the Toast and ConfirmDialog components are rendered
    expect(wrapper.find('.p-toast').exists()).toBe(true)
    expect(wrapper.find('.p-confirmdialog').exists()).toBe(true)
  })

  it('renders Login component when not authenticated', () => {
    // Check that the Login component is rendered when not authenticated
    expect(wrapper.find('.mock-login').exists()).toBe(true)
    expect(wrapper.find('.p-menubar').exists()).toBe(false)
  })

  it('renders Menubar and main content when authenticated', async () => {
    // Set authenticated state
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }
    
    // Force re-render
    await wrapper.vm.$nextTick()
    
    // Check that the Menubar and main content are rendered
    expect(wrapper.find('.p-menubar').exists()).toBe(true)
    expect(wrapper.find('.main-content').exists()).toBe(true)
    expect(wrapper.find('.mock-login').exists()).toBe(false)
  })

  it('has logout button when authenticated', async () => {
    // Set authenticated state
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }
    
    // Force re-render
    await wrapper.vm.$nextTick()
    
    // Check that the logout button is rendered
    const logoutButton = wrapper.find('.p-button')
    expect(logoutButton.exists()).toBe(true)
    expect(logoutButton.text()).toContain('Logout')
  })

  it('calls logout action when logout button is clicked', async () => {
    // Set authenticated state
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }
    
    // Force re-render
    await wrapper.vm.$nextTick()
    
    // Find and click the logout button
    const logoutButton = wrapper.find('.p-button')
    await logoutButton.trigger('click')
    
    // Check that the logout action was dispatched
    expect(store.modules.auth.actions.logout).toHaveBeenCalled()
  })

  it('navigates to login page after logout', async () => {
    // Set authenticated state
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }
    
    // Mock router.push
    const routerPushSpy = jest.spyOn(router, 'push')
    
    // Force re-render
    await wrapper.vm.$nextTick()
    
    // Call logout method directly
    await wrapper.vm.logout()
    
    // Check that router.push was called with the login route
    expect(routerPushSpy).toHaveBeenCalledWith('/login')
  })

  it('handles login success event', async () => {
    // Mock router.push
    const routerPushSpy = jest.spyOn(router, 'push')
    
    // Trigger login-success event
    wrapper.findComponent({ name: 'Login' }).vm.$emit('login-success')
    
    // Check that router.push was called with the dashboard route
    expect(routerPushSpy).toHaveBeenCalledWith('/')
  })

  it('has the expected menu items', async () => {
    // Set authenticated state
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }
    
    // Force re-render
    await wrapper.vm.$nextTick()
    
    // Check that the menu items are defined
    const menuItems = wrapper.vm.menuItems
    
    // Check that the dashboard menu item is defined
    const dashboardItem = menuItems.find(item => item.label === 'Dashboard')
    expect(dashboardItem).toBeDefined()
    expect(dashboardItem.icon).toBe('pi pi-fw pi-home')
    expect(dashboardItem.to).toBe('/')
    
    // Check that the surgeries menu item is defined
    const surgeriesItem = menuItems.find(item => item.label === 'Surgeries')
    expect(surgeriesItem).toBeDefined()
    expect(surgeriesItem.icon).toBe('pi pi-fw pi-calendar')
    expect(surgeriesItem.to).toBe('/surgeries')
    
    // Check that the admin menu item is defined
    const adminItem = menuItems.find(item => item.label === 'Admin')
    expect(adminItem).toBeDefined()
    expect(adminItem.icon).toBe('pi pi-fw pi-cog')
    expect(adminItem.items).toBeDefined()
    expect(adminItem.items.length).toBe(2)
  })
})
