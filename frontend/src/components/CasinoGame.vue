<script setup>
import { ref, computed } from 'vue'

const activeGame = ref('slots')
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
const gameStatus = ref('betting')

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
  const suit = suits[Math.floor(Math.random() * suits.length)]
  return { val: val.n, suit, weight: val.w, color: (suit === '♥' || suit === '♦') ? 'red' : 'black' }
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
const wheelRotation = ref(0)
const numbersOrder = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

const playRoulette = () => {
  if (credits.value < 15 || isRolling.value) return
  credits.value -= 15
  isRolling.value = true
  lastResult.value = ''
  
  const num = numbersOrder[Math.floor(Math.random() * numbersOrder.length)]
  const index = numbersOrder.indexOf(num)
  const segmentAngle = 360 / 37
  
  // To make index land at the top (pointer), wheel must be at -(index * segmentAngle)
  const targetRotation = 360 - (index * segmentAngle)
  const extraTurns = 1800 // 5 full turns
  const currentRotBase = wheelRotation.value - (wheelRotation.value % 360)
  
  wheelRotation.value = currentRotBase + extraTurns + targetRotation
  
  setTimeout(() => {
    rouletteResult.value = num
    const isRed = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(num)
    const color = num === 0 ? 'green' : (isRed ? 'red' : 'black')
    
    if (color === selectedColor.value) {
      credits.value += 30
      lastResult.value = `Saiu ${num} (${color}). Ganhaste 30!`
    } else {
      lastResult.value = `Saiu ${num} (${color}). Perdeste.`
    }
    isRolling.value = false
  }, 2000)
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
        <div class="cards">
          <span v-for="c in dealerHand" class="card" :style="{ color: c.color }">{{ c.val }}{{ c.suit }}</span>
        </div>
        <div class="hand-label">Tu: {{ calculateScore(playerHand) }}</div>
        <div class="cards">
          <span v-for="c in playerHand" class="card player" :style="{ color: c.color }">{{ c.val }}{{ c.suit }}</span>
        </div>
        <div v-if="gameStatus === 'playing'" class="bj-controls">
          <button @click="hit" class="btn-bj">Hit</button>
          <button @click="stand" class="btn-bj stand">Stand</button>
        </div>
        <button v-else @click="gameStatus = 'betting'" class="btn-action">Novo Jogo</button>
      </div>
    </div>

    <!-- ROULETTE VIEW -->
    <div v-if="activeGame === 'roulette'" class="game-view">
      <div class="roulette-wrapper">
        <div class="roulette-pointer">▼</div>
        <div class="roulette-wheel-2d" :style="{ transform: `rotate(${wheelRotation}deg)` }">
          <div v-for="(n, i) in numbersOrder" :key="i" class="segment" :style="{ transform: `rotate(${i * (360/37)}deg)` }">
            <span :class="{ 'red': [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n), 'green': n === 0, 'black': n !== 0 && ![1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) }">
              {{ n }}
            </span>
          </div>
          <div class="roulette-hub"></div>
        </div>
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
.casino-nav button { flex: 1; padding: 6px; border-radius: 8px; border: none; font-size: 0.8rem; cursor: pointer; background: #cbd5e1; color: #1e293b; font-weight: 700; }
.casino-nav button.active { background: #0d9488 !important; color: white !important; }

.game-view { min-height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.credits-badge { background: #0d9488; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; margin-bottom: 10px; }

/* SLOTS */
.reels-container {
  width: 100%;
  max-width: 280px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}

.reel {
  height: 72px;
  border-radius: 12px;
  border: 2px solid #0d9488;
  background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: inset 0 2px 8px rgba(15, 23, 42, 0.1), 0 2px 4px rgba(2, 6, 23, 0.15);
}

.reel.spinning {
  animation: slotPulse 0.18s linear infinite;
}

@keyframes slotPulse {
  0% { transform: translateY(0); filter: saturate(100%); }
  50% { transform: translateY(-2px); filter: saturate(130%); }
  100% { transform: translateY(0); filter: saturate(100%); }
}

/* BLACKJACK */
.blackjack-table { width: 100%; }
.hand-label { font-size: 0.7rem; color: #64748b; font-weight: 800; text-transform: uppercase; }
.cards { display: flex; justify-content: center; gap: 6px; margin: 8px 0; }
.card { 
  width: 38px; height: 50px; background: white; border: 1px solid #94a3b8; border-radius: 4px;
  display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.card.player { border-color: #0d9488; background: #f0fdfa; }
.bj-controls {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 10px;
}
.btn-bj {
  border: none;
  border-radius: 10px;
  padding: 10px 0;
  font-weight: 900;
  font-size: 0.95rem;
  cursor: pointer;
  color: #ffffff;
  background: linear-gradient(180deg, #0ea5a4 0%, #0d9488 100%);
  box-shadow: 0 4px 0 #0f766e;
}
.btn-bj.stand {
  background: linear-gradient(180deg, #475569 0%, #334155 100%);
  box-shadow: 0 4px 0 #1e293b;
}
.btn-bj:active {
  transform: translateY(2px);
  box-shadow: 0 2px 0 #0f766e;
}
.btn-bj.stand:active {
  box-shadow: 0 2px 0 #1e293b;
}

/* ROULETTE 2D */
.roulette-wrapper { position: relative; width: 172px; height: 172px; margin-bottom: 15px; }
.roulette-pointer { 
  position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  z-index: 12; color: #f59e0b; font-size: 1.35rem; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.35));
}
.roulette-wheel-2d {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 5px solid #94a3b8;
  position: relative;
  overflow: hidden;
  transition: transform 2s cubic-bezier(0.1, 0, 0.2, 1);
  background:
    radial-gradient(circle at center, #0b1324 0 31%, transparent 31%),
    radial-gradient(circle at center, transparent 0 66%, #0b1324 66% 100%),
    linear-gradient(180deg, #111827 0%, #0f172a 100%);
  box-shadow: inset 0 0 0 3px #1e293b, 0 8px 22px rgba(2, 6, 23, 0.45);
}
.segment {
  position: absolute;
  width: 18px;
  height: 82px;
  left: 50%;
  top: 50%;
  margin-left: -9px;
  margin-top: -82px;
  transform-origin: 9px 82px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.segment span {
  width: 16px;
  height: 16px;
  font-size: 0.5rem;
  font-weight: 900;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}
.segment span.red { background: #ef4444; }
.segment span.black { background: #000; }
.segment span.green { background: #22c55e; }
.roulette-hub {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 30px;
  height: 30px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #f8fafc 0%, #cbd5e1 55%, #64748b 100%);
  box-shadow: 0 0 0 3px #1e293b, 0 3px 10px rgba(2, 6, 23, 0.45);
  z-index: 8;
}

/* BUTTONS */
.color-picker { display: flex; gap: 8px; margin-bottom: 10px; width: 100%; }
.color-picker button { flex: 1; padding: 10px; border-radius: 10px; border: 3px solid transparent; color: white; font-weight: 900; cursor: pointer; }
.c-red { background: #ef4444; }
.c-black { background: #1e293b; }
.color-picker button.active { border-color: #fbbf24; transform: scale(1.02); }

.btn-action { width: 100%; background: #f59e0b; color: white; border: none; padding: 12px; border-radius: 12px; font-weight: 900; cursor: pointer; box-shadow: 0 4px 0 #92400e; }
.btn-action:active { transform: translateY(2px); box-shadow: 0 2px 0 #92400e; }

.result-text { margin-top: 10px; font-weight: 800; color: #1e293b; min-height: 1.2em; }
.result-text.win { color: #059669; }

/* DARK MODE FIXES */
:global(.theme-dark) .casino-container { background: rgba(255, 255, 255, 0.05); }
:global(.theme-dark) .reel {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  border-color: #22d3ee;
}
:global(.theme-dark) .card { background: #f8fafc; border-color: #cbd5e1; color: #0f172a; }
:global(.theme-dark) .card.player { background: #ccfbf1; border-color: #0d9488; }
:global(.theme-dark) .btn-bj { background: linear-gradient(180deg, #14b8a6 0%, #0d9488 100%); }
:global(.theme-dark) .btn-bj.stand { background: linear-gradient(180deg, #64748b 0%, #475569 100%); }
:global(.theme-dark) .result-text { color: #f8fafc; }
:global(.theme-dark) .casino-nav button { background: #334155; color: #cbd5e1; }
:global(.theme-dark) .hand-label { color: #94a3b8; }
</style>
