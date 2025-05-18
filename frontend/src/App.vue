<template>
  <div class="app-container">
    <Toast />
    <ConfirmDialog />

    <div v-if="isAuthenticated">
      <div class="hidden md:block">
        <Menubar :model="menuItems" class="mb-4">
          <template #end>
            <WebSocketIndicator />
            <NotificationCenter class="mr-2" />
            <Button label="Logout" icon="pi pi-power-off" @click="logout" class="p-button-text" />
          </template>
        </Menubar>
      </div>

      <div class="block md:hidden">
        <Toolbar class="mb-4">
          <template #start>
            <Button icon="pi pi-bars" @click="mobileSidebar = true" class="p-button-text" />
          </template>
          <template #center>
            <h1 class="text-xl font-bold">Surgery Scheduler</h1>
          </template>
          <template #end>
            <WebSocketIndicator />
            <NotificationCenter class="mr-2" />
            <Button icon="pi pi-power-off" @click="logout" class="p-button-text" />
          </template>
        </Toolbar>

        <Sidebar v-model:visible="mobileSidebar" :baseZIndex="1000" class="p-sidebar-md">
          <h2 class="text-xl font-bold mb-4">Menu</h2>
          <Menu :model="mobileMenuItems" />
          <template #footer>
            <Button label="Logout" icon="pi pi-power-off" @click="logout" class="p-button-text w-full" />
          </template>
        </Sidebar>
      </div>

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
import NotificationCenter from './components/NotificationCenter.vue'
import WebSocketIndicator from './components/WebSocketIndicator.vue'

export default {
  name: 'App',
  components: {
    Login,
    NotificationCenter,
    WebSocketIndicator
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const mobileSidebar = ref(false)

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
        items: [
          {
            label: 'Table View',
            icon: 'pi pi-fw pi-table',
            to: '/schedule'
          },
          {
            label: 'Gantt Chart',
            icon: 'pi pi-fw pi-chart-bar',
            to: '/schedule-gantt'
          },
          {
            label: 'Surgeon Availability',
            icon: 'pi pi-fw pi-user-plus',
            to: '/surgeon-availability'
          },
          {
            label: 'Room Availability',
            icon: 'pi pi-fw pi-building',
            to: '/room-availability'
          }
        ]
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
        label: 'Reports',
        icon: 'pi pi-fw pi-file-pdf',
        to: '/reports'
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

    // Convert menubar items to mobile menu format
    const mobileMenuItems = computed(() => {
      const items = [];

      // Process each top-level menu item
      menuItems.value.forEach(item => {
        if (item.visible !== undefined && !item.visible) {
          return;
        }

        if (item.items) {
          // For items with subitems, create a submenu
          const subItems = item.items.filter(subItem =>
            subItem.visible === undefined || subItem.visible
          ).map(subItem => ({
            label: subItem.label,
            icon: subItem.icon,
            command: () => {
              if (subItem.to) {
                router.push(subItem.to);
                mobileSidebar.value = false;
              }
            }
          }));

          if (subItems.length > 0) {
            items.push({
              label: item.label,
              icon: item.icon,
              items: subItems
            });
          }
        } else {
          // For items without subitems, create a direct link
          items.push({
            label: item.label,
            icon: item.icon,
            command: () => {
              if (item.to) {
                router.push(item.to);
                mobileSidebar.value = false;
              }
            }
          });
        }
      });

      return items;
    });

    return {
      isAuthenticated,
      menuItems,
      mobileMenuItems,
      mobileSidebar,
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
  padding: 1rem;
}

/* Responsive styles */
@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
  }
}

/* Touch-friendly styles */
@media (hover: none) {
  .p-button {
    min-height: 44px; /* Minimum touch target size */
  }

  .p-inputtext,
  .p-dropdown,
  .p-multiselect,
  .p-calendar {
    min-height: 44px; /* Minimum touch target size */
  }

  .p-checkbox .p-checkbox-box,
  .p-radiobutton .p-radiobutton-box {
    width: 24px;
    height: 24px;
  }
}
</style>
