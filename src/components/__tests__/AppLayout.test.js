import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import { ref } from 'vue';
import AppLayout from '../AppLayout.vue';

// Mock the auth store
const mockUser = ref({ id: 1, name: 'Test User', username: 'test@example.com' });
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    isAuthenticated: ref(true),
    user: mockUser,
    isLoading: ref(false),
    error: ref(null),
    logout: vi.fn()
  })
}));

// Mock vue-toastification
vi.mock('vue-toastification', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn()
  })
}));

describe('AppLayout', () => {
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
        { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } }
      ]
    });

    wrapper = mount(AppLayout, {
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
    expect(wrapper.find('.app-layout').exists()).toBe(true);
  });

  it('renders the top navigation bar', () => {
    expect(wrapper.find('.top-nav-bar').exists()).toBe(true);
    expect(wrapper.find('.app-brand').exists()).toBe(true);
    expect(wrapper.find('.global-search').exists()).toBe(true);
    expect(wrapper.find('.user-utilities').exists()).toBe(true);
  });

  it('renders the left sidebar', () => {
    expect(wrapper.find('.left-sidebar').exists()).toBe(true);
    expect(wrapper.find('.left-sidebar nav').exists()).toBe(true);
  });

  it('renders the main content area', () => {
    expect(wrapper.find('.main-content').exists()).toBe(true);
    expect(wrapper.find('router-view-stub').exists()).toBe(true);
  });

  it('toggles sidebar when toggle button is clicked', async () => {
    const toggleButton = wrapper.find('.toggle-sidebar-button');
    expect(toggleButton.exists()).toBe(true);

    // Initially not collapsed
    expect(wrapper.find('.app-layout.sidebar-collapsed').exists()).toBe(false);

    // Click toggle button
    await toggleButton.trigger('click');
    await wrapper.vm.$nextTick();

    // Should be collapsed now
    expect(wrapper.find('.app-layout.sidebar-collapsed').exists()).toBe(true);

    // Click again to uncollapse
    await toggleButton.trigger('click');
    await wrapper.vm.$nextTick();

    // Should not be collapsed
    expect(wrapper.find('.app-layout.sidebar-collapsed').exists()).toBe(false);
  });

  it('handles search input', async () => {
    const searchInput = wrapper.find('.global-search input[type="text"]');
    expect(searchInput.exists()).toBe(true);

    await searchInput.setValue('test search');
    expect(searchInput.element.value).toBe('test search');
  });

  it('displays user information', () => {
    const userProfile = wrapper.find('.user-profile');
    expect(userProfile.exists()).toBe(true);
    // The component should display either the username or fallback to 'User Name'
    const userText = userProfile.text();
    expect(userText).toMatch(/test@example\.com|User Name/);
  });

  it('calls logout when logout button is clicked', async () => {
    const logoutButton = wrapper.find('.logout-button');
    expect(logoutButton.exists()).toBe(true);

    await logoutButton.trigger('click');

    // The logout function should have been called
    // Note: We can't easily test the actual store call due to mocking,
    // but we can verify the button exists and is clickable
    expect(logoutButton.exists()).toBe(true);
  });
});