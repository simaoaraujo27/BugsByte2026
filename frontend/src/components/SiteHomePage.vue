<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import SidebarNav from './SidebarNav.vue'
import DashboardHome from './DashboardHome.vue'
import Negotiator from './Negotiator.vue'
import ShopFinder from './ShopFinder.vue'
import ProfilePanel from './ProfilePanel.vue'
import VisionRecipe from './VisionRecipe.vue'

const sections = [
  { id: 'inicio', label: 'Inicio', icon: '🏠' },
  { id: 'gerar-receita', label: 'Gerar Receita', icon: '🍽️' },
  { id: 'tenho-fome', label: 'Tenho Fome', icon: '🍔' },
  { id: 'supermercados', label: 'Supermercados & Compras', icon: '🛒' },
  { id: 'diario', label: 'Diario / Tracking', icon: '📊' },
  { id: 'favoritos', label: 'Favoritos', icon: '❤️' },
  { id: 'perfil', label: 'Perfil', icon: '👤' },
  { id: 'definicoes', label: 'Definicoes', icon: '⚙️' }
]

const activeSection = ref('inicio')
const isDarkMode = ref(false)

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

const sectionContent = {
  inicio: {
    title: 'Dashboard Inicial',
    subtitle: 'Calorias do dia, streak e o atalho para "Tenho Fome".'
  },
  'gerar-receita': {
    title: 'Gerar Receita',
    subtitle: 'Receitas saudaveis, por ingredientes ou por upload de foto.'
  },
  'tenho-fome': {
    title: 'Tenho Fome (Asneira Mode)',
    subtitle: 'Escolhe um prato e recebe versao DIY saudavel.'
  },
  supermercados: {
    title: 'Supermercados & Compras',
    subtitle: 'Lista automatica de compras e ingredientes necessarios.'
  },
  diario: {
    title: 'Diario / Tracking',
    subtitle: 'Acompanha calorias, historico semanal e progresso.'
  },
  favoritos: {
    title: 'Favoritos',
    subtitle: 'Receitas e restaurantes guardados.'
  },
  perfil: {
    title: 'Perfil',
    subtitle: 'Dados fisicos, objetivo, dieta, alergenios e localizacao.'
  },
  definicoes: {
    title: 'Definicoes',
    subtitle: 'Preferencias da conta, notificacoes e opcoes da aplicacao.'
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('dashboardTheme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
    return
  }

  isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
})

watch(isDarkMode, (value) => {
  localStorage.setItem('dashboardTheme', value ? 'dark' : 'light')
})
</script>

<template>
  <div class="site-layout" :class="{ 'theme-dark': isDarkMode }">
    <SidebarNav :sections="sections" :active-section="activeSection" @select="selectSection" />

    <main class="content">
      <div v-if="activeSection === 'inicio'">
        <DashboardHome @navigate="selectSection" />
      </div>

      <div v-else-if="activeSection === 'tenho-fome'">
        <Negotiator @choice="handleNegotiationChoice" />
      </div>
      
      <div v-else-if="activeSection === 'gerar-receita'">
        <VisionRecipe />
      </div>

      <div v-else-if="activeSection === 'supermercados'">
        <ShopFinder 
          :initial-ingredients="shopParams.ingredients" 
          mode="shop" 
        />
      </div>

      <div v-else-if="activeSection === 'definicoes'" class="settings-panel">
        <h1>{{ sectionContent[activeSection].title }}</h1>
        <p>{{ sectionContent[activeSection].subtitle }}</p>

        <div class="settings-card">
          <div>
            <h3>Modo Escuro</h3>
            <small>Ativa um tema mais confortavel para ambientes com pouca luz.</small>
          </div>
          <button
            type="button"
            class="theme-toggle"
            :class="{ active: isDarkMode }"
            @click="toggleTheme"
            :aria-pressed="isDarkMode"
          >
            <span class="toggle-knob"></span>
          </button>
        </div>
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
  --bg-main: #0f1728;
  --bg-elevated: #162034;
  --text-main: #e6edf7;
  --text-muted: #a6b6cc;
  --line: #24334d;
  --sidebar-bg: #111a2b;
  --menu-hover-bg: #1d2a42;
  --menu-active-bg: #123d36;
  --menu-active-text: #92f2da;
  --menu-highlight-bg: #4a2f13;
  --menu-highlight-hover-bg: #5e3a16;
  --menu-highlight-active-bg: #704417;
  --menu-highlight-text: #ffd39f;
  --menu-highlight-active-text: #ffe3c2;
  background: radial-gradient(circle at 20% 0%, #1a2740 0%, #0f1728 45%, #0b1220 100%);
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

.settings-panel {
  max-width: 760px;
}

.settings-card {
  margin-top: 26px;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.settings-card h3 {
  margin: 0;
  font-size: 1.02rem;
}

.settings-card small {
  display: block;
  margin-top: 6px;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.theme-toggle {
  width: 56px;
  height: 32px;
  border-radius: 99px;
  border: 1px solid var(--line);
  background: #d6dee8;
  padding: 3px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.site-layout.theme-dark .theme-toggle {
  background: #23314a;
}

.theme-toggle.active {
  background: #07a374;
  border-color: #07a374;
}

.toggle-knob {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ffffff;
  transition: transform 0.2s ease;
}

.theme-toggle.active .toggle-knob {
  transform: translateX(24px);
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