<script setup>
import { computed } from 'vue'
import WeightChart from './WeightChart.vue'

const emit = defineEmits(['navigate'])

const goToHungryMode = () => {
  emit('navigate', 'tenho-fome')
}

const goToFridgeRaid = () => {
  // Navega para a secção que permite gerar receitas a partir de ingredientes
  emit('navigate', 'gerar-receita')
}

// Dummy data for now
const dailyCalories = {
  consumed: 0,
  target: 2200
}
const calorieProgress = computed(() => {
  if (dailyCalories.target === 0) return 0
  return (dailyCalories.consumed / dailyCalories.target) * 100
})

const calorieMessage = computed(() => {
  if (dailyCalories.consumed === 0) {
    return 'Regista a tua primeira refeição do dia.'
  }
  if (calorieProgress.value > 100) {
    return 'Excedeste o teu objetivo diário.'
  }
  return 'Estás no caminho certo para o teu objetivo.'
})

const streak = 0

const streakMessage = computed(() => {
  if (streak === 0) {
    return 'Regista uma refeição para começar a tua streak!'
  }
  return 'Continua o bom trabalho!'
})
</script>

<template>
  <div class="dashboard-home">
    <header class="panel-header">
      <h1>Dashboard</h1>
      <p>Bem-vindo de volta! Aqui está um resumo da tua atividade.</p>
    </header>

    <div class="dashboard-grid">
      <!-- Calorie Tracker Card -->
      <article class="card calorie-card">
        <h3>Calorias Diárias</h3>
        <div class="calorie-tracker">
          <div class="progress-bar">
            <div class="progress" :style="{ width: calorieProgress + '%' }"></div>
          </div>
          <div class="calorie-text">
            <strong>{{ dailyCalories.consumed }}</strong> / {{ dailyCalories.target }} kcal
          </div>
        </div>
        <p class="card-subtitle">{{ calorieMessage }}</p>
      </article>

      <!-- Streak Card -->
      <article class="card streak-card">
        <h3>Streak de Registo</h3>
        <div class="streak-display">
          <span class="streak-icon" aria-hidden="true">🔥</span>
          <strong class="streak-count">{{ streak }}</strong>
          <span v-if="streak > 0">{{ streak === 1 ? 'dia seguido' : 'dias seguidos' }}</span>
        </div>
        <p class="card-subtitle">{{ streakMessage }}</p>
      </article>

      <!-- Weight Chart Card -->
      <WeightChart />

      <!-- "Tenho Fome" Shortcut Card -->
      <article class="card hungry-card" @click="goToHungryMode" role="button" tabindex="0">
        <div class="hungry-card-content">
          <span class="hungry-icon" aria-hidden="true">🍔</span>
          <h2>Tenho Fome?</h2>
          <p>Diz-nos o que te apetece e nós damos-te uma versão saudável.</p>
          <span class="hungry-cta">Começar &rarr;</span>
        </div>
      </article>

      <!-- "Fridge Raid" Shortcut Card -->
      <article class="card fridge-card" @click="goToFridgeRaid" role="button" tabindex="0">
        <div class="fridge-card-content">
          <span class="fridge-icon" aria-hidden="true">🧊</span>
          <h2>Assalto ao Frigorífico</h2>
          <p>Diz-nos o que tens em casa e nós criamos uma receita para ti.</p>
          <span class="fridge-cta">Ver Sugestões &rarr;</span>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
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

.dashboard-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 22px;
}

.card {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card h3 {
  margin: 0 0 16px;
  font-size: 1.05rem;
  font-weight: 700;
}

.card-subtitle {
  margin-top: 12px;
  font-size: 0.9rem;
  color: var(--text-muted);
}

/* Hungry Card */
.hungry-card {
  background: linear-gradient(135deg, var(--menu-highlight-bg), var(--menu-highlight-hover-bg));
  color: var(--menu-highlight-text);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.hungry-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.1);
}

.hungry-card-content {
  text-align: center;
  width: 100%;
}

.hungry-icon {
  font-size: 2.5rem;
}

.hungry-card h2 {
  margin: 8px 0;
  font-size: 1.8rem;
  color: var(--menu-highlight-active-text);
}

.hungry-card p {
  margin: 0 auto 16px;
  max-width: 45ch;
  opacity: 0.9;
  color: var(--menu-highlight-text);
}

.hungry-cta {
  font-weight: 700;
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(0,0,0,0.05);
}

/* Fridge Card */
.fridge-card {
  background: linear-gradient(135deg, #e0f2fe, #dbeafe);
  color: #0c4a6e;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.fridge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.1);
}

.fridge-card-content {
  text-align: center;
  width: 100%;
}

.fridge-icon {
  font-size: 2.5rem;
}

.fridge-card h2 {
  margin: 8px 0;
  font-size: 1.8rem;
  color: #1e3a8a;
}

.fridge-card p {
  margin: 0 auto 16px;
  max-width: 45ch;
  opacity: 0.9;
  color: #0c4a6e;
}

.fridge-cta {
  font-weight: 700;
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(0,0,0,0.05);
}

/* Calorie Card */
.calorie-tracker {
  margin-top: 16px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: var(--line);
  border-radius: 99px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: #10b981; /* A nice green */
  border-radius: 99px;
  transition: width 0.5s ease;
}

.calorie-text {
  margin-top: 8px;
  font-size: 0.95rem;
  color: var(--text-muted);
}

.calorie-text strong {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
}

/* Streak Card */
.streak-display {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.streak-icon {
  font-size: 2.5rem;
}

.streak-count {
  font-size: 2.8rem;
  font-weight: 800;
  color: #f97316; /* A nice orange */
  line-height: 1;
}

.streak-display span {
  color: var(--text-muted);
}

:global(.theme-dark) .card {
  box-shadow: 0 10px 22px rgba(3, 8, 18, 0.35);
}

:global(.theme-dark) .progress {
  background: #34d399;
}

:global(.theme-dark) .fridge-card {
  background: linear-gradient(135deg, #1e293b, #172554);
  color: #93c5fd;
}
:global(.theme-dark) .fridge-card h2 {
  color: #bfdbfe;
}
:global(.theme-dark) .fridge-card p {
  color: #93c5fd;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
  }
  .calorie-card {
    grid-column: 1 / 2;
    grid-row: 1;
  }
  .streak-card {
    grid-column: 2 / 3;
    grid-row: 1;
  }
  .weight-chart-card {
    grid-column: 1 / -1;
    grid-row: 2;
  }
  .hungry-card {
    grid-column: 1 / 2;
    grid-row: 3;
  }
  .fridge-card {
    grid-column: 2 / 3;
    grid-row: 3;
  }
}
</style>