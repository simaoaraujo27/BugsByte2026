<script setup>
import { ref, computed } from 'vue'

const items = [
  { name: 'Arroz Cozido', gPerSpoon: 25, calPer100g: 130 },
  { name: 'Azeite', gPerSpoon: 12, calPer100g: 884 },
  { name: 'Aveia', gPerSpoon: 10, calPer100g: 389 },
  { name: 'Manteiga de Amendoim', gPerSpoon: 15, calPer100g: 588 },
  { name: 'Mel', gPerSpoon: 20, calPer100g: 304 }
]

const selectedItem = ref(items[0])
const quantity = ref(1)

const totalGrams = computed(() => quantity.value * selectedItem.value.gPerSpoon)
const totalCalories = computed(() => Math.round((totalGrams.value * selectedItem.value.calPer100g) / 100))
</script>

<template>
  <div class="converter-container">
    <h4>Conversor de Medidas 🥄</h4>
    
    <div class="input-group">
      <label>Alimento</label>
      <select v-model="selectedItem">
        <option v-for="item in items" :key="item.name" :value="item">
          {{ item.name }}
        </option>
      </select>
    </div>

    <div class="input-group">
      <label>Quantidade (Colheres de Sopa)</label>
      <input type="number" v-model="quantity" min="1" max="20" />
    </div>

    <div class="result-card">
      <div class="res-item">
        <span class="label">Peso Estimado</span>
        <span class="value">{{ totalGrams }}g</span>
      </div>
      <div class="res-item">
        <span class="label">Calorias</span>
        <span class="value">{{ totalCalories }} kcal</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.converter-container {
  margin-top: 15px;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

h4 { margin: 0 0 15px; font-size: 1rem; color: var(--text-main); }

.input-group {
  margin-bottom: 12px;
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.input-group select, .input-group input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--bg-main);
  color: var(--text-main);
  outline: none;
}

.result-card {
  margin-top: 15px;
  background: var(--menu-active-bg);
  padding: 12px;
  border-radius: 12px;
  display: flex;
  justify-content: space-around;
}

.res-item { display: flex; flex-direction: column; }
.res-item .label { font-size: 0.7rem; color: var(--menu-active-text); font-weight: 600; }
.res-item .value { font-size: 1.1rem; font-weight: 800; color: var(--menu-active-text); }
</style>
