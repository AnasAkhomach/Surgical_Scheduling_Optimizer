import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import KeyboardShortcutsHelp from '../KeyboardShortcutsHelp.vue';

// Mock the keyboard shortcuts service
vi.mock('@/services/keyboardShortcuts', () => {
  const mockShortcuts = [
    {
      key: 's',
      ctrlKey: true,
      description: 'Save current work',
      scope: 'global'
    },
    {
      key: 'n',
      ctrlKey: true,
      description: 'Create new item',
      scope: 'global'
    },
    {
      key: 'f',
      ctrlKey: true,
      description: 'Find and search',
      scope: 'search'
    },
    {
      key: 'escape',
      description: 'Cancel current action',
      scope: 'navigation'
    },
    {
      key: '?',
      shiftKey: true,
      description: 'Show keyboard shortcuts help',
      scope: 'global'
    }
  ];

  return {
    default: {
      getShortcuts: vi.fn(() => mockShortcuts),
      register: vi.fn(() => vi.fn()), // Returns unregister function
    }
  };
});

describe('KeyboardShortcutsHelp', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(KeyboardShortcutsHelp);
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders correctly when not visible', () => {
    expect(wrapper.exists()).toBe(true);
    // Modal should not be visible initially
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();
  });

  it('shows modal when show method is called', async () => {
    wrapper.vm.show();
    await nextTick();

    const overlay = document.querySelector('.keyboard-shortcuts-overlay');
    expect(overlay).toBeTruthy();
    expect(overlay.querySelector('.keyboard-shortcuts-modal')).toBeTruthy();
  });

  it('hides modal when close method is called', async () => {
    wrapper.vm.show();
    await nextTick();
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeTruthy();

    wrapper.vm.close();
    await nextTick();
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();
  });

  it('toggles modal visibility when toggle method is called', async () => {
    // Initially hidden
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();

    // Toggle to show
    wrapper.vm.toggle();
    await nextTick();
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeTruthy();

    // Toggle to hide
    wrapper.vm.toggle();
    await nextTick();
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();
  });

  it('displays modal title correctly', async () => {
    wrapper.vm.show();
    await nextTick();

    const title = document.querySelector('.modal-header h2');
    expect(title.textContent).toBe('Keyboard Shortcuts');
  });

  it('closes modal when close button is clicked', async () => {
    wrapper.vm.show();
    await nextTick();

    const closeButton = document.querySelector('.close-button');
    closeButton.click();
    await nextTick();

    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();
  });

  it('closes modal when overlay is clicked', async () => {
    wrapper.vm.show();
    await nextTick();

    const overlay = document.querySelector('.keyboard-shortcuts-overlay');
    overlay.click();
    await nextTick();

    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();
  });

  it('does not close modal when modal content is clicked', async () => {
    wrapper.vm.show();
    await nextTick();

    const modal = document.querySelector('.keyboard-shortcuts-modal');
    modal.click();
    await nextTick();

    // Modal should still be visible
    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeTruthy();
  });

  it('closes modal when footer close button is clicked', async () => {
    wrapper.vm.show();
    await nextTick();

    const footerButton = document.querySelector('.modal-footer .btn');
    footerButton.click();
    await nextTick();

    expect(document.querySelector('.keyboard-shortcuts-overlay')).toBeFalsy();
  });

  it('groups shortcuts by scope correctly', async () => {
    wrapper.vm.show();
    await nextTick();

    const groups = document.querySelectorAll('.shortcut-group');
    expect(groups.length).toBe(3); // global, search, navigation

    // Check that groups have correct titles
    const groupTitles = Array.from(groups).map(group =>
      group.querySelector('h3').textContent
    );
    expect(groupTitles).toContain('Global');
    expect(groupTitles).toContain('Search');
    expect(groupTitles).toContain('Navigation');
  });

  it('displays shortcuts with correct formatting', async () => {
    wrapper.vm.show();
    await nextTick();

    // Check that shortcuts are displayed in tables
    const tables = document.querySelectorAll('table');
    expect(tables.length).toBeGreaterThan(0);

    // Check table headers
    const headers = document.querySelectorAll('th');
    expect(headers[0].textContent).toBe('Shortcut');
    expect(headers[1].textContent).toBe('Description');

    // Check that key combinations are displayed
    const keyElements = document.querySelectorAll('.key');
    expect(keyElements.length).toBeGreaterThan(0);
  });

  it('formats special keys correctly', () => {
    // Test the formatKeyName method through the component
    const testCases = [
      { input: 'escape', expected: 'Esc' },
      { input: ' ', expected: 'Space' },
      { input: 'arrowup', expected: '↑' },
      { input: 'arrowdown', expected: '↓' },
      { input: 'enter', expected: 'Enter' },
      { input: 'a', expected: 'A' }
    ];

    testCases.forEach(({ input, expected }) => {
      const result = wrapper.vm.formatKeyName(input);
      expect(result).toBe(expected);
    });
  });

  it('formats scope names correctly', () => {
    expect(wrapper.vm.formatScopeName('global')).toBe('Global');
    expect(wrapper.vm.formatScopeName('search')).toBe('Search');
    expect(wrapper.vm.formatScopeName('navigation')).toBe('Navigation');
  });

  it('registers keyboard shortcut on mount', async () => {
    const keyboardShortcuts = await import('@/services/keyboardShortcuts');
    expect(keyboardShortcuts.default.register).toHaveBeenCalledWith(
      '?',
      expect.any(Function),
      {
        shiftKey: true,
        description: 'Show keyboard shortcuts help',
        scope: 'global'
      }
    );
  });

  it('displays modifier keys correctly', async () => {
    wrapper.vm.show();
    await nextTick();

    // Find a shortcut with Ctrl key (like Ctrl+S)
    const shortcutRows = document.querySelectorAll('tbody tr');
    const ctrlSRow = Array.from(shortcutRows).find(row =>
      row.textContent.includes('Save current work')
    );

    expect(ctrlSRow).toBeTruthy();
    const keys = ctrlSRow.querySelectorAll('.key');
    expect(keys.length).toBe(2); // Ctrl + S
    expect(keys[0].textContent).toBe('Ctrl');
    expect(keys[1].textContent).toBe('S');
  });

  it('has proper accessibility attributes', async () => {
    wrapper.vm.show();
    await nextTick();

    const closeButton = document.querySelector('.close-button');
    expect(closeButton.getAttribute('aria-label')).toBe('Close keyboard shortcuts help');
  });

  it('calls getShortcuts from keyboard shortcuts service', async () => {
    const keyboardShortcuts = await import('@/services/keyboardShortcuts');
    expect(keyboardShortcuts.default.getShortcuts).toHaveBeenCalled();
  });
});