<template>
  <div class="app-container">
    <Toast />
    <ConfirmDialog />
    
    <div v-if="isAuthenticated">
      <Menubar :model="menuItems" class="mb-4">
        <template #end>
          <Button label="Logout" icon="pi pi-power-off" @click="logout" class="p-button-text" />
        </template>
      </Menubar>
      
      <div class="main-content p-4">
        <router-view />
      </div>
    </div>
    
    <div v-else>
      <Login @login-success="onLoginSuccess" />
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import Login from './components/Login.vue'

export default {
  name: 'App',
  components: {
    Login
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    
    const menuItems = ref([
      {
        label: 'Dashboard',
        icon: 'pi pi-fw pi-home',
        to: '/'
      },
      {
        label: 'Surgeries',
        icon: 'pi pi-fw pi-calendar',
        to: '/surgeries'
      },
      {
        label: 'Schedule',
        icon: 'pi pi-fw pi-calendar-plus',
        to: '/schedule'
      },
      {
        label: 'Resources',
        icon: 'pi pi-fw pi-briefcase',
        items: [
          {
            label: 'Operating Rooms',
            icon: 'pi pi-fw pi-building',
            to: '/operating-rooms'
          },
          {
            label: 'Surgeons',
            icon: 'pi pi-fw pi-user-plus',
            to: '/surgeons'
          },
          {
            label: 'Staff',
            icon: 'pi pi-fw pi-users',
            to: '/staff'
          }
        ]
      },
      {
        label: 'Patients',
        icon: 'pi pi-fw pi-user',
        to: '/patients'
      },
      {
        label: 'Appointments',
        icon: 'pi pi-fw pi-calendar-times',
        to: '/appointments'
      },
      {
        label: 'Admin',
        icon: 'pi pi-fw pi-cog',
        visible: computed(() => store.getters['auth/isAdmin']),
        items: [
          {
            label: 'Users',
            icon: 'pi pi-fw pi-user-edit',
            to: '/users'
          },
          {
            label: 'Settings',
            icon: 'pi pi-fw pi-sliders-h',
            to: '/settings'
          }
        ]
      }
    ])
    
    const logout = () => {
      store.dispatch('auth/logout')
      router.push('/login')
    }
    
    const onLoginSuccess = () => {
      router.push('/')
    }
    
    return {
      isAuthenticated,
      menuItems,
      logout,
      onLoginSuccess
    }
  }
}
</script>

<style>
.app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
