<script setup>
import { ref } from 'vue';

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

    if (!response.ok) throw new Error("Erro na negociação");
    result.value = await response.json();
  } catch (e) {
    error.value = "Ocorreu um erro ao negociar. Tenta novamente.";
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const goToIngredients = () => {
  const ingredients = result.value.recipe.ingredients.join(',');
  window.location.href = `/shops?ingredients=${encodeURIComponent(ingredients)}`;
};

const goToRestaurants = () => {
  // For now, we reuse the shop finder but maybe searching for 'restaurant' tag if we update backend,
  // or just search for the term as a generic search if we had a generic map.
  // Since the current ShopFinder searches for *shops* that sell *ingredients*, 
  // we might want to adapt it or just say "Here are supermarkets, buy stuff!"
  // But the prompt says "sugestões perto" (lazy option). 
  // For the hackathon, reusing ShopFinder to find supermarkets is "DIY",
  // Finding restaurants needs the Overpass API to query `amenity=restaurant`.
  // Our backend `find_nearby_shops` uses `shop=[tag]`.
  // We might need to update backend to support restaurants too.
  // For now, let's just search for the dish name as an ingredient? No that's wrong.
  // Let's assume Option B sends them to a map of restaurants.
  // We can pass a special flag to ShopFinder?
  window.location.href = `/shops?mode=restaurant&term=${encodeURIComponent(result.value.restaurant_search_term)}`;
};
</script>

<template>
  <div class="negotiator-container">
    <div v-if="!result" class="start-screen">
      <h1 class="title">TENHO FOME E QUERO ASNEIRA</h1>
      <div class="input-wrapper">
        <input 
          v-model="craving" 
          type="text" 
          placeholder="O que te apetece? (ex: Francesinha)" 
          @keyup.enter="negotiate"
        />
        <button @click="negotiate" :disabled="loading" class="btn-action">
          {{ loading ? 'A Negociar...' : 'Resolver Problema' }}
        </button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div v-else class="results-screen">
      <h2>{{ result.message }}</h2>
      
      <div class="options-grid">
        <!-- Option A: DIY -->
        <div class="option-card diy">
          <div class="card-header">
            <h3>Opção A: Faz tu mesmo (Saudável)</h3>
            <span class="calories">{{ result.recipe.calories }} kcal</span>
          </div>
          <div class="recipe-content">
            <h4>{{ result.recipe.title }}</h4>
            <p><strong>Tempo:</strong> {{ result.recipe.time_minutes }} min</p>
            <ul>
              <li v-for="step in result.recipe.steps" :key="step">{{ step }}</li>
            </ul>
          </div>
          <button @click="goToIngredients" class="btn-primary">
            🛒 Comprar Ingredientes
          </button>
        </div>

        <!-- Option B: Lazy -->
        <div class="option-card lazy">
          <div class="card-header">
            <h3>Opção B: Preguiça (Restaurantes)</h3>
          </div>
          <p>Não queres cozinhar? Encontra onde comer perto de ti.</p>
          <button @click="goToRestaurants" class="btn-secondary">
            🍔 Ver Restaurantes
          </button>
        </div>
      </div>
      
      <button @click="result = null" class="btn-back">Voltar</button>
    </div>
  </div>
</template>

<style scoped>
.negotiator-container {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
  font-family: 'Sora', sans-serif;
  padding: 40px 20px;
}

.title {
  font-size: 3rem;
  font-weight: 800;
  color: #e74c3c;
  margin-bottom: 40px;
  text-transform: uppercase;
  line-height: 1.2;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 500px;
  margin: 0 auto;
}

input {
  padding: 20px;
  font-size: 1.2rem;
  border: 2px solid #ddd;
  border-radius: 12px;
  text-align: center;
}

.btn-action {
  padding: 16px;
  font-size: 1.2rem;
  font-weight: bold;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.1s;
}

.btn-action:hover {
  transform: scale(1.02);
  background: #c0392b;
}

.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 32px;
  text-align: left;
}

.option-card {
  border: 1px solid #ddd;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.diy {
  background: #f4fbf8;
  border-color: #07a374;
}

.lazy {
  background: #fdf2f2;
  border-color: #e74c3c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 1.1rem;
  margin: 0;
}

.calories {
  background: #07a374;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: bold;
}

.recipe-content ul {
  padding-left: 20px;
  font-size: 0.9rem;
  color: #555;
}

.btn-primary, .btn-secondary {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 16px;
}

.btn-primary {
  background: #07a374;
  color: white;
}

.btn-secondary {
  background: #e74c3c;
  color: white;
}

.btn-back {
  margin-top: 32px;
  background: none;
  border: none;
  text-decoration: underline;
  cursor: pointer;
  color: #666;
}

@media (max-width: 768px) {
  .options-grid {
    grid-template-columns: 1fr;
  }
}
</style>
