<script setup>
import { computed, onMounted, ref } from 'vue'
import { auth, API_URL } from '@/auth'

const emit = defineEmits(['navigate'])

const goToDiary = () => emit('navigate', 'diario')
const goToHungryMode = () => emit('navigate', 'tenho-fome')
const goToFridgeMode = () => emit('navigate', 'tenho-fome')

const greetingName = ref('Utilizador')
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

const nutritionCards = computed(() => [
  {
    title: 'Calorias',
    value: String(dashboardData.value.consumed_calories),
    unit: '',
    goalLabel: `Meta: ${dashboardData.value.calorie_goal} kcal`,
    percent: Math.min(100, Math.round((dashboardData.value.consumed_calories / (dashboardData.value.calorie_goal || 1)) * 100)),
    accent: '#16a34a',
    icon: '🔥'
  },
  {
    title: 'Proteínas',
    value: String(Math.round(dashboardData.value.protein)),
    unit: 'g',
    goalLabel: 'Meta: 120g',
    percent: Math.min(100, Math.round((dashboardData.value.protein / 120) * 100)),
    accent: '#2563eb',
    icon: '💪'
  },
  {
    title: 'Carboidratos',
    value: String(Math.round(dashboardData.value.carbs)),
    unit: 'g',
    goalLabel: 'Meta: 250g',
    percent: Math.min(100, Math.round((dashboardData.value.carbs / 250) * 100)),
    accent: '#14b8a6',
    icon: '🍎'
  },
  {
    title: 'Água',
    value: String(dashboardData.value.water_liters),
    unit: 'L',
    goalLabel: 'Meta: 2.5L',
    percent: Math.min(100, Math.round((dashboardData.value.water_liters / 2.5) * 100)),
    accent: '#0891b2',
    icon: '💧'
  }
])

const chartPeriods = [
  { id: '1S', label: '1S' },
  { id: '1M', label: '1M' },
  { id: '3M', label: '3M' },
  { id: 'ALL', label: 'Tudo' }
]

const selectedPeriod = ref('1M')

const chartData = computed(() => {
  if (dashboardData.value.weight_history && dashboardData.value.weight_history.labels && dashboardData.value.weight_history.labels.length > 0) {
    return dashboardData.value.weight_history
  }
  return {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
    values: [78.5, 77.9, 77.4, 76.9]
  }
})

const currentSeries = computed(() => chartData.value)

const yRange = computed(() => {
  const values = currentSeries.value.values
  const min = Math.min(...values)
  const max = Math.max(...values)
  const padding = 0.6
  return {
    min: Number((min - padding).toFixed(1)),
    max: Number((max + padding).toFixed(1))
  }
})

const chartPoints = computed(() => {
  const { values } = currentSeries.value
  const min = yRange.value.min
  const max = yRange.value.max
  const span = Math.max(0.001, max - min)
  const top = 10
  const bottom = 16
  const left = 8
  const right = 92
  const usableHeight = 100 - top - bottom

  return values.map((value, index) => {
    const x = values.length === 1 ? 50 : left + (index / (values.length - 1)) * (right - left)
    const y = top + ((max - value) / span) * usableHeight
    return { x, y, value }
  })
})

const chartLinePath = computed(() => {
  return chartPoints.value
    .map((point, idx) => `${idx === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ')
})

const areaPath = computed(() => {
  if (!chartPoints.value.length) return ''
  const first = chartPoints.value[0]
  const last = chartPoints.value[chartPoints.value.length - 1]
  const baselineY = 84
  return `${chartLinePath.value} L ${last.x} ${baselineY} L ${first.x} ${baselineY} Z`
})

const yTicks = computed(() => {
  const steps = 4
  const values = []
  for (let i = 0; i <= steps; i += 1) {
    const v = yRange.value.max - ((yRange.value.max - yRange.value.min) / steps) * i
    values.push(Number(v.toFixed(1)))
  }
  return values
})

const streakDays = computed(() => dashboardData.value.streak_days)
const weeklyGoals = [
  { label: 'Beber 2.5L água/dia', done: true },
  { label: '5 refeições registadas', done: true },
  { label: 'Treinar 3x', done: false }
]

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
    }
  } catch (err) {
    console.error('Error fetching dashboard data:', err)
  }
}

const loadGreetingName = async () => {
  try {
    const me = await auth.getMe()
    greetingName.value = formatDisplayName(me?.username)
  } catch {
    greetingName.value = 'Utilizador'
  }
}

const loadData = async () => {
  await Promise.all([
    loadGreetingName(),
    fetchDashboardData()
  ])
}

onMounted(loadData)
</script>

<template>
  <div class="dashboard-home">
    <header class="header-row">
      <div>
        <h1>Olá, {{ greetingName }}! 👋</h1>
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
            <h3>{{ card.value }}{{ card.unit }}</h3>
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
      <article class="card chart-card">
        <div class="chart-head">
          <div>
            <h3>Evolução do Peso</h3>
            <p>Acompanha o teu progresso real 🎉</p>
          </div>
          <div class="periods">
            <button
              v-for="period in chartPeriods"
              :key="period.id"
              :class="['period-btn', { active: selectedPeriod === period.id }]"
              @click="selectedPeriod = period.id"
            >
              {{ period.label }}
            </button>
          </div>
        </div>

        <div class="chart-wrap">
          <div class="y-axis">
            <span v-for="tick in yTicks" :key="tick">{{ tick }}kg</span>
          </div>

          <div class="plot">
            <div class="grid-lines">
              <span v-for="tick in yTicks" :key="`grid-${tick}`"></span>
            </div>

            <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Gráfico do peso">
              <path :d="areaPath" class="area" />
              <path :d="chartLinePath" class="line" />
              <circle
                v-for="(point, idx) in chartPoints"
                :key="`point-${idx}`"
                :cx="point.x"
                :cy="point.y"
                r="1.4"
                class="dot"
              />
            </svg>

            <div class="x-axis" :style="{ gridTemplateColumns: `repeat(${currentSeries.labels.length}, minmax(0, 1fr))` }">
              <span v-for="label in currentSeries.labels" :key="label">{{ label }}</span>
            </div>
          </div>
        </div>
      </article>

      <aside class="side-stack">
        <article class="card streak-card">
          <p class="streak-label">🔥 Dias Consecutivos</p>
          <h3>{{ streakDays }}</h3>
          <p>Continue assim! 🔥</p>
        </article>

        <article class="card goals-card">
          <h3>Metas da Semana</h3>
          <ul>
            <li v-for="goal in weeklyGoals" :key="goal.label" :class="{ done: goal.done }">
              <span class="dot-goal">{{ goal.done ? '✓' : '•' }}</span>
              {{ goal.label }}
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
  background: var(--bg-elevated);
  border: 1px solid var(--line);
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

.chart-card {
  min-height: 430px;
  overflow: hidden;
}

.chart-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
}

.chart-head h3 {
  margin: 0;
  font-size: 1.9rem;
}

.chart-head p {
  margin: 6px 0 0;
  color: var(--text-muted);
}

.periods {
  display: inline-flex;
  gap: 6px;
  background: var(--bg-main);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 4px;
}

.period-btn {
  border: 0;
  background: transparent;
  color: var(--text-muted);
  border-radius: 10px;
  padding: 7px 13px;
  font-weight: 700;
  cursor: pointer;
}

.period-btn.active {
  background: var(--bg-elevated);
  color: var(--menu-active-text);
}

.chart-wrap {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 70px 1fr;
  gap: 12px;
  height: 310px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding-top: 6px;
}

.plot {
  position: relative;
  display: grid;
  grid-template-rows: 1fr auto;
  overflow: hidden;
  border-radius: 12px;
}

.grid-lines {
  position: absolute;
  inset: 0 0 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}

.grid-lines span {
  border-top: 1px dashed color-mix(in srgb, var(--line), transparent 15%);
}

.plot svg {
  width: 100%;
  height: calc(100% - 32px);
  position: relative;
  z-index: 1;
}

.area {
  fill: rgba(16, 185, 129, 0.13);
}

.line {
  fill: none;
  stroke: #10b981;
  stroke-width: 1.2;
  vector-effect: non-scaling-stroke;
}

.dot {
  fill: #10b981;
}

.x-axis {
  display: grid;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.x-axis span {
  text-align: center;
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

.goals-card li.done {
  color: var(--text-main);
}

.dot-goal {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #dcfce7;
  color: #15803d;
  font-size: 0.82rem;
  font-weight: 800;
  flex-shrink: 0;
}

.goals-card li:not(.done) .dot-goal {
  background: #e5e7eb;
  color: #9ca3af;
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