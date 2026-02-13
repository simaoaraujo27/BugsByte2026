<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'

const router = useRouter()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const calorieBudget = ref(1850)
const errorMessage = ref('')
const successMessage = ref('')

// Clear messages on input
const clearMessages = () => {
    errorMessage.value = ''
    successMessage.value = ''
}

const handleLogin = async () => {
  clearMessages()
  // Basic validation logic
  if (!email.value || !password.value) {
    errorMessage.value = 'Please fill in all fields before signing in.'
    return
  }
  
  try {
    const response = await fetch('http://localhost:8000/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: email.value, 
        password: password.value,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Login failed')
    }

    const data = await response.json()
    console.log('Login successful:', data)
    successMessage.value = 'Welcome back, Chef!'
    
    // Store user info
    localStorage.setItem('user_id', data.user_id)
    
    setTimeout(() => { 
        successMessage.value = '' 
        // Redirect to dashboard
        router.push('/dashboard')
    }, 1500)

  } catch (error) {
    console.error('Login error:', error)
    errorMessage.value = error.message
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      
      <!-- Header / Logo Area -->
      <div class="text-center mb-8">
        <div class="logo-container">
            <img :src="logo" alt="NutriVentures Logo" />
        </div>
        <h1 class="auth-title">NutriVentures</h1>
        <p class="auth-subtitle">Smart Food Negotiator</p>
      </div>

      <!-- Live Region for Alerts -->
      <div role="alert" aria-live="assertive" class="min-h-[1.5rem] mb-4">
          <p v-if="errorMessage" class="message error">
              <span class="mr-2" aria-hidden="true">⚠️</span> {{ errorMessage }}
          </p>
          <p v-if="successMessage" class="message success">
              <span class="mr-2" aria-hidden="true">✅</span> {{ successMessage }}
          </p>
      </div>
      
      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="auth-form" novalidate>
        <div class="form-group">
          <label for="email">Email Address</label>
          <input 
            v-model="email"
            @input="clearMessages"
            type="email" 
            id="email"
            autocomplete="email"
            required
            placeholder="chef@nutriventures.com"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            v-model="password"
            @input="clearMessages"
            type="password" 
            id="password"
            autocomplete="current-password"
            required
            placeholder="••••••••"
          />
        </div>

        <div class="flex items-center justify-between mb-6">
          <label class="checkbox-label">
            <input 
              v-model="rememberMe"
              type="checkbox" 
            />
            <span class="ml-2">Remember me</span>
          </label>
          <router-link to="/forgot-password" class="forgot-link">Forgot password?</router-link>
        </div>

        <button type="submit" class="btn btn-primary">
          Sign In
        </button>
        
        <div class="text-center mt-6">
          <span class="text-sm text-gray-600">Don't have an account? </span>
          <router-link to="/signup" class="signup-link">
            Sign up instead
          </router-link>
        </div>
      </form>

      <!-- Divider -->
      <div class="divider">
        <span>Hackathon Mode</span>
      </div>

      <!-- Footer -->
      <div class="footer">
        <router-link to="/" class="back-link">
          &larr; Back to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Unified Auth Page Style (Same as Signup/Forgot) */
.auth-page {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('https://images.unsplash.com/photo-1490818387583-1baba5e638af?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 20px;
}

.auth-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

.auth-card {
  --bg-soft: #ffffff;
  --text-main: #13293d;
  --text-muted: #3b566d;
  --accent: #0f766e;
  --accent-hover: #0b5c56;
  --line: #d7e7e0;
  --error: #e53e3e;
  --success: #38a169;

  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 450px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  color: var(--text-main);
}

.logo-container {
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.logo-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.auth-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
}

.auth-subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-top: 4px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.checkbox-label {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  cursor: pointer;
  color: var(--text-muted);
}

.checkbox-label input {
  accent-color: var(--accent);
  width: 16px;
  height: 16px;
}

.forgot-link {
  font-size: 0.9rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
}

.forgot-link:hover {
  text-decoration: underline;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 999px;
  background: var(--accent);
  color: white;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(15, 118, 110, 0.2);
}

.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(15, 118, 110, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}

.signup-link {
  color: var(--accent);
  font-weight: 700;
  text-decoration: none;
}

.signup-link:hover {
  text-decoration: underline;
}

.message {
  padding: 10px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.message.error {
  background: #fff5f5;
  color: var(--error);
  border: 1px solid #feb2b2;
}

.message.success {
  background: #f0fff4;
  color: var(--success);
  border: 1px solid #9ae6b4;
}

.divider {
  margin: 30px 0;
  position: relative;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  border-top: 1px solid var(--line);
}

.divider span {
  background: white; /* Matches form bg but slightly simpler */
  padding: 0 10px;
  position: relative;
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(255, 255, 255, 0.95); /* Match card bg */
}

.footer {
  text-align: center;
  margin-top: 20px;
}

.back-link {
  color: var(--text-muted);
  font-size: 0.9rem;
  text-decoration: none;
  font-weight: 600;
}

.back-link:hover {
  color: var(--text-main);
}
</style>
