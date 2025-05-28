import { createRouter, createWebHistory } from 'vue-router';
// import { ref } from 'vue'; // No longer needed as auth state is in Pinia store

import LoginScreen from '../components/LoginScreen.vue';
import AppLayout from '../components/AppLayout.vue';
import DashboardScreen from '../components/DashboardScreen.vue';
// Import other placeholder components
import SchedulingScreen from '../components/SchedulingScreen.vue';
import ResourceManagementScreen from '../components/ResourceManagementScreen.vue';
import SDSTManagementScreen from '../components/SDSTManagementScreen.vue';
import ReportingAnalyticsScreen from '../components/ReportingAnalyticsScreen.vue';
import AnalyticsDashboard from '../components/AnalyticsDashboard.vue';
import UtilizationReports from '../components/UtilizationReports.vue';
import SchedulingEfficiencyReports from '../components/SchedulingEfficiencyReports.vue';
import CustomReportBuilder from '../components/CustomReportBuilder.vue';
import NotificationsScreen from '../components/NotificationsScreen.vue';
import AdministrationScreen from '../components/AdministrationScreen.vue';
import MyProfileSettingsScreen from '../components/MyProfileSettingsScreen.vue';
import HelpDocumentationScreen from '../components/HelpDocumentationScreen.vue';
import NotFound from '../components/NotFound.vue';
import MobileTestComponent from '../components/MobileTestComponent.vue';

// Import the authentication store
import { useAuthStore } from '@/stores/authStore';

// Simple authentication state (for simulation) - REMOVED, using authStore instead
// const isAuthenticated = ref(false);

// Function to set authentication status - REMOVED, authStore handles this
// const setAuthenticated = (status) => {
//   isAuthenticated.value = status;
// };

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginScreen,
  },
  {
    path: '/', // Use a parent route for authenticated sections
    component: AppLayout, // Use the layout component
    meta: { requiresAuth: true }, // Apply auth guard to this parent route
    children: [
        {
            path: '/dashboard',
            name: 'Dashboard',
            component: DashboardScreen,
        },
        {
            path: '/scheduling',
            name: 'Scheduling',
            component: SchedulingScreen,
        },
        {
            path: '/master-schedule',
            name: 'MasterSchedule',
            component: () => import('../components/MasterScheduleScreen.vue'),
        },
        {
            path: '/resource-management',
            name: 'ResourceManagement',
            component: ResourceManagementScreen,
        },
        {
            path: '/sdst-data-management',
            name: 'SDSTDataManagement',
            component: SDSTManagementScreen,
        },
        {
            path: '/reporting-analytics',
            component: ReportingAnalyticsScreen,
            children: [
                {
                    path: '',
                    name: 'AnalyticsDashboard',
                    component: AnalyticsDashboard,
                },
                {
                    path: 'utilization',
                    name: 'UtilizationReports',
                    component: UtilizationReports,
                },
                {
                    path: 'efficiency',
                    name: 'SchedulingEfficiencyReports',
                    component: SchedulingEfficiencyReports,
                },
                {
                    path: 'custom',
                    name: 'CustomReportBuilder',
                    component: CustomReportBuilder,
                },
            ],
        },
        {
            path: '/notifications',
            name: 'Notifications',
            component: NotificationsScreen,
        },
        {
            path: '/administration',
            name: 'Administration',
            component: AdministrationScreen,
        },
        {
            path: '/patient-management',
            name: 'PatientManagement',
            component: () => import('../components/PatientManagementScreen.vue'),
        },
        {
            path: '/my-profile-settings',
            name: 'MyProfileSettings',
            component: MyProfileSettingsScreen,
        },
        {
            path: '/help-documentation',
            name: 'HelpDocumentation',
            component: HelpDocumentationScreen,
        },
        {
            path: '/optimization',
            name: 'OptimizationEngine',
            component: () => import('../components/OptimizationEngine.vue'),
        },
        {
            path: '/mobile-test',
            name: 'MobileTest',
            component: MobileTestComponent,
        },
         // Add a redirect for the base authenticated path if needed
        {
            path: '',
            redirect: '/dashboard' // Redirect / to /dashboard when authenticated
        }
    ]
  },
  // Add a catch-all route for 404s if needed
  {
    path: '/:pathMatch(.*)*', // Catch-all route
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  // Use the auth store to check authentication status
  const authStore = useAuthStore(); // Get store instance inside the guard

  if (requiresAuth && !authStore.isAuthenticated) {
    // User is not authenticated and route requires auth, redirect to login
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // If the user is authenticated and tries to go to login, redirect to dashboard
     next({ name: 'Dashboard' });
  }else {
    // Otherwise, allow navigation
    next();
  }
});

// export { setAuthenticated }; // REMOVED, authStore handles setting auth state

export default router;
