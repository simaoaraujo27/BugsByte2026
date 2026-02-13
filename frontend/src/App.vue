<template>
  <div class="page-background">
    <header class="topbar">
      <img alt="Logo" class="logo" src="./assets/logo.svg" />
      <p class="app-name">BugsByte</p>
    </header>
    <router-view />
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

.logo {
  display: block;
  width: 56px;
  height: 56px;
}

.app-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #3b566d;
}

@media (max-width: 640px) {
  .page-background {
    padding: 16px;
  }
}
</style>