<template>
  <main class="page">
    <section class="hero section">
      <div class="hero-content">
        <p class="eyebrow">O QUE VAMOS COMER HOJE?</p>
        <h1>Come melhor sem deixar de comer o que gostas.</h1>
        <p class="subtitle">
          A nossa app adapta receitas as tuas calorias e mostra onde comprar ingredientes ou pedir takeaway perto de ti.
        </p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="/profile">Comecar Agora</a>
          <button class="btn btn-secondary" type="button">Saber Mais</button>
        </div>
      </div>

      <aside class="hero-card" aria-label="Pre-visualizacao da app">
        <span class="shape" aria-hidden="true"></span>
        <p class="card-label">EXEMPLO RAPIDO</p>
        <h2>"Quero francesinha."</h2>
        <p class="card-text">Versao 800 kcal + supermercado mais proximo para comprar ingredientes.</p>
        <span class="card-pill">2 opcoes sugeridas</span>
      </aside>
    </section>

    <section class="section split">
      <article class="panel panel-problem">
        <h3>O Problema</h3>
        <ul>
          <li>E dificil comer saudavel sem perder tempo.</li>
          <li>Nem sempre sabes o que cozinhar com o que tens em casa.</li>
          <li>Quando ha pressa, acabas por escolher opcoes piores.</li>
        </ul>
      </article>

      <article class="panel panel-solution">
        <h3>A Nossa Solucao</h3>
        <ul>
          <li>AI que transforma desejos em opcoes equilibradas.</li>
          <li>Receitas personalizadas ao teu objetivo calorico.</li>
          <li>Sugestoes locais para comprar ingredientes ou pedir comida.</li>
        </ul>
      </article>
    </section>

    <section class="section how">
      <h3 class="section-title">Como funciona</h3>
      <p class="section-subtitle">Comeca em menos de 2 minutos</p>
      <div class="steps">
        <article class="step-card">
          <span class="step-index">1</span>
          <h4>Criar conta</h4>
          <p>Definir perfil, alergenios e objetivo.</p>
        </article>
        <article class="step-card">
          <span class="step-index">2</span>
          <h4>Dizer o que queres</h4>
          <p>Exemplo: "quero uma francesinha".</p>
        </article>
        <article class="step-card">
          <span class="step-index">3</span>
          <h4>Receber opcoes</h4>
          <p>Receita ajustada + locais proximos.</p>
        </article>
      </div>
    </section>

    <section class="section features-section">
      <h3 class="section-title">Features principais</h3>
      <p class="section-subtitle">Tudo o que precisas para comer melhor</p>
      <div class="features">
        <article class="feature-card">
          <span class="tag tag-ai">AI</span>
          <h4>Receitas adaptadas</h4>
          <p>Versoes mais leves sem perder o sabor que procuras.</p>
        </article>
        <article class="feature-card">
          <span class="tag tag-gps">GPS</span>
          <h4>Geo Inteligente</h4>
          <p>Supermercados e restaurantes adequados perto de ti.</p>
        </article>
        <article class="feature-card">
          <span class="tag tag-home">HOME</span>
          <h4>Com o que tens</h4>
          <p>Sugestoes com ingredientes que ja tens em casa.</p>
        </article>
        <article class="feature-card">
          <span class="tag tag-goal">GOAL</span>
          <h4>Objetivo diario</h4>
          <p>Calorias e escolhas alinhadas com a tua meta.</p>
        </article>
      </div>
    </section>

    <section class="cta-wrap">
      <div class="cta-inner section">
        <h3>Pronto para comecar?</h3>
        <p>Comeca em menos de 2 minutos e recebe sugestoes a tua medida.</p>
        <button class="btn btn-primary" type="button">Criar Conta Gratuitamente</button>
      </div>

      <footer class="footer section">
        <p class="brand">VitaMeal</p>
        <p class="copyright">© 2026 VitaMeal. Todos os direitos reservados.</p>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.page {
  --surface: #ffffff;
  --bg: #eef3f8;
  --text: #0a1f47;
  --muted: #4c6381;
  --line: #dae4f0;
  --primary: #07a374;
  --primary-dark: #078661;
  --navy: #05163c;

  color: var(--text);
}

.section {
  width: min(1120px, calc(100% - 20px));
  margin: 0 auto;
}

.hero {
  margin-top: 24px;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 32px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 0.9rem;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: var(--primary);
}

.hero-content h1 {
  margin: 0;
  max-width: 14ch;
  font-size: clamp(2.4rem, 5.5vw, 4.6rem);
  line-height: 1.04;
}

.subtitle {
  margin: 24px 0 0;
  max-width: 54ch;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--muted);
}

.hero-actions {
  margin-top: 28px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  border-radius: 999px;
  padding: 13px 28px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  border: 0;
  background: var(--primary);
  color: #f2fffc;
  box-shadow: 0 10px 22px rgba(7, 163, 116, 0.24);
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.btn-secondary {
  border: 1px solid #bccbdf;
  background: #f6f9fd;
  color: #254164;
}

.hero-card {
  position: relative;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.85);
  padding: 28px;
}

.shape {
  position: absolute;
  top: -18px;
  right: -18px;
  width: 92px;
  height: 92px;
  border-radius: 18px;
  background: rgba(122, 215, 199, 0.42);
  transform: rotate(12deg);
}

.card-label {
  margin: 0;
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--primary);
}

.hero-card h2 {
  margin: 12px 0 10px;
  font-size: 2.1rem;
}

.card-text {
  margin: 0;
  color: var(--muted);
  font-size: 1.1rem;
  line-height: 1.5;
}

.card-pill {
  display: inline-block;
  margin-top: 16px;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #0c7858;
  background: #ddf5ed;
}

.split {
  margin-top: 72px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.panel {
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 28px;
}

.panel h3 {
  margin: 0 0 16px;
  font-size: 2rem;
}

.panel ul {
  margin: 0;
  padding-left: 22px;
}

.panel li {
  color: var(--muted);
  font-size: 1.08rem;
  line-height: 1.65;
}

.panel li + li {
  margin-top: 8px;
}

.panel-problem {
  background: #eef3f9;
}

.panel-solution {
  background: #e6f5f1;
  border-color: #b7e8d8;
}

.how {
  margin-top: 84px;
}

.section-title {
  margin: 0;
  text-align: center;
  font-size: 3rem;
}

.section-subtitle {
  margin: 12px 0 0;
  text-align: center;
  color: var(--muted);
  font-size: 1rem;
}

.steps {
  margin-top: 38px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
}

.step-card {
  position: relative;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--surface);
  padding: 22px;
}

.step-card:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 50%;
  right: -22px;
  width: 20px;
  height: 2px;
  background: #8be6cd;
}

.step-index {
  display: inline-flex;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  align-items: center;
  justify-content: center;
  background: var(--primary);
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 700;
}

.step-card h4 {
  margin: 16px 0 8px;
  font-size: 1.85rem;
}

.step-card p {
  margin: 0;
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.5;
}

.features-section {
  margin-top: 86px;
}

.features {
  margin-top: 36px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.feature-card {
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 20px;
  background: #f7f9fd;
}

.tag {
  display: inline-block;
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 0.82rem;
  font-weight: 700;
}

.tag-ai {
  color: #6f56e3;
  background: #ece7ff;
}

.tag-gps {
  color: #2b67ea;
  background: #e8efff;
}

.tag-home {
  color: #d47d00;
  background: #fff2dc;
}

.tag-goal {
  color: #0a8a67;
  background: #dcf6ed;
}

.feature-card h4 {
  margin: 12px 0 8px;
  font-size: 1.7rem;
}

.feature-card p {
  margin: 0;
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.5;
}

.cta-wrap {
  margin-top: 84px;
  background: var(--navy);
  color: #eef3ff;
}

.cta-inner {
  text-align: center;
  padding: 84px 0 64px;
}

.cta-inner h3 {
  margin: 0;
  font-size: 3rem;
}

.cta-inner p {
  margin: 14px 0 30px;
  font-size: 1rem;
  color: #9eb1d0;
}

.footer {
  border-top: 1px solid #14284f;
  padding: 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.brand {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.copyright {
  margin: 0;
  font-size: 0.92rem;
  color: #7f92b4;
}

@media (max-width: 1024px) {
  .hero,
  .split,
  .steps,
  .features {
    grid-template-columns: 1fr;
  }

  .step-card:not(:last-child)::after {
    display: none;
  }
}

@media (max-width: 640px) {
  .hero-content h1 {
    font-size: clamp(2rem, 9vw, 3rem);
  }

  .btn {
    width: 100%;
  }

  .footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
