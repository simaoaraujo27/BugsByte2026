<script setup>
import { ref } from 'vue'
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
const isMenuOpen = ref(false)

const handleLogout = () => {
  auth.logout()
  router.push('/')
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const handleSelect = (id) => {
  isMenuOpen.value = false
  emit('select', id)
}
</script>

<template>
  <aside class="sidebar">
    <div class="header-mobile">
      <div class="logo-wrap">
        <img :src="logo" alt="Logo" class="logo" />
      </div>
      <button class="hamburger-btn" :class="{ 'is-active': isMenuOpen }" @click="toggleMenu" aria-label="Menu">
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
      </button>
    </div>

    <div class="menu-container" :class="{ 'is-open': isMenuOpen }">
      <div class="menu-divider" aria-hidden="true"></div>

      <nav class="menu" aria-label="Navegacao principal">
        <SidebarItem
          v-for="section in sections"
          :key="section.id"
          :label="section.label"
          :icon="section.icon"
          :active="activeSection === section.id"
          :highlight="Boolean(section.highlight)"
          @select="handleSelect(section.id)"
        />
      </nav>

      <div class="sidebar-footer">
        <div class="menu-divider" aria-hidden="true"></div>
        <button type="button" class="logout-btn" @click="handleLogout">
          <span class="item-icon">🚪</span>
          <span class="item-label">Sair</span>
        </button>
      </div>
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
  transition: all 0.3s ease;
  overflow-x: hidden;
  box-sizing: border-box;
}

.header-mobile {
  display: flex;
  justify-content: center; /* Centered on desktop effectively */
  align-items: center;
  width: 100%;
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

.hamburger-btn {
  display: none; /* Hidden on desktop */
  flex-direction: column;
  justify-content: space-between;
  width: 30px;
  height: 21px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-left: auto; /* Pushes to right on mobile */
  z-index: 101;
}

.hamburger-line {
  width: 100%;
  height: 3px;
  background-color: var(--sidebar-text);
  border-radius: 3px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.hamburger-btn.is-active .hamburger-line:nth-child(1) {
  transform: translateY(9px) rotate(45deg);
}

.hamburger-btn.is-active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.is-active .hamburger-line:nth-child(3) {
  transform: translateY(-9px) rotate(-45deg);
}

.menu-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  min-height: 0;
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
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 10px;
  overscroll-behavior: contain;
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
    z-index: 100;
  }

  .header-mobile {
    justify-content: space-between;
    padding-bottom: 0;
  }

  .logo-wrap {
    padding-bottom: 0;
  }

  .logo {
    width: 48px;
    height: 48px;
    padding: 6px;
    border-radius: 12px;
  }

  .hamburger-btn {
    display: flex;
  }

  .menu-container {
    display: none; /* Hidden by default on mobile */
    padding-top: 16px;
  }

  .menu-container.is-open {
    display: flex;
  }

  .menu-divider {
    margin: 10px 0;
  }

  .menu {
    flex-direction: column; /* Keep vertical */
    max-height: 60vh; /* Scrollable if too long */
  }

  .sidebar-footer {
    margin-top: 16px;
  }
}
</style>
