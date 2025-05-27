import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import ToastNotification from '../ToastNotification.vue';

describe('ToastNotification', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(ToastNotification, {
      global: {
        config: {
          globalProperties: {
            // Mock any global properties if needed
          }
        }
      }
    });
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders correctly with no toasts initially', () => {
    expect(wrapper.exists()).toBe(true);
    // Since the component uses Teleport to body, check the document body
    const toastContainer = document.querySelector('.toast-container');
    expect(toastContainer).toBeTruthy();
    expect(document.querySelectorAll('.toast')).toHaveLength(0);
  });

  it('adds a basic toast notification', async () => {
    const toast = {
      type: 'info',
      message: 'Test message'
    };

    wrapper.vm.addToast(toast);
    await nextTick();

    const toastElements = document.querySelectorAll('.toast');
    expect(toastElements).toHaveLength(1);
    expect(toastElements[0].classList.contains('toast-info')).toBe(true);
    expect(toastElements[0].textContent).toContain('Test message');
  });

  it('adds toast with title', async () => {
    const toast = {
      type: 'success',
      title: 'Success!',
      message: 'Operation completed successfully'
    };

    wrapper.vm.addToast(toast);
    await nextTick();

    const toastElement = document.querySelector('.toast');
    expect(toastElement.querySelector('.toast-title').textContent).toBe('Success!');
    expect(toastElement.querySelector('.toast-message').textContent).toBe('Operation completed successfully');
    expect(toastElement.classList.contains('toast-success')).toBe(true);
  });

  it('displays correct icons for different toast types', async () => {
    const toastTypes = [
      { type: 'success', icon: '✓' },
      { type: 'error', icon: '✕' },
      { type: 'warning', icon: '⚠' },
      { type: 'info', icon: 'ℹ' }
    ];

    for (const { type, icon } of toastTypes) {
      wrapper.vm.addToast({ type, message: `${type} message` });
      await nextTick();

      const toastElements = document.querySelectorAll('.toast');
      const toastElement = toastElements[toastElements.length - 1];
      expect(toastElement.querySelector('.toast-icon').textContent).toBe(icon);
      expect(toastElement.classList.contains(`toast-${type}`)).toBe(true);
    }
  });

  it('dismisses toast when close button is clicked', async () => {
    wrapper.vm.addToast({ message: 'Test message' });
    await nextTick();

    expect(document.querySelectorAll('.toast')).toHaveLength(1);

    const closeButton = document.querySelector('.toast-close');
    closeButton.click();
    await nextTick();

    expect(document.querySelectorAll('.toast')).toHaveLength(0);
  });

  it('adds toast with action button', async () => {
    const actionCallback = vi.fn();
    const toast = {
      type: 'warning',
      message: 'Action required',
      action: {
        label: 'Retry',
        callback: actionCallback
      }
    };

    wrapper.vm.addToast(toast);
    await nextTick();

    const toastElement = document.querySelector('.toast');
    expect(toastElement.classList.contains('with-action')).toBe(true);

    const actionButton = toastElement.querySelector('.toast-action');
    expect(actionButton).toBeTruthy();
    expect(actionButton.textContent).toBe('Retry');
    expect(actionButton.getAttribute('aria-label')).toBe('Retry');

    actionButton.click();
    expect(actionCallback).toHaveBeenCalled();
  });

  it('auto-dismisses toast after specified duration', async () => {
    vi.useFakeTimers();

    wrapper.vm.addToast({
      message: 'Auto dismiss test',
      duration: 1000
    });
    await nextTick();

    expect(document.querySelectorAll('.toast')).toHaveLength(1);

    // Fast-forward time by 1000ms
    vi.advanceTimersByTime(1000);
    await nextTick();

    expect(document.querySelectorAll('.toast')).toHaveLength(0);

    vi.useRealTimers();
  });

  it('does not auto-dismiss toast with duration 0', async () => {
    // Don't use fake timers for this test to avoid interference
    const id = wrapper.vm.addToast({
      message: 'Persistent toast',
      duration: 0
    });
    await nextTick();

    expect(document.querySelectorAll('.toast')).toHaveLength(1);

    // Check that no timeout was set for this toast
    expect(wrapper.vm.toastTimeouts[id]).toBeUndefined();

    // Verify the toast is still in the component state
    expect(wrapper.vm.toasts.some(t => t.id === id)).toBe(true);
  });

  it('dismisses specific toast by ID', async () => {
    const id1 = wrapper.vm.addToast({ message: 'First toast' });
    const id2 = wrapper.vm.addToast({ message: 'Second toast' });
    await nextTick();

    expect(document.querySelectorAll('.toast')).toHaveLength(2);

    wrapper.vm.dismissToast(id1);
    await nextTick();

    const remainingToasts = document.querySelectorAll('.toast');
    expect(remainingToasts).toHaveLength(1);
    expect(remainingToasts[0].textContent).toContain('Second toast');
  });

  it('handles multiple toasts correctly', async () => {
    const toasts = [
      { type: 'info', message: 'Info message' },
      { type: 'success', message: 'Success message' },
      { type: 'error', message: 'Error message' }
    ];

    toasts.forEach(toast => wrapper.vm.addToast(toast));
    await nextTick();

    const toastElements = document.querySelectorAll('.toast');
    expect(toastElements).toHaveLength(3);

    toasts.forEach((toast, index) => {
      expect(toastElements[index].textContent).toContain(toast.message);
      expect(toastElements[index].classList.contains(`toast-${toast.type}`)).toBe(true);
    });
  });

  it('has proper accessibility attributes', async () => {
    wrapper.vm.addToast({
      message: 'Accessible toast',
      action: { label: 'Action', callback: vi.fn() }
    });
    await nextTick();

    const toastElement = document.querySelector('.toast');
    expect(toastElement.getAttribute('role')).toBe('alert');
    expect(toastElement.getAttribute('aria-live')).toBe('assertive');

    const closeButton = toastElement.querySelector('.toast-close');
    expect(closeButton.getAttribute('aria-label')).toBe('Close notification');

    const actionButton = toastElement.querySelector('.toast-action');
    expect(actionButton.getAttribute('aria-label')).toBe('Action');
  });

  it('cleans up timeouts on unmount', async () => {
    vi.useFakeTimers();
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');

    wrapper.vm.addToast({ message: 'Test', duration: 5000 });
    await nextTick();

    wrapper.unmount();

    expect(clearTimeoutSpy).toHaveBeenCalled();

    vi.useRealTimers();
    clearTimeoutSpy.mockRestore();
  });

  it('returns unique IDs for each toast', async () => {
    const id1 = wrapper.vm.addToast({ message: 'First' });
    await nextTick();
    const id2 = wrapper.vm.addToast({ message: 'Second' });
    await nextTick();

    expect(id1).toBeDefined();
    expect(id2).toBeDefined();
    expect(id1).not.toBe(id2);
    expect(typeof id1).toBe('string');
    expect(typeof id2).toBe('string');
  });

  it('uses default values for missing properties', async () => {
    wrapper.vm.addToast({ message: 'Minimal toast' });
    await nextTick();

    const toastElement = document.querySelector('.toast');
    expect(toastElement.classList.contains('toast-info')).toBe(true); // Default type
    expect(toastElement.querySelector('.toast-title')).toBeFalsy(); // No title
    expect(toastElement.querySelector('.toast-action')).toBeFalsy(); // No action
  });
});
