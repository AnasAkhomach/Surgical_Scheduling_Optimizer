import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import Dashboard from '../views/Dashboard.vue'
import Login from '../components/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/surgeries',
    name: 'Surgeries',
    component: () => import('../views/Surgeries.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/Schedule.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/operating-rooms',
    name: 'OperatingRooms',
    component: () => import('../views/OperatingRooms.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/surgeons',
    name: 'Surgeons',
    component: () => import('../views/Surgeons.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/staff',
    name: 'Staff',
    component: () => import('../views/Staff.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients',
    name: 'Patients',
    component: () => import('../views/Patients.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: () => import('../views/Appointments.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

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

export default router
