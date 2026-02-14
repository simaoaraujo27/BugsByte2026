<template>
  <div class="favorites-page">
    <div class="header">
      <h1>Os Meus Favoritos</h1>
      <p class="subtitle">Aqui encontras as receitas e restaurantes que guardaste.</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>A carregar os teus favoritos...</p>
    </div>

    <div v-else class="favorites-content">
      <section class="favorites-section">
        <div class="section-header">
          <h2>🍽️ Receitas Guardadas</h2>
          <span class="count-badge">{{ favoriteRecipes.length }}</span>
        </div>
        
        <div v-if="favoriteRecipes.length === 0" class="empty-state">
          <p>Ainda não guardaste nenhuma receita.</p>
          <button @click="$emit('navigate', 'gerar-receita')" class="action-btn">
            Explorar Receitas
          </button>
        </div>

        <div v-else class="cards-grid">
          <div v-for="recipe in favoriteRecipes" :key="recipe.id" class="card recipe-card">
            <div class="card-content">
              <h3>{{ recipe.name }}</h3>
              <div class="card-meta">
                <span v-if="recipe.ingredients">{{ recipe.ingredients.split(',').length }} ingredientes</span>
              </div>
              <p class="description" v-if="recipe.instructions">
                {{ truncate(recipe.instructions, 100) }}
              </p>
            </div>
            <div class="card-actions">
              <button class="btn-remove" @click="removeRecipe(recipe.id)" title="Remover dos favoritos">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="favorites-section">
        <div class="section-header">
          <h2>🏪 Restaurantes Guardados</h2>
          <span class="count-badge">{{ favoriteRestaurants.length }}</span>
        </div>

        <div v-if="favoriteRestaurants.length === 0" class="empty-state">
          <p>Ainda não guardaste nenhum restaurante.</p>
          <button @click="$emit('navigate', 'tenho-fome')" class="action-btn">
            Procurar Restaurantes
          </button>
        </div>

        <div v-else class="cards-grid">
          <div v-for="restaurant in favoriteRestaurants" :key="restaurant.id" class="card restaurant-card">
            <div class="card-content">
              <h3>{{ restaurant.name }}</h3>
              <p class="address" v-if="restaurant.address">📍 {{ restaurant.address }}</p>
              <p class="phone" v-if="restaurant.phone">📞 {{ restaurant.phone }}</p>
            </div>
            <div class="card-actions">
              <button class="btn-remove" @click="removeRestaurant(restaurant.id)" title="Remover dos favoritos">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { auth } from '@/auth.js';

export default {
  name: 'FavoritesPage',
  data() {
    return {
      favoriteRecipes: [],
      favoriteRestaurants: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.fetchFavorites();
  },
  methods: {
    truncate(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    },
    
    async fetchFavorites() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:8000/users/me/favorites', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) throw new Error('Failed to fetch favorites');
        
        const data = await response.json();
        this.favoriteRecipes = data.favorite_recipes || [];
        this.favoriteRestaurants = data.favorite_restaurants || [];
      } catch (err) {
        console.error('Error fetching favorites:', err);
        this.error = 'Não foi possível carregar os favoritos.';
      } finally {
        this.loading = false;
      }
    },

    async removeRecipe(id) {
      if (!confirm('Tens a certeza que queres remover esta receita dos favoritos?')) return;
      
      try {
        const response = await fetch(`http://localhost:8000/users/me/favorites/recipes/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          this.favoriteRecipes = this.favoriteRecipes.filter(r => r.id !== id);
        }
      } catch (err) {
        console.error('Error removing recipe:', err);
      }
    },

    async removeRestaurant(id) {
      if (!confirm('Tens a certeza que queres remover este restaurante dos favoritos?')) return;

      try {
        const response = await fetch(`http://localhost:8000/users/me/favorites/restaurants/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          this.favoriteRestaurants = this.favoriteRestaurants.filter(r => r.id !== id);
        }
      } catch (err) {
        console.error('Error removing restaurant:', err);
      }
    }
  }
};
</script>

<style scoped>
.favorites-page {
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  margin-bottom: 32px;
}

.subtitle {
  color: var(--text-muted);
  margin-top: 8px;
}

.favorites-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 1.5rem;
  margin: 0;
  color: var(--text-main);
}

.count-badge {
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 0.9rem;
  font-weight: 600;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.card {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.06);
}

.card-content h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  line-height: 1.4;
}

.card-meta {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.description {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.address, .phone {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 4px 0;
}

.card-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}

.btn-remove {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
  opacity: 0.7;
}

.btn-remove:hover {
  background: #ffe5e5;
  opacity: 1;
}

.empty-state {
  background: var(--bg-elevated);
  border: 2px dashed var(--line);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.action-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: var(--menu-active-text);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 0.9;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--line);
  border-top-color: var(--menu-active-text);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
