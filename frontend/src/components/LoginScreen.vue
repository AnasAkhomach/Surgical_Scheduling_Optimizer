<template>
  <div class="login-container">
    <div class="login-box">
      <header class="app-header">
        <!-- Placeholder for Logo -->
        <!-- Using /vite.svg directly as it's in the public directory -->
        <img src="/vite.svg" alt="App Logo" class="app-logo">
        <h1>Surgery Scheduling System</h1>
      </header>
      <h2 class="form-title">{{ isRegistering ? 'Create Account' : 'Login' }}</h2>

      <!-- Login Form -->
      <form v-if="!isRegistering" class="login-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input type="text" id="username" name="username" v-model="username" required autocomplete="username">
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" v-model="password" required autocomplete="current-password">
          <!-- Password visibility toggle could be added later -->
        </div>
        <button type="submit" class="login-button" :disabled="isLoading">{{ isLoading ? 'Logging in...' : 'Login' }}</button>
         <!-- Display login error -->
        <p v-if="loginError" class="error-message" aria-live="polite">{{ loginError }}</p>

        <p class="toggle-form-link">
          Don't have an account? <a href="#" @click.prevent="toggleForm">Create one</a>
        </p>
        <!-- Forgot password link only if FR-AUTH-005 is implemented -->
        <!-- <a href="#" class="forgot-password-link">Forgot Password?</a> -->
      </form>

      <!-- Registration Form -->
      <form v-if="isRegistering" class="login-form" @submit.prevent="handleRegister">
        <div class="input-group">
          <label for="new-username">Username *</label>
          <input
            type="text"
            id="new-username"
            v-model="newUsername"
            required
            autocomplete="new-username"
            :class="{ 'error': validationErrors.username }"
            @blur="validateUsername"
          >
          <span v-if="validationErrors.username" class="field-error">{{ validationErrors.username }}</span>
        </div>
        <div class="input-group">
          <label for="new-email">Email *</label>
          <input
            type="email"
            id="new-email"
            v-model="newEmail"
            required
            autocomplete="email"
            :class="{ 'error': validationErrors.email }"
            @blur="validateEmail"
          >
          <span v-if="validationErrors.email" class="field-error">{{ validationErrors.email }}</span>
        </div>
        <div class="input-group">
          <label for="full-name">Full Name</label>
          <input
            type="text"
            id="full-name"
            v-model="fullName"
            autocomplete="name"
          >
        </div>
        <div class="input-group">
          <label for="new-password">Password *</label>
          <input
            type="password"
            id="new-password"
            v-model="newPassword"
            required
            autocomplete="new-password"
            :class="{ 'error': validationErrors.password }"
            @blur="validatePassword"
          >
          <span v-if="validationErrors.password" class="field-error">{{ validationErrors.password }}</span>
          <div class="password-strength" v-if="newPassword">
            <div class="strength-bar">
              <div :class="['strength-fill', passwordStrength.class]" :style="{ width: passwordStrength.width }"></div>
            </div>
            <span :class="['strength-text', passwordStrength.class]">{{ passwordStrength.text }}</span>
          </div>
        </div>
        <div class="input-group">
          <label for="confirm-password">Confirm Password *</label>
          <input
            type="password"
            id="confirm-password"
            v-model="confirmPassword"
            required
            autocomplete="new-password"
            :class="{ 'error': validationErrors.confirmPassword }"
            @blur="validateConfirmPassword"
          >
          <span v-if="validationErrors.confirmPassword" class="field-error">{{ validationErrors.confirmPassword }}</span>
        </div>
        <button type="submit" class="login-button" :disabled="isLoading || !isFormValid">
          {{ isLoading ? 'Creating Account...' : 'Create Account' }}
        </button>
         <!-- Display registration errors/success -->
        <p v-if="registrationError" class="error-message" aria-live="polite">{{ registrationError }}</p>
        <p v-if="registrationSuccess" class="success-message" aria-live="polite">{{ registrationSuccess }}</p>

        <p class="toggle-form-link">
          Already have an account? <a href="#" @click.prevent="toggleForm">Login</a>
        </p>
      </form>

      <!-- Optional Footer -->
      <footer class="app-footer">
        <p>&copy; 2023 Your Organization. All rights reserved.</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const router = useRouter();
const authStore = useAuthStore(); // Initialize auth store

const username = ref('');
const password = ref('');
const loginError = ref('');

const isRegistering = ref(false);
const newUsername = ref('');
const newEmail = ref('');
const fullName = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const registrationError = ref('');
const registrationSuccess = ref('');

const isLoading = ref(false); // State to manage loading indicator

// Validation
const validationErrors = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

// Computed properties
const passwordStrength = computed(() => {
  const password = newPassword.value;
  if (!password) return { class: '', width: '0%', text: '' };

  let score = 0;
  let feedback = [];

  // Length check
  if (password.length >= 8) score += 1;
  else feedback.push('at least 8 characters');

  // Uppercase check
  if (/[A-Z]/.test(password)) score += 1;
  else feedback.push('uppercase letter');

  // Lowercase check
  if (/[a-z]/.test(password)) score += 1;
  else feedback.push('lowercase letter');

  // Number check
  if (/\d/.test(password)) score += 1;
  else feedback.push('number');

  // Special character check
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
  else feedback.push('special character');

  const strength = {
    0: { class: 'very-weak', width: '20%', text: 'Very Weak' },
    1: { class: 'weak', width: '40%', text: 'Weak' },
    2: { class: 'fair', width: '60%', text: 'Fair' },
    3: { class: 'good', width: '80%', text: 'Good' },
    4: { class: 'strong', width: '100%', text: 'Strong' },
    5: { class: 'very-strong', width: '100%', text: 'Very Strong' }
  };

  return strength[score] || strength[0];
});

const isFormValid = computed(() => {
  return newUsername.value &&
         newEmail.value &&
         newPassword.value &&
         confirmPassword.value &&
         !validationErrors.value.username &&
         !validationErrors.value.email &&
         !validationErrors.value.password &&
         !validationErrors.value.confirmPassword;
});

// Validation functions
const validateUsername = () => {
  const username = newUsername.value.trim();
  if (!username) {
    validationErrors.value.username = 'Username is required';
  } else if (username.length < 3) {
    validationErrors.value.username = 'Username must be at least 3 characters';
  } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    validationErrors.value.username = 'Username can only contain letters, numbers, and underscores';
  } else {
    validationErrors.value.username = '';
  }
};

const validateEmail = () => {
  const email = newEmail.value.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    validationErrors.value.email = 'Email is required';
  } else if (!emailRegex.test(email)) {
    validationErrors.value.email = 'Please enter a valid email address';
  } else {
    validationErrors.value.email = '';
  }
};

const validatePassword = () => {
  const password = newPassword.value;
  if (!password) {
    validationErrors.value.password = 'Password is required';
  } else if (password.length < 8) {
    validationErrors.value.password = 'Password must be at least 8 characters';
  } else {
    validationErrors.value.password = '';
  }
  // Re-validate confirm password if it exists
  if (confirmPassword.value) {
    validateConfirmPassword();
  }
};

const validateConfirmPassword = () => {
  if (!confirmPassword.value) {
    validationErrors.value.confirmPassword = 'Please confirm your password';
  } else if (newPassword.value !== confirmPassword.value) {
    validationErrors.value.confirmPassword = 'Passwords do not match';
  } else {
    validationErrors.value.confirmPassword = '';
  }
};

// --- Authentication Logic ---
const handleLogin = async () => {
  loginError.value = ''; // Clear previous errors

  if (!username.value || !password.value) {
    loginError.value = 'Please enter both username and password.';
    return;
  }

  isLoading.value = true; // Show loading indicator

  try {
    await authStore.login(username.value, password.value);
    // Check if there was an error from the auth store
    if (authStore.error) {
      loginError.value = authStore.error;
    } else if (authStore.isAuthenticated) {
      // Successful login - redirect is handled by the authStore
      router.push({ name: 'Dashboard' });
    }
  } catch (error) {
    console.error('Login component error:', error);
    loginError.value = 'An unexpected error occurred during login.';
  } finally {
    isLoading.value = false;
  }
};

const handleRegister = async () => {
  loginError.value = ''; // Clear login errors on register attempt
  registrationError.value = '';
  registrationSuccess.value = ''; // Clear previous success/error messages

  // Validate all fields
  validateUsername();
  validateEmail();
  validatePassword();
  validateConfirmPassword();

  // Check if form is valid
  if (!isFormValid.value) {
    registrationError.value = 'Please fix the errors above.';
    return;
  }

  isLoading.value = true; // Show loading indicator

  try {
    const success = await authStore.register(
      newUsername.value,
      newPassword.value,
      newEmail.value,
      fullName.value
    );
    if (success) {
      registrationSuccess.value = 'Account created successfully! Please log in.';
      // Clear form
      newUsername.value = '';
      newEmail.value = '';
      fullName.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
      // Clear validation errors
      validationErrors.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      };
      isRegistering.value = false; // Switch to login form
    } else {
      // Check authStore.error for the specific error message
      registrationError.value = authStore.error || 'Registration failed.';
    }
  } catch (error) {
    console.error('Registration component error:', error);
    registrationError.value = 'An unexpected error occurred during registration.';
  } finally {
    isLoading.value = false;
  }
};

const toggleForm = () => {
  isRegistering.value = !isRegistering.value;
  loginError.value = ''; // Clear errors when toggling
  registrationError.value = '';
  registrationSuccess.value = ''; // Clear success message when form is manually toggled
  // Clear input fields when toggling
  username.value = '';
  password.value = '';
  if (!isRegistering.value) { // Only clear new user fields when switching *to* login
      newUsername.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--color-background); /* Use global background variable */
  color: var(--color-very-dark-gray); /* Use global text color variable */
}

.login-box {
  background-color: var(--color-white); /* Use global white variable */
  padding: var(--spacing-xl); /* Use global spacing variable */
  border-radius: var(--border-radius-md); /* Use global border radius variable */
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.app-header {
  margin-bottom: var(--spacing-lg); /* Use global spacing variable */
}

.app-logo {
  height: 70px;
  margin-bottom: var(--spacing-md); /* Use global spacing variable */
}

.app-header h1 {
  font-size: var(--font-size-xl); /* Use global font size variable */
  color: var(--color-very-dark-gray);
  margin: 0;
}

.form-title {
  font-size: var(--font-size-lg); /* Use global font size variable */
  color: var(--color-very-dark-gray);
  margin-bottom: var(--spacing-lg); /* Use global spacing variable */
}

.login-form {
  text-align: left;
}

.input-group {
  margin-bottom: var(--spacing-md); /* Use global spacing variable */
}

.input-group label {
  display: block;
  margin-bottom: var(--spacing-xs); /* Use global spacing variable */
  font-weight: var(--font-weight-medium); /* Use global font weight variable */
  color: var(--color-dark-gray); /* Use global text color variable */
  font-size: var(--font-size-base); /* Use global font size variable */
}

.input-group input[type="text"],
.input-group input[type="password"],
.input-group input[type="email"] {
  width: 100%;
  padding: var(--spacing-sm); /* Use global spacing variable */
  border: 1px solid var(--color-gray); /* Use global border color variable */
  border-radius: var(--border-radius-sm); /* Use global border radius variable */
  box-sizing: border-box;
  font-size: var(--font-size-base); /* Use global font size variable */
  color: var(--color-very-dark-gray);
  background-color: var(--color-white);
  transition: border-color 0.2s ease;
}

.input-group input.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

/* Consistent focus styles using global variables */
.input-group input[type="text"]:focus,
.input-group input[type="password"]:focus {
    outline: 2px solid var(--color-accent); /* Use global accent color for focus */
    outline-offset: 2px;
    border-color: transparent; /* Hide default border on focus */
    box-shadow: none; /* Remove default shadow */
}

.login-button {
  width: 100%;
  padding: var(--spacing-sm); /* Use global spacing variable */
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: var(--border-radius-sm); /* Use global border radius variable */
  font-size: var(--font-size-base); /* Use global font size variable */
  font-weight: var(--font-weight-medium); /* Use global font weight variable */
  cursor: pointer;
  transition: background-color 0.25s ease, opacity 0.25s ease; /* Add opacity transition for disabled state */
}

.login-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.login-button:disabled {
    opacity: 0.7; /* Dim disabled button */
    cursor: not-allowed;
}

.forgot-password-link {
  display: block;
  margin-top: var(--spacing-md); /* Use global spacing variable */
  font-size: var(--font-size-sm); /* Use global font size variable */
  color: var(--color-primary);
  text-decoration: none;
  text-align: center; /* Center the link */
}

.forgot-password-link:hover {
  text-decoration: underline;
}

.toggle-form-link {
  text-align: center;
  margin-top: var(--spacing-md); /* Use global spacing variable */
  font-size: var(--font-size-sm); /* Use global font size variable */
   color: var(--color-very-dark-gray); /* Use global text color */
}

.toggle-form-link a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-bold); /* Use global font weight variable */
}

.toggle-form-link a:hover {
  text-decoration: underline;
}

.app-footer {
  margin-top: var(--spacing-lg); /* Use global spacing variable */
  font-size: var(--font-size-sm); /* Use global font size variable */
  color: var(--color-dark-gray); /* Use global text color variable */
}

.error-message {
  color: var(--color-danger); /* Use global danger color variable */
  margin-top: var(--spacing-md); /* Use global spacing variable */
  font-size: var(--font-size-sm); /* Use global font size variable */
  text-align: center; /* Center error message */
}

.success-message {
  color: var(--color-success); /* Use global success color variable */
  margin-top: var(--spacing-md); /* Use global spacing variable */
  font-size: var(--font-size-sm); /* Use global font size variable */
  text-align: center;
}

.field-error {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.password-strength {
  margin-top: 8px;
}

.strength-bar {
  width: 100%;
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-fill.very-weak {
  background-color: #dc3545;
}

.strength-fill.weak {
  background-color: #fd7e14;
}

.strength-fill.fair {
  background-color: #ffc107;
}

.strength-fill.good {
  background-color: #20c997;
}

.strength-fill.strong {
  background-color: #28a745;
}

.strength-fill.very-strong {
  background-color: #198754;
}

.strength-text {
  font-size: 12px;
  font-weight: 500;
}

.strength-text.very-weak {
  color: #dc3545;
}

.strength-text.weak {
  color: #fd7e14;
}

.strength-text.fair {
  color: #ffc107;
}

.strength-text.good {
  color: #20c997;
}

.strength-text.strong {
  color: #28a745;
}

.strength-text.very-strong {
  color: #198754;
}
</style>