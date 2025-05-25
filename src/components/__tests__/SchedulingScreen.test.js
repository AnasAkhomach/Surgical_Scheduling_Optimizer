import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import SchedulingScreen from '../SchedulingScreen.vue';
import { createPinia, setActivePinia } from 'pinia';
import { ref } from 'vue';
import flushPromises from 'flush-promises';

// Mock DataTransfer for JSDOM environment
global.DataTransfer = class DataTransfer {
  constructor() {
    this.data = {};
    this.effectAllowed = 'all';
    this.dropEffect = 'none';
  }

  setData(format, data) {
    this.data[format] = data;
  }

  getData(format) {
    return this.data[format] || '';
  }

  setDragImage() {
    // Mock implementation
  }
};

// Mock the stores
const mockPendingSurgeries = ref([
  {
    id: 1,
    patientId: 'P12345',
    patientName: 'John Doe',
    type: 'CABG',
    fullType: 'Coronary Artery Bypass Graft',
    estimatedDuration: 120,
    priority: 'High',
    status: 'Pending',
    requiredSpecialty: 'Cardiology'
  },
  {
    id: 2,
    patientId: 'P67890',
    patientName: 'Jane Smith',
    type: 'KNEE',
    fullType: 'Knee Replacement',
    estimatedDuration: 90,
    priority: 'Medium',
    status: 'Pending',
    requiredSpecialty: 'Orthopedics'
  }
]);

vi.mock('@/stores/scheduleStore', () => ({
  useScheduleStore: () => ({
    pendingSurgeries: mockPendingSurgeries,
    scheduledSurgeries: ref([]),
    selectedSurgeryId: ref(null),
    isLoading: ref(false),
    loadInitialData: vi.fn()
  })
}));

vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: () => ({
    addNotification: vi.fn(),
    setToastRef: vi.fn()
  })
}));

// Mock child components
vi.mock('./GanttChart.vue', () => ({
  default: {
    name: 'GanttChart',
    template: '<div data-testid="gantt-chart">Gantt Chart</div>'
  }
}));

vi.mock('./ToastNotification.vue', () => ({
  default: {
    name: 'ToastNotification',
    template: '<div data-testid="toast-notification">Toast</div>'
  }
}));

vi.mock('./KeyboardShortcutsHelp.vue', () => ({
  default: {
    name: 'KeyboardShortcutsHelp',
    template: '<div data-testid="keyboard-shortcuts">Shortcuts</div>'
  }
}));

vi.mock('@/services/keyboardShortcuts', () => ({
  default: {
    init: vi.fn(),
    destroy: vi.fn(),
    register: vi.fn(() => vi.fn()) // Returns an unregister function
  }
}));

// Mock the router
// Remove the mock for SchedulingScreen.vue
// vi.mock('../SchedulingScreen.vue', () => ({...

describe('SchedulingScreen.vue', () => {
  let wrapper;
  let pinia;

  beforeEach(async () => {
    // Create a fresh Pinia instance for each test
    pinia = createPinia();
    setActivePinia(pinia);

    wrapper = mount(SchedulingScreen, {
      global: {
        plugins: [pinia]
      }
    });

    await flushPromises();
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders the main scheduling container', () => {
    expect(wrapper.find('.scheduling-container').exists()).toBe(true);
  });

  it('displays the main title "Surgery Scheduling"', () => {
    expect(wrapper.find('h1').text()).toBe('Surgery Scheduling');
  });

  it('renders all three panels: left, main, and right', () => {
    expect(wrapper.find('.left-panel').exists()).toBe(true);
    expect(wrapper.find('.main-panel').exists()).toBe(true);
    expect(wrapper.find('.right-panel').exists()).toBe(true);
  });

  it('displays pending surgeries in the left panel', async () => {
    await flushPromises();
    const pendingSurgeryItems = wrapper.findAll('.pending-surgery-item');
    expect(pendingSurgeryItems.length).toBe(2); // Based on our mock data

    // Check if the first surgery is displayed correctly
    const firstSurgery = pendingSurgeryItems[0];
    expect(firstSurgery.text()).toContain('P12345');
    expect(firstSurgery.text()).toContain('High');
    expect(firstSurgery.text()).toContain('CABG');
    expect(firstSurgery.text()).toContain('120');
  });

  it('renders filter controls', () => {
    expect(wrapper.find('#filter-priority').exists()).toBe(true);
    expect(wrapper.find('#filter-specialty').exists()).toBe(true);
    expect(wrapper.find('#filter-status').exists()).toBe(true);
  });

  it('filters pending surgeries by priority', async () => {
    // Select 'High' priority filter
    await wrapper.find('#filter-priority').setValue('High');
    await wrapper.vm.$nextTick();

    // Should only show surgeries with 'High' priority
    const filteredItems = wrapper.findAll('.pending-surgery-item');
    expect(filteredItems.length).toBe(1);
    expect(filteredItems[0].text()).toContain('High');
  });

  it('shows advanced filters when toggle is clicked', async () => {
    // Initially advanced filters should not be visible
    expect(wrapper.find('#filter-surgeon').exists()).toBe(false);

    // Click the show advanced button
    const advancedToggle = wrapper.find('button').element.textContent.includes('Show Advanced');
    const toggleButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Show Advanced')
    );

    if (toggleButton) {
      await toggleButton.trigger('click');
      await wrapper.vm.$nextTick();

      // Advanced filters should now be visible
      expect(wrapper.find('#filter-surgeon').exists()).toBe(true);
      expect(wrapper.find('#filter-equipment').exists()).toBe(true);
    }
  });

  it('selects a surgery for viewing details when clicked', async () => {
    const pendingSurgeryItems = wrapper.findAll('.pending-surgery-item');
    expect(pendingSurgeryItems.length).toBeGreaterThan(0);

    // Click on the first surgery item
    await pendingSurgeryItems[0].trigger('click');
    await wrapper.vm.$nextTick();

    // Check if the right panel shows surgery details
    const rightPanel = wrapper.find('.right-panel');
    expect(rightPanel.exists()).toBe(true);
    expect(rightPanel.text()).toContain('Surgery Details');
  });

  it('renders gantt chart area', () => {
    expect(wrapper.find('#gantt-chart-container').exists()).toBe(true);
    expect(wrapper.find('.gantt-chart-container').exists()).toBe(true);
  });

  it('renders schedule controls', () => {
    expect(wrapper.find('.schedule-controls').exists()).toBe(true);
    expect(wrapper.text()).toContain('Previous');
    expect(wrapper.text()).toContain('Next');
    expect(wrapper.text()).toContain('Day View');
    expect(wrapper.text()).toContain('Week View');
    expect(wrapper.text()).toContain('Create New Surgery');
  });

  it('renders sort controls', () => {
    expect(wrapper.find('.sort-controls').exists()).toBe(true);
    const sortSelect = wrapper.find('.sort-controls select');
    expect(sortSelect.exists()).toBe(true);

    // Check sort options
    expect(wrapper.text()).toContain('Priority');
    expect(wrapper.text()).toContain('Patient Name');
    expect(wrapper.text()).toContain('Surgery Type');
    expect(wrapper.text()).toContain('Duration');
  });

  it('renders create new surgery button', () => {
    const createButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Create New Surgery')
    );
    expect(createButton.exists()).toBe(true);
  });

  it('renders surgery form fields in right panel', () => {
    expect(wrapper.text()).toContain('Patient ID');
    expect(wrapper.text()).toContain('Patient Name');
    expect(wrapper.text()).toContain('Surgery Type');
    expect(wrapper.text()).toContain('Estimated Duration');
    expect(wrapper.text()).toContain('Priority Level');
  });

  it('renders draggable pending surgery items', () => {
    const pendingSurgeryItems = wrapper.findAll('.pending-surgery-item');
    expect(pendingSurgeryItems.length).toBeGreaterThan(0);

    // Check that items are draggable
    pendingSurgeryItems.forEach(item => {
      expect(item.attributes('draggable')).toBe('true');
    });
  });

  it('renders gantt chart drop area', () => {
    const ganttContainer = wrapper.find('#gantt-chart-container');
    expect(ganttContainer.exists()).toBe(true);
    expect(ganttContainer.attributes('data-drop-message')).toBeDefined();
  });

  it('shows placeholder text when Gantt chart is not initialized', () => {
    const placeholderText = wrapper.find('.gantt-placeholder-text');
    expect(placeholderText.exists()).toBe(true);
    expect(placeholderText.text()).toContain('Gantt Chart Area');
  });

  it('renders child components', () => {
    // Check for component instances since they use Teleport
    expect(wrapper.findComponent({ name: 'ToastNotification' }).exists()).toBe(true);
    expect(wrapper.findComponent({ name: 'KeyboardShortcutsHelp' }).exists()).toBe(true);
  });

  it('renders surgery action buttons', () => {
    const pendingSurgeryItems = wrapper.findAll('.pending-surgery-item');
    if (pendingSurgeryItems.length > 0) {
      const firstItem = pendingSurgeryItems[0];
      expect(firstItem.text()).toContain('View');
      expect(firstItem.text()).toContain('Schedule');
    }
  });

  it('renders SDST information panel', () => {
    expect(wrapper.text()).toContain('SDST (Setup, Disinfection, Sterilization Time)');
    expect(wrapper.text()).toContain('Resource Conflicts');
  });
});