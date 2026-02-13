<script setup>
import { ref } from 'vue'
import SidebarNav from './SidebarNav.vue'

const sections = [
  { id: 'inicio', label: 'Inicio' },
  { id: 'receitas', label: 'Receitas' },
  { id: 'favoritos', label: 'Favoritos' },
  { id: 'perfil', label: 'Perfil' }
]

const activeSection = ref('inicio')

const sectionContent = {
  inicio: {
    title: 'Pagina Inicial',
    subtitle: 'Este sera o dashboard principal da aplicacao.'
  },
  receitas: {
    title: 'Receitas',
    subtitle: 'Aqui vao aparecer receitas ajustadas ao teu objetivo.'
  },
  favoritos: {
    title: 'Favoritos',
    subtitle: 'Nesta area vais guardar as tuas opcoes preferidas.'
  },
  perfil: {
    title: 'Perfil',
    subtitle: 'Dados pessoais, metas e preferencias alimentares.'
  }
}
</script>

<template>
  <div class="site-layout">
    <SidebarNav :sections="sections" :active-section="activeSection" @select="activeSection = $event" />

    <main class="content">
      <h1>{{ sectionContent[activeSection].title }}</h1>
      <p>{{ sectionContent[activeSection].subtitle }}</p>
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
