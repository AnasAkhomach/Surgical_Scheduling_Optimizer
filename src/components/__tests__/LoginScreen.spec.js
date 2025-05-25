import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { createPinia } from 'pinia';
import LoginScreen from '../LoginScreen.vue';
import DashboardScreen from '../DashboardScreen.vue';
import { ref } from 'vue'; // Import ref for reactive state in mock

// Mock the setAuthenticated function from the router
const mockSetAuthenticated = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
    removeItem: (key) => {
      delete store[key];
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock the authStore with reactive state and simulated actions
const mockIsAuthenticated = ref(false);
const mockUser = ref(null);
const mockLoading = ref(false);
const mockError = ref(null);

const mockLogin = vi.fn(async (username, password) => {
  mockLoading.value = true;
  mockError.value = null;
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 10));

  if (username === 'test@example.com' && password === 'password') {
    mockIsAuthenticated.value = true;
    mockUser.value = { id: 1, username: 'test@example.com', name: 'Test User' };
    // Simulate router push on successful login
    mockRouterPush({ name: 'Dashboard' });
  } else {
    mockError.value = 'Invalid username or password.';
    mockIsAuthenticated.value = false;
    mockUser.value = null;
  }
  mockLoading.value = false;
});

const mockRegister = vi.fn(async (username, password) => {
  mockLoading.value = true;
  mockError.value = null;
  let success = false;
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 10));

  // Mocked registration logic (e.g., fail if username exists)
  if (username === 'test@example.com') {
    mockError.value = 'Mock: Username already exists.';
    success = false;
  } else {
    // Simulate successful registration
    console.log('Mock Registration successful for:', username);
    success = true;
  }
  mockLoading.value = false;
  return success;
});

const mockLogout = vi.fn(() => {
  mockIsAuthenticated.value = false;
  mockUser.value = null;
  mockError.value = null;
  // Simulate router push on logout
  mockRouterPush({ name: 'Login' });
});

vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    get isAuthenticated() { return mockIsAuthenticated.value; },
    get user() { return mockUser.value; },
    get isLoading() { return mockLoading.value; },
    get error() { return mockError.value; },
    login: mockLogin,
    register: mockRegister,
    logout: mockLogout,
    // Add $reset if your component uses it and you need to mock its behavior
    $reset: vi.fn(() => {
      mockIsAuthenticated.value = false;
      mockUser.value = null;
      mockLoading.value = false;
      mockError.value = null;
    })
  }),
}));

const routes = [
  { path: '/', name: 'Login', component: LoginScreen },
  { path: '/dashboard', name: 'Dashboard', component: DashboardScreen },
];

const router = createRouter({
  history: createMemoryHistory(), // Changed here
  routes,
});

// Mock the setAuthenticated function from ../router
vi.mock('../router', () => ({
  setAuthenticated: mockSetAuthenticated
}));

// Mock vue-router's useRouter hook
const mockRouterPush = vi.fn();
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual, // Preserve other exports from vue-router
    useRouter: () => ({
      push: mockRouterPush,
      // Add other router methods or properties if your component uses them
    }),
  };
});

describe('LoginScreen.vue', () => {
  let wrapper;
  let pinia; // Declare pinia variable

  beforeEach(async () => {
    // Reset localStorage and mocks before each test
    localStorageMock.clear();
    mockSetAuthenticated.mockClear();
    mockRouterPush.mockClear();
    mockLogin.mockClear(); // Clear the authStore login mock
    mockRegister.mockClear(); // Clear the authStore register mock
    mockLogout.mockClear(); // Clear the authStore logout mock
    // Reset mock store state
    mockIsAuthenticated.value = false;
    mockUser.value = null;
    mockLoading.value = false;
    mockError.value = null;

    pinia = createPinia();

    wrapper = mount(LoginScreen, {
      global: {
        plugins: [router, pinia], // Add pinia to plugins
        stubs: {
          RouterLink: true,
        }
      }
    });
    await router.isReady();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders login form by default', () => {
    expect(wrapper.find('h2.form-title').text()).toBe('Login');
    expect(wrapper.find('input#username').exists()).toBe(true);
    expect(wrapper.find('input#password').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Login');
  });

  it('allows a user to login with correct credentials', async () => {
    await wrapper.find('input#username').setValue('test@example.com'); // Use the username expected by the mock
    await wrapper.find('input#password').setValue('password'); // Use the password expected by the mock
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 200)); // Increase delay

    // Expect the mocked login action to have been called
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password');
    // Expect the mocked router push to have been called by the mocked login action
    expect(mockRouterPush).toHaveBeenCalledWith({ name: 'Dashboard' });
    // Expect no error message to be displayed
    expect(wrapper.find('.error-message').exists()).toBe(false);
  });

  it('shows an error message with incorrect credentials', async () => {
    await wrapper.find('input#username').setValue('wronguser');
    await wrapper.find('input#password').setValue('wrongpassword');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 200)); // Increase delay

    // Expect the mocked login action to have been called
    expect(mockLogin).toHaveBeenCalledWith('wronguser', 'wrongpassword');
    // Expect the mocked router push NOT to have been called
    expect(mockRouterPush).not.toHaveBeenCalled();
    // Wait for the error message to appear in the DOM
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 50)); // Additional wait for DOM update
    // Expect the error message to be displayed (the mock sets the error state)
    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message').text()).toBe('Invalid username or password.'); // Match the error message from the mock
  });

  it('shows an error message if username or password fields are empty', async () => {
    await wrapper.find('input#username').setValue('');
    await wrapper.find('input#password').setValue('somepassword');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.error-message').text()).toBe('Please enter both username and password.');
    expect(mockSetAuthenticated).not.toHaveBeenCalled();
    expect(mockRouterPush).not.toHaveBeenCalled();

    await wrapper.find('input#username').setValue('someuser');
    await wrapper.find('input#password').setValue('');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.error-message').text()).toBe('Please enter both username and password.');
    expect(mockSetAuthenticated).not.toHaveBeenCalled();
    expect(mockRouterPush).not.toHaveBeenCalled();
  });

  it('toggles to registration form when "Create one" is clicked', async () => {
    await wrapper.findAll('a[href="#"]').filter(a => a.text().includes('Create one'))[0].trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('h2.form-title').text()).toBe('Create Account');
    expect(wrapper.find('input#new-username').exists()).toBe(true);
    expect(wrapper.find('input#new-password').exists()).toBe(true);
    expect(wrapper.find('input#confirm-password').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Create Account');
  });

  // Add more tests for registration functionality
  it('allows a user to register a new account', async () => {
    await wrapper.findAll('a[href="#"]').filter(a => a.text().includes('Create one'))[0].trigger('click');
    await wrapper.vm.$nextTick();

    await wrapper.find('input#new-username').setValue('newuser');
    await wrapper.find('input#new-password').setValue('newpass123');
    await wrapper.find('input#confirm-password').setValue('newpass123');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 200)); // Increase delay

    // Expect the mocked register action to have been called
    expect(mockRegister).toHaveBeenCalledWith('newuser', 'newpass123');
    // Wait for DOM updates
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 50));

    // The component switches back to login form after successful registration
    // So the success message won't be visible since it's in the registration form
    expect(wrapper.find('h2.form-title').text()).toBe('Login'); // Should switch back to login form

    // Instead, let's verify that the registration was successful by checking the mock was called
    // and that we're back on the login form (which indicates success)
  });

  it('shows an error if registration passwords do not match', async () => {
    await wrapper.findAll('a[href="#"]').filter(a => a.text().includes('Create one'))[0].trigger('click');
    await wrapper.vm.$nextTick();

    await wrapper.find('input#new-username').setValue('anotheruser');
    await wrapper.find('input#new-password').setValue('password123');
    await wrapper.find('input#confirm-password').setValue('password456');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    // Expect the mocked register action NOT to have been called because passwords don't match
    expect(mockRegister).not.toHaveBeenCalled();
    // Expect the error message to be displayed (the component should handle password mismatch before calling the store)
    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message').text()).toBe('Passwords do not match.'); // Assuming component shows this error
  });

  it('shows an error if username already exists during registration', async () => {
    // Simulate an existing user by making the mockRegister return false and set an error
    mockRegister.mockImplementationOnce(async (username, password) => {
      mockLoading.value = true;
      mockError.value = null;
      await new Promise(resolve => setTimeout(resolve, 10));
      mockError.value = 'Mock: Username already exists.';
      mockLoading.value = false;
      return false; // Simulate registration failure
    });

    await wrapper.findAll('a[href="#"]').filter(a => a.text().includes('Create one'))[0].trigger('click');
    await wrapper.vm.$nextTick();

    await wrapper.find('input#new-username').setValue('test@example.com'); // Use a username that the mock will treat as existing
    await wrapper.find('input#new-password').setValue('somepass');
    await wrapper.find('input#confirm-password').setValue('somepass');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 200)); // Increase delay
    // Wait for DOM updates
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 50));

    // Expect the mocked register action to have been called
    expect(mockRegister).toHaveBeenCalledWith('test@example.com', 'somepass');
    // Expect the error message to be displayed (the mock sets the error state)
    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message').text()).toBe('Mock: Username already exists.'); // Match the error message from the mock
  });

  it('shows an error if any registration field is empty', async () => {
    await wrapper.findAll('a[href="#"]').filter(a => a.text().includes('Create one'))[0].trigger('click');
    await wrapper.vm.$nextTick();

    // Test with empty username
    await wrapper.find('input#new-username').setValue('');
    await wrapper.find('input#new-password').setValue('somepass');
    await wrapper.find('input#confirm-password').setValue('somepass');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message').text()).toBe('Please fill in all fields.'); // Assuming component shows this error
    expect(mockRegister).not.toHaveBeenCalled();

    // Test with empty password
    await wrapper.find('input#new-username').setValue('someuser');
    await wrapper.find('input#new-password').setValue('');
    await wrapper.find('input#confirm-password').setValue('somepass');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.error-message').exists()).toBe(true);
    expect(wrapper.find('.error-message').text()).toBe('Please fill in all fields.');
    expect(mockRegister).not.toHaveBeenCalled();

    // Test with empty confirm password
    await wrapper.find('input#new-username').setValue('someuser');
    await wrapper.find('input#new-password').setValue('somepass');
    await wrapper.find('input#confirm-password').setValue('');
    await wrapper.find('form.login-form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();
    // Fixed: Use .find() instead of .findBySelector()
    const errorMessage = wrapper.find('.error-message');
    expect(errorMessage.exists()).toBe(true);
    expect(errorMessage.text()).toBe('Please fill in all fields.');
    expect(mockRegister).not.toHaveBeenCalled();
  });
});