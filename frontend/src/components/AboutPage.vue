<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="about-page">
    <header class="topbar">
      <img alt="Logo" class="logo" src="../assets/logo.png" />
      <p class="hackathon-badge">Built for Hackathon 2026</p>
    </header>
    <main class="content">
      <h1 class="page-title">Sobre o NutriVentures</h1>
      <p class="intro">
        O NutriVentures é o teu assistente de cozinha pessoal, concebido para te ajudar a comer de forma mais saudável sem sacrificar o sabor ou a conveniência. A nossa missão é tornar a alimentação saudável acessível, divertida e personalizada para todos.
      </p>

      <section class="feature-section">
        <h2 class="section-title">O Que Fazemos?</h2>
        <div class="feature-list">
          <div class="feature-item">
            <h3>Transformação de Refeições</h3>
            <p>Desejas uma lasanha, mas estás preocupado com as calorias? Diz-nos o que queres comer e a nós entregamos-te uma versão mais saudável da receita, ajustada às tuas necessidades calóricas, sem comprometer o sabor.</p>
          </div>
          <div class="feature-item">
            <h3>Sugestões Locais Inteligentes</h3>
            <p>Depois de escolheres a tua receita, mostramos-te os supermercados mais próximos onde podes comprar os ingredientes. Se não te apetecer cozinhar, também sugerimos restaurantes de takeaway que oferecem opções saudáveis semelhantes ou supermercados com refeições já prontas.</p>
          </div>
          <div class="feature-item">
            <h3>"Assalto ao Frigorífico"</h3>
            <p>Não sabes o que fazer com os ingredientes que tens em casa? Tira uma foto ao interior do teu frigorífico ou dá-nos uma lista de ingredientes e nós sugerimos-te receitas deliciosas e saudáveis que podes fazer com o que já tens.</p>
          </div>
          <div class="feature-item">
            <h3>Acompanhamento de Objetivos</h3>
            <p>Define os teus objetivos de saúde, como perder peso, manter ou ganhar massa muscular, e o NutriVentures ajuda-te a manter o rumo, sugerindo refeições que se alinham com as tuas metas diárias de calorias e macronutrientes.</p>
          </div>
        </div>
      </section>

      <section class="team-section">
        <h2 class="section-title">A Nossa Equipa</h2>
        <p>Somos uma equipa de entusiastas da tecnologia e da nutrição, unidos por uma paixão por resolver problemas do dia-a-dia. O NutriVentures nasceu num hackathon, com o objetivo de criar uma ferramenta que realmente fizesse a diferença na vida das pessoas.</p>
      </section>
    </main>
    <footer class="footer">
      <button class="btn btn-secondary" @click="goHome">
        &larr; Voltar à Página Inicial
      </button>
    </footer>
  </div>
</template>

<style scoped>
.about-page {
  --bg-main: #f4fbf8;
  --text-main: #13293d;
  --text-muted: #3b566d;
  --accent: #0f766e;
  --line: #d7e7e0;
  
  min-height: 100vh;
  background-color: var(--bg-main);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
  color: var(--text-main);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 24px;
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
  background: rgba(255, 255, 255, 0.75);
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

.btn-secondary {
  border: 1px solid var(--line);
  background: var(--bg-soft, #ffffff);
  color: var(--text-main);
}

.content {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 24px 48px;
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  text-align: center;
  margin-bottom: 16px;
  color: var(--text-main);
}

.intro {
  font-size: 1.15rem;
  line-height: 1.7;
  text-align: center;
  max-width: 70ch;
  margin: 0 auto 48px;
  color: var(--text-muted);
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 24px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--accent);
  display: inline-block;
}

.feature-list {
  display: grid;
  gap: 28px;
}

.feature-item h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.feature-item p {
  color: var(--text-muted);
  line-height: 1.6;
}

.team-section {
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
}

.team-section p {
  color: var(--text-muted);
  line-height: 1.6;
}

.footer {
  text-align: center;
  padding-bottom: 48px;
}
</style>
