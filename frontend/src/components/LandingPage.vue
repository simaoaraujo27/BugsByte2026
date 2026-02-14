<script setup>
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="landing">
    <header class="topbar">
      <div class="container nav-inner">
        <div class="brand">
          <img :src="logo" alt="NutriVentures" class="brand-logo" />
          <span class="brand-name">NutriVida</span>
        </div>

        <nav class="menu-links" aria-label="Navegação principal">
          <a href="#servicos">Funcionalidades</a>
          <a href="#beneficios">Benefícios</a>
          <a href="#testemunhos">Equipa</a>
        </nav>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <p class="tag">Nutrição & Tecnologia</p>
            <h1>A Revolução da IA na tua Alimentação</h1>
            <p>
              A tua assistente inteligente de bolso. Analisa ingredientes por foto, 
              negocia desejos calóricos e encontra opções saudáveis perto de ti.
            </p>

            <div class="hero-actions">
              <button class="btn btn-main" type="button" @click="goToLogin">Começar Agora</button>
            </div>
          </div>

          <div class="hero-visual" aria-label="Prato saudável">
            <div class="hero-shape"></div>
            <img src="https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=1200&q=80" alt="Prato saudável" />
            <div class="floating-card top">IA Avançada</div>
            <div class="floating-card bottom">Foco na Saúde</div>
          </div>
        </div>
      </section>

      <section id="servicos" class="section-light">
        <div class="container">
          <p class="section-tag">Funcionalidades</p>
          <h2>O Poder da IA no teu Prato</h2>
          <p class="section-subtitle">Ferramentas tecnológicas avançadas para simplificar a tua dieta.</p>

          <div class="cards-grid">
            <article class="service-card">
              <h3>📸 Chef Vision IA</h3>
              <p>Tira uma foto aos ingredientes que tens em casa e recebe instantaneamente uma receita saudável e criativa.</p>
            </article>
            <article class="service-card">
              <h3>🍔 Negociador de Desejos</h3>
              <p>Apetece-te "asneira"? A nossa IA negocia contigo alternativas mais saudáveis ou versões caseiras deliciosas.</p>
            </article>
            <article class="service-card">
              <h3>📍 Radar Saudável</h3>
              <p>Encontra supermercados e restaurantes compatíveis com a tua dieta na tua localização atual.</p>
            </article>
          </div>
        </div>
      </section>

      <section id="beneficios" class="benefits">
        <div class="container benefits-grid">
          <div>
            <p class="section-tag">Porque escolher-nos</p>
            <h2>Benefícios que vão além da balança</h2>
            <p class="section-subtitle">
              Alimentação equilibrada com foco em energia, saúde e hábitos sustentáveis.
            </p>

            <ul class="check-list">
              <li>Mais energia no dia a dia</li>
              <li>Melhoria da disposição e do foco</li>
              <li>Hábitos saudáveis duradouros</li>
              <li>Resultados consistentes e sustentáveis</li>
            </ul>
          </div>

          <div class="mosaic" aria-label="Imagens de alimentação saudável">
            <img src="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80" alt="Ingredientes frescos" />
            <img src="https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=900&q=80" alt="Comida saudável" />
            <img src="https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=900&q=80" alt="Refeição equilibrada" />
            <img src="https://images.unsplash.com/photo-1511690743698-d9d85f2fbf38?auto=format&fit=crop&w=900&q=80" alt="Salada colorida" />
          </div>
        </div>
      </section>

      <section id="testemunhos" class="testimonials">
        <div class="container">
          <p class="section-tag section-tag-light">Hackathon 2026</p>
          <h2>A Visão dos Criadores</h2>

          <div class="cards-grid">
            <article class="testimonial-card">
              <p>“Acreditamos que a Inteligência Artificial deve servir a saúde de forma intuitiva e imediata.”</p>
              <strong>Pedro</strong>
              <span>Dev Team</span>
            </article>
            <article class="testimonial-card">
              <p>“O nosso objetivo é simplificar a decisão diária do 'o que comer' para todos.”</p>
              <strong>Simão</strong>
              <span>Dev Team</span>
            </article>
            <article class="testimonial-card">
              <p>“Criámos o NutriVida para demonstrar como a tecnologia pode quebrar barreiras na nutrição.”</p>
              <strong>Francisco</strong>
              <span>Dev Team</span>
            </article>
          </div>
        </div>
      </section>

      <section class="final-cta">
        <div class="container final-cta-inner">
          <h2>Pronto para testar o futuro da nutrição?</h2>
          <p>Junta-te à NutriVida e experimenta todas as ferramentas de Inteligência Artificial agora.</p>
          <button class="btn btn-main" type="button" @click="goToLogin">Começar Agora</button>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="container footer-grid">
        <div>
          <div class="brand">
            <img :src="logo" alt="NutriVentures" class="brand-logo" />
            <span class="brand-name light">NutriVida</span>
          </div>
          <p>Inovação tecnológica aplicada à nutrição para simplificar decisões saudáveis.</p>
        </div>

        <div>
          <h4>Projeto</h4>
          <ul>
            <li>Hackathon 2026</li>
            <li>Tecnologia</li>
            <li>Open Source</li>
          </ul>
        </div>

        <div>
          <h4>Equipa Dev</h4>
          <ul>
            <li>Francisco Barbosa</li>
            <li>João Teixeira</li>
            <li>Pedro Morais</li>
            <li>Simão Araújo</li>
            <li>Simão Mendes</li>
          </ul>
        </div>

        <div>
          <h4>Contactos</h4>
          <ul>
            <li>nutriventuresbugs@gmail.com</li>
            <li>+351 969 139 181</li>
            <li>+351 939 350 345</li>
            <li>Braga, Portugal</li> 
          </ul>
        </div>
      </div>

      <div class="container footer-bottom">
        © 2026 NutriVida. Desenvolvido com ❤️ na Hackathon.
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing {
  --bg: #f3f8f5;
  --bg-soft: #ffffff;
  --text: #10243c;
  --muted: #4d6278;
  --line: #d8e7e0;
  --green: #0a9a6c;
  --green-dark: #087b57;
  --green-soft: #dff4ec;
  --nav-h: 74px;

  color: var(--text);
  background: var(--bg);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
}

.container {
  width: min(1240px, calc(100% - 48px));
  margin: 0 auto;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--nav-h);
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #c9e7da;
  backdrop-filter: blur(8px);
}

.nav-inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #fff;
  padding: 6px;
}

.brand-name {
  font-size: 1.95rem;
  font-weight: 700;
}

.menu-links {
  display: flex;
  gap: 28px;
}

.menu-links a {
  color: var(--muted);
  text-decoration: none;
  font-weight: 600;
}

.menu-links a:hover {
  color: var(--text);
}

.btn {
  border: 0;
  border-radius: 999px;
  min-height: 44px;
  padding: 0 24px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-main {
  background: var(--green);
  color: #fff;
  box-shadow: 0 10px 24px rgba(10, 154, 108, 0.26);
}

.btn-main:hover {
  background: var(--green-dark);
}

.btn-ghost {
  background: #fff;
  border: 1px solid #9fddc7;
  color: var(--green-dark);
}

.hero {
  padding: 50px 0 70px;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 30px;
  align-items: center;
}

.tag,
.section-tag {
  display: inline-block;
  margin: 0 0 14px;
  padding: 8px 14px;
  border-radius: 999px;
  background: var(--green-soft);
  color: var(--green-dark);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.hero-copy h1,
h2 {
  margin: 0;
  font-size: clamp(2rem, 4.5vw, 4rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
}

.hero-copy p,
.section-subtitle {
  margin: 16px 0 0;
  color: var(--muted);
  font-size: 1.04rem;
  line-height: 1.7;
}

.hero-actions {
  margin-top: 28px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.social-proof {
  margin-top: 26px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.social-proof p {
  margin: 0;
  color: var(--muted);
}

.avatars {
  display: flex;
}

.avatars span {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #2ac082;
  border: 2px solid #f4fbf8;
  margin-left: -6px;
}

.avatars span:first-child {
  margin-left: 0;
}

.hero-visual {
  position: relative;
  min-height: 430px;
}

.hero-shape {
  position: absolute;
  inset: 24px -8px -18px 20px;
  background: #b3ebd2;
  border-radius: 58px;
  transform: rotate(4deg);
}

.hero-visual img {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 430px;
  object-fit: cover;
  border-radius: 56px;
  box-shadow: 0 18px 46px rgba(9, 26, 48, 0.2);
}

.floating-card {
  position: absolute;
  z-index: 2;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 16px;
  padding: 12px 16px;
  font-weight: 700;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.16);
}

.floating-card.top {
  left: -20px;
  top: 150px;
}

.floating-card.bottom {
  right: -16px;
  bottom: 68px;
}

.section-light,
.benefits,
.final-cta {
  padding: 80px 0;
}

.section-light {
  background: #fff;
}

.section-light h2,
.benefits h2,
.testimonials h2,
.final-cta h2 {
  font-size: clamp(1.8rem, 3.4vw, 3.1rem);
  text-align: center;
}

.section-light .section-subtitle,
.final-cta p {
  text-align: center;
  max-width: 700px;
  margin: 16px auto 0;
}

.cards-grid {
  margin-top: 32px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.service-card,
.testimonial-card {
  border-radius: 24px;
  padding: 26px;
  box-shadow: 0 12px 24px rgba(10, 33, 54, 0.09);
}

.service-card {
  background: #ffffff;
  border: 1px solid var(--line);
}

.service-card h3 {
  margin: 0;
  font-size: 1.45rem;
}

.service-card p {
  margin: 12px 0 16px;
  color: var(--muted);
}

.service-card a {
  color: var(--green);
  font-weight: 700;
  text-decoration: none;
}

.benefits-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
  align-items: center;
}

.check-list {
  margin: 24px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.check-list li {
  color: var(--muted);
  padding-left: 28px;
  position: relative;
}

.check-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  top: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #c8efdf;
  color: var(--green-dark);
  font-weight: 800;
  font-size: 0.76rem;
}

.mosaic {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.mosaic img {
  width: 100%;
  height: 190px;
  object-fit: cover;
  border-radius: 24px;
}

.testimonials {
  background: linear-gradient(180deg, #14ad68 0%, #18b96d 100%);
  padding-bottom: 92px;
}

.section-tag-light {
  color: #dcfff0;
  background: rgba(255, 255, 255, 0.16);
}

.testimonials h2 {
  color: #f0fff7;
  text-align: center;
}

.testimonial-card {
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ebfff6;
}

.testimonial-card p {
  margin: 0 0 18px;
  line-height: 1.7;
}

.testimonial-card strong {
  display: block;
}

.testimonial-card span {
  color: #cbf8e5;
  font-size: 0.93rem;
}

.testimonials .cards-grid {
  margin-bottom: 14px;
}

.final-cta {
  background: #f6fbf8;
}

.final-cta-inner {
  text-align: center;
}

.final-cta .btn {
  margin-top: 24px;
}

.footer {
  background: #081833;
  color: #d6e6ff;
  padding: 54px 0 20px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 18px;
}

.footer .light {
  color: #fff;
}

.footer p,
.footer li {
  color: #a8bfdc;
}

.footer h4 {
  margin: 0 0 10px;
  color: #fff;
}

.footer ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.footer-bottom {
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  text-align: center;
  color: #8ea8ca;
}

@media (max-width: 1020px) {
  .menu-links {
    display: none;
  }

  .hero-grid,
  .benefits-grid,
  .cards-grid,
  .footer-grid {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    min-height: 320px;
  }

  .hero-visual img {
    min-height: 320px;
  }

  .floating-card.top,
  .floating-card.bottom {
    position: static;
    margin-top: 10px;
    display: inline-block;
  }

  .check-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .container {
    width: min(1240px, calc(100% - 28px));
  }

  .brand-name {
    font-size: 1.6rem;
  }

  .topbar .btn {
    min-height: 40px;
    padding: 0 14px;
    font-size: 0.82rem;
  }
}
</style>
