<script setup>
import { computed, ref } from 'vue'

const selectedPeriod = ref('1M') // 1S, 1M, 1A, ALL
const timePeriods = [
  { id: '1S', label: '1S' },
  { id: '1M', label: '1M' },
  { id: '1A', label: '1A' },
  { id: 'ALL', label: 'Tudo' }
]

// Dummy data for now
const weightData = {
  '1S': {
    labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
    data: [70.5, 70.2, 70.3, 69.9, 70.0, 69.8, 69.7]
  },
  '1M': {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
    data: [71.0, 70.5, 70.1, 69.7]
  },
  '1A': {
    labels: [], // Simulating no data for this period
    data: []
  },
  'ALL': {
    labels: ['2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4', '2024-Q1', '2024-Q2'],
    data: [75, 74, 73, 72, 71, 69.7]
  }
}

const hasDataForPeriod = computed(() => {
  const periodData = weightData[selectedPeriod.value]
  return periodData && periodData.data && periodData.data.length > 0
})

const chartLabels = computed(() => weightData[selectedPeriod.value].labels || [])
const chartValues = computed(() => weightData[selectedPeriod.value].data || [])

const chartPoints = computed(() => {
  const values = chartValues.value
  if (!values.length) return []

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = Math.max(0.1, max - min)
  const top = 16
  const bottom = 30
  const height = 100 - top - bottom

  return values.map((value, index) => {
    const x = (100 / values.length) * (index + 0.5)
    const y = top + ((max - value) / range) * height
    return { x, y, value }
  })
})

const chartPath = computed(() => {
  if (!chartPoints.value.length) return ''
  return chartPoints.value
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ')
})
</script>

<template>
  <article class="card weight-chart-card">
    <div class="chart-header">
      <h3>Evolução do Peso</h3>
      <div class="period-selector">
        <button
          v-for="period in timePeriods"
          :key="period.id"
          type="button"
          class="period-btn"
          :class="{ active: selectedPeriod === period.id }"
          @click="selectedPeriod = period.id"
        >
          {{ period.label }}
        </button>
      </div>
    </div>
    <div class="chart-container">
      <div v-if="hasDataForPeriod" class="svg-chart-wrap">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" class="svg-chart" aria-label="Grafico de peso">
          <line x1="0" y1="70" x2="100" y2="70" class="axis" />
          <path :d="chartPath" class="line-path" />
          <circle v-for="(point, idx) in chartPoints" :key="idx" :cx="point.x" :cy="point.y" r="1.5" class="dot" />
        </svg>
        <div class="labels-row">
          <span v-for="label in chartLabels" :key="label">{{ label }}</span>
        </div>
      </div>
      <div v-else class="no-data-message">
        <p>Sem dados de peso para este período.</p>
        <small>Regista o teu peso regularmente no diário.</small>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.card h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.weight-chart-card {
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.period-selector {
  display: flex;
  gap: 4px;
  background: var(--bg-main);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid var(--line);
}

.period-btn {
  border: 0;
  background: transparent;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.period-btn.active {
  background: var(--bg-elevated);
  color: var(--text-main);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chart-container {
  position: relative;
  height: 250px;
  flex-grow: 1;
}

.svg-chart-wrap {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.svg-chart {
  flex: 1;
  width: 100%;
}

.axis {
  stroke: rgba(148, 163, 184, 0.45);
  stroke-width: 0.5;
}

.line-path {
  fill: none;
  stroke: #10b981;
  stroke-width: 1.2;
  vector-effect: non-scaling-stroke;
}

.dot {
  fill: #10b981;
}

.labels-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 4px;
  margin-top: 6px;
}

.labels-row span {
  color: var(--text-muted);
  font-size: 0.72rem;
  text-align: center;
}

.no-data-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--text-muted);
}

.no-data-message p {
  margin: 0;
  font-weight: 600;
}

.no-data-message small {
  margin-top: 6px;
  font-size: 0.9rem;
}

:global(.theme-dark) .card {
  box-shadow: 0 10px 22px rgba(3, 8, 18, 0.35);
}
</style>
