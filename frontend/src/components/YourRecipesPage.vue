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
  max-width: 1040px;
  margin: 0;
  display: grid;
  gap: 28px;
}

.page-header h1 {
  margin: 0;
}

.page-header p {
  margin-top: 8px;
  color: var(--text-muted);
}

.recipes-block {
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--bg-elevated), transparent 8%);
  border-radius: 18px;
  padding: 18px;
}

.block-head {
  margin-bottom: 14px;
}

.block-head h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-main);
}
</style>
