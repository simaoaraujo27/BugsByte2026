<script setup>
import { ref, onMounted, watch } from 'vue';
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
const searchRadius = ref(3000); 
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
    map.setView([lat, lon], 14);
    updateUserMarker(lat, lon);
    return;
  }
  
  map = L.map('map').setView([lat, lon], 14);

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
    (position) => {
      userLocation.value = {
        lat: position.coords.latitude,
        lon: position.coords.longitude
      };
      localStorage.setItem('locationConsent', 'granted');
      locationConsent.value = 'granted';
      initMap(userLocation.value.lat, userLocation.value.lon);
      error.value = null;
      
      // Auto search if ingredients are present
      if (ingredients.value) {
        findShops();
      }
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

const selectLocation = (loc) => {
  userLocation.value = { lat: parseFloat(loc.lat), lon: parseFloat(loc.lon) };
  manualQuery.value = loc.display_name;
  showSuggestions.value = false;
  locationSuggestions.value = [];
  locationConsent.value = 'denied'; // Manual mode
  localStorage.setItem('locationConsent', 'denied');
  
  initMap(userLocation.value.lat, userLocation.value.lon);
  
  // Auto search if ingredients present
  if (ingredients.value) {
    findShops();
  }
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

  // Clear existing shop markers
  markers.forEach(marker => map.removeLayer(marker));
  markers = [];

  try {
    const ingredientList = ingredients.value.split(',').map(i => i.trim());
    
    // Mock data check
    if (ingredientList.includes('mock')) {
        const baseLat = userLocation.value.lat;
        const baseLon = userLocation.value.lon;
        shops.value = [
          { name: "Supermercado Exemplo 1", lat: baseLat + 0.002, lon: baseLon + 0.002, distance: 350 },
          { name: "Mercearia Local", lat: baseLat - 0.003, lon: baseLon - 0.001, distance: 500 },
          { name: "Hipermercado", lat: baseLat + 0.001, lon: baseLon - 0.004, distance: 750 },
        ];
    } else {
      const payload = {
        ingredients: ingredientList,
        lat: userLocation.value.lat,
        lon: userLocation.value.lon,
        radius: searchRadius.value,
        mode: searchMode.value
      };

      const response = await fetch('http://localhost:8000/shops/find', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Falha ao obter resultados');
      shops.value = await response.json();
    }

    if (shops.value.length === 0) {
      error.value = "Não foram encontrados resultados nas proximidades.";
    }

    // Add markers
    shops.value.forEach(shop => {
      const isRestaurant = searchMode.value === 'restaurant';
      const marker = L.marker([shop.lat, shop.lon], {
        icon: L.icon({
          iconUrl: isRestaurant 
            ? 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
            : 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
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
    console.error(err);
    error.value = "Erro ao procurar. Verifica a ligação.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
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