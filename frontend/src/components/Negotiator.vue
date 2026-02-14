<script setup>
import { ref } from 'vue';

const emit = defineEmits(['choice']);

const craving = ref('');
const result = ref(null);
const loading = ref(false);
const error = ref(null);

const negotiate = async () => {
  if (!craving.value.trim()) return;

  loading.value = true;
  error.value = null;
  result.value = null;

  try {
    const response = await fetch('http://localhost:8000/negotiator/negotiate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ craving: craving.value, target_calories: 600 })
    });

    if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Erro na negociação");
    }
    result.value = await response.json();
  } catch (e) {
    error.value = e.message;
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const goToIngredients = () => {
  emit('choice', {
    type: 'diy',
    ingredients: result.value.recipe.ingredients.join(',')
  });
};
</script>

<template>
  <div class="negotiator-container">
    <div v-if="!result" class="hero-section">
      <h1 class="glow-title">TENHO FOME!</h1>
      <p class="subtitle">Diz-nos o que te apetece e o nosso Chef Nutricionista vai negociar uma alternativa irresistível.</p>
      
      <div class="search-box-large">
        <input 
          v-model="craving" 
          type="text" 
          placeholder="O que te apetece comer? (Ex: Lasanha, Pizza...)" 
          @keyup.enter="negotiate"
          :disabled="loading"
        />
        <button @click="negotiate" :disabled="loading" class="btn-glow">
          {{ loading ? 'A analisar...' : 'Negociar Agora' }}
        </button>
      </div>
      
      <div v-if="error" class="error-bubble">{{ error }}</div>
      <p class="disclaimer">Por favor, introduz apenas pedidos relacionados com alimentação.</p>
      
      <div class="suggestions-chips">
        <span>Sugestões:</span>
        <button @click="craving = 'Hambúrguer Gourmet'; negotiate()">🍔 Hambúrguer</button>
        <button @click="craving = 'Pizza Pepperoni'; negotiate()">🍕 Pizza</button>
        <button @click="craving = 'Sushi Variado'; negotiate()">🍣 Sushi</button>
      </div>
    </div>

    <div v-else-if="result && result.recipe" class="recipe-display fade-in">
      <header class="recipe-header">
        <div class="badge-calories">{{ result.recipe.calories }} kcal</div>
        <h2 class="recipe-title">{{ result.recipe.title }}</h2>
        <p class="chef-message">"{{ result.message }}"</p>
        
        <div class="recipe-meta">
          <span>⏱️ {{ result.recipe.time_minutes }} min</span>
          <span>👨‍🍳 Dificuldade: Média</span>
          <span>🌱 100% Saudável</span>
        </div>
      </header>

      <div class="recipe-content-grid">
        <!-- Ingredients Column -->
        <section class="ingredients-card">
          <h3>🛒 Ingredientes</h3>
          <ul class="styled-list">
            <li v-for="ing in result.recipe.ingredients" :key="ing">{{ ing }}</li>
          </ul>
          <button @click="goToIngredients" class="btn-shop-link">
            Encontrar Ingredientes Perto 📍
          </button>
        </section>

        <!-- Steps Column -->
        <section class="steps-card">
          <h3>👨‍🍳 Modo de Preparação</h3>
          <div class="steps-timeline">
            <div v-for="(step, index) in result.recipe.steps" :key="index" class="step-item">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-text">{{ step }}</div>
            </div>
          </div>
        </section>
      </div>
      
      <footer class="recipe-actions">
        <button @click="result = null" class="btn-secondary">🔙 Outro Desejo</button>
        <button @click="negotiate" class="btn-refresh">🔄 Outra Receita</button>
      </footer>
    </div>

    <!-- Rejection Screen -->
    <div v-else-if="result && !result.recipe" class="rejection-card fade-in">
      <div class="icon">🚫</div>
      <h2>Pedido Inválido</h2>
      <p>{{ result.message }}</p>
      <button @click="result = null" class="btn-primary">Tentar Novamente</button>
    </div>
  </div>
</template>

<style scoped>
.negotiator-container {
  max-width: 1000px;
  margin: 0 auto;
  font-family: 'Sora', sans-serif;
  padding-bottom: 60px;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 60px 20px;
}

.glow-title {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 900;
  color: #e74c3c;
  text-shadow: 0 0 20px rgba(231, 76, 60, 0.2);
  margin-bottom: 16px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto 40px;
}

.search-box-large {
  display: flex;
  background: var(--bg-elevated);
  padding: 8px;
  border-radius: 20px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.08);
  max-width: 700px;
  margin: 0 auto 24px;
}

.search-box-large input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 16px 24px;
  font-size: 1.1rem;
  border-radius: 16px;
  outline: none;
  color: var(--text-main);
}

.btn-glow {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0 32px;
  border-radius: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(231, 76, 60, 0.3);
}

.suggestions-chips {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.suggestions-chips button {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  color: var(--text-main);
  font-weight: 600;
}

/* Recipe Display */
.recipe-display {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 32px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.05);
  overflow: hidden;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.recipe-header {
  background: linear-gradient(135deg, var(--bg-main) 0%, var(--bg-elevated) 100%);
  padding: 48px;
  text-align: center;
  border-bottom: 1px solid var(--line);
  position: relative;
}

.badge-calories {
  position: absolute;
  top: 24px; right: 24px;
  background: #07a374;
  color: white;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 800;
}

.recipe-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-main);
  margin-bottom: 12px;
}

.chef-message {
  font-style: italic;
  color: var(--text-muted);
  font-size: 1.1rem;
  margin-bottom: 24px;
}

.recipe-meta {
  display: flex;
  justify-content: center;
  gap: 24px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.9rem;
}

.recipe-content-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 40px;
  padding: 48px;
}

.ingredients-card h3, .steps-card h3 {
  font-size: 1.4rem;
  margin-bottom: 24px;
  color: var(--text-main);
}

.styled-list {
  list-style: none;
  padding: 0;
}

.styled-list li {
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 10px;
}

.styled-list li::before { content: "•"; color: #07a374; font-weight: bold; }

.btn-shop-link {
  width: 100%;
  margin-top: 24px;
  padding: 16px;
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
  border: 2px dashed var(--menu-active-text);
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.steps-timeline {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.step-item {
  display: flex;
  gap: 20px;
}

.step-number {
  background: var(--text-main);
  color: var(--bg-main);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-weight: 800;
}

.step-text {
  color: var(--text-main);
  line-height: 1.6;
  padding-top: 4px;
}

.recipe-actions {
  padding: 32px 48px;
  background: var(--bg-main);
  display: flex;
  justify-content: space-between;
}

.btn-secondary {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  color: var(--text-main);
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-refresh {
  background: var(--text-main);
  color: var(--bg-main);
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

.error-bubble {
  background: #fff5f5;
  color: #c53030;
  padding: 12px 24px;
  border-radius: 12px;
  display: inline-block;
  margin-bottom: 20px;
  font-weight: 600;
}

.disclaimer {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: -10px;
  margin-bottom: 30px;
}

.rejection-card {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  padding: 60px;
  border-radius: 32px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.05);
  max-width: 500px;
  margin: 0 auto;
}

.rejection-card .icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.rejection-card h2 {
  color: var(--text-main);
  margin-bottom: 16px;
}

.rejection-card p {
  color: var(--text-muted);
  margin-bottom: 32px;
  line-height: 1.6;
}

.btn-primary {
  background: #07a374;
  color: white;
  padding: 12px 32px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 850px) {
  .recipe-content-grid { grid-template-columns: 1fr; }
  .recipe-header { padding: 32px 24px; }
  .recipe-title { font-size: 1.8rem; }
}
</style>
