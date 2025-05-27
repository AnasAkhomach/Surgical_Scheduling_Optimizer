<template>
  <Teleport to="body">
    <div v-if="isVisible" class="keyboard-shortcuts-overlay" data-testid="keyboard-shortcuts" @click="close">
      <div class="keyboard-shortcuts-modal" @click.stop>
        <div class="modal-header">
          <h2>Keyboard Shortcuts</h2>
          <button class="close-button" @click="close" aria-label="Close keyboard shortcuts help">
            ✕
          </button>
        </div>
        <div class="modal-body">
          <div v-for="(shortcuts, scope) in groupedShortcuts" :key="scope" class="shortcut-group">
            <h3>{{ formatScopeName(scope) }}</h3>
            <table>
              <thead>
                <tr>
                  <th>Shortcut</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(shortcut, index) in shortcuts" :key="index">
                  <td>
                    <div class="shortcut-keys">
                      <span v-if="shortcut.ctrlKey" class="key">Ctrl</span>
                      <span v-if="shortcut.altKey" class="key">Alt</span>
                      <span v-if="shortcut.shiftKey" class="key">Shift</span>
                      <span v-if="shortcut.metaKey" class="key">Meta</span>
                      <span class="key">{{ formatKeyName(shortcut.key) }}</span>
                    </div>
                  </td>
                  <td>{{ shortcut.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="close">Close</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import keyboardShortcuts from '@/services/keyboardShortcuts';

const isVisible = ref(false);

// Group shortcuts by scope
const groupedShortcuts = computed(() => {
  const shortcuts = keyboardShortcuts.getShortcuts();
  const groups = {};

  shortcuts.forEach(shortcut => {
    if (!groups[shortcut.scope]) {
      groups[shortcut.scope] = [];
    }
    groups[shortcut.scope].push(shortcut);
  });

  return groups;
});

// Format scope name for display
const formatScopeName = (scope) => {
  return scope.charAt(0).toUpperCase() + scope.slice(1);
};

// Format key name for display
const formatKeyName = (key) => {
  const specialKeys = {
    ' ': 'Space',
    'arrowup': '↑',
    'arrowdown': '↓',
    'arrowleft': '←',
    'arrowright': '→',
    'escape': 'Esc',
    'delete': 'Del',
    'backspace': 'Backspace',
    'tab': 'Tab',
    'enter': 'Enter',
    'return': 'Return',
    'capslock': 'Caps',
    'shift': 'Shift',
    'control': 'Ctrl',
    'alt': 'Alt',
    'meta': 'Meta',
    'pageup': 'PgUp',
    'pagedown': 'PgDn',
    'home': 'Home',
    'end': 'End',
    'insert': 'Ins',
    'f1': 'F1',
    'f2': 'F2',
    'f3': 'F3',
    'f4': 'F4',
    'f5': 'F5',
    'f6': 'F6',
    'f7': 'F7',
    'f8': 'F8',
    'f9': 'F9',
    'f10': 'F10',
    'f11': 'F11',
    'f12': 'F12',
  };

  const formattedKey = specialKeys[key.toLowerCase()] || key.toUpperCase();
  return formattedKey;
};

// Show the keyboard shortcuts help
const show = () => {
  isVisible.value = true;
};

// Close the keyboard shortcuts help
const close = () => {
  isVisible.value = false;
};

// Toggle the keyboard shortcuts help
const toggle = () => {
  isVisible.value = !isVisible.value;
};

// Register keyboard shortcut to show/hide the help
let unregisterShortcut;

onMounted(() => {
  unregisterShortcut = keyboardShortcuts.register('?', toggle, {
    shiftKey: true,
    description: 'Show keyboard shortcuts help',
    scope: 'global'
  });
});

onUnmounted(() => {
  if (unregisterShortcut) {
    unregisterShortcut();
  }
});

// Expose methods to parent components
defineExpose({
  show,
  close,
  toggle
});
</script>

<style scoped>
.keyboard-shortcuts-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.keyboard-shortcuts-modal {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-text);
}

.close-button {
  background: none;
  border: none;
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--border-radius-sm);
}

.close-button:hover {
  color: var(--color-text);
  background-color: var(--color-background-mute);
}

.modal-body {
  padding: var(--spacing-md);
  overflow-y: auto;
  flex-grow: 1;
}

.shortcut-group {
  margin-bottom: var(--spacing-lg);
}

.shortcut-group h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
  font-size: var(--font-size-md);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--spacing-xs);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 1px solid var(--color-border-soft);
}

th {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-secondary);
}

.shortcut-keys {
  display: flex;
  gap: var(--spacing-xs);
}

.key {
  display: inline-block;
  padding: 2px 6px;
  background-color: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  font-family: monospace;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  min-width: 20px;
  text-align: center;
}

.modal-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}
</style>
