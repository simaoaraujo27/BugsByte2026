<script setup>
import { useRouter } from 'vue-router'
import { auth } from '@/auth'
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

const emit = defineEmits(['select'])
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push('/')
}
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

    <div class="sidebar-footer">
      <div class="menu-divider" aria-hidden="true"></div>
      <button type="button" class="logout-btn" @click="handleLogout">
        <span class="item-icon">🚪</span>
        <span class="item-label">Sair</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  border-right: 1px solid var(--line);
  background: var(--sidebar-bg);
  padding: 32px 20px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
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
  flex: 1;
}

.sidebar-footer {
  margin-top: auto;
}

.logout-btn {
  border: 0;
  border-radius: 12px;
  padding: 12px 16px;
  text-align: left;
  font-size: 0.95rem;
  font-weight: 600;
  color: #e53e3e;
  background: transparent;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.logout-btn:hover {
  background: #fff5f5;
  transform: translateX(4px);
}

:global(.theme-dark) .logout-btn:hover {
  background: rgba(229, 62, 62, 0.1);
}

.item-icon {
  font-size: 1.25rem;
  line-height: 1;
}

@media (max-width: 860px) {
  .sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 16px;
    height: auto;
    position: relative;
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

  .sidebar-footer {
    margin-top: 16px;
  }
  
  .logout-btn {
    width: auto;
  }
}
</style>
