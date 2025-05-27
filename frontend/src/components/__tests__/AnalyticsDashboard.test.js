import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import AnalyticsDashboard from '../AnalyticsDashboard.vue';
import { createPinia, storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { ref, reactive } from 'vue';

// Mock the router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
  })),
}));

// Mock the analytics store
vi.mock('@/stores/analyticsStore', () => ({
  useAnalyticsStore: vi.fn(() => ({
    // Make properties reactive
    isLoading: ref(false),
    error: ref(null),
    dateRange: reactive({ start: new Date(), end: new Date() }),
    cachedData: reactive({}),
    // Keep methods as vi.fn()
    loadAnalyticsData: vi.fn(),
    setDateRange: vi.fn(),
  })),
}));

describe('AnalyticsDashboard', () => {
  let wrapper;
  let analyticsStore;
  let router;

  beforeEach(() => {
    const pinia = createPinia();
    analyticsStore = useAnalyticsStore();
    router = useRouter();

    wrapper = mount(AnalyticsDashboard, {
      global: {
        plugins: [pinia],
        mocks: {
          $router: router,
          $route: {},
        },
      },
    });
  });

  // Basic rendering test
  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true);
  });

  // Test if the main heading is rendered
  it('renders the main heading', () => {
    expect(wrapper.find('h1').exists()).toBe(true);
    expect(wrapper.find('h1').text()).toBe('Analytics Dashboard');
  });

  // Test if the date range selector section is rendered
  it('renders the date range selector section', () => {
    expect(wrapper.find('.date-range-selector').exists()).toBe(true);
    expect(wrapper.find('.date-range-selector h3').text()).toBe('Date Range');
  });

  // Test if date inputs and apply button are rendered
  it('renders date inputs and apply button', () => {
    expect(wrapper.find('#start-date').exists()).toBe(true);
    expect(wrapper.find('#end-date').exists()).toBe(true);
    expect(wrapper.find('.apply-button').exists()).toBe(true);
    expect(wrapper.find('.apply-button').text()).toBe('Apply');
  });

  // Test if quick range buttons are rendered
  it('renders quick range buttons', () => {
    const buttons = wrapper.findAll('.quick-ranges button');
    expect(buttons.length).toBe(4);
    expect(buttons[0].text()).toBe('Last 7 Days');
    expect(buttons[1].text()).toBe('Last 30 Days');
    expect(buttons[2].text()).toBe('This Month');
    expect(buttons[3].text()).toBe('Last Month');
  });

  // Test if summary metrics section is rendered (when not loading or error)
  it('renders summary metrics section when data is loaded', async () => {
    // Ensure loading and error are false in the mock
    analyticsStore.isLoading.value = false;
    analyticsStore.error.value = null;
    await wrapper.vm.$nextTick(); // Wait for DOM update
    expect(wrapper.find('.summary-metrics').exists()).toBe(true);
  });

  // Test if chart sections are rendered (when not loading or error)
  it('renders chart sections when data is loaded', async () => {
    // Ensure loading and error are false in the mock
    analyticsStore.isLoading.value = false;
    analyticsStore.error.value = null;
    await wrapper.vm.$nextTick(); // Wait for DOM update
    const chartContainers = wrapper.findAll('.chart-container');
    expect(chartContainers.length).toBe(4);
    expect(chartContainers[0].find('h3').text()).toBe('Daily Surgery Volume');
    expect(chartContainers[1].find('h3').text()).toBe('OR Utilization by Room');
    expect(chartContainers[2].find('h3').text()).toBe('Surgery Type Distribution');
    expect(chartContainers[3].find('h3').text()).toBe('Surgeon Performance');
  });

  // Test if report links section is rendered (when not loading or error)
  it('renders report links section when data is loaded', async () => {
    // Ensure loading and error are false in the mock
    analyticsStore.isLoading.value = false;
    analyticsStore.error.value = null;
    await wrapper.vm.$nextTick(); // Wait for DOM update
    expect(wrapper.find('.report-links').exists()).toBe(true);
    expect(wrapper.find('.report-links h3').text()).toBe('Detailed Reports');
  });

  // Test if loading indicator is shown when isLoading is true
  it('shows loading indicator when isLoading is true', async () => {
    analyticsStore.isLoading.value = true;
    analyticsStore.error.value = null;
    // await wrapper.vm.$nextTick(); // Wait for DOM update
    expect(await wrapper.find('.loading-overlay').exists()).toBe(true);
    expect(wrapper.find('.dashboard-content').exists()).toBe(false);
    expect(wrapper.find('.error-message').exists()).toBe(false);
  });

  // Test if error message is shown when error is not null
  it('shows error message when error is not null', async () => {
    analyticsStore.isLoading.value = false;
    analyticsStore.error.value = 'Failed to load data';
    // await wrapper.vm.$nextTick(); // Wait for DOM update
    expect(await wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message p').text()).toBe('Failed to load data');
    expect(wrapper.find('.dashboard-content').exists()).toBe(false);
    expect(wrapper.find('.loading-overlay').exists()).toBe(false);
  });

  // Add more tests here based on component functionality (props, data, events, methods, etc.)

  // Test user interaction with date inputs and apply button
  it('updates date range and loads data when apply button is clicked', async () => {
    const startDateInput = wrapper.find('#start-date');
    const endDateInput = wrapper.find('#end-date');
    const applyButton = wrapper.find('.apply-button');

    // Simulate user input
    await startDateInput.setValue('2023-01-01');
    await endDateInput.setValue('2023-01-31');

    // Click the apply button
    await applyButton.trigger('click');

    // Check if setDateRange was called with the correct dates
    expect(analyticsStore.setDateRange).toHaveBeenCalledWith({
      start: new Date('2023-01-01'),
      end: new Date('2023-01-31'),
    });

    // Check if loadAnalyticsData was called
    expect(analyticsStore.loadAnalyticsData).toHaveBeenCalled();
  });

  // Test user interaction with quick range buttons
  it('updates date range and loads data when a quick range button is clicked', async () => {
    const quickRangeButtons = wrapper.findAll('.quick-ranges button');
    const last7DaysButton = quickRangeButtons[0];

    // Click the 'Last 7 Days' button
    await last7DaysButton.trigger('click');

    // Check if setDateRange was called (the exact dates will depend on the current date, so we just check if it was called)
    expect(analyticsStore.setDateRange).toHaveBeenCalled();

    // Check if loadAnalyticsData was called
    expect(analyticsStore.loadAnalyticsData).toHaveBeenCalled();
  });
});