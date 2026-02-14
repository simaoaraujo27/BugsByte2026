<template>
  <div class="auth-page">
    <div class="auth-form-container">
      <h2 class="form-title">Reset Password</h2>
      <p class="form-subtitle">Vamos enviar um link de recuperação para o email associado.</p>

      <div v-if="errorMessage" class="message error">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="message success">
        {{ successMessage }}
      </div>

      <form @submit.prevent="submitForm" class="form-grid">
        <div class="form-group full-width">
          <label>Email associado</label>
          <p class="email-target">{{ targetEmail || 'Sem email disponível' }}</p>
        </div>

        <div class="form-actions full-width">
          <button type="submit" class="btn btn-primary" :disabled="isLoading || !targetEmail">
            {{ isLoading ? 'A enviar...' : 'Enviar link de recuperação' }}
          </button>
          
          <div class="login-link">
            <router-link to="/login">Voltar ao login</router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { API_URL } from '@/auth';

const route = useRoute();
const targetEmail = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const isLoading = ref(false);
const hasAutoSent = ref(false);

const submitForm = async () => {
  if (!targetEmail.value || isLoading.value) return;

  errorMessage.value = '';
  successMessage.value = '';
  isLoading.value = true;

  try {
    const response = await fetch(`${API_URL}/forgot-password/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: targetEmail.value }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.detail || 'Não foi possível enviar o pedido.');
    }

    successMessage.value = data.message || 'Se o email existir, enviámos um link de recuperação.';

  } catch (error) {
    console.error('Forgot Password error:', error);
    errorMessage.value = error?.message || "Ocorreu um erro. Tenta novamente.";
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  const routeEmail = typeof route.query.email === 'string' ? route.query.email : '';
  const rememberedEmail = localStorage.getItem('rememberedEmail') || '';
  targetEmail.value = (routeEmail || rememberedEmail).trim();

  if (!targetEmail.value) {
    errorMessage.value = 'Não foi possível detetar o email. Volta ao login e preenche o email da conta.';
    return;
  }
});
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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

.auth-form-container {
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
  max-width: 480px; /* Smaller than signup */
  margin: 0;
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
  letter-spacing: -0.02em;
  color: var(--text-main);
  text-align: center;
}

.form-subtitle {
  margin: 0 0 24px;
  font-size: 1rem;
  color: var(--text-muted);
  text-align: center;
}

.message {
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.message.error {
  background-color: #fff5f5;
  color: var(--error);
  border: 1px solid #feb2b2;
}

.message.success {
  background-color: #f0fff4;
  color: var(--success);
  border: 1px solid #9ae6b4;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.form-group label {
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fdfdfd;
  font-size: 1rem;
  font-family: inherit;
  color: var(--text-main);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.email-target {
  margin: 0;
  min-height: 46px;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f3f7f9;
  font-size: 1rem;
  color: var(--text-main);
  word-break: break-all;
}

.form-actions {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.btn {
  border-radius: 999px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
  width: 100%;
  border: 0;
  background: var(--accent);
  color: #f2fffc;
  box-shadow: 0 4px 14px rgba(15, 118, 110, 0.2);
}

.btn:hover:not(:disabled) {
  background: var(--accent-hover);
  box-shadow: 0 6px 18px rgba(15, 118, 110, 0.28);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-link {
    font-size: 0.9rem;
    color: var(--text-muted);
}

.login-link a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 700;
}

.login-link a:hover {
    text-decoration: underline;
}
</style>
