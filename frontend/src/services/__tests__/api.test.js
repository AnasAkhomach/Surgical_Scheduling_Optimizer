import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { authAPI } from '../api.js';

// Mock fetch globally
global.fetch = vi.fn();

describe('Authentication API', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset fetch mock
    fetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('login', () => {
    it('should send FormData with correct fields', async () => {
      // Mock successful response
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const result = await authAPI.login('testuser', 'testpass');

      // Verify fetch was called correctly
      expect(fetch).toHaveBeenCalledTimes(1);
      const [url, options] = fetch.mock.calls[0];
      
      expect(url).toBe('http://localhost:8000/api/auth/token');
      expect(options.method).toBe('POST');
      expect(options.body).toBeInstanceOf(FormData);
      
      // Verify FormData contains correct fields
      const formData = options.body;
      expect(formData.get('username')).toBe('testuser');
      expect(formData.get('password')).toBe('testpass');
      expect(formData.get('grant_type')).toBe('password');
      
      // Verify Content-Type is not set (should be undefined for FormData)
      expect(options.headers['Content-Type']).toBeUndefined();
      
      expect(result).toEqual(mockResponse);
    });

    it('should handle login errors correctly', async () => {
      const mockError = {
        detail: 'Incorrect username or password',
        error_code: 'AUTHENTICATION_ERROR'
      };

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => mockError
      });

      await expect(authAPI.login('wronguser', 'wrongpass'))
        .rejects.toThrow('Incorrect username or password');
    });

    it('should handle validation errors correctly', async () => {
      const mockError = {
        detail: 'Validation error',
        error_code: 'VALIDATION_ERROR',
        field_errors: {
          username: ['Field required'],
          password: ['Field required']
        }
      };

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => mockError
      });

      await expect(authAPI.login('', ''))
        .rejects.toThrow('Validation error');
    });
  });

  describe('register', () => {
    it('should send JSON data with correct fields', async () => {
      const mockResponse = {
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse
      });

      const userData = {
        username: 'testuser',
        password: 'testpass123',
        email: 'test@example.com',
        full_name: 'Test User'
      };

      const result = await authAPI.register(userData);

      // Verify fetch was called correctly
      expect(fetch).toHaveBeenCalledTimes(1);
      const [url, options] = fetch.mock.calls[0];
      
      expect(url).toBe('http://localhost:8000/api/auth/register');
      expect(options.method).toBe('POST');
      expect(options.headers['Content-Type']).toBe('application/json');
      expect(options.body).toBe(JSON.stringify(userData));
      
      expect(result).toEqual(mockResponse);
    });

    it('should handle registration errors correctly', async () => {
      const mockError = {
        detail: 'Username or email already registered',
        error_code: 'DUPLICATE_USER'
      };

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => mockError
      });

      const userData = {
        username: 'existinguser',
        password: 'testpass123',
        email: 'existing@example.com',
        full_name: 'Existing User'
      };

      await expect(authAPI.register(userData))
        .rejects.toThrow('Username or email already registered');
    });
  });

  describe('getCurrentUser', () => {
    it('should include authorization header when token exists', async () => {
      localStorage.setItem('authToken', 'test-token');

      const mockResponse = {
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const result = await authAPI.getCurrentUser();

      // Verify fetch was called with authorization header
      expect(fetch).toHaveBeenCalledTimes(1);
      const [url, options] = fetch.mock.calls[0];
      
      expect(url).toBe('http://localhost:8000/api/auth/me');
      expect(options.headers.Authorization).toBe('Bearer test-token');
      
      expect(result).toEqual(mockResponse);
    });

    it('should handle unauthorized access correctly', async () => {
      const mockError = {
        detail: 'Not authenticated',
        error_code: 'NOT_AUTHENTICATED'
      };

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => mockError
      });

      await expect(authAPI.getCurrentUser())
        .rejects.toThrow('Not authenticated');
    });
  });
});
