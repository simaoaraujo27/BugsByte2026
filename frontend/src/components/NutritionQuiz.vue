<script setup>
import { ref } from 'vue'

const questions = [
  { q: 'Beber água às refeições dificulta a digestão?', a: false, exp: 'A água pode até ajudar a suavizar o bolo alimentar.' },
  { q: 'Pão torrado tem menos calorias que pão normal?', a: false, exp: 'Apenas perde água, as calorias mantêm-se as mesmas.' },
  { q: 'Ovos aumentam perigosamente o colesterol?', a: false, exp: 'Ovos são nutritivos e o impacto no colesterol é mínimo para a maioria.' },
  { q: 'Comer fruta à noite engorda mais?', a: false, exp: 'A fruta tem as mesmas calorias a qualquer hora do dia.' },
  { q: 'Beber água morna com limão em jejum queima gordura?', a: false, exp: 'Ajuda na hidratação, mas não tem propriedades mágicas de queima.' }
]

const currentIndex = ref(0)
const score = ref(0)
const showResult = ref(false)
const feedback = ref(null)

const answer = (val) => {
  const correct = val === questions[currentIndex.value].a
  if (correct) score.value++
  
  feedback.value = {
    correct,
    text: questions[currentIndex.value].exp
  }
}

const next = () => {
  feedback.value = null
  if (currentIndex.value < questions.length - 1) {
    currentIndex.value++
  } else {
    showResult.value = true
  }
}

const restart = () => {
  currentIndex.value = 0
  score.value = 0
  showResult.value = false
  feedback.value = null
}
</script>

<template>
  <div class="quiz-container">
    <div v-if="!showResult">
      <div class="quiz-header">
        Questão {{ currentIndex + 1 }}/{{ questions.length }}
      </div>
      
      <div class="question-text">
        {{ questions[currentIndex].q }}
      </div>

      <div v-if="!feedback" class="quiz-actions">
        <button @click="answer(true)" class="btn-quiz btn-true">Verdadeiro</button>
        <button @click="answer(false)" class="btn-quiz btn-false">Falso</button>
      </div>

      <div v-else class="feedback-area" :class="{ 'is-correct': feedback.correct }">
        <div class="feedback-status">
          {{ feedback.correct ? '✅ Correto!' : '❌ Errado.' }}
        </div>
        <p>{{ feedback.text }}</p>
        <button @click="next" class="btn-next">
          {{ currentIndex < questions.length - 1 ? 'Próxima Questão' : 'Ver Resultados' }}
        </button>
      </div>
    </div>

    <div v-else class="quiz-result">
      <h3>Quiz Terminado! 🏆</h3>
      <div class="final-score">{{ score }} / {{ questions.length }}</div>
      <p v-if="score === questions.length">Perfeito! És um perito em nutrição.</p>
      <p v-else-if="score > questions.length / 2">Muito bem! Tens bons conhecimentos.</p>
      <p v-else>Continua a aprender com a Nutra!</p>
      <button @click="restart" class="btn-restart">Tentar Novamente</button>
    </div>
  </div>
</template>

<style scoped>
.quiz-container {
  margin-top: 15px;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.quiz-header {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.question-text {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-main);
  line-height: 1.4;
}

.quiz-actions {
  display: flex;
  gap: 12px;
}

.btn-quiz {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  border: 2px solid transparent;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-true {
  background: #ecfdf5;
  color: #059669;
}

.btn-true:hover { background: #d1fae5; }

.btn-false {
  background: #fef2f2;
  color: #dc2626;
}

.btn-false:hover { background: #fee2e2; }

.feedback-area {
  padding: 15px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.feedback-area.is-correct {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.feedback-status {
  font-weight: 800;
  margin-bottom: 8px;
}

.feedback-area p {
  font-size: 0.9rem;
  margin-bottom: 15px;
  color: var(--text-muted);
}

.btn-next, .btn-restart {
  background: var(--menu-active-text);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.quiz-result h3 {
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.final-score {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--menu-active-text);
  margin-bottom: 10px;
}

:global(.theme-dark) .feedback-area {
  background: #1e293b;
  border-color: #334155;
}
</style>
