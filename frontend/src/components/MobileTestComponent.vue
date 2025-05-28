<template>
  <div class="mobile-test-component">
    <h1>Mobile Responsiveness Test</h1>

    <!-- Screen Size Indicator -->
    <div class="screen-info">
      <div class="info-card">
        <h3>Current Screen Info</h3>
        <p><strong>Width:</strong> {{ screenWidth }}px</p>
        <p><strong>Height:</strong> {{ screenHeight }}px</p>
        <p><strong>Device Type:</strong> {{ deviceType }}</p>
        <p><strong>Orientation:</strong> {{ orientation }}</p>
        <p><strong>Touch Device:</strong> {{ isTouchDevice ? 'Yes' : 'No' }}</p>
      </div>
    </div>

    <!-- Responsive Grid Test -->
    <div class="test-section">
      <h2>Responsive Grid Test</h2>
      <div class="responsive-grid">
        <div class="grid-item">Item 1</div>
        <div class="grid-item">Item 2</div>
        <div class="grid-item">Item 3</div>
        <div class="grid-item">Item 4</div>
      </div>
    </div>

    <!-- Touch Target Test -->
    <div class="test-section">
      <h2>Touch Target Test</h2>
      <div class="touch-test">
        <button class="btn-touch">Touch-Friendly Button</button>
        <button class="btn-regular">Regular Button</button>
        <input type="text" placeholder="Touch-friendly input" class="form-control-mobile">
      </div>
    </div>

    <!-- Mobile Navigation Test -->
    <div class="test-section">
      <h2>Mobile Navigation Test</h2>
      <div class="mobile-nav-test">
        <div class="mobile-only">Mobile Only Content</div>
        <div class="tablet-only">Tablet Only Content</div>
        <div class="desktop-only">Desktop Only Content</div>
      </div>
    </div>

    <!-- Responsive Typography Test -->
    <div class="test-section">
      <h2>Typography Test</h2>
      <div class="typography-test">
        <h1>Heading 1</h1>
        <h2>Heading 2</h2>
        <h3>Heading 3</h3>
        <p>This is a paragraph of text that should be readable on all devices.</p>
        <small>Small text for mobile devices</small>
      </div>
    </div>

    <!-- Spacing Test -->
    <div class="test-section">
      <h2>Spacing Test</h2>
      <div class="spacing-test">
        <div class="mobile-p-sm">Mobile Small Padding</div>
        <div class="mobile-p-md">Mobile Medium Padding</div>
        <div class="mobile-p-lg">Mobile Large Padding</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

// Reactive screen dimensions
const screenWidth = ref(window.innerWidth);
const screenHeight = ref(window.innerHeight);

// Computed properties for device detection
const deviceType = computed(() => {
  if (screenWidth.value < 480) return 'Small Mobile';
  if (screenWidth.value < 768) return 'Mobile';
  if (screenWidth.value < 1024) return 'Tablet';
  if (screenWidth.value < 1200) return 'Small Desktop';
  return 'Desktop';
});

const orientation = computed(() => {
  return screenWidth.value > screenHeight.value ? 'Landscape' : 'Portrait';
});

const isTouchDevice = computed(() => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
});

// Handle window resize
const handleResize = () => {
  screenWidth.value = window.innerWidth;
  screenHeight.value = window.innerHeight;
};

// Lifecycle hooks
onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.mobile-test-component {
  padding: var(--spacing-md);
  max-width: 1200px;
  margin: 0 auto;
}

.screen-info {
  margin-bottom: var(--spacing-lg);
}

.info-card {
  background-color: var(--color-background-soft);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  border-left: 4px solid var(--color-primary);
}

.test-section {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
}

.test-section h2 {
  margin-top: 0;
  color: var(--color-primary);
}

/* Grid test styles */
.grid-item {
  background-color: var(--color-primary);
  color: white;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-sm);
  text-align: center;
  font-weight: var(--font-weight-medium);
}

/* Touch test styles */
.touch-test {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  align-items: flex-start;
}

.btn-regular {
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
}

/* Mobile nav test styles */
.mobile-nav-test {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.mobile-nav-test > div {
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  text-align: center;
  font-weight: var(--font-weight-medium);
}

.mobile-only {
  background-color: var(--color-success);
  color: white;
}

.tablet-only {
  background-color: var(--color-warning);
  color: white;
}

.desktop-only {
  background-color: var(--color-primary);
  color: white;
}

/* Typography test styles */
.typography-test {
  line-height: 1.6;
}

/* Spacing test styles */
.spacing-test {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.spacing-test > div {
  background-color: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .mobile-test-component {
    padding: var(--spacing-sm);
  }

  .test-section {
    padding: var(--spacing-sm);
  }

  .touch-test {
    width: 100%;
  }

  .touch-test button,
  .touch-test input {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .mobile-test-component {
    padding: var(--spacing-xs);
  }

  .info-card {
    padding: var(--spacing-sm);
  }

  .test-section {
    padding: var(--spacing-xs);
  }
}
</style>
