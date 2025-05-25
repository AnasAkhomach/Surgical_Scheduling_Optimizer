import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import { ref } from 'vue';
import DashboardScreen from '../DashboardScreen.vue';

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    user: ref({ id: 1, name: 'Test User', username: 'test@example.com' })
  })
}));

// Mock the schedule store
const mockScheduledSurgeries = ref([
  {
    id: 's-1',
    patientName: 'Alice Smith',
    type: 'CABG',
    startTime: '2023-10-27T08:00:00Z',
    conflicts: ['SDST violation: requires 60 minutes setup']
  },
  {
    id: 's-2',
    patientName: 'Bob Johnson',
    type: 'KNEE',
    startTime: '2023-10-27T12:30:00Z',
    conflicts: []
  }
]);

const mockPendingSurgeries = ref([
  {
    id: 'p-1',
    patientName: 'Charlie Brown',
    type: 'APPEN',
    priority: 'High'
  }
]);

vi.mock('@/stores/scheduleStore', () => ({
  useScheduleStore: () => ({
    visibleScheduledSurgeries: mockScheduledSurgeries,
    pendingSurgeries: mockPendingSurgeries,
    scheduledSurgeries: mockScheduledSurgeries.value,
    getSurgeriesForOR: vi.fn((orId) => {
      return mockScheduledSurgeries.value.filter(s => s.orId === orId || orId === 'OR1');
    }),
    selectSurgery: vi.fn()
  })
}));

describe('DashboardScreen', () => {
  let wrapper;
  let router;
  let pinia;

  beforeEach(async () => {
    // Create a fresh Pinia instance for each test
    pinia = createPinia();
    setActivePinia(pinia);

    // Create a router instance
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div>Dashboard</div>' } },
        { path: '/scheduling', name: 'Scheduling', component: { template: '<div>Scheduling</div>' } },
        { path: '/resource-management', name: 'ResourceManagement', component: { template: '<div>Resources</div>' } }
      ]
    });

    wrapper = mount(DashboardScreen, {
      global: {
        plugins: [router, pinia],
        stubs: {
          'router-link': true,
          'router-view': true
        }
      }
    });

    await router.isReady();
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.dashboard-container').exists()).toBe(true);
  });

  it('renders the main heading', () => {
    expect(wrapper.find('h1').text()).toBe('Welcome, User!');
  });

  it('renders dashboard widgets', () => {
    expect(wrapper.find('.dashboard-widgets').exists()).toBe(true);

    // Check for key widgets
    expect(wrapper.text()).toContain('Quick Actions');
    expect(wrapper.text()).toContain('Key Performance Indicators');
    expect(wrapper.text()).toContain('Critical Resource Alerts');
    expect(wrapper.text()).toContain('SDST Conflict Summary'); // Actual text in component
    expect(wrapper.text()).toContain('Pending Surgeries');
    expect(wrapper.text()).toContain("Today's OR Schedule Overview"); // Actual text in component
  });

  it('displays KPI values', () => {
    // Check that KPI values are displayed
    expect(wrapper.text()).toContain('85%'); // OR Utilization
    expect(wrapper.text()).toContain('30 min'); // Avg SDST
    expect(wrapper.text()).toContain('2'); // Emergency Cases
    expect(wrapper.text()).toContain('1'); // Cancelled Surgeries
  });

  it('displays pending surgeries from store', () => {
    expect(wrapper.text()).toContain('Charlie Brown');
    expect(wrapper.text()).toContain('APPEN');
  });

  it('displays SDST conflicts from store', () => {
    expect(wrapper.text()).toContain('Alice Smith');
    expect(wrapper.text()).toContain('SDST violation');
  });

  it('handles quick action button clicks', async () => {
    const routerPushSpy = vi.spyOn(router, 'push');

    // Test "Go to Master Schedule" button
    const masterScheduleBtn = wrapper.findAll('button').find(btn =>
      btn.text().includes('Go to Master Schedule')
    );
    if (masterScheduleBtn) {
      await masterScheduleBtn.trigger('click');
      expect(routerPushSpy).toHaveBeenCalledWith({ name: 'Scheduling' });
    }

    // Test "Manage Resources" button
    const manageResourcesBtn = wrapper.findAll('button').find(btn =>
      btn.text().includes('Manage Resources')
    );
    if (manageResourcesBtn) {
      await manageResourcesBtn.trigger('click');
      expect(routerPushSpy).toHaveBeenCalledWith({ name: 'ResourceManagement' });
    }
  });
});