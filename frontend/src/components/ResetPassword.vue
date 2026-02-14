<template>
  <div class="auth-page">
    <div class="auth-form-container">
      <h2 class="form-title">Nova Palavra-passe</h2>
      <p class="form-subtitle">Defina uma nova palavra-passe para concluir a recuperação.</p>

      <div v-if="errorMessage" class="message error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="message success">{{ successMessage }}</div>

      <form v-if="!successMessage" @submit.prevent="submitForm" class="form-grid">
        <div class="form-group full-width">
          <label for="password">Nova Palavra-passe</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Mínimo 8 caracteres"
            minlength="8"
            required
          />
        </div>

        <div class="form-group full-width">
          <label for="confirmPassword">Confirmar Palavra-passe</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Repita a palavra-passe"
            minlength="8"
            required
          />
        </div>

        <div class="form-actions full-width">
          <button type="submit" class="btn btn-primary" :disabled="isLoading">
            {{ isLoading ? 'A alterar...' : 'Alterar Palavra-passe' }}
          </button>
        </div>
      </form>

      <div class="login-link">
        <router-link to="/login">Voltar ao Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const submitForm = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  const token = route.query.token
  if (!token || typeof token !== 'string') {
    errorMessage.value = 'Link inválido ou expirado.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'As palavras-passe não coincidem.'
    return
  }

  isLoading.value = true

  try {
    const response = await fetch('http://localhost:8000/reset-password/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: password.value })
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data?.detail || 'Não foi possível alterar a palavra-passe.')
    }

    successMessage.value = data.message || 'Palavra-passe alterada com sucesso.'
    password.value = ''
    confirmPassword.value = ''
  } catch (error) {
    errorMessage.value = error.message || 'Ocorreu um erro ao alterar a palavra-passe.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
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
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

.auth-form-container {
  --text-main: #13293d;
  --text-muted: #3b566d;
  --line: #d7e7e0;
  --accent: #0f766e;
  --accent-hover: #0b5c56;
  --error: #e53e3e;
  --success: #38a169;

  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 480px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  color: var(--text-main);
}

.form-title {
  margin: 0 0 8px;
  font-size: 1.8rem;
  text-align: center;
  color: var(--text-main);
}

.form-subtitle {
  margin: 0 0 24px;
  color: var(--text-muted);
  text-align: center;
}

.message {
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 600;
}

.message.error { background-color: #fff5f5; color: var(--error); border: 1px solid #feb2b2; }
.message.success { background-color: #f0fff4; color: var(--success); border: 1px solid #9ae6b4; }

.form-group { display: flex; flex-direction: column; margin-bottom: 16px; }
.form-group label { margin-bottom: 8px; font-weight: 600; color: var(--text-main); }

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fdfdfd;
  font-size: 1rem;
  color: var(--text-main);
}

.form-group input::placeholder {
  color: #6b7f92;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.form-actions { margin-top: 8px; }

.btn {
  width: 100%;
  border-radius: 999px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 700;
  border: 0;
  cursor: pointer;
  background: var(--accent);
  color: #f2fffc;
}

.btn:hover:not(:disabled) { background: var(--accent-hover); }
.btn:disabled { opacity: 0.7; cursor: not-allowed; }

.login-link { margin-top: 16px; text-align: center; }
.login-link a { color: var(--accent); font-weight: 700; text-decoration: none; }
.login-link a:hover { text-decoration: underline; }
</style>
