<template>
  <div class="user-management">
    <div class="header">
      <h2>User Management</h2>
      <button @click="showCreateForm = true" class="btn btn-primary">
        <i class="icon-plus"></i> Add New User
      </button>
    </div>

    <!-- User Creation Form -->
    <div v-if="showCreateForm" class="modal-overlay" @click="closeCreateForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New User</h3>
          <button @click="closeCreateForm" class="btn-close">&times;</button>
        </div>
        <form @submit.prevent="createUser" class="user-form">
          <div class="form-group">
            <label for="username">Username *</label>
            <input 
              type="text" 
              id="username" 
              v-model="newUser.username" 
              required 
              :disabled="isLoading"
            >
          </div>
          <div class="form-group">
            <label for="email">Email *</label>
            <input 
              type="email" 
              id="email" 
              v-model="newUser.email" 
              required 
              :disabled="isLoading"
            >
          </div>
          <div class="form-group">
            <label for="password">Password *</label>
            <input 
              type="password" 
              id="password" 
              v-model="newUser.password" 
              required 
              :disabled="isLoading"
            >
          </div>
          <div class="form-group">
            <label for="fullName">Full Name</label>
            <input 
              type="text" 
              id="fullName" 
              v-model="newUser.full_name" 
              :disabled="isLoading"
            >
          </div>
          <div class="form-group">
            <label for="role">Role *</label>
            <select id="role" v-model="newUser.role" required :disabled="isLoading">
              <option value="">Select Role</option>
              <option value="user">User</option>
              <option value="admin">Admin</option>
              <option value="surgeon">Surgeon</option>
              <option value="staff">Staff</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeCreateForm" class="btn btn-secondary" :disabled="isLoading">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Creating...' : 'Create User' }}
            </button>
          </div>
          <div v-if="createError" class="error-message">{{ createError }}</div>
        </form>
      </div>
    </div>

    <!-- Users List -->
    <div class="users-list">
      <div v-if="loadingUsers" class="loading">Loading users...</div>
      <div v-else-if="users.length === 0" class="no-users">No users found.</div>
      <div v-else class="users-table">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Full Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.full_name || '-' }}</td>
              <td>
                <span :class="['role-badge', `role-${user.role}`]">
                  {{ user.role }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td class="actions">
                <button @click="editUser(user)" class="btn btn-sm btn-secondary">Edit</button>
                <button 
                  @click="deleteUser(user)" 
                  class="btn btn-sm btn-danger"
                  :disabled="user.user_id === currentUser?.user_id"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const users = ref([])
const loadingUsers = ref(false)
const showCreateForm = ref(false)
const isLoading = ref(false)
const createError = ref('')

const newUser = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: ''
})

// Computed
const currentUser = computed(() => authStore.user)

// Methods
const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await fetch('http://localhost:8000/api/users', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    if (response.ok) {
      users.value = await response.json()
    } else {
      throw new Error('Failed to load users')
    }
  } catch (error) {
    console.error('Error loading users:', error)
    toast.error('Failed to load users')
  } finally {
    loadingUsers.value = false
  }
}

const createUser = async () => {
  isLoading.value = true
  createError.value = ''
  
  try {
    const response = await fetch('http://localhost:8000/api/users/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(newUser.value)
    })
    
    if (response.ok) {
      toast.success('User created successfully')
      closeCreateForm()
      await loadUsers()
    } else {
      const errorData = await response.json()
      createError.value = errorData.detail || 'Failed to create user'
    }
  } catch (error) {
    console.error('Error creating user:', error)
    createError.value = 'An unexpected error occurred'
  } finally {
    isLoading.value = false
  }
}

const closeCreateForm = () => {
  showCreateForm.value = false
  newUser.value = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: ''
  }
  createError.value = ''
}

const editUser = (user) => {
  // TODO: Implement edit functionality
  toast.info('Edit functionality coming soon')
}

const deleteUser = async (user) => {
  if (!confirm(`Are you sure you want to delete user "${user.username}"?`)) {
    return
  }
  
  try {
    const response = await fetch(`http://localhost:8000/api/users/${user.user_id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      toast.success('User deleted successfully')
      await loadUsers()
    } else {
      const errorData = await response.json()
      toast.error(errorData.detail || 'Failed to delete user')
    }
  } catch (error) {
    console.error('Error deleting user:', error)
    toast.error('An unexpected error occurred')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 0;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.user-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.users-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background: #f8f9fa;
  font-weight: 600;
}

.role-badge,
.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-admin {
  background: #dc3545;
  color: white;
}

.role-surgeon {
  background: #28a745;
  color: white;
}

.role-staff {
  background: #ffc107;
  color: #212529;
}

.role-user {
  background: #6c757d;
  color: white;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  gap: 8px;
}

.loading,
.no-users {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
  font-size: 14px;
}
</style>
