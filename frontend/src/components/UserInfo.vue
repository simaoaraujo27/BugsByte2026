<template>
  <div class="signup-page">
    <div class="user-info-form">
      <h2 class="form-title">Criar Conta</h2>
      <p class="form-subtitle">Precisamos de alguns detalhes para criar o seu perfil.</p>

      <!-- Error/Success Messages -->
      <div v-if="errorMessage" class="message error">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="message success">
        {{ successMessage }}
      </div>

      <form @submit.prevent="submitForm" class="form-grid">
        <!-- Account Info -->
        <div class="form-group full-width">
          <label for="username">E-mail (Nome de utilizador)</label>
          <input type="email" id="username" v-model="form.username" placeholder="chef@nutriventures.com" required />
        </div>

        <div class="form-group full-width">
          <label for="password">Palavra-passe</label>
          <input type="password" id="password" v-model="form.password" placeholder="••••••••" required />
        </div>

        <!-- Personal Info -->
        <div class="form-group">
          <label for="gender">Género</label>
          <select id="gender" v-model="form.sexo">
            <option value="male">Masculino</option>
            <option value="female">Feminino</option>
            <option value="other">Outro</option>
          </select>
        </div>

        <div class="form-group">
          <label for="age">Idade</label>
          <input type="number" id="age" v-model.number="form.idade" placeholder="25" required />
        </div>

        <div class="form-group">
          <label for="height">Altura (cm)</label>
          <input type="number" id="height" v-model.number="form.altura" placeholder="175" required />
        </div>

        <div class="form-group">
          <label for="weight">Peso (kg)</label>
          <input type="number" id="weight" v-model.number="form.peso" placeholder="70" required />
        </div>

        <div class="form-group full-width">
          <label>Objetivo Principal</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" name="goal" value="lose" v-model="form.goal" />
              Perder Peso
            </label>
            <label class="radio-label">
              <input type="radio" name="goal" value="maintain" v-model="form.goal" />
              Manter Peso
            </label>
            <label class="radio-label">
              <input type="radio" name="goal" value="gain" v-model="form.goal" />
              Ganhar Massa Muscular
            </label>
          </div>
        </div>

        <div class="form-group full-width">
          <label>Nível de Atividade</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" name="activity" value="sedentary" v-model="form.activity_level" />
              Sedentário
            </label>
            <label class="radio-label">
              <input type="radio" name="activity" value="light" v-model="form.activity_level" />
              Ligeiro
            </label>
            <label class="radio-label">
              <input type="radio" name="activity" value="moderate" v-model="form.activity_level" />
              Moderado
            </label>
            <label class="radio-label">
              <input type="radio" name="activity" value="high" v-model="form.activity_level" />
              Elevado
            </label>
          </div>
        </div>
        
        <div class="form-group full-width">
          <label for="allergies">Alergias (separadas por vírgula)</label>
          <input type="text" id="allergies" v-model="allergiesInput" placeholder="Ex: glúten, lactose" />
        </div>

        <div class="form-actions full-width">
          <button type="submit" class="btn btn-primary max-w-xs mx-auto">Registar</button>
          
          <div class="login-link">
              Já tem uma conta? <router-link to="/login">Entrar</router-link>
          </div>

          <div class="footer-actions">
            <router-link to="/" class="back-link">
              &larr; Voltar ao Início
            </router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const errorMessage = ref('');
const successMessage = ref('');
const allergiesInput = ref('');

const form = reactive({
  username: '',
  password: '',
  sexo: 'male',
  idade: null,
  altura: null,
  peso: null,
  goal: 'maintain',
  activity_level: 'sedentary',
});

const submitForm = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  // Process allergies from string to array
  const allergens = allergiesInput.value
    .split(',')
    .map(a => a.trim())
    .filter(a => a.length > 0);

  const payload = {
    ...form,
    allergens: allergens
  };

  try {
    const response = await fetch('http://localhost:8000/users/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Falha no registo');
    }

    const data = await response.json();
    console.log('User created:', data);
    successMessage.value = 'Perfil criado com sucesso! A redirecionar para o início de sessão...';
    
    setTimeout(() => {
        router.push('/login');
    }, 2000);

  } catch (error) {
    console.error('Registration error:', error);
    errorMessage.value = error.message;
  }
};
</script>

<style scoped>
.signup-page {
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image:
    linear-gradient(120deg, rgba(6, 24, 48, 0.58) 0%, rgba(10, 20, 34, 0.46) 45%, rgba(13, 18, 26, 0.5) 100%),
    url('https://images.unsplash.com/photo-1490818387583-1baba5e638af?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 20px;
  overflow: hidden;
}

.user-info-form {
  --bg-main: #f4fbf8;
  --bg-soft: #ffffff;
  --text-main: #13293d;
  --text-muted: #3b566d;
  --accent: #0f766e;
  --accent-hover: #0b5c56;
  --line: #d7e7e0;
  --error: #e53e3e;
  --success: #38a169;

  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 720px;
  /* Remove margin auto since parent flex centers it */
  margin: 0; 
  padding: 28px;
  background: rgba(255, 255, 255, 0.95); /* Slightly transparent white background */
  backdrop-filter: blur(10px); /* Frosted glass effect */
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  color: var(--text-main);
}

.form-title {
  margin: 0 0 8px;
  font-size: 2.1rem;
  letter-spacing: -0.02em;
  color: var(--text-main);
  text-align: center;
}

.form-subtitle {
  margin: 0 0 24px;
  font-size: 1.05rem;
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
}

.form-group input,
.form-group select {
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

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 4px;
  justify-content: flex-start;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
  background: var(--bg-soft);
  transition: border-color 0.2s, background-color 0.2s;
  white-space: nowrap;
}

.radio-label:hover {
  border-color: #b8d5cb;
}

.radio-label input[type='radio'] {
  accent-color: var(--accent);
}

.form-actions {
  grid-column: 1 / -1;
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  
  text-align: center;
}

.footer-actions {
  margin-top: 8px;
  border-top: 1px solid var(--line);
  padding-top: 16px;
  width: 100%;
}

.back-link {
  color: var(--text-muted);
  font-size: 0.9rem;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--text-main);
}

.btn {
  border-radius: 999px;
  padding: 12px 48px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
  width: 100%;
}

.btn-primary {
  border: 0;
  background: var(--accent);
  color: #f2fffc;
  box-shadow: 0 4px 14px rgba(15, 118, 110, 0.2);
}

.btn-primary:hover {
  background: var(--accent-hover);
  box-shadow: 0 6px 18px rgba(15, 118, 110, 0.28);
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

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
