<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const route = useRoute();
const ingredients = ref('');
const shops = ref([]);
// ... (rest of vars) ...

// ... (functions) ...

onMounted(() => {
  const ingredientsParam = route.query.ingredients;
  const modeParam = route.query.mode;
  const termParam = route.query.term;

  if (modeParam) {
      searchMode.value = modeParam;
  }
  
  if (ingredientsParam) {
    ingredients.value = ingredientsParam;
  } else if (termParam) {
    ingredients.value = termParam;
  }

  if (locationConsent.value === 'granted') {
    askForLocation();
  }
});
</script>

<template>
  <div class="shop-finder">
    <h2>{{ searchMode === 'restaurant' ? 'Encontrar Restaurantes' : 'Encontrar Ingredientes' }}</h2>
    
    <!-- Location Selection (if not set) -->
    <div v-if="!userLocation" class="location-setup">
      <div class="consent-box" v-if="locationConsent === 'ask'">
        <p>Partilha a tua localização para melhores resultados.</p>
        <div class="buttons">
          <button @click="askForLocation" class="btn-primary">📍 Usar GPS Atual</button>
          <span class="or">ou</span>
        </div>
      </div>

      <div class="manual-search">
        <label>Pesquisar zona manualmente:</label>
        <div class="search-wrapper">
          <input 
            v-model="manualQuery" 
            type="text" 
            placeholder="Ex: Braga, Porto, Lisboa..."
            @input="searchLocation"
          />
          <ul v-if="showSuggestions && locationSuggestions.length" class="suggestions">
            <li 
              v-for="loc in locationSuggestions" 
              :key="loc.place_id" 
              @click="selectLocation(loc)"
            >
              {{ loc.display_name }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Interface -->
    <div v-else class="interface-container">
      <div class="top-bar">
        <span class="location-label">
          📍 {{ manualQuery || 'Localização Atual' }}
        </span>
        <button @click="resetLocation" class="btn-text">Alterar</button>
      </div>

      <div class="controls">
        <div class="input-group">
          <input 
            v-model="ingredients" 
            type="text" 
            :placeholder="searchMode === 'restaurant' ? 'Restaurante ou Prato (ex: Pizza)' : 'Ingredientes (ex: leite, pão)'"
            @keyup.enter="findShops"
          />
        </div>
        
        <div class="radius-control">
          <span>Raio: {{ searchRadius }}m</span>
          <input type="range" v-model="searchRadius" min="500" max="10000" step="500">
        </div>

        <button @click="findShops" :disabled="loading" class="search-btn">
          {{ loading ? 'A procurar...' : (searchMode === 'restaurant' ? '🔍 Encontrar Restaurantes' : '🔍 Encontrar Lojas') }}
        </button>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div id="map"></div>

      <div v-if="shops.length > 0" class="shop-list">
        <h3>{{ shops.length }} Resultados:</h3>
        <ul class="shop-items">
          <li v-for="shop in shops" :key="shop.id || shop.lat" class="shop-item">
            <div class="info">
              <strong>{{ shop.name }}</strong>
              <small>{{ shop.distance }}m</small>
            </div>
            <span class="tag">Aberto</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shop-finder {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  font-family: 'Sora', sans-serif;
}

.location-setup {
  background: white;
  padding: 24px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.consent-box {
  margin-bottom: 24px;
}

.buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
}

.or {
  color: #999;
  font-size: 0.9rem;
}

.manual-search {
  text-align: left;
}

.manual-search label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #666;
}

.search-wrapper {
  position: relative;
}

.search-wrapper input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin: 4px 0 0;
  padding: 0;
  list-style: none;
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.suggestions li {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.9rem;
}

.suggestions li:hover {
  background: #f9f9f9;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.location-label {
  font-weight: 600;
  color: #333;
}

.btn-primary {
  background: #07a374;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.btn-text {
  background: none;
  border: none;
  color: #07a374;
  text-decoration: underline;
  cursor: pointer;
}

.controls {
  background: white;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 12px;
}

.radius-control {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  color: #666;
}

.radius-control input {
  flex: 1;
}

.search-btn {
  width: 100%;
  padding: 12px;
  background: #07a374;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.search-btn:disabled {
  background: #ccc;
}

#map {
  height: 350px;
  width: 100%;
  border-radius: 12px;
  margin-bottom: 24px;
}

.shop-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #eee;
  margin-bottom: 8px;
}

.tag {
  background: #e6fcf5;
  color: #0ca678;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}
</style>
