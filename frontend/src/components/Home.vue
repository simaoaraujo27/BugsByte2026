<template>
  <div class="page">
    <main>
      <section class="hero section">
        <div class="hero-content fade-in-up">
          <p class="eyebrow">O que vamos comer hoje?</p>
          <h1>Come melhor sem deixar de comer o que gostas.</h1>
          <p class="subtitle">
            A nossa app adapta receitas às tuas calorias e mostra onde comprar ingredientes ou pedir takeaway perto de ti.
          </p>
          <div class="hero-actions">
            <router-link to="/login" class="btn btn-primary">Começar Agora</router-link>
            <button class="btn btn-secondary" type="button">Saber Mais</button>
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
            <li>É difícil comer saudável sem perder tempo.</li>
            <li>Nem sempre sabes o que cozinhar com o que tens em casa.</li>
            <li>Quando há pressa, acabas por escolher opções piores.</li>
          </ul>
        </article>

        <article class="panel">
          <h3>A Nossa Solução</h3>
          <ul>
            <li>AI que transforma desejos em opções equilibradas.</li>
            <li>Receitas personalizadas ao teu objetivo calórico.</li>
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
            <p>Definir perfil, alergénios e objetivo.</p>
          </article>
          <article class="step-card">
            <span class="step-index">2</span>
            <h4>Dizer o que queres</h4>
            <p>Exemplo: “quero uma francesinha”.</p>
          </article>
          <article class="step-card">
            <span class="step-index">3</span>
            <h4>Receber opções</h4>
            <p>Receita ajustada + locais próximos.</p>
          </article>
        </div>
      </section>

      <section class="section">
        <h3 class="section-title">Features principais</h3>
        <div class="features">
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">AI</p>
            <h4>Receitas adaptadas</h4>
            <p>Versões mais leves sem perder o sabor que procuras.</p>
          </article>
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">GPS</p>
            <h4>Geo inteligente</h4>
            <p>Supermercados e restaurantes adequados perto de ti.</p>
          </article>
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">HOME</p>
            <h4>Com o que tens</h4>
            <p>Sugestões com ingredientes que já tens em casa.</p>
          </article>
          <article class="feature-card">
            <p class="feature-icon" aria-hidden="true">GOAL</p>
            <h4>Objetivo diário</h4>
            <p>Calorias e escolhas alinhadas com a tua meta.</p>
          </article>
        </div>
      </section>

      <section class="section cta-final">
        <h3>Pronto para começar?</h3>
        <p>Começa em menos de 2 minutos e recebe sugestões à tua medida.</p>
        <router-link to="/login" class="btn btn-primary">Criar Conta Gratuitamente</router-link>
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

  min-height: 100vh;
  width: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at 15% 10%, rgba(155, 228, 208, 0.25), transparent 30%),
    radial-gradient(circle at 86% 18%, rgba(177, 214, 241, 0.22), transparent 26%),
    linear-gradient(160deg, #f8fcff 0%, var(--bg-main) 100%);
  color: var(--text-main);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
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
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  border: 0;
  background: var(--accent);
  color: #f2fffc;
  box-shadow: 0 8px 20px rgba(15, 118, 110, 0.25);
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-secondary {
  border: 1px solid var(--line);
  background: var(--bg-soft);
  color: var(--text-main);
}

.hero-card {
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 22px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(2px);
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
  color: #2f5668;
}

.card-pill {
  display: inline-block;
  margin-top: 14px;
  border-radius: 999px;
  padding: 7px 11px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #0f5258;
  background: #ddf4ef;
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
  background: rgba(255, 255, 255, 0.78);
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
}

.step-index {
  display: inline-flex;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  align-items: center;
  justify-content: center;
  background: #ddf4ef;
  color: #0c5f5d;
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
}

.feature-icon {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #0f6d65;
}

.cta-final {
  margin-top: 54px;
  margin-bottom: 22px;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 28px;
  text-align: center;
  background: rgba(255, 255, 255, 0.86);
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

  .hero {
    margin-top: 28px;
    gap: 18px;
  }

  .hero-content h1 {
    font-size: clamp(1.8rem, 9vw, 2.5rem);
  }
}
</style>