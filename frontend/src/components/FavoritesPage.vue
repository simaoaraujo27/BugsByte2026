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

        <div v-else class="recipe-carousel-wrap">
          <div ref="recipeScroller" class="cards-row" @scroll="updateRecipeScrollState">
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
                <button
                  class="btn-expand"
                  @click="openRecipeModal(recipe)"
                  title="Ver receita completa"
                >
                  Expandir
                </button>
                <button class="btn-remove" @click="requestRemoveRecipe(recipe)" title="Remover dos favoritos">
                  🗑️
                </button>
              </div>
            </div>
          </div>

          <div v-if="showRecipeScrollLeft" class="carousel-fade carousel-fade-left"></div>
          <div v-if="showRecipeScrollRight" class="carousel-fade carousel-fade-right"></div>

          <button
            v-if="showRecipeScrollLeft"
            class="scroll-arrow scroll-arrow-left"
            @click="scrollRecipesLeft"
            aria-label="Ver receitas anteriores"
            title="Ver receitas anteriores"
          >
            ‹
          </button>

          <button
            v-if="showRecipeScrollRight"
            class="scroll-arrow scroll-arrow-right"
            @click="scrollRecipesRight"
            aria-label="Ver mais receitas"
            title="Ver mais receitas"
          >
            ›
          </button>
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
              <button class="btn-remove" @click="requestRemoveRestaurant(restaurant)" title="Remover dos favoritos">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div v-if="selectedRecipe" class="modal-overlay" @click.self="closeRecipeModal">
      <div class="recipe-modal" role="dialog" aria-modal="true" aria-label="Detalhes da receita">
        <div class="modal-header">
          <h3>{{ selectedRecipe.name }}</h3>
          <button class="btn-close" @click="closeRecipeModal" aria-label="Fechar">
            ✕
          </button>
        </div>

        <div class="modal-body">
          <p v-if="selectedRecipe.ingredients" class="modal-section-title">Ingredientes</p>
          <ul v-if="selectedRecipe.ingredients" class="ingredients-list">
            <li v-for="(ingredient, idx) in ingredientsList" :key="`${selectedRecipe.id}-${idx}`">
              {{ ingredient }}
            </li>
          </ul>

          <p v-if="selectedRecipe.instructions" class="modal-section-title">Preparação</p>
          <p v-if="selectedRecipe.instructions" class="instructions-full">
            {{ selectedRecipe.instructions }}
          </p>
        </div>
      </div>
    </div>

    <div v-if="confirmDialog" class="modal-overlay" @click.self="closeConfirmDialog">
      <div class="confirm-modal" role="dialog" aria-modal="true" aria-label="Confirmar remoção">
        <h3>Remover dos favoritos?</h3>
        <p>
          <strong>{{ confirmDialog.name }}</strong> vai ser removido(a) da tua lista.
        </p>
        <div class="confirm-actions">
          <button class="btn-secondary" @click="closeConfirmDialog">Cancelar</button>
          <button class="btn-danger" @click="confirmRemoval">Remover</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { auth, API_URL } from '@/auth.js';

export default {
  name: 'FavoritesPage',
  data() {
    return {
      favoriteRecipes: [],
      favoriteRestaurants: [],
      loading: true,
      error: null,
      selectedRecipe: null,
      confirmDialog: null,
      showRecipeScrollLeft: false,
      showRecipeScrollRight: false
    };
  },
  computed: {
    ingredientsList() {
      if (!this.selectedRecipe?.ingredients) return [];
      return this.selectedRecipe.ingredients
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);
    }
  },
  async mounted() {
    await this.fetchFavorites();
    window.addEventListener('resize', this.updateRecipeScrollState);
    this.$nextTick(() => this.updateRecipeScrollState());
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateRecipeScrollState);
  },
  methods: {
    truncate(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    },

    openRecipeModal(recipe) {
      this.selectedRecipe = recipe;
    },

    closeRecipeModal() {
      this.selectedRecipe = null;
    },

    requestRemoveRecipe(recipe) {
      this.confirmDialog = {
        type: 'recipe',
        id: recipe.id,
        name: recipe.name
      };
    },

    requestRemoveRestaurant(restaurant) {
      this.confirmDialog = {
        type: 'restaurant',
        id: restaurant.id,
        name: restaurant.name
      };
    },

    closeConfirmDialog() {
      this.confirmDialog = null;
    },

    async confirmRemoval() {
      if (!this.confirmDialog) return;

      const { type, id } = this.confirmDialog;
      this.closeConfirmDialog();

      if (type === 'recipe') {
        await this.deleteRecipe(id);
      } else {
        await this.deleteRestaurant(id);
      }
    },

    updateRecipeScrollState() {
      const scroller = this.$refs.recipeScroller;
      if (!scroller) {
        this.showRecipeScrollLeft = false;
        this.showRecipeScrollRight = false;
        return;
      }

      this.showRecipeScrollLeft = scroller.scrollLeft > 6;
      const remaining = scroller.scrollWidth - (scroller.scrollLeft + scroller.clientWidth);
      this.showRecipeScrollRight = remaining > 6;
    },

    scrollRecipesLeft() {
      const scroller = this.$refs.recipeScroller;
      if (!scroller) return;

      scroller.scrollBy({
        left: -Math.max(scroller.clientWidth * 0.85, 260),
        behavior: 'smooth'
      });
    },

    scrollRecipesRight() {
      const scroller = this.$refs.recipeScroller;
      if (!scroller) return;

      scroller.scrollBy({
        left: Math.max(scroller.clientWidth * 0.85, 260),
        behavior: 'smooth'
      });
    },

    async fetchFavorites() {
      this.loading = true;
      try {
        const response = await fetch(`${API_URL}/users/me/favorites`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) throw new Error('Failed to fetch favorites');

        const data = await response.json();
        this.favoriteRecipes = data.favorite_recipes || [];
        this.favoriteRestaurants = data.favorite_restaurants || [];
        this.$nextTick(() => this.updateRecipeScrollState());
      } catch (err) {
        console.error('Error fetching favorites:', err);
        this.error = 'Não foi possível carregar os favoritos.';
      } finally {
        this.loading = false;
      }
    },

    async deleteRecipe(id) {
      try {
        const response = await fetch(`${API_URL}/users/me/favorites/recipes/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.ok) {
          this.favoriteRecipes = this.favoriteRecipes.filter(r => r.id !== id);
          if (this.selectedRecipe?.id === id) {
            this.closeRecipeModal();
          }
          this.$nextTick(() => this.updateRecipeScrollState());
        }
      } catch (err) {
        console.error('Error removing recipe:', err);
      }
    },

    async deleteRestaurant(id) {
      try {
        const response = await fetch(`${API_URL}/users/me/favorites/restaurants/${id}`, {
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

.recipe-carousel-wrap {
  position: relative;
}

.cards-row {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  padding-bottom: 6px;
  padding-right: 54px;
  scroll-snap-type: x proximity;
}

.cards-row::-webkit-scrollbar {
  height: 8px;
}

.cards-row::-webkit-scrollbar-thumb {
  background: var(--line);
  border-radius: 99px;
}

.cards-row .card {
  flex: 0 0 280px;
  scroll-snap-align: start;
}

.carousel-fade {
  position: absolute;
  top: 0;
  bottom: 14px;
  width: 88px;
  pointer-events: none;
  z-index: 3;
}

.carousel-fade-left {
  left: 0;
  background: linear-gradient(to right, rgba(6, 13, 33, 0.92), rgba(6, 13, 33, 0));
}

.carousel-fade-right {
  right: 0;
  background: linear-gradient(to left, rgba(6, 13, 33, 0.92), rgba(6, 13, 33, 0));
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
  gap: 8px;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}

.btn-expand {
  background: transparent;
  border: 1px solid var(--line);
  color: var(--text-main);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s, border-color 0.2s;
}

.btn-expand:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--menu-active-text);
}

.btn-remove {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--line);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 10px;
  transition: background 0.2s, border-color 0.2s, transform 0.2s;
  opacity: 0.9;
}

.btn-remove:hover {
  background: rgba(240, 81, 81, 0.15);
  border-color: rgba(240, 81, 81, 0.42);
  opacity: 1;
  transform: translateY(-1px);
}

.scroll-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  background: rgba(8, 22, 52, 0.7);
  backdrop-filter: blur(8px);
  color: #f4fbff;
  font-size: 1.9rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.26);
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.scroll-arrow-left {
  left: 8px;
}

.scroll-arrow-right {
  right: 8px;
}

.scroll-arrow:hover {
  border-color: var(--menu-active-text);
  background: rgba(11, 29, 67, 0.85);
  transform: translateY(-50%) scale(1.06);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 1200;
}

.recipe-modal {
  width: min(720px, 100%);
  max-height: 85vh;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.confirm-modal {
  width: min(420px, 100%);
  background: linear-gradient(165deg, rgba(18, 31, 62, 0.97), rgba(10, 19, 40, 0.97));
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.35);
}

.confirm-modal h3 {
  margin: 0 0 8px 0;
  color: var(--text-main);
}

.confirm-modal p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.confirm-actions {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-secondary {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
}

.btn-danger {
  border: 1px solid rgba(240, 81, 81, 0.5);
  background: rgba(240, 81, 81, 0.18);
  color: #ffdede;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
}

.modal-header {
  padding: 18px 20px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-main);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-main);
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  padding: 4px 8px;
  border-radius: 8px;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.08);
}

.modal-body {
  padding: 20px;
  overflow: auto;
}

.modal-section-title {
  margin: 0 0 10px 0;
  font-weight: 700;
  color: var(--text-main);
}

.ingredients-list {
  margin: 0 0 18px 0;
  padding-left: 20px;
  color: var(--text-muted);
}

.ingredients-list li {
  margin-bottom: 6px;
}

.instructions-full {
  margin: 0;
  white-space: pre-line;
  color: var(--text-muted);
  line-height: 1.6;
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

  .cards-row {
    padding-right: 44px;
  }

  .cards-row .card {
    flex-basis: min(78vw, 280px);
  }

  .modal-overlay {
    padding: 12px;
  }

  .recipe-modal {
    max-height: 90vh;
  }
}
</style>
