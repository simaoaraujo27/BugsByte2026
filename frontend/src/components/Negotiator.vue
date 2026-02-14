<script setup>
import { ref } from 'vue';
import { auth } from '@/auth';

const emit = defineEmits(['choice']);

// Views: 'landing', 'text_input', 'vision_input', 'mood_select', 'mood_analysis', 'recipe', 'rejection'
const activeView = ref('landing');
const loading = ref(false);
const error = ref(null);

const craving = ref('');
const selectedMood = ref('');
const moodAnalysis = ref(null);
const recipeResult = ref(null);
const detectedIngredients = ref([]);

// Vision
const fileInput = ref(null);
const previewImage = ref(null);

const moods = [
  { id: 'stressado', label: 'Stressado(a)', icon: '🌋' },
  { id: 'aborrecido', label: 'Aborrecido(a)', icon: '☁️' },
  { id: 'recompensa', label: 'Recompensa', icon: '💎' },
  { id: 'social', label: 'Social', icon: '🥂' },
  { id: 'hormonal', label: 'Hormonal', icon: '🌙' },
  { id: 'fome fisica', label: 'Fome Real', icon: '🥑' },
  { id: 'outro', label: 'Outro', icon: '✨' }
];

// --- TEXT FLOW ---
const generateTextRecipe = async () => {
  if (!craving.value.trim()) return;
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch('http://localhost:8000/negotiator/negotiate', {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ craving: craving.value, target_calories: 600 })
    });

    if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Erro na negociação");
    }
    const data = await response.json();
    recipeResult.value = data;
    activeView.value = data.recipe ? 'recipe' : 'rejection';
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

// --- MOOD FLOW ---
const selectMood = async (moodId) => {
  selectedMood.value = moodId;
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch('http://localhost:8000/negotiator/analyze-mood', {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ mood: moodId, craving: 'geral' })
    });

    if (!response.ok) throw new Error("Erro na análise emocional");
    moodAnalysis.value = await response.json();
    activeView.value = 'mood_analysis';
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

const generateMoodRecipe = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch('http://localhost:8000/negotiator/negotiate', {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ craving: 'Menu Saudável', mood: selectedMood.value })
    });

    if (!response.ok) throw new Error("Erro ao gerar receita");
    recipeResult.value = await response.json();
    activeView.value = 'recipe';
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

// --- VISION FLOW ---
const triggerFileSelect = () => fileInput.value.click();
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => previewImage.value = e.target.result;
    reader.readAsDataURL(file);
    uploadAndAnalyze(file);
  }
};

const uploadAndAnalyze = async (file) => {
  loading.value = true;
  error.value = null;
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/vision/analyze', {
      method: 'POST',
      headers: auth.getAuthHeaders(false),
      body: formData,
    });

    if (!response.ok) throw new Error('Erro ao analisar a imagem');
    const data = await response.json();
    detectedIngredients.value = data.detected_ingredients;
    recipeResult.value = { recipe: data.recipe, message: data.message };
    activeView.value = 'recipe';
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

// --- SHARED ---
const goToIngredients = () => {
  emit('choice', {
    type: 'diy',
    ingredients: recipeResult.value.recipe.ingredients.join(',')
  });
};

const reset = () => {
  activeView.value = 'landing';
  craving.value = '';
  selectedMood.value = '';
  moodAnalysis.value = null;
  recipeResult.value = null;
  previewImage.value = null;
  detectedIngredients.value = [];
  error.value = null;
};
</script>

<template>
  <div class="negotiator-container">
    
    <!-- LANDING -->
    <div v-if="activeView === 'landing'" class="view-wrapper fade-in">
      <div class="hero-header">
        <h1 class="tight-title">Chef Inteligente</h1>
        <p class="small-subtitle">A tua jornada para uma alimentação consciente começa aqui.</p>
      </div>
      
      <div class="compact-grid">
        <div class="slim-card" @click="activeView = 'text_input'">
          <div class="s-icon">✍️</div>
          <h3>Desejo</h3>
          <p>Adapta o que te apetece para uma versão saudável.</p>
          <button class="s-btn">Começar</button>
        </div>

        <div class="slim-card highlight" @click="activeView = 'mood_select'">
          <div class="s-icon">🧠</div>
          <h3>Estado de Alma</h3>
          <p>Refeições alinhadas com o teu humor atual.</p>
          <button class="s-btn">Fazer Check-in</button>
        </div>

        <div class="slim-card" @click="activeView = 'vision_input'">
          <div class="s-icon">📸</div>
          <h3>O que tenho?</h3>
          <p>Gera receitas através de uma foto dos teus ingredientes.</p>
          <button class="s-btn">Digitalizar</button>
        </div>
      </div>
    </div>

    <!-- SUBMENU: Text Input -->
    <div v-if="activeView === 'text_input'" class="view-wrapper centered-content fade-in">
      <div class="header-minimal">
        <h2>O que te apetece comer?</h2>
      </div>

      <div class="premium-input-wrap">
        <input v-model="craving" type="text" placeholder="Ex: Risotto saudável..." @keyup.enter="generateTextRecipe" autofocus />
        <button @click="generateTextRecipe" :disabled="loading" class="btn-primary-slim">
          {{ loading ? '...' : 'Ir' }}
        </button>
      </div>

      <div class="chips-container-centered">
        <button @click="craving = 'Hambúrguer'; generateTextRecipe()" class="mini-chip">🍔 Hambúrguer</button>
        <button @click="craving = 'Lasanha'; generateTextRecipe()" class="mini-chip">🍝 Lasanha</button>
        <button @click="craving = 'Sushi'; generateTextRecipe()" class="mini-chip">🍣 Sushi</button>
      </div>

      <div v-if="error" class="error-msg-slim">{{ error }}</div>
      <button @click="reset" class="btn-formatted-back">← Voltar</button>
    </div>

    <!-- SUBMENU: Mood Selection -->
    <div v-if="activeView === 'mood_select'" class="view-wrapper centered-content fade-in">
      <div class="header-minimal">
        <h2>Como te sentes agora?</h2>
      </div>

      <div class="mood-pill-grid-centered">
        <button v-for="mood in moods" :key="mood.id" @click="selectMood(mood.id)" class="mood-pill-item" :disabled="loading">
          <span class="p-emoji">{{ mood.icon }}</span>
          <span class="p-label">{{ mood.label }}</span>
        </button>
      </div>
      
      <div v-if="loading" class="spinner-container-v2"><div class="spinner-dot"></div></div>
      <button @click="reset" class="btn-formatted-back">← Voltar</button>
    </div>

    <!-- SUBMENU: Vision Input -->
    <div v-if="activeView === 'vision_input'" class="view-wrapper centered-content fade-in">
      <div class="header-minimal">
        <h2>Ingredientes por Foto</h2>
      </div>

      <div class="large-upload-zone" @click="triggerFileSelect">
        <div v-if="!loading" class="u-box-large">
          <div class="u-icon-anim-large">📸</div>
          <h3>Clica para carregar ou tirar foto</h3>
          <p>O Chef vai detetar todos os teus ingredientes</p>
        </div>
        <div v-else class="u-status-large">
          <div class="spinner-dot"></div>
          <p>O Chef está a analisar os ingredientes...</p>
        </div>
        <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleFileChange" />
      </div>
      <button v-if="!loading" @click="reset" class="btn-formatted-back">← Voltar</button>
    </div>

    <!-- VIEW: Mood Analysis -->
    <div v-if="activeView === 'mood_analysis' && moodAnalysis" class="view-wrapper fade-in">
      <div class="analysis-card-refined">
        <header class="an-head">
          <span class="an-tag">{{ moodAnalysis.mood_type }}</span>
          <h3>Análise do Assistente</h3>
        </header>
        
        <div class="an-content">
          <p class="an-text-empathy">"{{ moodAnalysis.empathy_message }}"</p>
          
          <div class="an-info-flex">
            <div class="an-box">
              <label>Mente</label>
              <p>{{ moodAnalysis.explanation }}</p>
            </div>
            <div class="an-box special">
              <label>Sugestão</label>
              <p>{{ moodAnalysis.eating_strategy }}</p>
            </div>
          </div>
        </div>

        <footer class="an-footer-v2">
          <button @click="generateMoodRecipe" :disabled="loading" class="btn-action-main">
            {{ loading ? '...' : 'Gerar Receita Ideal' }}
          </button>
          <button @click="reset" class="btn-formatted-back">← Voltar</button>
        </footer>
      </div>
    </div>

    <!-- VIEW: Final Recipe -->
    <div v-if="activeView === 'recipe' && recipeResult" class="recipe-view-refined fade-in">
      <div v-if="detectedIngredients.length > 0" class="vision-indicator">
        🔎 Detetado: {{ detectedIngredients.join(', ') }}
      </div>

      <div class="recipe-main-body">
        <header class="rec-head">
          <div class="rec-cal-badge">{{ recipeResult.recipe.calories }} kcal</div>
          <h2 class="rec-title-v2">{{ recipeResult.recipe.title }}</h2>
          <p class="rec-chef-note">"{{ recipeResult.message }}"</p>
        </header>

        <div class="rec-details-grid">
          <section class="rec-section">
            <h4>🛒 Ingredientes</h4>
            <ul class="rec-ul">
              <li v-for="ing in recipeResult.recipe.ingredients" :key="ing">{{ ing }}</li>
            </ul>
            <button @click="goToIngredients" class="btn-map-slim">Localizar Lojas 📍</button>
          </section>

          <section class="rec-section">
            <h4>👨‍🍳 Preparação</h4>
            <div class="rec-steps-v2">
              <div v-for="(step, i) in recipeResult.recipe.steps" :key="i" class="rec-step-v2">
                <div class="rec-idx">{{ i + 1 }}</div>
                <div class="rec-txt">{{ step }}</div>
              </div>
            </div>
          </section>
        </div>

        <div class="rec-final-action">
          <button @click="reset" class="btn-formatted-back">← Voltar</button>
        </div>
      </div>
    </div>

    <!-- VIEW: Rejection -->
    <div v-if="activeView === 'rejection'" class="view-wrapper fade-in">
      <div class="rejection-card-v2">
        <div class="rej-icon-v2">🚫</div>
        <h3>Pedido Inválido</h3>
        <p>{{ recipeResult?.message }}</p>
        <button @click="reset" class="btn-primary-slim">← Voltar</button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.negotiator-container { 
  max-width: 1000px; 
  margin: 0 auto; 
  font-family: 'Sora', sans-serif; 
  min-height: 600px; 
  display: flex;
  flex-direction: column;
}
.fade-in { animation: fadeIn 0.4s ease-out both; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.view-wrapper { width: 100%; display: flex; flex-direction: column; align-items: center; }
.centered-content { justify-content: center; text-align: center; padding: 40px 0; }

/* Headers */
.hero-header { text-align: center; padding: 40px 0 30px; }
.tight-title { font-size: 3rem; font-weight: 900; color: #e74c3c; margin-bottom: 8px; }
.small-subtitle { color: var(--text-muted); font-size: 1.1rem; }
.header-minimal { margin-bottom: 30px; }
.header-minimal h2 { font-size: 2rem; font-weight: 800; color: var(--text-main); }

/* Landing Grid */
.compact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; width: 100%; }
.slim-card { background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 32px; padding: 40px 24px; cursor: pointer; transition: all 0.3s; text-align: center; }
.slim-card:hover { border-color: #e74c3c; transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
.slim-card.highlight { border-color: #07a374; border-width: 2px; }
.s-icon { font-size: 3.5rem; margin-bottom: 24px; }
.slim-card h3 { font-size: 1.5rem; margin-bottom: 12px; color: var(--text-main); }
.slim-card p { font-size: 0.95rem; color: var(--text-muted); margin-bottom: 32px; line-height: 1.6; }
.s-btn { background: var(--bg-main); border: 1px solid var(--line); padding: 10px 24px; border-radius: 12px; font-weight: 800; color: var(--text-main); font-size: 0.8rem; text-transform: uppercase; cursor: pointer; }

/* Inputs & Suggestion Chips */
.premium-input-wrap { display: flex; background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 24px; padding: 8px; width: 100%; max-width: 650px; box-shadow: 0 15px 40px rgba(0,0,0,0.06); }
.premium-input-wrap input { flex: 1; border: none; padding: 16px 24px; background: transparent; color: var(--text-main); font-size: 1.2rem; outline: none; }
.btn-primary-slim { background: #e74c3c; color: white; border: none; padding: 0 32px; border-radius: 16px; font-weight: 800; cursor: pointer; }

.chips-container-centered { display: flex; gap: 12px; justify-content: center; margin-top: 24px; flex-wrap: wrap; }
.mini-chip { background: var(--bg-elevated); border: 1px solid var(--line); padding: 10px 20px; border-radius: 25px; font-size: 0.9rem; font-weight: 700; color: var(--text-main); cursor: pointer; transition: 0.2s; }
.mini-chip:hover { border-color: #e74c3c; background: var(--bg-main); }

/* Mood Grid */
.mood-pill-grid-centered { display: flex; flex-wrap: wrap; gap: 14px; justify-content: center; max-width: 850px; margin: 0 auto; }
.mood-pill-item { background: var(--bg-elevated); border: 1px solid var(--line); padding: 16px 28px; border-radius: 40px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: 0.3s; }
.mood-pill-item:hover { border-color: #e74c3c; transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.05); }
.p-emoji { font-size: 1.6rem; }
.p-label { font-weight: 800; color: var(--text-main); font-size: 1rem; }

/* Vision Upload LARGE */
.large-upload-zone { background: var(--bg-elevated); border: 3px dashed var(--line); border-radius: 40px; padding: 100px 60px; text-align: center; cursor: pointer; width: 100%; max-width: 700px; transition: 0.3s; }
.large-upload-zone:hover { border-color: #07a374; background: var(--bg-main); }
.u-icon-anim-large { font-size: 6rem; margin-bottom: 24px; transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.large-upload-zone:hover .u-icon-anim-large { transform: scale(1.15) rotate(5deg); }
.u-box-large h3 { font-size: 1.8rem; color: var(--text-main); margin-bottom: 12px; }
.u-box-large p { color: var(--text-muted); font-size: 1.1rem; }

/* Formatted Back Button */
.btn-formatted-back { 
  background: var(--bg-elevated); border: 1px solid var(--line); padding: 12px 32px; border-radius: 16px;
  color: var(--text-main); font-weight: 800; font-size: 1rem; cursor: pointer; transition: all 0.3s; 
  margin-top: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.btn-formatted-back:hover { background: var(--bg-main); border-color: #e74c3c; transform: translateX(-4px); }

/* Analysis Card */
.analysis-card-refined { background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 32px; padding: 50px; width: 100%; box-shadow: 0 25px 60px rgba(0,0,0,0.06); }
.an-tag { background: var(--menu-highlight-bg); color: var(--menu-highlight-text); padding: 6px 16px; border-radius: 12px; font-size: 0.8rem; font-weight: 900; text-transform: uppercase; }
.an-text-empathy { font-size: 1.5rem; font-style: italic; color: var(--text-main); margin: 32px 0; border-left: 5px solid #e74c3c; padding-left: 24px; line-height: 1.5; }
.an-info-flex { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-bottom: 40px; }
.an-box.special { background: var(--menu-active-bg); padding: 24px; border-radius: 20px; color: var(--menu-active-text); }
.btn-action-main { background: #11263f; color: white; border: none; padding: 18px 40px; border-radius: 16px; font-weight: 800; cursor: pointer; font-size: 1.1rem; }

/* Recipe Details */
.recipe-view-refined { background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 40px; overflow: hidden; width: 100%; box-shadow: 0 30px 80px rgba(0,0,0,0.1); }
.rec-head { padding: 60px 40px; text-align: center; background: linear-gradient(135deg, var(--bg-main) 0%, var(--bg-elevated) 100%); border-bottom: 1px solid var(--line); }
.rec-cal-badge { background: #07a374; color: white; padding: 8px 20px; border-radius: 12px; font-weight: 900; margin-bottom: 24px; display: inline-block; }
.rec-title-v2 { font-size: 3rem; font-weight: 950; color: var(--text-main); margin-bottom: 16px; letter-spacing: -0.02em; }
.rec-details-grid { display: grid; grid-template-columns: 350px 1fr; gap: 60px; padding: 60px; }
.rec-section h4 { font-size: 1.4rem; font-weight: 900; margin-bottom: 32px; color: var(--text-main); text-transform: uppercase; }
.rec-idx { background: #11263f; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: 900; }
.btn-map-slim { width: 100%; margin-top: 32px; padding: 18px; background: var(--menu-active-bg); color: var(--menu-active-text); border: 2px dashed var(--menu-active-text); border-radius: 16px; font-weight: 900; cursor: pointer; }

/* Utils */
.spinner-dot { width: 50px; height: 50px; border: 5px solid rgba(0,0,0,0.05); border-top-color: #e74c3c; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .rec-details-grid, .an-info-flex { grid-template-columns: 1fr; }
  .rec-title-v2 { font-size: 2rem; }
}
</style>