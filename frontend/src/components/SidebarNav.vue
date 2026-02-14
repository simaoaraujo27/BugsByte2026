<script setup>
import logo from '@/assets/logo.png'
import SidebarItem from './SidebarItem.vue'

defineProps({
  sections: {
    type: Array,
    required: true
  },
  activeSection: {
    type: String,
    required: true
  }
})

defineEmits(['select'])
</script>

<template>
  <aside class="sidebar">
    <div class="logo-wrap">
      <img :src="logo" alt="Logo" class="logo" />
    </div>

    <div class="menu-divider" aria-hidden="true"></div>

    <nav class="menu" aria-label="Navegacao principal">
      <SidebarItem
        v-for="section in sections"
        :key="section.id"
        :label="section.label"
        :icon="section.icon"
        :active="activeSection === section.id"
        :highlight="Boolean(section.highlight)"
        @select="$emit('select', section.id)"
      />
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  border-right: 1px solid var(--line);
  background: var(--sidebar-bg);
  padding: 32px 20px;
  display: flex;
  flex-direction: column;
}

.logo-wrap {
  display: flex;
  justify-content: center;
  padding-bottom: 24px;
}

.logo {
  width: 72px;
  height: 72px;
  object-fit: contain;
  background: white;
  padding: 10px;
  border-radius: 18px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.menu-divider {
  height: 1px;
  width: 100%;
  background: var(--line);
  margin: 12px 0 20px;
  opacity: 0.6;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

@media (max-width: 860px) {
  .sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 16px;
  }

  .logo-wrap {
    justify-content: flex-start;
  }

  .logo {
    width: 56px;
    height: 56px;
  }

  .menu {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>
