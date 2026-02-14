<script setup>
import { computed, onMounted, ref } from 'vue'
import { auth } from '@/auth'

const loading = ref(true)
const errorMessage = ref('')
const passwordMessage = ref('')
const passwordLoading = ref(false)
const userProfile = ref(null)

const displayName = computed(() => {
  const email = userProfile.value?.username || ''
  const localPart = email.split('@')[0] || 'Utilizador'
  return localPart
    .replace(/[._-]+/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
})

const formatGender = (value) => {
  const normalized = (value || '').toLowerCase()
  if (normalized === 'male') return 'Masculino'
  if (normalized === 'female') return 'Feminino'
  if (normalized === 'other') return 'Outro'
  return value || 'N/A'
}

const formatGoal = (value) => {
  const normalized = (value || '').toLowerCase()
  if (normalized === 'lose') return 'Perder Peso'
  if (normalized === 'maintain') return 'Manter Peso'
  if (normalized === 'gain') return 'Ganhar Massa Muscular'
  return value || 'N/A'
}

const formatActivityLevel = (value) => {
  const normalized = (value || '').toLowerCase()
  if (normalized === 'sedentary') return 'Sedentário'
  if (normalized === 'light') return 'Ligeiro'
  if (normalized === 'moderate') return 'Moderado'
  if (normalized === 'high') return 'Elevado'
  return value || 'N/A'
}

const bmi = computed(() => {
  if (!userProfile.value?.altura || !userProfile.value?.peso) return null
  const heightM = Number(userProfile.value.altura) / 100
  if (!heightM) return null
  return Number(userProfile.value.peso) / (heightM * heightM)
})

const bmr = computed(() => {
  const profile = userProfile.value
  if (!profile?.peso || !profile?.altura || !profile?.idade) return null

  const weight = Number(profile.peso)
  const height = Number(profile.altura)
  const age = Number(profile.idade)
  const gender = (profile.sexo || '').toLowerCase()

  if (gender === 'male') return 10 * weight + 6.25 * height - 5 * age + 5
  if (gender === 'female') return 10 * weight + 6.25 * height - 5 * age - 161
  return 10 * weight + 6.25 * height - 5 * age - 78
})

const activityFactor = computed(() => {
  const level = (userProfile.value?.activity_level || '').toLowerCase()
  if (level === 'sedentary') return 1.0
  if (level === 'light') return 1.175
  if (level === 'moderate') return 1.35
  if (level === 'high') return 1.525
  return null
})

const tdee = computed(() => {
  if (!bmr.value || !activityFactor.value) return null
  return bmr.value * activityFactor.value
})

const bmiCategory = computed(() => {
  if (!bmi.value) return 'N/A'
  if (bmi.value < 18.5) return 'Abaixo do peso'
  if (bmi.value < 25) return 'Peso normal'
  if (bmi.value < 30) return 'Excesso de peso'
  return 'Obesidade'
})

const allergiesText = computed(() => {
  if (!userProfile.value?.allergens?.length) return 'Nenhum'
  return userProfile.value.allergens.map((item) => item.name).join(', ')
})

const fetchProfile = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    userProfile.value = await auth.getMe()
    
    if (!userProfile.value) {
      errorMessage.value = 'Não existe nenhum perfil disponível.'
    }
  } catch (error) {
    if (error instanceof TypeError) {
      errorMessage.value = 'Não foi possível ligar ao servidor. Verifique se o backend está ativo.'
    } else {
      errorMessage.value = error.message || 'Erro ao obter o perfil.'
    }
  } finally {
    loading.value = false
  }
}

const requestPasswordChange = async () => {
  if (!userProfile.value?.username || passwordLoading.value) return

  passwordLoading.value = true
  passwordMessage.value = ''

  try {
    const response = await fetch('' + (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/forgot-password/', {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ username: userProfile.value.username })
    })

    if (!response.ok) throw new Error('Não foi possível iniciar a alteração da palavra-passe.')

    const data = await response.json()
    passwordMessage.value = data.message || 'Pedido enviado.'
  } catch (error) {
    passwordMessage.value = error instanceof TypeError
      ? 'Backend indisponível para alterar a palavra-passe.'
      : (error.message || 'Erro ao iniciar a alteração da palavra-passe.')
  } finally {
    passwordLoading.value = false
  }
}

onMounted(fetchProfile)
</script>

<template>
  <section class="profile-panel">
    <header class="panel-header">
      <h1>Perfil</h1>
      <p>Informação da conta e métricas de saúde</p>
    </header>

    <div v-if="loading" class="status-card">A carregar perfil...</div>
    <div v-else-if="errorMessage" class="status-card error">{{ errorMessage }}</div>

    <template v-else-if="userProfile">
      <article class="hero-card">
        <div class="hero-content">
          <div class="avatar-tile" aria-hidden="true">👤</div>
          <div>
            <h2>{{ displayName }}</h2>
            <p class="hero-email">✉ {{ userProfile.username }}</p>
          </div>
        </div>
      </article>

      <div class="grid">
        <article class="card details-card">
          <h3><span class="badge green">●</span> Dados Pessoais</h3>
          <ul class="detail-list">
            <li>
              <span>Género</span>
              <strong>{{ formatGender(userProfile.sexo) }}</strong>
            </li>
            <li>
              <span>Idade</span>
              <strong>{{ userProfile.idade }} anos</strong>
            </li>
            <li>
              <span>Altura</span>
              <strong>{{ userProfile.altura }} cm</strong>
            </li>
            <li>
              <span>Peso</span>
              <strong>{{ userProfile.peso }} kg</strong>
            </li>
            <li>
              <span>Objetivo</span>
              <strong>{{ formatGoal(userProfile.goal) }}</strong>
            </li>
            <li>
              <span>Nível de Atividade</span>
              <strong>{{ formatActivityLevel(userProfile.activity_level) }}</strong>
            </li>
            <li>
              <span>Alergénios</span>
              <strong>{{ allergiesText }}</strong>
            </li>
          </ul>
        </article>

        <article class="card metrics-card">
          <h3><span class="badge rose">●</span> Métricas de Saúde</h3>
          <div class="metric-box">
            <p>Índice de Massa Corporal</p>
            <strong>{{ bmi ? bmi.toFixed(1) : '-' }} kg/m²</strong>
            <small>{{ bmiCategory }}</small>
          </div>
          <div class="metric-box">
            <p>Taxa Metabólica Basal</p>
            <strong>{{ bmr ? Math.round(bmr) : '-' }} kcal/dia</strong>
          </div>
          <div class="metric-box">
            <p>Kcal normais (TDEE)</p>
            <strong>{{ tdee ? Math.round(tdee) : '-' }} kcal/dia</strong>
            <small>Manutenção diária com base no nível de atividade.</small>
          </div>
        </article>

        <article class="card full">
          <h3>Alterar Palavra-passe</h3>
          <p class="muted">Envie um pedido de recuperação de palavra-passe para o seu e-mail.</p>
          <button type="button" class="btn" :disabled="passwordLoading" @click="requestPasswordChange">
            {{ passwordLoading ? 'A enviar...' : 'Alterar Palavra-passe' }}
          </button>
          <p v-if="passwordMessage" class="password-message">{{ passwordMessage }}</p>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.profile-panel {
  max-width: 980px;
}

.panel-header h1 {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.panel-header p {
  margin-top: 6px;
  color: var(--text-muted);
}

.status-card {
  margin-top: 24px;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 12px;
  padding: 16px;
  color: var(--text-main);
}

.status-card.error {
  border-color: #dc2626;
  color: #dc2626;
}

.hero-card {
  margin-top: 24px;
  background: linear-gradient(105deg, #19b88a 0%, #20c4b3 55%, #28a8cf 100%);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: visible;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.hero-content {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar-tile {
  width: 82px;
  height: 82px;
  border-radius: 14px;
  background: #f7fbff;
  border: 1px solid #dce9f5;
  display: grid;
  place-items: center;
  font-size: 2rem;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.12);
}

.hero-content h2 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.15;
  color: #f6fffe;
}

.hero-email {
  margin-top: 4px;
  color: rgba(236, 255, 252, 0.9);
}

.grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.card {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.card.full {
  grid-column: 1 / -1;
}

.card h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.badge {
  font-size: 0.8rem;
  vertical-align: middle;
  margin-right: 8px;
}

.badge.green {
  color: #10b981;
}

.badge.rose {
  color: #f43f5e;
}

.detail-list {
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0;
}

.detail-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.detail-list li:last-child {
  border-bottom: 0;
}

.detail-list li span {
  color: var(--text-muted);
}

.detail-list li strong {
  color: var(--text-main);
  text-align: right;
}

.metrics-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metric-box {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 14px 12px;
  background: rgba(148, 163, 184, 0.12);
}

.metric-box p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.metric-box strong {
  display: block;
  margin-top: 8px;
  font-size: 1.35rem;
}

.metric-box small {
  display: inline-block;
  margin-top: 4px;
  color: var(--text-muted);
}

.muted {
  margin-top: 8px;
  color: var(--text-muted);
}

.btn {
  margin-top: 12px;
  border: 0;
  border-radius: 10px;
  background: #0ea5a0;
  color: #f8fffe;
  font-weight: 700;
  padding: 10px 16px;
  cursor: pointer;
}

.btn:hover {
  background: #0b8f8b;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.password-message {
  margin-top: 10px;
  color: var(--text-muted);
}

:global(.theme-dark) .hero-card,
:global(.theme-dark) .card {
  box-shadow: 0 10px 22px rgba(3, 8, 18, 0.35);
}

:global(.theme-dark) .avatar-tile {
  background: #0f1a2b;
  border-color: #30415e;
}

:global(.theme-dark) .metric-box {
  background: rgba(15, 23, 40, 0.55);
}

@media (max-width: 860px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .hero-content h2 {
    font-size: 1.6rem;
  }
}
</style>
