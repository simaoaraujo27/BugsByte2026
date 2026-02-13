<script setup>
import { ref, computed } from 'vue'
import SidebarNav from './SidebarNav.vue'
import Negotiator from './Negotiator.vue'
import ShopFinder from './ShopFinder.vue'

const sections = [
  { id: 'inicio', label: 'Inicio', icon: '🏠' },
  { id: 'gerar-receita', label: 'Gerar Receita', icon: '🍽️' },
  { id: 'tenho-fome', label: 'Tenho Fome', icon: '🍔', highlight: true },
  { id: 'supermercados', label: 'Supermercados & Compras', icon: '🛒' },
  { id: 'restaurantes', label: 'Restaurantes Perto', icon: '🍴' },
  { id: 'diario', label: 'Diario / Tracking', icon: '📊' },
  { id: 'favoritos', label: 'Favoritos', icon: '❤️' },
  { id: 'perfil', label: 'Perfil', icon: '👤' }
]

const activeSection = ref('inicio')

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
  } else if (choice.type === 'lazy') {
    shopParams.value = {
      ingredients: '',
      mode: 'restaurant',
      term: choice.term
    }
    activeSection.value = 'restaurantes'
  }
}

// When manually clicking supermarket or restaurant, maybe reset params?
// Or keep them. Usually better to reset if not coming from Negotiator.
const selectSection = (id) => {
  if (id !== 'supermercados' && id !== 'restaurantes' && id !== 'tenho-fome') {
    // Reset if going elsewhere? Optional.
  }
  activeSection.value = id
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
    subtitle: 'Escolhe um prato e recebe versao DIY saudavel e versao restaurante perto.'
  },
  supermercados: {
    title: 'Supermercados & Compras',
    subtitle: 'Lista automatica de compras e ingredientes necessarios.'
  },
  restaurantes: {
    title: 'Restaurantes Perto',
    subtitle: 'Restaurantes num raio local, abertos agora e alinhados com calorias.'
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
  }
}
</script>

<template>
  <div class="site-layout">
    <SidebarNav :sections="sections" :active-section="activeSection" @select="selectSection" />

    <main class="content">
      <div v-if="activeSection === 'tenho-fome'">
        <Negotiator @choice="handleNegotiationChoice" />
      </div>
      
      <div v-else-if="activeSection === 'supermercados'">
        <ShopFinder 
          :initial-ingredients="shopParams.ingredients" 
          mode="shop" 
        />
      </div>

      <div v-else-if="activeSection === 'restaurantes'">
        <ShopFinder 
          :initial-ingredients="shopParams.term" 
          mode="restaurant" 
        />
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
  --text-main: #11263f;
  --text-muted: #54667e;

  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: linear-gradient(160deg, #f8fbff 0%, var(--bg-main) 100%);
  color: var(--text-main);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
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

@media (max-width: 860px) {
  .site-layout {
    grid-template-columns: 1fr;
  }
}
</style>
