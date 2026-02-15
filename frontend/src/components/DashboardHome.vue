<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { auth, API_URL } from '@/auth'
import { useUser } from '@/store/userStore'

const emit = defineEmits(['navigate', 'update-water'])

const { 
  user,
  displayName, 
  targetCalories,
  customMacroPercents
} = useUser()

const goToDiary = () => emit('navigate', 'diario')
const goToHungryMode = () => emit('navigate', 'tenho-fome')
const goToFridgeMode = () => emit('navigate', 'gerar-receita')
const waterDraft = ref('0.0')

const saveWater = async (amount) => {
  const safeAmount = Math.max(0, Math.min(10, amount))
  dashboardData.value.water_liters = Number(safeAmount.toFixed(2))
  waterDraft.value = dashboardData.value.water_liters.toFixed(1)

  try {
    const today = new Date().toISOString().split('T')[0]
    await fetch(`${API_URL}/diary/${today}/water`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ water_liters: safeAmount })
    })
    emit('update-water')
  } catch (e) {
    console.error("Water update failed", e)
  }
}

const addWater = async () => {
  const newAmount = Math.min(10, dashboardData.value.water_liters + 0.25)
  await saveWater(newAmount)
}

const removeWater = async () => {
  if (dashboardData.value.water_liters <= 0) return
  const newAmount = Math.max(0, dashboardData.value.water_liters - 0.25)
  await saveWater(newAmount)
}

const applyWaterInput = async () => {
  const normalized = String(waterDraft.value || '').replace(',', '.')
  const parsed = Number(normalized)
  if (!Number.isFinite(parsed)) {
    waterDraft.value = dashboardData.value.water_liters.toFixed(1)
    return
  }
  await saveWater(parsed)
}

const dashboardData = ref({
  consumed_calories: 0,
  calorie_goal: 2000,
  protein: 0,
  carbs: 0,
  fat: 0,
  streak_days: 0,
  water_liters: 0,
  weight_history: { labels: [], values: [] }
})

const nutritionCards = computed(() => {
  const goal = targetCalories.value || dashboardData.value.calorie_goal || 2000
  
  // Calculate goals based on custom percentages
  const proteinGoal = Math.round((goal * (customMacroPercents.value.protein / 100)) / 4)
  const carbsGoal = Math.round((goal * (customMacroPercents.value.carbs / 100)) / 4)
  const fatGoal = Math.round((goal * (customMacroPercents.value.fat / 100)) / 9)

  return [
    {
      title: 'Calorias',
      value: String(dashboardData.value.consumed_calories),
      unit: ' kcal',
      goalLabel: `Meta: ${goal} kcal`,
      percent: Math.min(100, Math.round((dashboardData.value.consumed_calories / (goal || 1)) * 100)),
      accent: '#16a34a',
      icon: '🔥'
    },
  {
    title: 'Proteínas',
    value: String(Math.round(dashboardData.value.protein)),
    unit: 'g',
    goalLabel: `Meta: ${proteinGoal}g`,
    percent: Math.min(100, Math.round((dashboardData.value.protein / (proteinGoal || 1)) * 100)),
    accent: '#2563eb',
    icon: '💪'
  },
  {
    title: 'Carboidratos',
    value: String(Math.round(dashboardData.value.carbs)),
    unit: 'g',
    goalLabel: `Meta: ${carbsGoal}g`,
    percent: Math.min(100, Math.round((dashboardData.value.carbs / (carbsGoal || 1)) * 100)),
    accent: '#14b8a6',
    icon: '🍎'
  },
  {
    title: 'Gorduras',
    value: String(Math.round(dashboardData.value.fat)),
    unit: 'g',
    goalLabel: `Meta: ${fatGoal}g`,
    percent: Math.min(100, Math.round((dashboardData.value.fat / (fatGoal || 1)) * 100)),
    accent: '#f59e0b',
    icon: '🥑'
  },
  {
    title: 'Água',
    value: String(dashboardData.value.water_liters),
    unit: ' L',
    goalLabel: 'Meta: 2.5L',
    percent: Math.min(100, Math.round((dashboardData.value.water_liters / 2.5) * 100)),
    accent: '#0891b2',
    icon: '💧',
    action: true // Marker for template
  }
]
})
const weightProjection = computed(() => {
  const weight = user.value?.peso || 70
  const height = user.value?.altura || 175
  const age = user.value?.idade || 25
  const gender = user.value?.sexo || 'male'
  const activityLevel = user.value?.activity_level || 'moderate'
  
  // Harris-Benedict Equation for BMR
  let bmr = 0
  if (gender === 'male') {
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
  } else {
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
  }
  
  const multipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    high: 1.725
  }
  
  const maintenance = bmr * (multipliers[activityLevel] || 1.2)
  const goal = targetCalories.value || dashboardData.value.calorie_goal || 2000
  const dailyDeficit = maintenance - goal
  
  // 7700 kcal approx = 1kg
  const kgPerDay = dailyDeficit / 7700
  
  const periods = [
    { label: '1 Semana', days: 7, icon: '📅', color: 'text-emerald-500' },
    { label: '1 Mês', days: 30, icon: '🗓️', color: 'text-emerald-500' },
    { label: '3 Meses', days: 90, icon: '🚀', color: 'text-blue-500' },
    { label: '1 Ano', days: 365, icon: '🏆', color: 'text-purple-500' }
  ]
  
  return periods.map(p => {
    const totalLost = kgPerDay * p.days
    const finalWeight = Math.max(40, weight - totalLost)
    return {
      ...p,
      lost: totalLost.toFixed(1),
      weight: finalWeight.toFixed(1),
      isLoss: totalLost >= 0
    }
  })
})

const streakDays = computed(() => dashboardData.value.streak_days)
const WEEKLY_GOALS_KEY = 'nutri_weekly_goals_v1'
const weeklyGoals = ref([
  { id: 1, label: 'Beber 2.5L água/dia', done: true },
  { id: 2, label: '5 refeições registadas', done: true },
  { id: 3, label: 'Treinar 3x', done: false }
])

const isListening = ref(false)
const activeGoalIndex = ref(null)
let recognitionInstance = null

const toggleGoalListening = async (index) => {
  if (isListening.value && activeGoalIndex.value === index) {
    stopListening()
    return
  }
  
  // Stop any existing session
  stopListening()
  activeGoalIndex.value = index

  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('O seu navegador não suporta reconhecimento de voz.')
    return
  }

  try {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognitionInstance = new Recognition()
    
    recognitionInstance.lang = 'pt-PT'
    recognitionInstance.continuous = false
    recognitionInstance.interimResults = true
    recognitionInstance.maxAlternatives = 1
    
    if ('lang' in recognitionInstance) {
      recognitionInstance.lang = 'pt-PT'
    }
    
    recognitionInstance.onstart = () => {
      isListening.value = true
    }
    
    recognitionInstance.onresult = (event) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          transcript += result[0].transcript + ' '
        } else {
          transcript += result[0].transcript
        }
      }
      
      if (transcript.trim() && activeGoalIndex.value !== null) {
        updateGoalLabel(weeklyGoals.value[activeGoalIndex.value], transcript.trim())
      }
    }
    
    recognitionInstance.onerror = (event) => {
      if (event.error !== 'aborted' && event.error !== 'no-speech') {
         console.error('Speech recognition error:', event.error)
      }
      stopListening()
    }
    
    recognitionInstance.onend = () => {
      stopListening()
    }
    
    recognitionInstance.start()
  } catch (err) {
    console.error('Failed to start speech recognition:', err)
    stopListening()
  }
}

const stopListening = () => {
  isListening.value = false
  activeGoalIndex.value = null
  if (recognitionInstance) {
    try { recognitionInstance.stop() } catch (e) {}
    recognitionInstance = null
  }
}

const persistWeeklyGoals = () => {
  localStorage.setItem(WEEKLY_GOALS_KEY, JSON.stringify(weeklyGoals.value))
}

const loadWeeklyGoals = () => {
  try {
    const raw = localStorage.getItem(WEEKLY_GOALS_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return
    weeklyGoals.value = parsed
      .filter((goal) => goal && typeof goal.label === 'string')
      .map((goal, index) => ({
        id: Number(goal.id) || (index + 1),
        label: goal.label,
        done: Boolean(goal.done)
      }))
  } catch {
    // fallback silently to defaults
  }
}

const updateGoalLabel = (goal, value) => {
  goal.label = value
  persistWeeklyGoals()
}

const toggleGoalDone = (goal) => {
  goal.done = !goal.done
  persistWeeklyGoals()
}

const formatDisplayName = (email) => {
  if (!email) return 'Utilizador'
  const localPart = email.split('@')[0] || 'Utilizador'
  return localPart
    .replace(/[._-]+/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const fetchDashboardData = async () => {
  try {
    const res = await fetch(`${API_URL}/users/me/dashboard`, {
      headers: auth.getAuthHeaders()
    })
    if (res.ok) {
      dashboardData.value = await res.json()
      waterDraft.value = Number(dashboardData.value.water_liters || 0).toFixed(1)
    }
  } catch (err) {
    console.error('Error fetching dashboard data:', err)
  }
}

const loadData = async () => {
  loadWeeklyGoals()
  await fetchDashboardData()
}

onMounted(loadData)
onUnmounted(() => {
  stopListening()
})
</script>

<template>
  <div class="dashboard-home">
    <header class="header-row">
      <div>
        <h1>Olá, {{ displayName }}! 👋</h1>
        <p>Aqui está o resumo da sua jornada nutricional</p>
      </div>
      <button class="btn-register" @click="goToDiary">+ Registar Refeição</button>
    </header>

    <section class="stats-grid">
      <article v-for="card in nutritionCards" :key="card.title" class="stat-card">
        <div class="stat-top">
          <div class="stat-icon" :style="{ backgroundColor: card.accent }">{{ card.icon }}</div>
          <div>
            <p class="stat-label">{{ card.title }}</p>
            <h3 v-if="card.action" class="water-value-row">
              <button @click="removeWater" class="btn-water-mini" title="Remover 250ml">−</button>
              <input
                v-model="waterDraft"
                type="text"
                inputmode="decimal"
                class="water-input"
                aria-label="Litros de água"
                @blur="applyWaterInput"
                @keyup.enter="applyWaterInput"
              />
              <span class="stat-unit">L</span>
              <button @click="addWater" class="btn-water-mini plus" title="Adicionar 250ml">+</button>
            </h3>
            <h3 v-else>
              {{ card.value }}<span class="stat-unit">{{ card.unit }}</span>
            </h3>
          </div>
        </div>
        <div class="stat-meta">
          <span>{{ card.goalLabel }}</span>
          <strong :style="{ color: card.accent }">{{ card.percent }}%</strong>
        </div>
        <div class="bar">
          <div class="fill" :style="{ width: `${card.percent}%`, backgroundColor: card.accent }"></div>
        </div>
      </article>
    </section>

    <section class="middle-grid">
      <article class="card projection-card">
        <div class="chart-head">
          <div>
            <h3>Projeção de Resultados</h3>
            <p>O que acontece se mantiveres o foco 🔥</p>
          </div>
          <div class="info-tag">Baseado no teu metabolismo</div>
        </div>

        <div class="projection-grid">
          <div v-for="item in weightProjection" :key="item.label" class="projection-item">
            <div class="proj-icon">{{ item.icon }}</div>
            <div class="proj-label">{{ item.label }}</div>
            <div class="proj-value" :class="item.color">
              {{ item.isLoss ? '-' : '+' }}{{ Math.abs(item.lost) }}kg
            </div>
            <div class="proj-footer">Peso est.: <strong>{{ item.weight }}kg</strong></div>
          </div>
        </div>

        <div class="projection-tip">
          <span class="tip-icon">💡</span>
          <p>
            Ao manteres o teu objetivo de <strong>{{ targetCalories || 2000 }} kcal</strong>, 
            estás a criar um impacto real. Esta projeção baseia-se na tua taxa metabólica e nível de atividade.
          </p>
        </div>
      </article>

      <aside class="side-stack">
        <article class="card streak-card">
          <p class="streak-label">🔥 Dias Consecutivos</p>
          <h3>{{ streakDays }} dias</h3>
          <p>Continue assim! 🔥</p>
        </article>

        <article class="card goals-card">
          <h3>Metas da Semana</h3>
          <ul>
            <li v-for="(goal, index) in weeklyGoals" :key="goal.id" :class="{ done: goal.done }">
              <label class="goal-check" :class="{ checked: goal.done }">
                <input
                  type="checkbox"
                  :checked="goal.done"
                  @change="toggleGoalDone(goal)"
                />
                <span class="checkmark" aria-hidden="true"></span>
              </label>
              <input
                class="goal-input"
                :value="goal.label"
                @input="updateGoalLabel(goal, $event.target.value)"
                placeholder="Escreve uma meta..."
              />
              <button 
                type="button" 
                class="mic-btn-goal" 
                :class="{ active: isListening && activeGoalIndex === index }"
                @click="toggleGoalListening(index)"
                title="Falar meta"
              >
                🎤
              </button>
            </li>
          </ul>
        </article>
      </aside>
    </section>

    <section class="action-grid">
      <article class="action-card hungry" @click="goToHungryMode" role="button" tabindex="0">
        <h3>Tenho Fome</h3>
        <p>Sugira-me algo saudável</p>
      </article>

      <article class="action-card fridge" @click="goToFridgeMode" role="button" tabindex="0">
        <h3>Assalto ao Frigorífico</h3>
        <p>O que posso fazer com o que tenho?</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.dashboard-home {
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
  min-width: 0;
  color: var(--text-main, #11263f);
}

.dashboard-home h1,
.dashboard-home h2,
.dashboard-home h3,
.dashboard-home h4 {
  color: var(--text-main);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.header-row h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.05;
}

.header-row p {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 1.05rem;
}

.btn-register {
  border: 0;
  border-radius: 14px;
  padding: 12px 24px;
  background: var(--menu-active-text);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 22px color-mix(in srgb, var(--menu-active-text), transparent 72%);
}

.stats-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card,
.card {
  background: var(--bg-elevated, #ffffff);
  border: 1px solid var(--line, #dbe3eb);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 10px 20px rgba(2, 12, 27, 0.06);
}

.stat-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 1.1rem;
}

.stat-label {
  margin: 0;
  font-size: 0.86rem;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.stat-card h3 {
  margin: 3px 0 0;
  font-size: 2rem;
  line-height: 1;
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.btn-water-mini {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid color-mix(in srgb, #0891b2, transparent 55%);
  background: color-mix(in srgb, #0891b2, transparent 88%);
  color: #22d3ee;
  font-weight: 800;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin: 0;
}

.btn-water-mini:hover {
  background: #0ea5e9;
  color: white;
  transform: translateY(-1px);
}

.btn-water-mini.plus {
  background: color-mix(in srgb, #10b981, transparent 84%);
  border-color: color-mix(in srgb, #10b981, transparent 52%);
  color: #34d399;
}

.water-value-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.water-input {
  width: 66px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: color-mix(in srgb, var(--bg-main), transparent 20%);
  color: var(--text-main);
  padding: 5px 8px;
  font: inherit;
  font-size: 1.25rem;
  font-weight: 700;
  text-align: center;
}

.water-input:focus {
  outline: none;
  border-color: #22d3ee;
  box-shadow: 0 0 0 2px color-mix(in srgb, #22d3ee, transparent 75%);
}

.stat-unit {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-muted);
}

.stat-meta {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
  font-size: 0.92rem;
  color: var(--text-muted);
}

.bar {
  margin-top: 8px;
  height: 9px;
  border-radius: 99px;
  background: color-mix(in srgb, var(--line), #ffffff 30%);
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: inherit;
}

.middle-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1.4fr 0.66fr;
  gap: 16px;
}

.projection-card {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.chart-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 24px;
}

.info-tag {
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}

.projection-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  flex: 1;
}

.projection-item {
  background: var(--bg-main);
  border: 1px solid var(--line);
  padding: 20px;
  border-radius: 20px;
  text-align: center;
  transition: transform 0.2s;
}

.projection-item:hover {
  transform: scale(1.02);
  border-color: var(--menu-active-text);
}

.proj-icon { font-size: 1.5rem; margin-bottom: 8px; }
.proj-label { font-size: 0.85rem; color: var(--text-muted); font-weight: 600; }
.proj-value { font-size: 1.8rem; font-weight: 900; margin: 4px 0; }
.proj-footer { font-size: 0.8rem; color: var(--text-muted); }

.projection-tip {
  margin-top: 24px;
  background: color-mix(in srgb, var(--menu-active-text), transparent 92%);
  padding: 16px;
  border-radius: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.projection-tip p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-main);
  line-height: 1.4;
}

.side-stack {
  display: grid;
  gap: 16px;
}

.streak-card {
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  color: #fff;
}

.streak-label {
  margin: 0;
  font-size: 1.05rem;
}

.streak-card h3 {
  margin: 10px 0 6px;
  font-size: 4rem;
  line-height: 1;
}

.streak-card p {
  margin: 0;
}

.goals-card h3 {
  margin: 0;
  font-size: 1.55rem;
}

.goals-card ul {
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 12px;
}

.goals-card li {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 10px;
}

.goal-check {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.goal-check input[type='checkbox'] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.checkmark {
  width: 24px;
  height: 24px;
  border-radius: 8px;
  border: 1.6px solid color-mix(in srgb, var(--line), #fff 10%);
  background: color-mix(in srgb, var(--bg-main), transparent 20%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.checkmark::after {
  content: '';
  width: 6px;
  height: 12px;
  border-right: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(45deg) scale(0);
  transition: transform 0.16s ease;
  margin-top: -1px;
}

.goals-card li.done {
  color: var(--text-main);
}

.goal-check:hover .checkmark {
  border-color: color-mix(in srgb, var(--menu-active-text), #fff 20%);
}

.goal-check.checked .checkmark {
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  border-color: transparent;
  box-shadow: 0 8px 14px rgba(20, 184, 166, 0.28);
}

.goal-check.checked .checkmark::after {
  transform: rotate(45deg) scale(1);
}

.goal-input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: color-mix(in srgb, var(--bg-main), transparent 30%);
  color: var(--text-main);
  padding: 9px 11px;
  font: inherit;
}

.goal-input:focus {
  outline: none;
  border-color: var(--menu-active-text);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--menu-active-text), transparent 80%);
}

.mic-btn-goal {
  background: transparent;
  border: none;
  font-size: 1.1rem;
  padding: 0 8px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mic-btn-goal:hover {
  background: var(--menu-hover-bg);
}
.mic-btn-goal.active {
  color: #ef4444;
  animation: pulse-mic 1.5s infinite;
}
@keyframes pulse-mic {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.action-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.action-card {
  border-radius: 18px;
  padding: 26px;
  min-height: 146px;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 16px 30px rgba(2, 20, 46, 0.18);
  transition: transform 0.2s ease;
}

.action-card:hover {
  transform: translateY(-2px);
}

.action-card h3 {
  margin: 0;
  font-size: 2rem;
}

.action-card p {
  margin: 8px 0 0;
  opacity: 0.95;
  font-size: 1.15rem;
}

.action-card.hungry {
  background: linear-gradient(135deg, #0f766e, #14b8a6);
}

.action-card.fridge {
  background: linear-gradient(135deg, #0ea5e9, #3b82f6);
}

:global(.theme-dark) .stat-card,
:global(.theme-dark) .card {
  box-shadow: 0 14px 26px rgba(2, 8, 18, 0.38);
}

:global(.theme-dark) .periods {
  background: #0b1220;
}

@media (max-width: 1220px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .middle-grid,
  .action-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .header-row {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-wrap {
    grid-template-columns: 54px 1fr;
  }

  .action-card h3 {
    font-size: 1.55rem;
  }

  .action-card p {
    font-size: 1rem;
  }
}
</style>
