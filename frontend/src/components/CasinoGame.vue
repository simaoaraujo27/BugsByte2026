<script setup>
import { ref, computed } from 'vue'

const activeGame = ref('slots') // 'slots', 'blackjack', 'roulette'
const credits = ref(100)
const lastResult = ref('')

// --- SLOTS LOGIC ---
const emojis = ['🍎', '🥦', '🍔', '🍕', '🥗', '🎰', '🥑', '🍩']
const reels = ref(['🎰', '🎰', '🎰'])
const spinning = ref(false)

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
      checkSlotsWin()
    }
  }, 100)
}

const checkSlotsWin = () => {
  const [r1, r2, r3] = reels.value
  if (r1 === r2 && r2 === r3) {
    let win = r1 === '🎰' ? 500 : (['🍎', '🥦', '🥗', '🥑'].includes(r1) ? 100 : 50)
    credits.value += win
    lastResult.value = `GANHASTE ${win} CRÉDITOS! 🎉`
  } else if (r1 === r2 || r2 === r3 || r1 === r3) {
    credits.value += 15
    lastResult.value = 'Quase! Ganhaste 15 créditos.'
  } else {
    lastResult.value = 'Tenta outra vez!'
  }
}

// --- BLACKJACK LOGIC ---
const playerHand = ref([])
const dealerHand = ref([])
const gameStatus = ref('betting') // 'betting', 'playing', 'finished'

const calculateScore = (hand) => {
  let score = 0
  let aces = 0
  hand.forEach(card => {
    if (card.val === 'A') aces++
    score += card.weight
  })
  while (score > 21 && aces > 0) {
    score -= 10
    aces--
  }
  return score
}

const drawCard = () => {
  const suits = ['♠', '♥', '♦', '♣']
  const values = [
    {n:'2',w:2}, {n:'3',w:3}, {n:'4',w:4}, {n:'5',w:5}, {n:'6',w:6}, {n:'7',w:7}, 
    {n:'8',w:8}, {n:'9',w:9}, {n:'10',w:10}, {n:'J',w:10}, {n:'Q',w:10}, {n:'K',w:10}, {n:'A',w:11}
  ]
  const val = values[Math.floor(Math.random() * values.length)]
  return { val: val.n, suit: suits[Math.floor(Math.random() * suits.length)], weight: val.w }
}

const startBlackjack = () => {
  if (credits.value < 20) return
  credits.value -= 20
  playerHand.value = [drawCard(), drawCard()]
  dealerHand.value = [drawCard()]
  gameStatus.value = 'playing'
  lastResult.value = ''
  if (calculateScore(playerHand.value) === 21) stand()
}

const hit = () => {
  playerHand.value.push(drawCard())
  if (calculateScore(playerHand.value) > 21) {
    gameStatus.value = 'finished'
    lastResult.value = 'Bust! Perdeste.'
  }
}

const stand = () => {
  while (calculateScore(dealerHand.value) < 17) {
    dealerHand.value.push(drawCard())
  }
  gameStatus.value = 'finished'
  const pScore = calculateScore(playerHand.value)
  const dScore = calculateScore(dealerHand.value)
  if (dScore > 21 || pScore > dScore) {
    credits.value += 40
    lastResult.value = 'Ganhaste! +40 créditos.'
  } else if (pScore === dScore) {
    credits.value += 20
    lastResult.value = 'Empate! Créditos devolvidos.'
  } else {
    lastResult.value = 'O Dealer ganha.'
  }
}

// --- ROULETTE LOGIC ---
const selectedColor = ref('red')
const isRolling = ref(false)
const rouletteResult = ref(null)

const playRoulette = () => {
  if (credits.value < 15 || isRolling.value) return
  credits.value -= 15
  isRolling.value = true
  lastResult.value = ''
  
  setTimeout(() => {
    const num = Math.floor(Math.random() * 37)
    rouletteResult.value = num
    const color = num === 0 ? 'green' : (num % 2 === 0 ? 'black' : 'red')
    
    if (color === selectedColor.value) {
      credits.value += 30
      lastResult.value = `Saiu ${num} (${color}). Ganhaste 30!`
    } else {
      lastResult.value = `Saiu ${num} (${color}). Perdeste.`
    }
    isRolling.value = false
  }, 1500)
}
</script>

<template>
  <div class="casino-container">
    <div class="casino-nav">
      <button @click="activeGame = 'slots'" :class="{ active: activeGame === 'slots' }">Slots</button>
      <button @click="activeGame = 'blackjack'" :class="{ active: activeGame === 'blackjack' }">Blackjack</button>
      <button @click="activeGame = 'roulette'" :class="{ active: activeGame === 'roulette' }">Roleta</button>
    </div>

    <div class="credits-badge">Créditos: {{ credits }}</div>

    <!-- SLOTS VIEW -->
    <div v-if="activeGame === 'slots'" class="game-view">
      <div class="reels-container">
        <div v-for="(emoji, i) in reels" :key="i" class="reel" :class="{ spinning }">{{ emoji }}</div>
      </div>
      <button @click="spin" :disabled="spinning || credits < 10" class="btn-action">GIRAR (10)</button>
    </div>

    <!-- BLACKJACK VIEW -->
    <div v-if="activeGame === 'blackjack'" class="game-view">
      <div v-if="gameStatus === 'betting'">
        <button @click="startBlackjack" class="btn-action">Apostar 20 e Jogar</button>
      </div>
      <div v-else class="blackjack-table">
        <div class="hand-label">Dealer: {{ dealerHand.length ? calculateScore(dealerHand) : 0 }}</div>
        <div class="cards"><span v-for="c in dealerHand" class="card">{{ c.val }}{{ c.suit }}</span></div>
        <div class="hand-label">Tu: {{ calculateScore(playerHand) }}</div>
        <div class="cards"><span v-for="c in playerHand" class="card player">{{ c.val }}{{ c.suit }}</span></div>
        <div v-if="gameStatus === 'playing'" class="bj-controls">
          <button @click="hit" class="btn-bj">Hit</button>
          <button @click="stand" class="btn-bj stand">Stand</button>
        </div>
        <button v-else @click="gameStatus = 'betting'" class="btn-action">Novo Jogo</button>
      </div>
    </div>

    <!-- ROULETTE VIEW -->
    <div v-if="activeGame === 'roulette'" class="game-view">
      <div class="roulette-wheel" :class="{ rolling: isRolling }">
        {{ isRolling ? '🎡' : (rouletteResult ?? '❓') }}
      </div>
      <div class="color-picker">
        <button @click="selectedColor = 'red'" :class="{ active: selectedColor === 'red' }" class="c-red">Vermelho</button>
        <button @click="selectedColor = 'black'" :class="{ active: selectedColor === 'black' }" class="c-black">Preto</button>
      </div>
      <button @click="playRoulette" :disabled="isRolling || credits < 15" class="btn-action">APOSTAR 15</button>
    </div>

    <div class="result-text" :class="{ win: lastResult.includes('Ganh') }">{{ lastResult }}</div>
  </div>
</template>

<style scoped>
.casino-container {
  margin-top: 15px; background: rgba(0, 0, 0, 0.05); border-radius: 16px; padding: 15px; text-align: center;
}
.casino-nav { display: flex; gap: 5px; margin-bottom: 12px; }
.casino-nav button { flex: 1; padding: 6px; border-radius: 8px; border: none; font-size: 0.8rem; cursor: pointer; background: #e2e8f0; }
.casino-nav button.active { background: #0d9488 !important; color: white !important; }

.game-view { min-height: 140px; display: flex; flex-direction: column; justify-content: center; }
.credits-badge { background: #0d9488; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; margin-bottom: 10px; display: inline-block; }

.reels-container { display: flex; justify-content: center; gap: 8px; margin-bottom: 12px; }
.reel { width: 50px; height: 50px; background: white; border: 2px solid #e2e8f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }

.blackjack-table { margin-bottom: 10px; }
.hand-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; }
.cards { display: flex; justify-content: center; gap: 5px; margin: 5px 0 10px; }
.card { padding: 5px 8px; background: white; border: 1px solid #cbd5e1; border-radius: 5px; font-weight: 700; font-size: 0.9rem; }
.card.player { border-color: #0d9488; color: #0d9488; }
.bj-controls { display: flex; gap: 10px; }
.btn-bj { flex: 1; padding: 8px; border-radius: 8px; border: none; font-weight: 700; cursor: pointer; background: #0d9488; color: white; }
.btn-bj.stand { background: #64748b; }

.roulette-wheel { font-size: 3rem; margin-bottom: 10px; }
.color-picker { display: flex; gap: 10px; margin-bottom: 10px; }
.color-picker button { flex: 1; padding: 8px; border-radius: 8px; border: 2px solid transparent; cursor: pointer; color: white; }
.c-red { background: #ef4444; }
.c-black { background: #1e293b; }
.color-picker button.active { border-color: #fbbf24; transform: scale(1.05); }

.btn-action { width: 100%; background: #f59e0b; color: white; border: none; padding: 10px; border-radius: 10px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 0 #92400e; }
.btn-action:active { transform: translateY(2px); box-shadow: 0 1px 0 #92400e; }

.result-text { margin-top: 10px; font-size: 0.9rem; font-weight: 700; color: #64748b; min-height: 1.2em; }
.result-text.win { color: #059669; }

:global(.theme-dark) .casino-container { background: rgba(255, 255, 255, 0.05); }
:global(.theme-dark) .reel, :global(.theme-dark) .card { background: #1e293b; color: white; border-color: #334155; }

.rolling {
  animation: spin 0.5s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
