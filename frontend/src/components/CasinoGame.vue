<script setup>
import { ref } from 'vue'

const emojis = ['🍎', '🥦', '🍔', '🍕', '🥗', '🎰', '🥑', '🍩']
const reels = ref(['🎰', '🎰', '🎰'])
const spinning = ref(false)
const credits = ref(100)
const lastResult = ref('')

const spin = () => {
  if (credits.value < 10 || spinning.value) return
  
  credits.value -= 10
  spinning.value = true
  lastResult.value = ''
  
  let spinCount = 0
  const interval = setInterval(() => {
    reels.value = reels.value.map(() => emojis[Math.floor(Math.random() * emojis.length)])
    spinCount++
    
    if (spinCount > 15) {
      clearInterval(interval)
      spinning.value = false
      checkWin()
    }
  }, 100)
}

const checkWin = () => {
  const [r1, r2, r3] = reels.value
  if (r1 === r2 && r2 === r3) {
    let win = 0
    if (r1 === '🎰') win = 500
    else if (r1 === '🍎' || r1 === '🥦' || r1 === '🥗' || r1 === '🥑') win = 100
    else win = 50 // Junk food win
    
    credits.value += win
    lastResult.value = `GANHASTE ${win} CRÉDITOS! 🎉`
  } else if (r1 === r2 || r2 === r3 || r1 === r3) {
    credits.value += 15
    lastResult.value = 'Quase! Ganhaste 15 créditos.'
  } else {
    lastResult.value = 'Tenta outra vez!'
  }
}
</script>

<template>
  <div class="casino-container">
    <div class="credits-badge">Créditos: {{ credits }}</div>
    
    <div class="reels-container">
      <div v-for="(emoji, i) in reels" :key="i" class="reel" :class="{ spinning }">
        {{ emoji }}
      </div>
    </div>
    
    <div class="result-text" :class="{ win: lastResult.includes('GANHASTE') }">
      {{ lastResult || 'Aposta 10 créditos!' }}
    </div>
    
    <button 
      @click="spin" 
      :disabled="spinning || credits < 10"
      class="spin-button"
    >
      {{ spinning ? 'A girar...' : 'GIRAR! 🎰' }}
    </button>
  </div>
</template>

<style scoped>
.casino-container {
  margin-top: 15px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.credits-badge {
  background: #0d9488;
  color: white;
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 12px;
}

.reels-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.reel {
  width: 60px;
  height: 60px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}

.reel.spinning {
  animation: reelBlur 0.1s infinite;
}

@keyframes reelBlur {
  0% { transform: translateY(-2px); filter: blur(1px); }
  50% { transform: translateY(2px); filter: blur(2px); }
  100% { transform: translateY(-2px); filter: blur(1px); }
}

.result-text {
  font-size: 0.9rem;
  font-weight: 600;
  min-height: 1.4em;
  margin-bottom: 12px;
  color: #64748b;
}

.result-text.win {
  color: #059669;
  animation: winPulse 0.5s infinite alternate;
}

@keyframes winPulse {
  from { transform: scale(1); }
  to { transform: scale(1.05); }
}

.spin-button {
  width: 100%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 10px;
  font-weight: 800;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 0 #92400e;
}

.spin-button:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.spin-button:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow: 0 1px 0 #92400e;
}

.spin-button:disabled {
  background: #cbd5e1;
  box-shadow: 0 4px 0 #94a3b8;
  cursor: not-allowed;
}

/* Dark mode adjustments if needed */
:global(.theme-dark) .casino-container {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

:global(.theme-dark) .reel {
  background: #1e293b;
  border-color: #334155;
  color: white;
}

:global(.theme-dark) .result-text {
  color: #94a3b8;
}
</style>
