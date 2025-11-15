<!--
Login Component
Handles user and admin login/registration
Setup: Include this component in your Vue app
-->

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h3 class="text-center mb-0">Vehicle Parking App</h3>
          </div>
          <div class="card-body">
            <!-- Tabs for Login/Register -->
            <ul class="nav nav-tabs mb-3" role="tablist">
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isLogin }" @click="isLogin = true" href="#">Login</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: !isLogin }" @click="isLogin = false" href="#">Register</a>
              </li>
            </ul>

            <!-- Login Form -->
            <div v-if="isLogin">
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="loginUsername" class="form-label">Username</label>
                  <input
                    type="text"
                    class="form-control"
                    id="loginUsername"
                    v-model="loginForm.username"
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="loginPassword" class="form-label">Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="loginPassword"
                    v-model="loginForm.password"
                    required
                  />
                </div>
                <div class="alert alert-info">
                  <small>Default admin: username='admin', password='admin123'</small>
                </div>
                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  {{ loading ? 'Logging in...' : 'Login' }}
                </button>
              </form>
            </div>

            <!-- Register Form -->
            <div v-if="!isLogin">
              <form @submit.prevent="handleRegister">
                <div class="mb-3">
                  <label for="regUsername" class="form-label">Username</label>
                  <input
                    type="text"
                    class="form-control"
                    id="regUsername"
                    v-model="registerForm.username"
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="regPassword" class="form-label">Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="regPassword"
                    v-model="registerForm.password"
                    required
                  />
                </div>
                <button type="submit" class="btn btn-success w-100" :disabled="loading">
                  {{ loading ? 'Registering...' : 'Register' }}
                </button>
              </form>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="alert alert-danger mt-3">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default {
  name: 'Login',
  data() {
    return {
      isLogin: true,
      loading: false,
      error: '',
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        password: ''
      }
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/login`, this.loginForm);
        
        // Store token and user info
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Redirect based on role
        if (response.data.user.role === 'admin') {
          this.$router.push('/admin');
        } else {
          this.$router.push('/user');
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    async handleRegister() {
      this.loading = true;
      this.error = '';
      
      try {
        await axios.post(`${API_BASE_URL}/auth/register`, this.registerForm);
        this.error = '';
        alert('Registration successful! Please login.');
        this.isLogin = true;
        this.loginForm.username = this.registerForm.username;
        this.registerForm = { username: '', password: '' };
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.nav-tabs .nav-link {
  cursor: pointer;
}
</style>

