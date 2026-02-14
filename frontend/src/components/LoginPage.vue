<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'
import { auth } from '@/auth'

const router = useRouter()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)
const calorieBudget = ref(1850)
const errorMessage = ref('')
const successMessage = ref('')

// Load saved credentials on component mount
onMounted(() => {
  const savedRememberMe = localStorage.getItem('rememberMe') === 'true'
  rememberMe.value = savedRememberMe
  
  if (savedRememberMe) {
    const savedEmail = localStorage.getItem('rememberedEmail')
    const savedPassword = localStorage.getItem('rememberedPassword')
    if (savedEmail) email.value = savedEmail
    if (savedPassword) password.value = savedPassword
    console.log('Loaded saved credentials from localStorage')
  }
})

// Clear messages on input
const clearMessages = () => {
    errorMessage.value = ''
    successMessage.value = ''
}

// Toggle password visibility (used by the eye icon button)
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
  console.log('Password visibility toggled:', showPassword.value ? 'visible' : 'hidden')
}

const handleLogin = async () => {
  if (isLoading.value) return
  
  clearMessages()
  // Basic validation logic
  if (!email.value || !password.value) {
    errorMessage.value = 'Por favor, preencha todos os campos antes de entrar.'
    return
  }
  
  isLoading.value = true
  try {
    const data = await auth.login(email.value, password.value)
    console.log('Login successful:', data)
    successMessage.value = 'Bem-vindo de volta, Chef!'

    // Handle remember me functionality
    localStorage.setItem('rememberMe', rememberMe.value.toString())
    if (rememberMe.value) {
      localStorage.setItem('rememberedEmail', email.value)
      localStorage.setItem('rememberedPassword', password.value)
      console.log('Credentials saved to localStorage')
    } else {
      localStorage.removeItem('rememberedEmail')
      localStorage.removeItem('rememberedPassword')
      console.log('Credentials removed from localStorage')
    }
    
    setTimeout(() => { 
        successMessage.value = '' 
        // Redirect to dashboard
        router.push('/dashboard')
    }, 1500)

  } catch (error) {
    console.error('Login error:', error)
    errorMessage.value = error.message || 'Falha no início de sessão'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      
      <!-- Header / Logo Area -->
      <div class="header-section">
        <div class="logo-container">
            <img :src="logo" alt="Logótipo NutriVentures" />
        </div>
        <h1 class="auth-title">NutriVentures</h1>
        <p class="auth-subtitle">Smart Food Negotiator</p>
      </div>

      <!-- Live Region for Alerts -->
      <div role="alert" aria-live="assertive" class="message-container">
          <p v-if="errorMessage" class="message error">
              <span class="message-icon" aria-hidden="true">⚠️</span> {{ errorMessage }}
          </p>
          <p v-if="successMessage" class="message success">
              <span class="message-icon" aria-hidden="true">✅</span> {{ successMessage }}
          </p>
      </div>
      
      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="auth-form" novalidate>
        <div class="form-group">
          <label for="email">Endereço de E-mail</label>
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
          <label for="password">Palavra-passe</label>
          <div class="password-input-wrapper">
            <input 
              v-model="password"
              @input="clearMessages"
              :type="showPassword ? 'text' : 'password'" 
              id="password"
              autocomplete="current-password"
              required
              placeholder="••••••••"
            />
            <button 
              type="button"
              @click="togglePasswordVisibility"
              class="password-toggle"
              :aria-label="showPassword ? 'Ocultar palavra-passe' : 'Mostrar palavra-passe'"
            >
              <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
          </div>
        </div>

        <div class="remember-forgot-row">
          <div class="checkbox-group">
            <label class="checkbox-label" for="remember-me">
              <input 
                v-model="rememberMe"
                type="checkbox"
                id="remember-me"
              />
              <span class="checkbox-text">Lembrar-me</span>
            </label>
          </div>
          <router-link to="/forgot-password" class="forgot-link">Esqueceu-se da palavra-passe?</router-link>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="isLoading">
          <span v-if="isLoading">A entrar...</span>
          <span v-else>Entrar</span>
        </button>
        
        <div class="signup-text">
          <span class="signup-text-muted">Não tem uma conta? </span>
          <router-link to="/signup" class="signup-link">
            Registe-se aqui
          </router-link>
        </div>
      </form>

      <!-- Footer -->
      <div class="footer">
        <router-link to="/" class="back-link">
          &larr; Voltar ao Início
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
  --text-muted: #4b6a88;
  --accent: #0f766e;
  --accent-hover: #0b5c56;
  --line: #e2e8f0;
  --error: #e53e3e;
  --success: #38a169;

  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 480px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  color: var(--text-main);
}

.header-section {
  text-align: center;
  margin-bottom: 24px;
}

.logo-container {
  width: 64px;
  height: 64px;
  background: white;
  border-radius: 18px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}

.logo-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.auth-title {
  font-size: 2.15rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.03em;
  color: #0f172a;
}

.auth-subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-top: 6px;
  font-weight: 500;
}

.message-container {
  min-height: 1.5rem;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #334155;
}

.form-group input {
  width: 100%;
  padding: 14px 16px;
  border: 1.5px solid var(--line);
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #f8fafc;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
  background: white;
  box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.1);
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  padding-right: 50px;
}

.password-toggle {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: var(--accent);
}

.password-toggle svg {
  width: 22px;
  height: 22px;
}

.remember-forgot-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: -8px;
  margin-bottom: 32px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
}

.checkbox-label {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  cursor: pointer;
  color: #64748b;
  user-select: none;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  accent-color: var(--accent);
  width: 20px;
  height: 20px;
  cursor: pointer;
  margin: 0;
  border-radius: 6px;
}

.checkbox-text {
  margin-left: 10px;
}

.forgot-link {
  font-size: 0.875rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.btn-primary {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 14px;
  background: var(--accent);
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 15px -3px rgba(15, 118, 110, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(15, 118, 110, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.signup-text {
  text-align: center;
  margin-top: 28px;
}

.signup-text-muted {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 500;
}

.signup-link {
  color: var(--accent);
  font-weight: 700;
  text-decoration: none;
  margin-left: 4px;
}

.signup-link:hover {
  text-decoration: underline;
}

.message {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.message-icon {
  margin-right: 12px;
  font-size: 1.1rem;
}

.message.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1.5px solid #fee2e2;
}

.message.success {
  background: #f0fdf4;
  color: #166534;
  border: 1.5px solid #dcfce7;
}

.footer {
  text-align: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1.5px solid #f1f5f9;
}

.back-link {
  color: #94a3b8;
  font-size: 0.9rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}

.back-link:hover {
  color: #475569;
}

/* Dark Mode Support */
:global(.theme-dark) .auth-card {
  background: rgba(15, 23, 42, 0.95);
  border-color: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}

:global(.theme-dark) .auth-title {
  color: #f8fafc;
}

:global(.theme-dark) .form-group label {
  color: #cbd5e1;
}

:global(.theme-dark) .form-group input {
  background: #1e293b;
  border-color: #334155;
  color: #f8fafc;
}

:global(.theme-dark) .form-group input:focus {
  border-color: #14b8a6;
  background: #1e293b;
}

:global(.theme-dark) .logo-container {
  background: #1e293b;
}

:global(.theme-dark) .footer {
  border-top-color: #334155;
}

:global(.theme-dark) .back-link {
  color: #64748b;
}

:global(.theme-dark) .signup-text-muted {
  color: #94a3b8;
}

:global(.theme-dark) .checkbox-label {
  color: #94a3b8;
}
</style>
