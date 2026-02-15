<template>
  <div class="history-page" :class="{ embedded }">
    <div v-if="!embedded || history.length" class="header-row" :class="{ embedded }">
      <div v-if="!embedded">
        <h1>Histórico de Receitas</h1>
        <p>Receitas recomendadas automaticamente no "Tenho Fome".</p>
      </div>
      <button v-if="history.length" class="btn-clear" @click="clearAll">Limpar Histórico</button>
    </div>

    <div v-if="!history.length" class="empty-state">
      <p>Ainda não tens recomendações no histórico.</p>
      <button class="action-btn" @click="$emit('navigate', 'tenho-fome')">Ir para Tenho Fome</button>
    </div>

    <div v-else class="history-carousel-wrap">
      <div ref="historyScroller" class="cards-row" @scroll="updateHistoryScrollState">
        <article v-for="item in history" :key="item.id" class="card">
          <div>
            <div class="card-top">
              <span class="source">{{ sourceLabel(item.source) }}</span>
              <span v-if="item.calories" class="kcal">{{ item.calories }} kcal</span>
            </div>
            <h3>{{ item.name }}</h3>
            <p class="meta">{{ formatDate(item.created_at) }}</p>
            <p class="description">{{ truncate(item.instructions.join(' '), 110) }}</p>
          </div>

          <div class="actions">
            <button class="btn-expand" @click="open(item)">Expandir</button>
            <button class="btn-remove" @click="remove(item)">🗑️</button>
          </div>
        </article>
      </div>

      <div v-if="showHistoryScrollLeft" class="carousel-fade carousel-fade-left"></div>
      <div v-if="showHistoryScrollRight" class="carousel-fade carousel-fade-right"></div>

      <button
        v-if="hasHorizontalOverflow"
        class="scroll-arrow scroll-arrow-left"
        @click="scrollHistoryLeft"
        :disabled="!showHistoryScrollLeft"
        aria-label="Ver receitas anteriores"
        title="Ver receitas anteriores"
      >
        ‹
      </button>

      <button
        v-if="hasHorizontalOverflow"
        class="scroll-arrow scroll-arrow-right"
        @click="scrollHistoryRight"
        :disabled="!showHistoryScrollRight"
        aria-label="Ver mais receitas"
        title="Ver mais receitas"
      >
        ›
      </button>
    </div>

    <div v-if="selected" class="modal-overlay" @click.self="close">
      <div class="modal" role="dialog" aria-modal="true" aria-label="Detalhes da receita">
        <div class="modal-header">
          <h3>{{ selected.name }}</h3>
          <button class="btn-close" @click="close">✕</button>
        </div>

        <div class="modal-body">
          <p class="block-title">Ingredientes</p>
          <ul class="ingredients">
            <li v-for="(ingredient, idx) in selected.ingredients" :key="idx">{{ ingredient }}</li>
          </ul>

          <p class="block-title">Preparação</p>
          <ol class="steps">
            <li v-for="(step, idx) in selected.instructions" :key="idx">{{ step }}</li>
          </ol>
        </div>
      </div>
    </div>

    <div v-if="pendingRemoval" class="modal-overlay" @click.self="cancelRemove">
      <div class="confirm-modal" role="dialog" aria-modal="true" aria-label="Confirmar remoção">
        <h3>Remover do histórico?</h3>
        <p><strong>{{ pendingRemoval.name }}</strong> será removida do histórico.</p>
        <div class="confirm-actions">
          <button class="btn-ghost" @click="cancelRemove">Cancelar</button>
          <button class="btn-danger" @click="confirmRemove">Remover</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { clearRecipeHistory, loadRecipeHistory, removeRecipeFromHistory } from '@/utils/recipeHistory';

export default {
  name: 'HistoryPage',
  emits: ['navigate'],
  props: {
    embedded: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      history: [],
      selected: null,
      pendingRemoval: null,
      showHistoryScrollLeft: false,
      showHistoryScrollRight: false,
      hasHorizontalOverflow: false
    };
  },
  mounted() {
    this.reload();
    window.addEventListener('storage', this.reload);
    window.addEventListener('resize', this.updateHistoryScrollState);
    this.$nextTick(() => this.updateHistoryScrollState());
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.reload);
    window.removeEventListener('resize', this.updateHistoryScrollState);
  },
  methods: {
    reload() {
      this.history = loadRecipeHistory();
      this.$nextTick(() => this.updateHistoryScrollState());
    },
    truncate(text, length) {
      if (!text) return '';
      return text.length > length ? text.slice(0, length) + '...' : text;
    },
    formatDate(value) {
      if (!value) return '';
      return new Date(value).toLocaleString('pt-PT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    sourceLabel(source) {
      if (source === 'mood') return 'Estado de Alma';
      if (source === 'vision') return 'Visão do Chef';
      return 'Desejo Específico';
    },
    open(item) {
      this.selected = item;
    },
    close() {
      this.selected = null;
    },
    remove(item) {
      this.pendingRemoval = item;
    },
    confirmRemove() {
      if (!this.pendingRemoval) return;
      const id = this.pendingRemoval.id;
      removeRecipeFromHistory(id);
      this.reload();
      if (this.selected?.id === id) this.close();
      this.pendingRemoval = null;
    },
    cancelRemove() {
      this.pendingRemoval = null;
    },
    clearAll() {
      clearRecipeHistory();
      this.close();
      this.reload();
    },
    updateHistoryScrollState() {
      const scroller = this.$refs.historyScroller;
      if (!scroller) {
        this.showHistoryScrollLeft = false;
        this.showHistoryScrollRight = false;
        this.hasHorizontalOverflow = false;
        return;
      }

      this.hasHorizontalOverflow = scroller.scrollWidth > scroller.clientWidth + 6;
      this.showHistoryScrollLeft = scroller.scrollLeft > 6;
      const remaining = scroller.scrollWidth - (scroller.scrollLeft + scroller.clientWidth);
      this.showHistoryScrollRight = remaining > 6;
    },
    scrollHistoryLeft() {
      const scroller = this.$refs.historyScroller;
      if (!scroller) return;

      scroller.scrollBy({
        left: -Math.max(scroller.clientWidth * 0.85, 260),
        behavior: 'smooth'
      });
    },
    scrollHistoryRight() {
      const scroller = this.$refs.historyScroller;
      if (!scroller) return;

      scroller.scrollBy({
        left: Math.max(scroller.clientWidth * 0.85, 260),
        behavior: 'smooth'
      });
    }
  }
};
</script>

<style scoped>
.history-page {
  max-width: 1040px;
  margin: 0 auto;
}

.history-page.embedded {
  max-width: none;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 26px;
}

.header-row.embedded {
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 12px;
}

.header-row p {
  margin-top: 8px;
  color: var(--text-muted);
}

.history-carousel-wrap {
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

.card {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 0 0 330px;
  scroll-snap-align: start;
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.source {
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
  font-weight: 700;
}

.kcal {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.card h3 {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.35;
}

.meta {
  margin: 8px 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.description {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-expand,
.btn-clear,
.action-btn {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  color: var(--text-main);
  border-radius: 10px;
  padding: 8px 12px;
  font-weight: 700;
  cursor: pointer;
}

.btn-remove {
  border: 1px solid rgba(240, 81, 81, 0.35);
  background: rgba(240, 81, 81, 0.12);
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
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
}

.confirm-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-ghost {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.btn-danger {
  border: 1px solid rgba(240, 81, 81, 0.4);
  background: rgba(240, 81, 81, 0.18);
  color: #ffdede;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.empty-state {
  border: 2px dashed var(--line);
  border-radius: 16px;
  padding: 36px;
  text-align: center;
  color: var(--text-muted);
  background: var(--bg-elevated);
}

.action-btn {
  margin-top: 12px;
  background: var(--menu-active-text);
  color: #fff;
  border-color: transparent;
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

.scroll-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(11, 20, 43, 0.92);
  color: #e4f5ff;
  font-size: 2rem;
  line-height: 1;
  cursor: pointer;
  z-index: 4;
  display: grid;
  place-items: center;
  transition: transform 0.18s ease, background 0.18s ease;
}

.scroll-arrow:hover {
  background: rgba(20, 37, 75, 0.96);
  transform: translateY(-50%) scale(1.04);
}

.scroll-arrow:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  transform: translateY(-50%);
}

.scroll-arrow-left {
  left: 8px;
}

.scroll-arrow-right {
  right: 8px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1200;
}

.modal {
  width: min(700px, 100%);
  max-height: 88vh;
  overflow: hidden;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--line);
}

.modal-header h3 {
  margin: 0;
}

.btn-close {
  border: 0;
  background: transparent;
  color: var(--text-main);
  font-size: 1.2rem;
  cursor: pointer;
}

.modal-body {
  padding: 18px;
  overflow: auto;
}

.block-title {
  margin: 0 0 10px;
  font-weight: 800;
}

.ingredients,
.steps {
  margin: 0 0 18px;
  padding-left: 20px;
  color: var(--text-muted);
}

.steps li,
.ingredients li {
  margin-bottom: 8px;
}

@media (max-width: 760px) {
  .header-row {
    flex-direction: column;
  }

  .card {
    flex-basis: 280px;
  }

  .scroll-arrow {
    width: 38px;
    height: 38px;
    font-size: 1.6rem;
  }
}
</style>
