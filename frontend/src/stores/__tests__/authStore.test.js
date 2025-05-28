import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '../authStore.js';
import { authAPI } from '../../services/api.js';

// Mock the API
vi.mock('../../services/api.js', () => ({
  authAPI: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    register: vi.fn()
  }
}));

// Mock router
const mockPush = vi.fn();
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useRouter: () => ({
      push: mockPush
    }),
    createRouter: vi.fn(),
    createWebHistory: vi.fn()
  };
});

describe('Auth Store', () => {
  let authStore;

  beforeEach(() => {
    setActivePinia(createPinia());
    authStore = useAuthStore();

    // Clear localStorage
    localStorage.clear();

    // Reset mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('login', () => {
    it('should store token in localStorage before calling getCurrentUser', async () => {
      // Mock successful login response
      const mockLoginResponse = {
        access_token: 'test-token-123',
        token_type: 'bearer'
      };

      const mockUserResponse = {
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com'
      };

      authAPI.login.mockResolvedValue(mockLoginResponse);
      authAPI.getCurrentUser.mockResolvedValue(mockUserResponse);

      // Track localStorage calls
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');

      await authStore.login('testuser', 'testpass');

      // Verify the sequence of operations
      expect(authAPI.login).toHaveBeenCalledWith('testuser', 'testpass');
      expect(authAPI.getCurrentUser).toHaveBeenCalled();

      // Verify token was stored in localStorage before getCurrentUser was called
      expect(setItemSpy).toHaveBeenCalledWith('authToken', 'test-token-123');
      expect(setItemSpy).toHaveBeenCalledWith('isAuthenticated', 'true');

      // Verify store state
      expect(authStore.token).toBe('test-token-123');
      expect(authStore.isAuthenticated).toBe(true);
      expect(authStore.user).toEqual(mockUserResponse);
      expect(authStore.error).toBeNull();

      // Verify localStorage contains all required data
      expect(localStorage.getItem('authToken')).toBe('test-token-123');
      expect(localStorage.getItem('isAuthenticated')).toBe('true');
      expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUserResponse));

      // Verify navigation
      expect(mockPush).toHaveBeenCalledWith({ name: 'Dashboard' });
    });

    it('should handle login success but getCurrentUser failure', async () => {
      const mockLoginResponse = {
        access_token: 'test-token-123',
        token_type: 'bearer'
      };

      authAPI.login.mockResolvedValue(mockLoginResponse);
      authAPI.getCurrentUser.mockRejectedValue(new Error('Not authenticated'));

      await authStore.login('testuser', 'testpass');

      // Verify login was successful but overall flow failed
      expect(authAPI.login).toHaveBeenCalledWith('testuser', 'testpass');
      expect(authAPI.getCurrentUser).toHaveBeenCalled();

      // Verify error state
      expect(authStore.error).toBe('Not authenticated');
      expect(authStore.isAuthenticated).toBe(false);
      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();

      // Verify localStorage was cleaned up
      expect(localStorage.getItem('authToken')).toBeNull();
      expect(localStorage.getItem('isAuthenticated')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });

    it('should handle login failure', async () => {
      authAPI.login.mockRejectedValue(new Error('Invalid credentials'));

      await authStore.login('wronguser', 'wrongpass');

      // Verify error state
      expect(authStore.error).toBe('Invalid credentials');
      expect(authStore.isAuthenticated).toBe(false);
      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();

      // Verify localStorage is clean
      expect(localStorage.getItem('authToken')).toBeNull();
      expect(localStorage.getItem('isAuthenticated')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();

      // Verify getCurrentUser was not called
      expect(authAPI.getCurrentUser).not.toHaveBeenCalled();
    });

    it('should set loading state correctly', async () => {
      const mockLoginResponse = {
        access_token: 'test-token-123',
        token_type: 'bearer'
      };

      const mockUserResponse = {
        user_id: 1,
        username: 'testuser'
      };

      // Make API calls return promises that we can control
      let resolveLogin, resolveGetUser;
      const loginPromise = new Promise(resolve => { resolveLogin = resolve; });
      const getUserPromise = new Promise(resolve => { resolveGetUser = resolve; });

      authAPI.login.mockReturnValue(loginPromise);
      authAPI.getCurrentUser.mockReturnValue(getUserPromise);

      // Start login
      const loginCall = authStore.login('testuser', 'testpass');

      // Verify loading state is true
      expect(authStore.isLoading).toBe(true);

      // Resolve login
      resolveLogin(mockLoginResponse);
      await new Promise(resolve => setTimeout(resolve, 0)); // Wait for next tick

      // Still loading because getCurrentUser hasn't resolved
      expect(authStore.isLoading).toBe(true);

      // Resolve getCurrentUser
      resolveGetUser(mockUserResponse);
      await loginCall;

      // Loading should be false now
      expect(authStore.isLoading).toBe(false);
    });
  });

  describe('register', () => {
    it('should handle successful registration', async () => {
      const mockUserResponse = {
        user_id: 1,
        username: 'newuser',
        email: 'new@example.com'
      };

      authAPI.register.mockResolvedValue(mockUserResponse);

      const result = await authStore.register('newuser', 'newpass', 'new@example.com', 'New User');

      expect(authAPI.register).toHaveBeenCalledWith({
        username: 'newuser',
        password: 'newpass',
        email: 'new@example.com',
        full_name: 'New User'
      });

      expect(result).toBe(true);
      expect(authStore.error).toBeNull();
      expect(authStore.isLoading).toBe(false);
    });

    it('should handle registration failure', async () => {
      authAPI.register.mockRejectedValue(new Error('Username already exists'));

      const result = await authStore.register('existinguser', 'pass', 'email@test.com', 'User');

      expect(result).toBe(false);
      expect(authStore.error).toBe('Username already exists');
      expect(authStore.isLoading).toBe(false);
    });
  });

  describe('logout', () => {
    it('should clear all auth data', () => {
      // Set up initial state
      authStore.isAuthenticated = true;
      authStore.token = 'test-token';
      authStore.user = { username: 'testuser' };
      authStore.error = 'some error';

      localStorage.setItem('authToken', 'test-token');
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('user', '{"username":"testuser"}');

      authStore.logout();

      // Verify state is cleared
      expect(authStore.isAuthenticated).toBe(false);
      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();
      expect(authStore.error).toBeNull();

      // Verify localStorage is cleared
      expect(localStorage.getItem('authToken')).toBeNull();
      expect(localStorage.getItem('isAuthenticated')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();

      // Verify navigation
      expect(mockPush).toHaveBeenCalledWith({ name: 'Login' });
    });
  });
});
