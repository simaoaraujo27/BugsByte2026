<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/logo.png'

const router = useRouter()

const getInitialTheme = () => {
  if (typeof window === 'undefined') return false
  try {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      return savedTheme === 'dark'
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  } catch (e) {
    return false
  }
}

const isDark = ref(getInitialTheme())

const goToLogin = () => {
  router.push('/login')
}

const toggleDarkMode = (e) => {
  e.preventDefault()
  isDark.value = !isDark.value
}

watch(isDark, (val) => {
  if (val) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}, { immediate: true })
</script>

<template>
  <div class="landing" :class="{ dark: isDark }">
    <header class="topbar">
      <div class="container nav-inner">
        <div class="brand">
          <img :src="logo" alt="NutriVentures" class="brand-logo" />
          <span class="brand-name">NutriVida</span>
        </div>

        <nav class="menu-links" aria-label="Navegação principal">
          <a href="#servicos">Serviços</a>
          <a href="#beneficios">Benefícios</a>
          <a href="#testemunhos">Testemunhos</a>
        </nav>

        <div class="header-actions">
          <button @click="toggleDarkMode" type="button" class="theme-toggle" :aria-label="isDark ? 'Ativar modo claro' : 'Ativar modo escuro'" style="pointer-events: auto;">
            <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-moon"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          </button>
          <button class="btn btn-main" type="button" @click="goToLogin">Agendar Consulta</button>
        </div>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <p class="tag">Nutrição Personalizada</p>
            <h1>Transforme a sua saúde com alimentação consciente</h1>
            <p>
              Planos alimentares ajustados aos seus objetivos, rotina e preferências,
              com acompanhamento contínuo para resultados reais e sustentáveis.
            </p>

            <div class="hero-actions">
              <button class="btn btn-main" type="button" @click="goToLogin">Começar Agora</button>
              <a class="btn btn-ghost" href="#servicos">Saber Mais</a>
            </div>

            <div class="social-proof">
              <div class="avatars" aria-hidden="true">
                <span></span><span></span><span></span><span></span>
              </div>
              <p>+500 clientes satisfeitos</p>
            </div>
          </div>

          <div class="hero-visual" aria-label="Prato saudável">
            <div class="hero-shape"></div>
            <img src="https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=1200&q=80" alt="Prato saudável" />
            <div class="floating-card top">98% satisfação</div>
            <div class="floating-card bottom">30+ consultas/semana</div>
          </div>
        </div>
      </section>

      <section id="servicos" class="section-light">
        <div class="container">
          <p class="section-tag">O que oferecemos</p>
          <h2>Serviços Personalizados</h2>
          <p class="section-subtitle">Cada plano alimentar é adaptado à sua realidade e objetivos.</p>

          <div class="cards-grid">
            <article class="service-card">
              <h3>Planos Alimentares</h3>
              <p>Estratégias nutricionais personalizadas para o seu estilo de vida.</p>
              <a href="#" @click.prevent>Saiba mais</a>
            </article>
            <article class="service-card">
              <h3>Acompanhamento</h3>
              <p>Consultas regulares para monitorizar progresso e ajustar o plano.</p>
              <a href="#" @click.prevent>Saiba mais</a>
            </article>
            <article class="service-card">
              <h3>Suporte Contínuo</h3>
              <p>Orientação prática para manter consistência no dia a dia.</p>
              <a href="#" @click.prevent>Saiba mais</a>
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
          <p class="section-tag section-tag-light">Testemunhos</p>
          <h2>O que dizem os nossos clientes</h2>

          <div class="cards-grid">
            <article class="testimonial-card">
              <p>“Melhorei a minha relação com a comida e perdi peso sem dietas extremas.”</p>
              <strong>Ana Silva</strong>
              <span>Empresária</span>
            </article>
            <article class="testimonial-card">
              <p>“O plano ajustado à minha rotina fez toda a diferença no meu rendimento.”</p>
              <strong>Miguel Costa</strong>
              <span>Atleta amador</span>
            </article>
            <article class="testimonial-card">
              <p>“Finalmente encontrei uma estratégia que consigo manter no dia a dia.”</p>
              <strong>Carla Mendes</strong>
              <span>Mãe de 3</span>
            </article>
          </div>
        </div>
      </section>

      <section class="final-cta">
        <div class="container final-cta-inner">
          <h2>Pronto para começar a sua transformação?</h2>
          <p>Agende a sua primeira consulta e receba um plano adequado às suas metas.</p>
          <button class="btn btn-main" type="button" @click="goToLogin">Agendar Consulta Gratuita</button>
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
          <p>Transformamos hábitos em resultados com acompanhamento personalizado.</p>
        </div>

        <div>
          <h4>Serviços</h4>
          <ul>
            <li>Consultas Online</li>
            <li>Planos Alimentares</li>
            <li>Acompanhamento</li>
          </ul>
        </div>

        <div>
          <h4>Empresa</h4>
          <ul>
            <li>Sobre Nós</li>
            <li>Equipa</li>
            <li>Contactos</li>
          </ul>
        </div>

        <div>
          <h4>Contacto</h4>
          <ul>
            <li>info@nutrivida.pt</li>
            <li>+351 900 000 000</li>
            <li>Lisboa, Portugal</li>
          </ul>
        </div>
      </div>

      <div class="container footer-bottom">
        © 2026 NutriVida. Todos os direitos reservados.
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
  --topbar-bg: rgba(255, 255, 255, 0.92);
  --hero-shape: #b3ebd2;
  --card-bg: rgba(255, 255, 255, 0.96);
  --check-bg: #c8efdf;

  color: var(--text);
  background: var(--bg);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.landing.dark {
  --bg: #0f172a;
  --bg-soft: #1e293b;
  --text: #f8fafc;
  --muted: #94a3b8;
  --line: #334155;
  --green: #10b981;
  --green-dark: #059669;
  --green-soft: #064e3b;
  --topbar-bg: rgba(15, 23, 42, 0.92);
  --hero-shape: #1e293b;
  --card-bg: rgba(30, 41, 59, 0.96);
  --check-bg: #064e3b;
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
  background: var(--topbar-bg);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(8px);
  transition: background-color 0.3s ease, border-color 0.3s ease;
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
  transition: background-color 0.3s;
}

.landing.dark .brand-logo {
  background: var(--line);
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
  transition: color 0.2s;
}

.menu-links a:hover {
  color: var(--text);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 12px;
  transition: background-color 0.2s, color 0.2s;
  border: 1px solid var(--line);
}

.theme-toggle:hover {
  background-color: var(--green-soft);
  color: var(--green);
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
  transition: all 0.2s;
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
  background: var(--bg-soft);
  border: 1px solid var(--green-soft);
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
  border: 2px solid var(--bg);
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
  background: var(--hero-shape);
  border-radius: 58px;
  transform: rotate(4deg);
  transition: background-color 0.3s;
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
  background: var(--card-bg);
  color: var(--text);
  border-radius: 16px;
  padding: 12px 16px;
  font-weight: 700;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.16);
  transition: background-color 0.3s;
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
  background: var(--bg-soft);
  transition: background-color 0.3s;
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
  transition: all 0.3s;
}

.service-card {
  background: var(--bg-soft);
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
  background: var(--check-bg);
  color: var(--green-dark);
  font-weight: 800;
  font-size: 0.76rem;
  transition: background-color 0.3s;
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
  background: var(--bg);
  transition: background-color 0.3s;
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
