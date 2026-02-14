<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const props = defineProps({
  initialIngredients: {
    type: String,
    default: ''
  },
  mode: {
    type: String,
    default: 'shop' // 'shop' or 'restaurant'
  }
});

const ingredients = ref(props.initialIngredients);
const searchMode = ref(props.mode);
const shops = ref([]);
const loading = ref(false);
const error = ref(null);
const userLocation = ref(null);
const searchRadius = ref(1000); // Updated to 1km default
const locationConsent = ref(localStorage.getItem('locationConsent') || 'ask'); 
const manualQuery = ref('');
const locationSuggestions = ref([]);
const showSuggestions = ref(false);

watch(() => props.initialIngredients, (newVal) => {
  ingredients.value = newVal;
  if (userLocation.value && newVal) {
    findShops();
  }
});

watch(() => props.mode, (newVal) => {
  searchMode.value = newVal;
});

let map = null;
let markers = [];
let userMarker = null;

const initMap = (lat, lon) => {
  if (map) {
    map.setView([lat, lon], 15);
    updateUserMarker(lat, lon);
    return;
  }
  
  map = L.map('map').setView([lat, lon], 15);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  updateUserMarker(lat, lon);
};

const updateUserMarker = (lat, lon) => {
  if (userMarker) {
    userMarker.setLatLng([lat, lon]);
  } else {
    userMarker = L.marker([lat, lon])
      .addTo(map)
      .bindPopup('A tua localização')
      .openPopup();
  }
};

const askForLocation = () => {
  if (!navigator.geolocation) {
    error.value = "Geolocalização não suportada. Introduz manualmente.";
    locationConsent.value = 'denied';
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      userLocation.value = {
        lat: position.coords.latitude,
        lon: position.coords.longitude
      };
      localStorage.setItem('locationConsent', 'granted');
      locationConsent.value = 'granted';
      
      await nextTick();
      initMap(userLocation.value.lat, userLocation.value.lon);
      error.value = null;
      
      if (ingredients.value) findShops();
    },
    (err) => {
      console.warn("Location error:", err);
      locationConsent.value = 'denied'; 
      localStorage.setItem('locationConsent', 'denied');
    }
  );
};

// Nominatim Search
let debounceTimer = null;
const searchLocation = () => {
  if (manualQuery.value.length < 3) return;
  
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(manualQuery.value)}&limit=5`);
      locationSuggestions.value = await res.json();
      showSuggestions.value = true;
    } catch (e) {
      console.error(e);
    }
  }, 500);
};

const selectLocation = async (loc) => {
  userLocation.value = { lat: parseFloat(loc.lat), lon: parseFloat(loc.lon) };
  manualQuery.value = loc.display_name;
  showSuggestions.value = false;
  locationSuggestions.value = [];
  locationConsent.value = 'denied'; 
  localStorage.setItem('locationConsent', 'denied');
  
  await nextTick();
  initMap(userLocation.value.lat, userLocation.value.lon);
  
  if (ingredients.value) findShops();
};

const resetLocation = () => {
  localStorage.removeItem('locationConsent');
  locationConsent.value = 'ask';
  userLocation.value = null;
  shops.value = [];
  manualQuery.value = '';
};

const findShops = async () => {
  if (!ingredients.value.trim()) {
    error.value = "Por favor introduz ingredientes ou termo de pesquisa.";
    return;
  }
  
  if (!userLocation.value) {
    error.value = "Define a tua localização primeiro.";
    return;
  }

  loading.value = true;
  error.value = null;
  shops.value = [];

  markers.forEach(marker => map.removeLayer(marker));
  markers = [];

  try {
    const ingredientList = ingredients.value.split(',').map(i => i.trim());
    const payload = {
      ingredients: ingredientList,
      lat: userLocation.value.lat,
      lon: userLocation.value.lon,
      radius: searchRadius.value,
      mode: searchMode.value
    };

    const response = await fetch('http://localhost:8000/shops/find', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Falha ao obter resultados');
    }
    
    shops.value = await response.json();

    if (shops.value.length === 0) {
      error.value = "Não foram encontrados resultados nas proximidades com este critério.";
    }

    shops.value.forEach(shop => {
      const marker = L.marker([shop.lat, shop.lon], {
        icon: L.icon({
          iconUrl: searchMode.value === 'restaurant' 
            ? 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
            : 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        })
      })
      .addTo(map)
      .bindPopup(`<b>${shop.name}</b><br>${shop.distance}m`);
      
      markers.push(marker);
    });

    if (markers.length > 0) {
      const group = new L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }

  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const openInMaps = (shop) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${shop.lat},${shop.lon}`;
    window.open(url, '_blank');
};

onMounted(() => {
  if (locationConsent.value === 'granted') {
    askForLocation();
  }
});
</script>

<template>
  <div class="shop-finder-container">
    <header class="section-header">
      <div class="header-info">
        <h2>{{ searchMode === 'restaurant' ? '🍴 Restaurantes Saudáveis' : '🛒 Supermercados & Compras' }}</h2>
        <p v-if="userLocation" class="location-badge">
          📍 {{ manualQuery || 'Localização Atual' }} 
          <button @click="resetLocation" class="btn-link">Alterar</button>
        </p>
      </div>
    </header>
    
    <!-- Location Selection -->
    <div v-if="!userLocation" class="location-card">
      <div class="card-icon">📍</div>
      <h3>Onde estás?</h3>
      <p>Precisamos da tua localização para encontrar as melhores opções perto de ti.</p>
      
      <div class="location-actions">
        <button @click="askForLocation" class="btn-gps">Usar GPS Atual</button>
        <div class="divider">ou pesquisa manual</div>
        <div class="search-box">
          <input 
            v-model="manualQuery" 
            type="text" 
            placeholder="Ex: Braga, Porto, Lisboa..."
            @input="searchLocation"
          />
          <ul v-if="showSuggestions && locationSuggestions.length" class="suggestions-list">
            <li v-for="loc in locationSuggestions" :key="loc.place_id" @click="selectLocation(loc)">
              {{ loc.display_name }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Interface -->
    <div v-else class="main-interface">
      <div class="control-panel">
        <div class="search-input-group">
          <input 
            v-model="ingredients" 
            type="text" 
            :placeholder="searchMode === 'restaurant' ? 'Prato ou tipo de comida...' : 'O que precisas comprar?'"
            @keyup.enter="findShops"
          />
          <button @click="findShops" :disabled="loading" class="btn-search">
            {{ loading ? '...' : '🔍' }}
          </button>
        </div>
        
        <div class="radius-slider">
          <label>Raio de Pesquisa: <strong>{{ searchRadius }}m</strong></label>
          <input type="range" v-model="searchRadius" min="500" max="5000" step="100">
        </div>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="content-grid">
        <div id="map"></div>
        
        <div class="results-panel">
          <div v-if="shops.length > 0" class="results-list">
            <div v-for="shop in shops" :key="shop.id || shop.lat" class="shop-card">
              <div class="shop-info">
                <span class="shop-icon">{{ searchMode === 'restaurant' ? '🍴' : '🏪' }}</span>
                <div class="text">
                  <h4 class="shop-name">{{ shop.name }}</h4>
                  <p class="shop-dist">{{ shop.distance }} metros de distância</p>
                </div>
              </div>
              <button @click="openInMaps(shop)" class="btn-maps">Ver no Mapa</button>
            </div>
          </div>
          <div v-else-if="!loading" class="empty-state">
            <img src="https://cdn-icons-png.flaticon.com/512/6108/6108830.png" width="60" />
            <p>Faz uma pesquisa para ver resultados</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shop-finder-container {
  --primary: #07a374;
  --secondary: #e74c3c;
  --bg-card: #ffffff;
  --text-dark: #11263f;
  --text-light: #54667e;
  
  max-width: 1100px;
  margin: 0 auto;
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-dark);
  margin: 0;
}

.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e3f7f2;
  color: var(--primary);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 8px;
}

.btn-link {
  background: none;
  border: none;
  text-decoration: underline;
  color: inherit;
  font-weight: 800;
  cursor: pointer;
  padding: 0;
}

/* Location Card */
.location-card {
  background: white;
  padding: 48px;
  border-radius: 24px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  max-width: 500px;
  margin: 40px auto;
}

.card-icon { font-size: 3rem; margin-bottom: 16px; }
.location-card h3 { font-size: 1.5rem; margin-bottom: 12px; }
.location-card p { color: var(--text-light); margin-bottom: 32px; }

.btn-gps {
  background: var(--primary);
  color: white;
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  font-size: 1.1rem;
}

.divider {
  margin: 20px 0;
  color: #ccc;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.search-box { position: relative; }
.search-box input {
  width: 100%;
  padding: 14px;
  border: 2px solid #edf2f7;
  border-radius: 12px;
  font-size: 1rem;
}

.suggestions-list {
  position: absolute;
  top: 100%; left: 0; right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  z-index: 1000;
  list-style: none;
  padding: 8px;
  text-align: left;
}

.suggestions-list li {
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.suggestions-list li:hover { background: #f7fafc; }

/* Main Interface */
.control-panel {
  display: flex;
  gap: 24px;
  background: white;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  align-items: center;
}

.search-input-group {
  flex: 1;
  display: flex;
  background: #f7fafc;
  border-radius: 12px;
  padding: 4px;
}

.search-input-group input {
  flex: 1;
  background: none;
  border: none;
  padding: 12px 16px;
  font-size: 1rem;
}

.btn-search {
  background: var(--primary);
  color: white;
  border: none;
  width: 48px;
  height: 48px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1.2rem;
}

.radius-slider {
  min-width: 200px;
}

.radius-slider label {
  display: block;
  font-size: 0.8rem;
  margin-bottom: 8px;
}

.radius-slider input {
  width: 100%;
  accent-color: var(--primary);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 24px;
  height: 500px;
}

#map {
  border-radius: 20px;
  border: 1px solid #edf2f7;
  z-index: 1;
}

.results-panel {
  background: white;
  border-radius: 20px;
  overflow-y: auto;
  padding: 16px;
  border: 1px solid #edf2f7;
}

.shop-card {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.2s;
}

.shop-card:hover { background: #fafcfe; }

.shop-info { display: flex; gap: 12px; }
.shop-icon { font-size: 1.5rem; }
.shop-name { margin: 0; font-size: 1rem; color: var(--text-dark); }
.shop-dist { margin: 2px 0 0; font-size: 0.8rem; color: var(--text-light); }

.btn-maps {
  background: #edf2f7;
  border: none;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--primary);
  cursor: pointer;
}

.btn-maps:hover { background: #e2e8f0; }

.error-msg {
  background: #fff5f5;
  color: #c53030;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  font-weight: 600;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #a0aec0;
  text-align: center;
  padding: 20px;
}

@media (max-width: 900px) {
  .content-grid { grid-template-columns: 1fr; height: auto; }
  #map { height: 300px; }
  .control-panel { flex-direction: column; align-items: stretch; }
}
</style>