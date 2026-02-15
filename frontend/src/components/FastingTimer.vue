<script setup>
import { ref, onUnmounted, computed } from 'vue'

const durationHours = ref(16)
const isRunning = ref(false)
const timeLeft = ref(0)
let timer = null

const startTimer = () => {
  timeLeft.value = durationHours.value * 3600
  isRunning.value = true
  
  timer = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
    } else {
      stopTimer()
    }
  }, 1000)
}

const stopTimer = () => {
  isRunning.value = false
  if (timer) clearInterval(timer)
}

const formattedTime = computed(() => {
  const h = Math.floor(timeLeft.value / 3600)
  const m = Math.floor((timeLeft.value % 3600) / 60)
  const s = timeLeft.value % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const progress = computed(() => {
  const total = durationHours.value * 3600
  return ((total - timeLeft.value) / total) * 100
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="timer-container">
    <h4>Cronómetro de Jejum ⏳</h4>
    
    <div v-if="!isRunning" class="setup-area">
      <div class="hours-selector">
        <button v-for="h in [12, 14, 16, 18]" :key="h" 
                @click="durationHours = h" 
                :class="{ active: durationHours === h }">
          {{ h }}h
        </button>
      </div>
      <button @click="startTimer" class="btn-start">Começar Jejum</button>
    </div>

    <div v-else class="running-area">
      <div class="progress-circle">
        <svg viewBox="0 0 36 36" class="circular-chart">
          <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          <path class="circle" :stroke-dasharray="`${progress}, 100`" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
        </svg>
        <div class="time-display">{{ formattedTime }}</div>
      </div>
      <button @click="stopTimer" class="btn-stop">Parar</button>
    </div>
  </div>
</template>

<style scoped>
.timer-container {
  margin-top: 15px;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
  text-align: center;
}

h4 { margin: 0 0 15px; font-size: 1rem; }

.hours-selector {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 15px;
}

.hours-selector button {
  background: var(--bg-main);
  border: 1px solid var(--line);
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-main);
}

.hours-selector button.active {
  background: var(--menu-active-text);
  color: white;
  border-color: var(--menu-active-text);
}

.btn-start, .btn-stop {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.btn-start { background: var(--menu-active-text); color: white; }
.btn-stop { background: #fee2e2; color: #dc2626; }

.progress-circle {
  position: relative;
  width: 120px;
  margin: 0 auto 15px;
}

.circular-chart { display: block; margin: 0 auto; max-width: 100%; max-height: 250px; }
.circle-bg { fill: none; stroke: var(--line); stroke-width: 2.8; }
.circle { fill: none; stroke: var(--menu-active-text); stroke-width: 2.8; stroke-linecap: round; transition: stroke-dasharray 0.3s; }
.time-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-main);
}
</style>
