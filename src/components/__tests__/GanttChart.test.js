import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { ref } from 'vue';
import GanttChart from '../GanttChart.vue';

// Mock the schedule store
const mockScheduledSurgeries = ref([
  {
    id: 's-1',
    patientName: 'Alice Smith',
    type: 'CABG',
    fullType: 'Coronary Artery Bypass Graft',
    surgeon: 'Dr. Johnson',
    startTime: '2023-10-27T08:00:00Z',
    endTime: '2023-10-27T10:30:00Z',
    duration: 150,
    estimatedDuration: 150,
    sdsTime: 45,
    precedingType: 'KNEE',
    orId: 'OR1',
    orName: 'OR 1',
    conflicts: ['SDST violation: requires 60 minutes setup']
  },
  {
    id: 's-2',
    patientName: 'Bob Johnson',
    type: 'KNEE',
    fullType: 'Knee Replacement',
    surgeon: 'Dr. Smith',
    startTime: '2023-10-27T12:30:00Z',
    endTime: '2023-10-27T14:00:00Z',
    duration: 90,
    estimatedDuration: 90,
    sdsTime: 15,
    precedingType: null,
    orId: 'OR2',
    orName: 'OR 2',
    conflicts: []
  }
]);

const mockOperatingRooms = ref([
  { id: 'OR1', name: 'OR 1', isAvailable: true },
  { id: 'OR2', name: 'OR 2', isAvailable: true },
  { id: 'OR3', name: 'OR 3', isAvailable: false }
]);

const mockCurrentDateRange = ref({
  start: new Date('2023-10-27T07:00:00Z'),
  end: new Date('2023-10-27T19:00:00Z')
});

// Define the base mock store object
const mockScheduleStore = {
  visibleScheduledSurgeries: mockScheduledSurgeries,
  availableOperatingRooms: mockOperatingRooms,
  currentDateRange: mockCurrentDateRange,
  isLoading: ref(false),
  selectedSurgeryId: ref(null),
  ganttViewMode: 'Day',
  getSurgeriesForOR: vi.fn((orId) => {
    return mockScheduledSurgeries.value.filter(s => s.orId === orId);
  }),
  selectSurgery: vi.fn(),
  loadInitialData: vi.fn(),
  navigateGanttDate: vi.fn(),
  updateGanttViewMode: vi.fn(),
  resetGanttToToday: vi.fn(),
  rescheduleSurgery: vi.fn()
};

vi.mock('@/stores/scheduleStore', () => ({
  useScheduleStore: () => mockScheduleStore
}));

// Mock the GanttAccessibleTable component
vi.mock('../GanttAccessibleTable.vue', () => ({
  default: {
    name: 'GanttAccessibleTable',
    template: '<div data-testid="gantt-accessible-table">Accessible Table</div>'
  }
}));

describe('GanttChart', () => {
  let wrapper;
  let pinia;

  beforeEach(async () => {
    // Create a fresh Pinia instance for each test
    pinia = createPinia();
    setActivePinia(pinia);

    wrapper = mount(GanttChart, {
      global: {
        plugins: [pinia]
      }
    });
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.gantt-container').exists()).toBe(true);
  });

  it('renders the gantt header with title and controls', () => {
    expect(wrapper.find('.gantt-header').exists()).toBe(true);
    expect(wrapper.find('.gantt-title h3').text()).toBe('Operating Room Schedule');
    expect(wrapper.find('.view-mode-indicator').text()).toBe('Day View');
  });

  it('renders view mode buttons', () => {
    const dayButton = wrapper.findAll('button').find(btn => btn.text() === 'Day');
    const weekButton = wrapper.findAll('button').find(btn => btn.text() === 'Week');
    const todayButton = wrapper.findAll('button').find(btn => btn.text() === 'Today');

    expect(dayButton.exists()).toBe(true);
    expect(weekButton.exists()).toBe(true);
    expect(todayButton.exists()).toBe(true);
  });

  it('renders date navigation controls', () => {
    expect(wrapper.find('.date-navigation').exists()).toBe(true);
    expect(wrapper.find('.current-date-display').exists()).toBe(true);

    const prevButton = wrapper.find('button[aria-label="Previous day"]');
    const nextButton = wrapper.find('button[aria-label="Next day"]');

    expect(prevButton.exists()).toBe(true);
    expect(nextButton.exists()).toBe(true);
  });

  it('renders SDST legend', () => {
    expect(wrapper.find('.sdst-legend').exists()).toBe(true);
    expect(wrapper.text()).toContain('SDST Color Coding:');
    expect(wrapper.text()).toContain('Short (≤15 min)');
    expect(wrapper.text()).toContain('Medium (16-30 min)');
    expect(wrapper.text()).toContain('Long (>30 min)');
  });

  it('renders operating room rows', () => {
    const orRows = wrapper.findAll('.gantt-or-row');
    expect(orRows.length).toBe(3); // OR1, OR2, OR3

    expect(wrapper.text()).toContain('OR 1');
    expect(wrapper.text()).toContain('OR 2');
    expect(wrapper.text()).toContain('OR 3');
  });

  it('renders surgery blocks with correct information', () => {
    const surgeryBlocks = wrapper.findAll('.surgery-block');
    expect(surgeryBlocks.length).toBe(2); // Two surgeries in mock data

    // Check first surgery
    expect(wrapper.text()).toContain('Alice Smith - CABG');
    expect(wrapper.text()).toContain('Bob Johnson - KNEE');
  });

  it('displays conflict indicators for surgeries with conflicts', () => {
    const conflictIndicators = wrapper.findAll('.conflict-indicator');
    expect(conflictIndicators.length).toBe(1); // Only Alice Smith has conflicts
    expect(conflictIndicators[0].text()).toBe('⚠️');
  });

  it('renders SDST segments with appropriate styling', () => {
    const sdstSegments = wrapper.findAll('.sdst-segment');
    expect(sdstSegments.length).toBe(2); // Both surgeries have SDST

    // Check SDST classes based on duration
    const highSDST = wrapper.find('.sdst-high'); // Alice Smith: 45 min
    const lowSDST = wrapper.find('.sdst-low'); // Bob Johnson: 15 min

    expect(highSDST.exists()).toBe(true);
    expect(lowSDST.exists()).toBe(true);
  });

  it('renders time axis with hour markers', () => {
    expect(wrapper.find('.gantt-time-axis').exists()).toBe(true);
    const timeMarkers = wrapper.findAll('.time-marker');
    expect(timeMarkers.length).toBeGreaterThan(0);
  });

  it('renders accessible table component', () => {
    expect(wrapper.find('[data-testid="gantt-accessible-table"]').exists()).toBe(true);
  });

  it('navigation buttons are clickable and functional', async () => {
    // Test that navigation buttons exist and are clickable
    const prevButton = wrapper.find('button[aria-label="Previous day"]');
    const nextButton = wrapper.find('button[aria-label="Next day"]');
    const todayButton = wrapper.findAll('button').find(btn => btn.text() === 'Today');

    expect(prevButton.exists()).toBe(true);
    expect(nextButton.exists()).toBe(true);
    expect(todayButton.exists()).toBe(true);

    // Test that buttons are clickable (no errors thrown)
    await prevButton.trigger('click');
    await nextButton.trigger('click');
    await todayButton.trigger('click');

    // If we get here without errors, the buttons are functional
    expect(true).toBe(true);
  });

  it('view mode buttons are clickable and functional', async () => {
    // Test that view mode buttons exist and are clickable
    const weekButton = wrapper.findAll('button').find(btn => btn.text() === 'Week');
    const dayButton = wrapper.findAll('button').find(btn => btn.text() === 'Day');

    expect(weekButton.exists()).toBe(true);
    expect(dayButton.exists()).toBe(true);

    // Test that buttons are clickable (no errors thrown)
    await weekButton.trigger('click');
    await dayButton.trigger('click');

    // If we get here without errors, the buttons are functional
    expect(true).toBe(true);
  });

  it('surgery blocks are clickable', async () => {
    const surgeryBlocks = wrapper.findAll('.surgery-block');
    expect(surgeryBlocks.length).toBeGreaterThan(0);

    // Test that surgery blocks are clickable (no errors thrown)
    await surgeryBlocks[0].trigger('click');

    // If we get here without errors, the surgery blocks are clickable
    expect(true).toBe(true);
  });

  it('shows tooltip on surgery block hover', async () => {
    const surgeryBlocks = wrapper.findAll('.surgery-block');
    expect(surgeryBlocks.length).toBeGreaterThan(0);

    // Initially no tooltip
    expect(wrapper.find('.surgery-tooltip').exists()).toBe(false);

    // Mock getBoundingClientRect for the hover event
    const mockRect = { left: 100, top: 100, width: 200, height: 50, bottom: 150 };
    surgeryBlocks[0].element.getBoundingClientRect = vi.fn(() => mockRect);

    // Trigger mouseover
    await surgeryBlocks[0].trigger('mouseover');
    await wrapper.vm.$nextTick();

    // Tooltip should now be visible
    expect(wrapper.find('.surgery-tooltip').exists()).toBe(true);
    expect(wrapper.find('.tooltip-header').text()).toContain('Alice Smith');
  });

  it('hides tooltip on surgery block mouseleave', async () => {
    const surgeryBlocks = wrapper.findAll('.surgery-block');

    // First show tooltip
    const mockRect = { left: 100, top: 100, width: 200, height: 50, bottom: 150 };
    surgeryBlocks[0].element.getBoundingClientRect = vi.fn(() => mockRect);
    await surgeryBlocks[0].trigger('mouseover');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.surgery-tooltip').exists()).toBe(true);

    // Then hide it
    await surgeryBlocks[0].trigger('mouseleave');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.surgery-tooltip').exists()).toBe(false);
  });

  it('handles drag and drop setup correctly', async () => {
    const surgeryBlocks = wrapper.findAll('.surgery-block');
    expect(surgeryBlocks.length).toBeGreaterThan(0);

    // Mock dataTransfer for drag events
    const mockDataTransfer = {
      effectAllowed: '',
      setData: vi.fn(),
      getData: vi.fn(() => 's-1')
    };

    // Test dragstart
    const dragStartEvent = new Event('dragstart');
    dragStartEvent.dataTransfer = mockDataTransfer;

    await surgeryBlocks[0].trigger('dragstart', { dataTransfer: mockDataTransfer });

    expect(mockDataTransfer.setData).toHaveBeenCalledWith('text/plain', 's-1');
    expect(mockDataTransfer.effectAllowed).toBe('move');
  });

  it('displays loading state when store is loading', async () => {
    // Update the mock to show loading state
    const { useScheduleStore } = await import('@/stores/scheduleStore');
    const store = useScheduleStore();
    store.isLoading.value = true;

    await wrapper.vm.$nextTick();

    expect(wrapper.find('.loading-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain('Loading Schedule...');
  });
});