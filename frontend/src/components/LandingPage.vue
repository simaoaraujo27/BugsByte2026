<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isDark = ref(true)

const toggleDarkMode = () => {
  isDark.value = !isDark.value
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div :class="['page', { 'dark-mode': isDark }]">
    <header class="topbar">
      <div class="logo-group">
        <img alt="Logo" class="logo" src="../assets/logo.png" />
        <p class="hackathon-badge">Desenvolvido para o Hackathon Bugsbyte 2026</p>
      </div>
      <button class="theme-toggle" @click="toggleDarkMode" :title="isDark ? 'Ativar modo claro' : 'Ativar modo escuro'">
        <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
      </button>
    </header>

    <main>
      <section class="hero section">
        <div class="hero-content fade-in-up">
          <p class="eyebrow">O que vamos comer hoje?</p>
          <h1>Coma melhor sem deixar de comer o que gosta.</h1>
          <p class="subtitle">
            A nossa app adapta receitas às suas calorias e mostra onde comprar ingredientes ou pedir takeaway perto de si.
          </p>
          <div class="hero-actions">
            <button class="btn btn-primary" type="button" @click="goToLogin">Começar Agora</button>
            <router-link to="/about" class="btn btn-secondary">Saber Mais</router-link>
          </div>
        </div>

        <aside class="hero-card fade-in-up-delayed" aria-label="Pré-visualização da app">
          <p class="card-label">Exemplo rápido</p>
          <h2>“Quero francesinha.”</h2>
          <p>Versão 600 kcal + supermercado mais próximo para comprar ingredientes.</p>
          <span class="card-pill">2 opções sugeridas</span>
        </aside>
      </section>

      <section class="section split">
        <article class="panel">
          <h3>O Problema</h3>
          <ul>
            <li>É difícil comer de forma saudável sem perder tempo.</li>
            <li>Nem sempre sabe o que cozinhar com o que tem em casa.</li>
            <li>Quando tem pressa, acaba por escolher as piores opções.</li>
          </ul>
        </article>

        <article class="panel">
          <h3>A Nossa Solução</h3>
          <ul>
            <li>IA que transforma desejos em opções equilibradas.</li>
            <li>Receitas personalizadas para o seu objetivo calórico.</li>
            <li>Sugestões locais para comprar ingredientes ou pedir comida.</li>
          </ul>
        </article>
      </section>

      <section class="section">
        <h3 class="section-title">Como funciona</h3>
        <div class="steps">
          <article class="step-card">
            <span class="step-index">1</span>
            <h4>Criar conta</h4>
            <p>Defina o seu perfil, alergénios e objetivos.</p>
          </article>
          <article class="step-card">
            <span class="step-index">2</span>
            <h4>Diga o que quer</h4>
            <p>Exemplo: “quero uma francesinha”.</p>
          </article>
          <article class="step-card">
            <span class="step-index">3</span>
            <h4>Receba opções</h4>
            <p>Receita ajustada + locais próximos.</p>
          </article>
        </div>
      </section>

      <section class="section">
        <h3 class="section-title">Principais funcionalidades</h3>
        <div class="features">
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">IA</p>
            <h4>Receitas adaptadas</h4>
            <p>Versões mais leves sem perder o sabor que procura.</p>
          </article>
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">GPS</p>
            <h4>Geo inteligente</h4>
            <p>Supermercados e restaurantes adequados perto de si.</p>
          </article>
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">CASA</p>
            <h4>Com o que tem</h4>
            <p>Sugestões com ingredientes que já tem em casa.</p>
          </article>
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">META</p>
            <h4>Objetivo diário</h4>
            <p>Calorias e escolhas alinhadas com a sua meta.</p>
          </article>
        </div>
      </section>

      <section class="section cta-final">
        <h3>Pronto para começar?</h3>
        <p>Comece em menos de 2 minutos e receba sugestões à sua medida.</p>
        <button class="btn btn-primary" type="button" @click="goToLogin">Criar Conta Gratuitamente</button>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page {
  --bg-main: #f4fbf8;
  --bg-soft: #ffffff;
  --text-main: #13293d;
  --text-muted: #3b566d;
  --accent: #0f766e;
  --accent-hover: #0b5c56;
  --line: #d7e7e0;
  --card-bg: rgba(255, 255, 255, 0.8);
  --badge-bg: rgba(255, 255, 255, 0.75);
  --pill-bg: #ddf4ef;
  --pill-text: #0f5258;

  min-height: 100vh;
  width: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at 15% 10%, rgba(155, 228, 208, 0.25), transparent 30%),
    radial-gradient(circle at 86% 18%, rgba(177, 214, 241, 0.22), transparent 26%),
    linear-gradient(160deg, #f8fcff 0%, var(--bg-main) 100%);
  color: var(--text-main);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  transition: background 0.3s ease, color 0.3s ease;
}

.page.dark-mode {
  --bg-main: #0f172a;
  --bg-soft: #1e293b;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --accent: #2dd4bf;
  --accent-hover: #14b8a6;
  --line: #334155;
  --card-bg: rgba(30, 41, 59, 0.7);
  --badge-bg: rgba(30, 41, 59, 0.8);
  --pill-bg: #134e4a;
  --pill-text: #2dd4bf;

  background:
    radial-gradient(circle at 15% 10%, rgba(45, 212, 191, 0.15), transparent 30%),
    radial-gradient(circle at 86% 18%, rgba(56, 189, 248, 0.1), transparent 26%),
    linear-gradient(160deg, #020617 0%, var(--bg-main) 100%);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-toggle {
  background: var(--bg-soft);
  border: 1px solid var(--line);
  color: var(--text-main);
  padding: 8px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.theme-toggle:hover {
  background: var(--line);
  transform: translateY(-1px);
}

.logo {
  width: 64px;
  height: 64px;
}

.hackathon-badge {
  margin: 0;
  padding: 6px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--badge-bg);
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
}

.section {
  max-width: 1120px;
  margin: 0 auto;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  align-items: center;
  gap: 28px;
  margin-top: 42px;
}

.hero-content h1 {
  margin: 0;
  font-size: clamp(2.1rem, 5vw, 3.9rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
}

.subtitle {
  margin: 16px 0 28px;
  max-width: 54ch;
  font-size: 1.03rem;
  line-height: 1.65;
  color: var(--text-muted);
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  border-radius: 999px;
  padding: 12px 18px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  border: 0;
  background: var(--accent);
  color: #f2fffc;
  box-shadow: 0 8px 20px rgba(15, 118, 110, 0.25);
}

.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
}

.btn-secondary {
  border: 1px solid var(--line);
  background: var(--bg-soft);
  color: var(--text-main);
}

.btn-secondary:hover {
  background: var(--line);
}

.hero-card {
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 22px;
  background: var(--card-bg);
  backdrop-filter: blur(8px);
}

.hero-card h2 {
  margin: 6px 0 10px;
  font-size: 1.5rem;
}

.hero-card p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.card-label {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
}

.card-pill {
  display: inline-block;
  margin-top: 14px;
  border-radius: 999px;
  padding: 7px 11px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--pill-text);
  background: var(--pill-bg);
}

.split {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 48px;
}

.panel {
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(4px);
}

.panel h3 {
  margin: 0 0 14px;
  font-size: 1.25rem;
}

.panel ul {
  margin: 0;
  padding-left: 20px;
  color: var(--text-muted);
}

.panel li + li {
  margin-top: 8px;
}

.section-title {
  margin: 54px 0 18px;
  font-size: 1.8rem;
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.step-card {
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
  background: var(--bg-soft);
  transition: transform 0.2s ease;
}

.step-card:hover {
  transform: translateY(-4px);
}

.step-index {
  display: inline-flex;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  align-items: center;
  justify-content: center;
  background: var(--pill-bg);
  color: var(--pill-text);
  font-weight: 700;
  font-size: 0.9rem;
}

.step-card h4,
.feature-card h4 {
  margin: 12px 0 8px;
  font-size: 1.06rem;
}

.step-card p,
.feature-card p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.features {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.feature-card {
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
  background: var(--bg-soft);
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: var(--accent);
}

.cta-final {
  margin-top: 54px;
  margin-bottom: 22px;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 28px;
  text-align: center;
  background: var(--card-bg);
  backdrop-filter: blur(8px);
}

.cta-final h3 {
  margin: 0 0 8px;
  font-size: 1.7rem;
}

.cta-final p {
  margin: 0 0 20px;
  color: var(--text-muted);
}

.fade-in-up {
  animation: fadeInUp 700ms ease-out both;
}

.fade-in-up-delayed {
  animation: fadeInUp 850ms ease-out both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1000px) {
  .hero,
  .split,
  .steps,
  .features {
    grid-template-columns: 1fr;
  }

  .section-title {
    margin-top: 40px;
  }
}

@media (max-width: 640px) {
  .page {
    padding: 16px;
  }

  .logo {
    width: 56px;
    height: 56px;
  }

  .hero {
    margin-top: 28px;
    gap: 18px;
  }

  .hero-content h1 {
    font-size: clamp(1.8rem, 9vw, 2.5rem);
  }

  .hackathon-badge {
    font-size: 0.72rem;
  }

  .cta-final {
    padding: 22px 16px;
  }
}
</style>
