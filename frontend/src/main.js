import { createApp } from 'vue'
import { createPinia } from 'pinia' // Add Pinia import
import './style.css'
import App from './App.vue'
import router from './router' // Import the router instance
import 'vue-toastification/dist/index.css'; // Import the CSS FIRST
import Toast from 'vue-toastification'; // Import vue-toastification

const app = createApp(App);
const pinia = createPinia(); // Create Pinia instance

// Test app.provide directly
try {
  if (typeof app.provide === 'function') {
    console.log('app.provide is a function on the app instance created by createApp.');
    app.provide('myCustomTestProvide', 'testValueFromMainJs');
    console.log('Successfully called app.provide directly in main.js.');
  } else {
    console.error('CRITICAL: app.provide is NOT a function on the app instance in main.js.', app);
  }
} catch (e) {
  console.error('Error encountered while testing app.provide directly in main.js:', e);
}

app.use(pinia); // Install Pinia BEFORE mounting
app.use(router); // Use the router
app.use(Toast); // Use vue-toastification

app.mount('#app');