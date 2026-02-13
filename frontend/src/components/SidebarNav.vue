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
  --sidebar-bg: #ffffff;
  --line: #dbe3eb;
  --text-main: #11263f;
  --text-muted: #54667e;
  --accent-soft: #e3f7f2;

  border-right: 1px solid var(--line);
  background: var(--sidebar-bg);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
}

.logo-wrap {
  display: flex;
  justify-content: center;
  padding-bottom: 12px;
}

.logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

.menu-divider {
  height: 1px;
  width: 100%;
  background: var(--line);
  margin: 8px 0 12px;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

  .menu {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>
