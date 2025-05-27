<template>
  <div class="login-container">
    <Card class="login-card">
      <template #title>
        <div class="text-center">
          <h1 class="text-3xl font-bold">Surgery Scheduler</h1>
          <h2 class="text-xl text-gray-600">Login</h2>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="login" class="p-fluid">
          <div class="field">
            <label for="username">Username</label>
            <InputText 
              id="username" 
              v-model="username" 
              :class="{ 'p-invalid': submitted && !username }"
              aria-describedby="username-error"
            />
            <small id="username-error" class="p-error" v-if="submitted && !username">Username is required.</small>
          </div>
          
          <div class="field">
            <label for="password">Password</label>
            <InputText 
              id="password" 
              type="password" 
              v-model="password" 
              :class="{ 'p-invalid': submitted && !password }"
              aria-describedby="password-error"
            />
            <small id="password-error" class="p-error" v-if="submitted && !password">Password is required.</small>
          </div>
          
          <div v-if="error" class="p-error mb-3">{{ error }}</div>
          
          <Button 
            type="submit" 
            label="Login" 
            icon="pi pi-sign-in" 
            :loading="loading"
            class="mt-3"
          />
        </form>
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Login',
  emits: ['login-success'],
  setup(props, { emit }) {
    const store = useStore()
    
    const username = ref('')
    const password = ref('')
    const submitted = ref(false)
    
    const loading = computed(() => store.getters['isLoading'])
    const error = computed(() => store.getters['errorMessage'])
    
    const login = async () => {
      submitted.value = true
      
      // Validate form
      if (!username.value || !password.value) {
        return
      }
      
      // Clear previous errors
      store.dispatch('clearError')
      
      // Attempt login
      const success = await store.dispatch('auth/login', {
        username: username.value,
        password: password.value
      })
      
      if (success) {
        emit('login-success')
      }
    }
    
    return {
      username,
      password,
      submitted,
      loading,
      error,
      login
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
