import { createRouter, createWebHistory } from 'vue-router'
import { createStore } from 'vuex'
import routes from '@/router/index'

describe('Router', () => {
  let router
  let store

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
            isAdmin: state => state.user && state.user.role === 'admin'
          }
        }
      }
    })

    // Create a fresh router before each test
    router = createRouter({
      history: createWebHistory(),
      routes
    })

    // Add navigation guards
    router.beforeEach((to, from, next) => {
      const isAuthenticated = store.getters['auth/isAuthenticated']
      const isAdmin = store.getters['auth/isAdmin']
      
      if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!isAuthenticated) {
          next({ name: 'Login' })
        } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
          next({ name: 'Dashboard' })
        } else {
          next()
        }
      } else {
        next()
      }
    })
  })

  it('has a route for each view', () => {
    // Check that all expected routes are defined
    const routeNames = router.getRoutes().map(route => route.name)
    
    expect(routeNames).toContain('Dashboard')
    expect(routeNames).toContain('Login')
    expect(routeNames).toContain('Surgeries')
    expect(routeNames).toContain('Schedule')
    expect(routeNames).toContain('OperatingRooms')
    expect(routeNames).toContain('Surgeons')
    expect(routeNames).toContain('Staff')
    expect(routeNames).toContain('Patients')
    expect(routeNames).toContain('Appointments')
    expect(routeNames).toContain('Users')
    expect(routeNames).toContain('Settings')
  })

  it('redirects to login when accessing protected route without authentication', async () => {
    // Set up store with no authentication
    store.state.auth.token = null
    store.state.auth.user = null

    // Try to navigate to a protected route
    await router.push('/surgeries')
    
    // Should be redirected to login
    expect(router.currentRoute.value.name).toBe('Login')
  })

  it('allows access to protected route when authenticated', async () => {
    // Set up store with authentication
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }

    // Try to navigate to a protected route
    await router.push('/surgeries')
    
    // Should be allowed access
    expect(router.currentRoute.value.name).toBe('Surgeries')
  })

  it('redirects to dashboard when non-admin accesses admin route', async () => {
    // Set up store with non-admin authentication
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'user' }

    // Try to navigate to an admin route
    await router.push('/users')
    
    // Should be redirected to dashboard
    expect(router.currentRoute.value.name).toBe('Dashboard')
  })

  it('allows access to admin route when authenticated as admin', async () => {
    // Set up store with admin authentication
    store.state.auth.token = 'test-token'
    store.state.auth.user = { id: 1, username: 'testuser', role: 'admin' }

    // Try to navigate to an admin route
    await router.push('/users')
    
    // Should be allowed access
    expect(router.currentRoute.value.name).toBe('Users')
  })

  it('allows access to login route when not authenticated', async () => {
    // Set up store with no authentication
    store.state.auth.token = null
    store.state.auth.user = null

    // Try to navigate to login route
    await router.push('/login')
    
    // Should be allowed access
    expect(router.currentRoute.value.name).toBe('Login')
  })

  it('has correct meta flags for routes', () => {
    // Check that routes have correct meta flags
    const dashboardRoute = router.getRoutes().find(route => route.name === 'Dashboard')
    expect(dashboardRoute.meta.requiresAuth).toBe(true)
    
    const loginRoute = router.getRoutes().find(route => route.name === 'Login')
    expect(loginRoute.meta.requiresAuth).toBeFalsy()
    
    const usersRoute = router.getRoutes().find(route => route.name === 'Users')
    expect(usersRoute.meta.requiresAuth).toBe(true)
    expect(usersRoute.meta.requiresAdmin).toBe(true)
  })
})
