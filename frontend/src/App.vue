<script setup>
import Home from './components/Home.vue'
import UserInfo from './components/UserInfo.vue'
import ShopFinder from './components/ShopFinder.vue'
import Negotiator from './components/Negotiator.vue'

const currentPath = window.location.pathname
</script>

<template>
  <div class="page-background">
    <header class="topbar">
      <a href="/" class="logo-link">
        <img alt="Logo" class="logo" src="./assets/logo.png" />
      </a>
      <nav class="nav-links">
        <a href="/shops" class="nav-link">Lojas</a>
        <a href="/negotiator" class="nav-link">SOS Fome</a>
        <a href="/profile" class="nav-link">Perfil</a>
      </nav>
    </header>
    <UserInfo v-if="currentPath === '/profile'" />
    <ShopFinder v-else-if="currentPath === '/shops'" />
    <Negotiator v-else-if="currentPath === '/negotiator'" />
    <Home v-else />
  </div>
</template>

<style scoped>
.page-background {
  --bg-main: #f4fbf8;
  min-height: 100vh;
  width: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at 15% 10%, rgba(155, 228, 208, 0.25), transparent 30%),
    radial-gradient(circle at 86% 18%, rgba(177, 214, 241, 0.22), transparent 26%),
    linear-gradient(160deg, #f8fcff 0%, var(--bg-main) 100%);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1120px;
  margin: 0 auto;
  padding-bottom: 16px;
}

.logo-link {
  display: block;
}

.logo {
  display: block;
  width: 56px;
  height: 56px;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  text-decoration: none;
  color: #05163c;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 20px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(7, 163, 116, 0.1);
  color: #07a374;
}

@media (max-width: 640px) {
  .page-background {
    padding: 16px;
  }
}
</style>
