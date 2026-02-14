<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import SidebarNav from './SidebarNav.vue'
import DashboardHome from './DashboardHome.vue'
import Negotiator from './Negotiator.vue'
import ShopFinder from './ShopFinder.vue'
import ProfilePanel from './ProfilePanel.vue'
import DiaryTracking from './DiaryTracking.vue'
import VisionRecipe from './VisionRecipe.vue'
import FavoritesPage from './FavoritesPage.vue'
import SettingsPage from './SettingsPage.vue'

const sections = [
  { id: 'inicio', label: 'Início', icon: '🏠' },
  { id: 'tenho-fome', label: 'Tenho Fome', icon: '🍔' },
  { id: 'supermercados', label: 'Supermercados & Compras', icon: '🛒' },
  { id: 'diario', label: 'Diário / Tracking', icon: '📊' },
  { id: 'favoritos', label: 'Favoritos', icon: '❤️' },
  { id: 'perfil', label: 'Perfil', icon: '👤' },
  { id: 'definicoes', label: 'Definições', icon: '⚙️' }
]

const activeSection = ref('inicio')
const isDarkMode = ref(false)
const colorBlindnessMode = ref('none')

// State for ShopFinder parameters
const shopParams = ref({
  ingredients: '',
  mode: 'shop',
  term: ''
})

const handleNegotiationChoice = (choice) => {
  if (choice.type === 'diy') {
    shopParams.value = {
      ingredients: choice.ingredients,
      mode: 'shop',
      term: ''
    }
    activeSection.value = 'supermercados'
  }
}

// When manually clicking supermarket or restaurant, maybe reset params?
// Or keep them. Usually better to reset if not coming from Negotiator.
const selectSection = (id) => {
  activeSection.value = id
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
}

const updateColorBlindness = (mode) => {
  colorBlindnessMode.value = mode
  localStorage.setItem('colorBlindnessMode', mode)
}

const sectionContent = {
  inicio: {
    title: 'Painel Inicial',
    subtitle: 'Calorias do dia, streak e o atalho para "Tenho Fome".'
  },
  'tenho-fome': {
    title: 'Tenho Fome (Intelligent Assistant)',
    subtitle: 'Escolhe como queres decidir a tua próxima refeição saudável.'
  },
  supermercados: {
    title: 'Supermercados & Compras',
    subtitle: 'Lista automática de compras e ingredientes necessários.'
  },
  diario: {
    title: 'Diário / Tracking',
    subtitle: 'Acompanha as tuas calorias, o histórico semanal e o teu progresso.'
  },
  favoritos: {
    title: 'Favoritos',
    subtitle: 'Receitas e restaurantes guardados.'
  },
  perfil: {
    title: 'Perfil',
    subtitle: 'Dados físicos, objetivo, dieta, alergénios e localização.'
  },
  definicoes: {
    title: 'Definições',
    subtitle: 'Preferências da conta, notificações e opções da aplicação.'
  }
}

const containerStyle = computed(() => {
  if (colorBlindnessMode.value === 'none') return {}
  return { filter: `url(#${colorBlindnessMode.value})` }
})

onMounted(() => {
  const savedTheme = localStorage.getItem('dashboardTheme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
  } else {
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  const savedColorMode = localStorage.getItem('colorBlindnessMode')
  if (savedColorMode) {
    colorBlindnessMode.value = savedColorMode
  }
})

watch(isDarkMode, (value) => {
  localStorage.setItem('dashboardTheme', value ? 'dark' : 'light')
})
</script>

<template>
  <!-- SVG Filters for Color Blindness -->
  <svg style="position: absolute; width: 0; height: 0; overflow: hidden;" aria-hidden="true">
    <defs>
      <filter id="protanopia">
        <feColorMatrix type="matrix" values="0.567, 0.433, 0, 0, 0 0.558, 0.442, 0, 0, 0 0, 0.242, 0.758, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
      <filter id="deuteranopia">
        <feColorMatrix type="matrix" values="0.625, 0.375, 0, 0, 0 0.7, 0.3, 0, 0, 0 0, 0.3, 0.7, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
      <filter id="tritanopia">
        <feColorMatrix type="matrix" values="0.95, 0.05, 0, 0, 0 0, 0.433, 0.567, 0, 0 0, 0.475, 0.525, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
      <filter id="achromatopsia">
        <feColorMatrix type="matrix" values="0.299, 0.587, 0.114, 0, 0 0.299, 0.587, 0.114, 0, 0 0.299, 0.587, 0.114, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
    </defs>
  </svg>

  <div class="site-layout" :class="{ 'theme-dark': isDarkMode }" :style="containerStyle">
    <SidebarNav :sections="sections" :active-section="activeSection" @select="selectSection" />

    <main class="content">
      <div v-if="activeSection === 'inicio'">
        <DashboardHome @navigate="selectSection" />
      </div>

      <div v-else-if="activeSection === 'tenho-fome'">
        <Negotiator @choice="handleNegotiationChoice" />
      </div>
      
      <div v-else-if="activeSection === 'supermercados'">
        <ShopFinder 
          :initial-ingredients="shopParams.ingredients" 
          mode="shop" 
        />
      </div>

      <div v-else-if="activeSection === 'diario'">
        <DiaryTracking />
      </div>
      
      <div v-else-if="activeSection === 'favoritos'">
        <FavoritesPage />
      </div>

      <div v-else-if="activeSection === 'definicoes'">
        <SettingsPage 
          :is-dark-mode="isDarkMode" 
          :color-blindness-mode="colorBlindnessMode"
          @toggle-theme="toggleTheme" 
          @update-color-blindness="updateColorBlindness"
        />
      </div>

      <div v-else-if="activeSection === 'perfil'">
        <ProfilePanel />
      </div>

      <div v-else>
        <h1>{{ sectionContent[activeSection].title }}</h1>
        <p>{{ sectionContent[activeSection].subtitle }}</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.site-layout {
  --bg-main: #f2f6f9;
  --bg-elevated: #ffffff;
  --text-main: #11263f;
  --text-muted: #54667e;
  --line: #dbe3eb;
  --sidebar-bg: #ffffff;
  --sidebar-text: #54667e;
  --menu-hover-bg: #f3f7fb;
  --menu-active-bg: #e3f7f2;
  --menu-active-text: #0a705d;
  --menu-highlight-bg: #fff1e7;
  --menu-highlight-hover-bg: #ffe5d2;
  --menu-highlight-active-bg: #ffd9bd;
  --menu-highlight-text: #9a3412;
  --menu-highlight-active-text: #7c2d12;

  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: linear-gradient(160deg, #f8fbff 0%, var(--bg-main) 100%);
  color: var(--text-main);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
}

.site-layout.theme-dark {
  --bg-main: #06090f;
  --bg-elevated: #0f172a;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --line: #1e293b;
  --sidebar-bg: #020617;
  --sidebar-text: #ffffff;
  --menu-hover-bg: #1e293b;
  --menu-active-bg: #064e3b;
  --menu-active-text: #34d399;
  --menu-highlight-bg: #451a03;
  --menu-highlight-hover-bg: #78350f;
  --menu-highlight-active-bg: #92400e;
  --menu-highlight-text: #fed7aa;
  --menu-highlight-active-text: #ffedd5;
  background: radial-gradient(circle at 0% 0%, #0f172a 0%, #06090f 50%, #020617 100%);
}

.content {
  padding: 44px;
}

.content h1 {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.content p {
  margin-top: 12px;
  max-width: 60ch;
  color: var(--text-muted);
  font-size: 1.02rem;
}

.site-layout.theme-dark :deep(.shop-finder .location-setup),
.site-layout.theme-dark :deep(.shop-finder .controls),
.site-layout.theme-dark :deep(.shop-finder .shop-item),
.site-layout.theme-dark :deep(.negotiator-container .option-card),
.site-layout.theme-dark :deep(.negotiator-container input) {
  background: var(--bg-elevated);
  border-color: var(--line);
  color: var(--text-main);
}

.site-layout.theme-dark :deep(.shop-finder input),
.site-layout.theme-dark :deep(.shop-finder .search-wrapper input) {
  background: #0f1728;
  border-color: var(--line);
  color: var(--text-main);
}

.site-layout.theme-dark :deep(.shop-finder label),
.site-layout.theme-dark :deep(.shop-finder .radius-control),
.site-layout.theme-dark :deep(.shop-finder .location-label),
.site-layout.theme-dark :deep(.negotiator-container .recipe-content ul),
.site-layout.theme-dark :deep(.negotiator-container .btn-back) {
  color: var(--text-muted);
}

.site-layout.theme-dark :deep(.shop-finder .suggestions),
.site-layout.theme-dark :deep(.shop-finder .suggestions li) {
  background: var(--bg-elevated);
  color: var(--text-main);
  border-color: var(--line);
}

@media (max-width: 860px) {
  .site-layout {
    grid-template-columns: 1fr;
  }
}
</style>