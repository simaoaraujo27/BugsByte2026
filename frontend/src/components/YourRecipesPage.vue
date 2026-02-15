<template>
  <div class="your-recipes-page">
    <header class="page-header">
      <h1>Tuas Receitas</h1>
      <p>As tuas receitas favoritas e o teu histórico num só lugar.</p>
    </header>

    <section class="recipes-block">
      <div class="block-head">
        <h2>❤️ Favoritos</h2>
      </div>
      <FavoritesPage embedded @navigate="$emit('navigate', $event)" />
    </section>

    <section class="recipes-block">
      <div class="block-head">
        <h2>🕘 Histórico</h2>
      </div>
      <HistoryPage embedded @navigate="$emit('navigate', $event)" />
    </section>
  </div>
</template>

<script setup>
import FavoritesPage from './FavoritesPage.vue'
import HistoryPage from './HistoryPage.vue'

defineEmits(['navigate'])
</script>

<style scoped>
.your-recipes-page {
  width: min(1240px, 100%);
  margin: 0;
  display: grid;
  gap: 22px;
}

.page-header {
  border: 1px solid color-mix(in srgb, var(--line), transparent 18%);
  background:
    radial-gradient(120% 160% at 0% 0%, color-mix(in srgb, var(--menu-active-text), transparent 88%) 0%, transparent 60%),
    color-mix(in srgb, var(--bg-elevated), transparent 6%);
  border-radius: 18px;
  padding: 18px 20px;
}

.page-header h1 {
  margin: 0;
  font-size: clamp(1.5rem, 2vw, 2rem);
  letter-spacing: -0.02em;
}

.page-header p {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 1rem;
  max-width: 70ch;
}

.recipes-block {
  border: 1px solid color-mix(in srgb, var(--line), transparent 12%);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-elevated), transparent 3%) 0%, color-mix(in srgb, var(--bg-elevated), transparent 10%) 100%);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 12px 30px rgba(4, 10, 24, 0.22);
  overflow: hidden;
}

.block-head {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.block-head h2 {
  margin: 0;
  font-size: 1.35rem;
  letter-spacing: -0.01em;
  color: var(--text-main);
}

/* Harmonize embedded pages and reduce visual noise */
:deep(.favorites-page.embedded),
:deep(.history-page.embedded) {
  margin: 0;
}

:deep(.favorites-page .section-header),
:deep(.history-page .header-row.embedded) {
  margin-bottom: 14px;
}

:deep(.favorites-page .empty-state),
:deep(.history-page .empty-state) {
  min-height: 150px;
  display: grid;
  place-items: center;
  text-align: center;
}

:deep(.favorites-page .cards-row),
:deep(.history-page .cards-row) {
  padding-bottom: 10px;
}

@media (max-width: 900px) {
  .recipes-block {
    padding: 16px;
  }
}
</style>
