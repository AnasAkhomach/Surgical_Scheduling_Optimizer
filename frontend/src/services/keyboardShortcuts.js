// Keyboard Shortcuts Service
// This service manages keyboard shortcuts for the application

class KeyboardShortcutsService {
  constructor() {
    this.shortcuts = new Map();
    this.isListening = false;
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  // Register a keyboard shortcut
  register(key, callback, options = {}) {
    const shortcut = {
      key: key.toLowerCase(),
      callback,
      ctrlKey: options.ctrlKey || false,
      altKey: options.altKey || false,
      shiftKey: options.shiftKey || false,
      metaKey: options.metaKey || false,
      description: options.description || '',
      scope: options.scope || 'global',
      disabled: options.disabled || false
    };

    // Create a unique ID for this shortcut
    const id = this.getShortcutId(shortcut);
    this.shortcuts.set(id, shortcut);

    // Start listening if not already
    if (!this.isListening) {
      this.startListening();
    }

    // Return a function to unregister this shortcut
    return () => this.unregister(id);
  }

  // Unregister a keyboard shortcut
  unregister(id) {
    this.shortcuts.delete(id);
    
    // Stop listening if no shortcuts remain
    if (this.shortcuts.size === 0) {
      this.stopListening();
    }
  }

  // Enable a shortcut
  enable(id) {
    const shortcut = this.shortcuts.get(id);
    if (shortcut) {
      shortcut.disabled = false;
    }
  }

  // Disable a shortcut
  disable(id) {
    const shortcut = this.shortcuts.get(id);
    if (shortcut) {
      shortcut.disabled = true;
    }
  }

  // Start listening for keyboard events
  startListening() {
    if (!this.isListening) {
      document.addEventListener('keydown', this.handleKeyDown);
      this.isListening = true;
    }
  }

  // Stop listening for keyboard events
  stopListening() {
    document.removeEventListener('keydown', this.handleKeyDown);
    this.isListening = false;
  }

  // Handle keydown events
  handleKeyDown(event) {
    // Skip if the event target is an input, textarea, or select
    if (this.shouldIgnoreEvent(event)) {
      return;
    }

    // Check if any registered shortcut matches this event
    for (const [id, shortcut] of this.shortcuts.entries()) {
      if (this.matchesShortcut(event, shortcut) && !shortcut.disabled) {
        event.preventDefault();
        shortcut.callback(event);
        break;
      }
    }
  }

  // Check if an event should be ignored (e.g., when typing in an input field)
  shouldIgnoreEvent(event) {
    const target = event.target;
    const tagName = target.tagName.toLowerCase();
    
    // Ignore if target is an input, textarea, or select
    if (tagName === 'input' || tagName === 'textarea' || tagName === 'select') {
      return true;
    }
    
    // Ignore if target has contentEditable attribute
    if (target.isContentEditable) {
      return true;
    }
    
    return false;
  }

  // Check if an event matches a shortcut
  matchesShortcut(event, shortcut) {
    const key = event.key.toLowerCase();
    
    return (
      key === shortcut.key &&
      event.ctrlKey === shortcut.ctrlKey &&
      event.altKey === shortcut.altKey &&
      event.shiftKey === shortcut.shiftKey &&
      event.metaKey === shortcut.metaKey
    );
  }

  // Get a unique ID for a shortcut
  getShortcutId(shortcut) {
    return `${shortcut.key}_${shortcut.ctrlKey}_${shortcut.altKey}_${shortcut.shiftKey}_${shortcut.metaKey}_${shortcut.scope}`;
  }

  // Get all registered shortcuts
  getShortcuts() {
    return Array.from(this.shortcuts.values());
  }

  // Get shortcuts for a specific scope
  getShortcutsForScope(scope) {
    return Array.from(this.shortcuts.values())
      .filter(shortcut => shortcut.scope === scope);
  }
}

// Create a singleton instance
const keyboardShortcuts = new KeyboardShortcutsService();

export default keyboardShortcuts;
