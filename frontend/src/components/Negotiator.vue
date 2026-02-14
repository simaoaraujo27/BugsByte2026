<script setup>
import { ref } from 'vue';
import { auth } from '@/auth';

const emit = defineEmits(['choice']);

// Views: 'landing', 'text_input', 'vision_input', 'mood_select', 'mood_analysis', 'recipe', 'rejection'
const activeView = ref('landing');
const loading = ref(false);
const saving = ref(false);
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

const saveRecipe = async () => {
  if (!recipeResult.value || !recipeResult.value.recipe) return;
  saving.value = true;

  try {
    const recipeData = {
      name: recipeResult.value.recipe.title,
      ingredients: recipeResult.value.recipe.ingredients.join(', '),
      instructions: recipeResult.value.recipe.steps.join('\n')
    };

    const createResponse = await fetch('http://localhost:8000/recipes/', {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify(recipeData)
    });

    if (!createResponse.ok) throw new Error('Falha ao criar receita');
    const createdRecipe = await createResponse.json();

    const favResponse = await fetch(`http://localhost:8000/users/me/favorites/recipes/${createdRecipe.id}`, {
      method: 'POST',
      headers: auth.getAuthHeaders()
    });

    if (!favResponse.ok) throw new Error('Falha ao adicionar aos favoritos');

    alert('Receita guardada com sucesso!');
  } catch (err) {
    console.error('Error saving recipe:', err);
    alert('Erro ao guardar a receita.');
  } finally {
    saving.value = false;
  }
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
    
    <!-- MAIN LANDING -->
    <div v-if="activeView === 'landing'" class="view-wrapper fade-in">
      <div class="hero-header">
        <h1 class="tight-title">Chef Inteligente</h1>
        <p class="small-subtitle">Decisões alimentares conscientes e personalizadas.</p>
      </div>
      
      <div class="premium-cards-grid">
        <div class="p-card" @click="activeView = 'text_input'">
          <div class="p-card-icon">✍️</div>
          <h3>Desejo Específico</h3>
          <p>Converte o que te apetece numa versão saudável e gourmet.</p>
          <button class="p-card-btn">Começar</button>
        </div>

        <div class="p-card featured" @click="activeView = 'mood_select'">
          <div class="p-card-icon">🕯️</div>
          <h3>Estado de Alma</h3>
          <p>Sintoniza a tua nutrição com as tuas emoções do momento.</p>
          <button class="p-card-btn">Check-in</button>
        </div>

        <div class="p-card" @click="activeView = 'vision_input'">
          <div class="p-card-icon">📸</div>
          <h3>Visão do Chef</h3>
          <p>Cria magia culinária a partir dos teus ingredientes atuais.</p>
          <button class="p-card-btn">Digitalizar</button>
        </div>
      </div>
    </div>

    <!-- SUBMENU: Text Input -->
    <div v-if="activeView === 'text_input'" class="view-wrapper centered-view fade-in">
      <div class="hero-header-small">
        <div class="v-icon-top">🍔</div>
        <h2 class="title-bold">O QUE TE APETECE?</h2>
        <p class="subtitle-muted">O Chef vai negociar uma alternativa irresistível e saudável.</p>
      </div>

      <div class="search-box-premium">
        <input v-model="craving" type="text" placeholder="Ex: Risotto de cogumelos..." @keyup.enter="generateTextRecipe" autofocus />
        <button @click="generateTextRecipe" :disabled="loading" class="btn-primary-action">
          {{ loading ? '...' : 'Negociar' }}
        </button>
      </div>

      <div class="suggestion-pills">
        <span>Sugestões:</span>
        <button @click="craving = 'Hambúrguer'; generateTextRecipe()" class="s-pill">🍔 Hambúrguer</button>
        <button @click="craving = 'Lasanha'; generateTextRecipe()" class="s-pill">🍝 Lasanha</button>
        <button @click="craving = 'Sushi'; generateTextRecipe()" class="s-pill">🍣 Sushi</button>
        <button @click="craving = 'Pizza'; generateTextRecipe()" class="s-pill">🍕 Pizza</button>
      </div>

      <button @click="reset" class="btn-formatted-back">← Voltar</button>
    </div>

    <!-- SUBMENU: Mood Selection -->
    <div v-if="activeView === 'mood_select'" class="view-wrapper centered-view fade-in">
      <div class="hero-header-small">
        <div class="v-icon-top">🧘</div>
        <h2 class="title-bold">COMO TE SENTES AGORA?</h2>
        <p class="subtitle-muted">A consciência emocional é o segredo para uma nutrição de sucesso.</p>
      </div>

      <div class="mood-pill-container-centered">
        <button v-for="mood in moods" :key="mood.id" @click="selectMood(mood.id)" class="mood-pill-btn" :disabled="loading">
          <span class="m-pill-emoji">{{ mood.icon }}</span>
          <span class="m-pill-label">{{ mood.label }}</span>
        </button>
      </div>
      
      <div v-if="loading" class="spinner-wrap"><div class="spinner-dot"></div></div>
      <button @click="reset" class="btn-formatted-back">← Voltar</button>
    </div>

    <!-- SUBMENU: Vision Input -->
    <div v-if="activeView === 'vision_input'" class="view-wrapper centered-view fade-in">
      <div class="hero-header-small">
        <div class="v-icon-top">🖼️</div>
        <h2 class="title-bold">VISÃO DO FRIGORÍFICO</h2>
        <p class="subtitle-muted">O reconhecimento visual irá ditar a ementa de hoje.</p>
      </div>

      <div class="premium-upload-zone" @click="triggerFileSelect">
        <div v-if="!loading" class="u-content-box">
          <div class="u-icon-pulse">📸</div>
          <h3>Clica para carregar ou tirar foto</h3>
          <p>O Chef vai detetar todos os teus ingredientes</p>
        </div>
        <div v-else class="u-loading-box">
          <div class="spinner-dot"></div>
          <p>A olhar para os ingredientes...</p>
        </div>
        <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleFileChange" />
      </div>
      <button v-if="!loading" @click="reset" class="btn-formatted-back">← Voltar</button>
    </div>

    <!-- VIEW: Mood Analysis Result -->
    <div v-if="activeView === 'mood_analysis' && moodAnalysis" class="view-wrapper centered-view fade-in">
      <div class="analysis-glass-card">
        <header class="an-header">
          <span class="an-badge">{{ moodAnalysis.mood_type }}</span>
          <h2>Análise do Assistente</h2>
        </header>
        <div class="an-body">
          <p class="an-empathy-quote">"{{ moodAnalysis.empathy_message }}"</p>
          <div class="an-details-grid">
            <div class="an-detail-item">
              <label>Contexto Mental</label>
              <p>{{ moodAnalysis.explanation }}</p>
            </div>
            <div class="an-detail-item highlight">
              <label>Protocolo Sugerido</label>
              <p>{{ moodAnalysis.eating_strategy }}</p>
            </div>
          </div>
        </div>
        <footer class="an-footer">
          <button @click="generateMoodRecipe" :disabled="loading" class="btn-reveal-recipe">
            {{ loading ? '...' : 'Revelar Receita Ideal 🥂' }}
          </button>
          <div class="an-footer-actions">
            <button @click="reset" class="btn-formatted-back">← Voltar</button>
          </div>
        </footer>
      </div>
    </div>

    <!-- VIEW: Recipe Result -->
    <div v-if="activeView === 'recipe' && recipeResult" class="view-wrapper fade-in">
      <div class="premium-recipe-display">
        <div v-if="detectedIngredients.length > 0" class="vision-bar-tags">
          <span>🔎 Detetado:</span> {{ detectedIngredients.join(', ') }}
        </div>
        <header class="rec-header-premium">
          <div class="rec-header-badge-container">
            <div class="rec-cal-badge-pill">{{ recipeResult.recipe.calories }} kcal</div>
          </div>
          <h2 class="rec-title-bold">{{ recipeResult.recipe.title }}</h2>
          <p class="rec-chef-message">"{{ recipeResult.message }}"</p>
        </header>
        <div class="rec-content-grid-premium">
          <section class="rec-col">
            <h4>🛒 Ingredientes</h4>
            <ul class="rec-list-styled">
              <li v-for="ing in recipeResult.recipe.ingredients" :key="ing">{{ ing }}</li>
            </ul>
            <button @click="goToIngredients" class="btn-map-link-premium">Localizar Lojas 📍</button>
          </section>
          <section class="rec-col">
            <h4>👨‍🍳 Preparação</h4>
            <div class="rec-timeline-premium">
              <div v-for="(step, i) in recipeResult.recipe.steps" :key="i" class="rec-step-premium">
                <div class="rec-step-num">{{ i + 1 }}</div>
                <div class="rec-step-txt">{{ step }}</div>
              </div>
            </div>
          </section>
        </div>

        <div class="rec-final-action">
          <button @click="reset" class="btn-formatted-back">← Voltar</button>
          <button @click="saveRecipe" class="btn-save" :disabled="saving">
            {{ saving ? 'A guardar...' : '❤️ Guardar Receita' }}
          </button>
        </div>
      </div>
    </div>

    <!-- VIEW: Rejection -->
    <div v-if="activeView === 'rejection'" class="view-wrapper centered-view fade-in">
      <div class="rejection-card-premium">
        <div class="rej-icon-large">🚫</div>
        <h2>Aviso do Chef</h2>
        <p>{{ recipeResult?.message }}</p>
        <button @click="reset" class="btn-formatted-back">← Voltar</button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.negotiator-container { 
  max-width: 1000px; margin: 0 auto; font-family: 'Sora', sans-serif; 
  min-height: 700px; display: flex; flex-direction: column;
}
.fade-in { animation: fadeIn 0.5s ease-out both; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

.view-wrapper { width: 100%; display: flex; flex-direction: column; align-items: center; }
.centered-view { text-align: center; padding: 40px 0; }

/* 1. Main Landing Styling */
.hero-header { text-align: center; padding: 60px 0 40px; }
.tight-title { font-size: 3rem; font-weight: 900; color: #e74c3c; margin-bottom: 8px; }
.small-subtitle { color: var(--text-muted); font-size: 1.1rem; }

.premium-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; width: 100%; padding: 20px; }
.p-card { background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 32px; padding: 40px 24px; text-align: center; cursor: pointer; transition: all 0.3s; position: relative; }
.p-card:hover { border-color: #e74c3c; transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.05); }
.p-card.featured { border-color: #07a374; border-width: 2px; }
.p-card-icon { font-size: 3.5rem; margin-bottom: 24px; }
.p-card h3 { font-size: 1.4rem; font-weight: 800; color: var(--text-main); margin-bottom: 12px; }
.p-card p { font-size: 0.95rem; color: var(--text-muted); margin-bottom: 32px; line-height: 1.6; }
.p-card-btn { background: var(--bg-main); border: 1px solid var(--line); padding: 10px 24px; border-radius: 12px; font-weight: 800; color: var(--text-main); font-size: 0.8rem; text-transform: uppercase; cursor: pointer; }

/* 2. Submenus Shared Styling */
.hero-header-small { margin-bottom: 40px; }
.v-icon-top { font-size: 4rem; margin-bottom: 16px; }
.title-bold { font-size: 2.2rem; font-weight: 950; color: var(--text-main); margin-bottom: 12px; }
.subtitle-muted { color: var(--text-muted); font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.5; }

/* 3. Text Input View */
.search-box-premium { 
  display: flex; background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 24px; padding: 8px; 
  width: 100%; max-width: 700px; box-shadow: 0 15px 40px rgba(0,0,0,0.06); margin-bottom: 24px;
}
.search-box-premium input { flex: 1; border: none; padding: 16px 24px; background: transparent; color: var(--text-main); font-size: 1.2rem; outline: none; }
.btn-primary-action { background: #e74c3c; color: white; border: none; padding: 0 32px; border-radius: 16px; font-weight: 800; cursor: pointer; transition: 0.3s; }

.suggestion-pills { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px; align-items: center; color: var(--text-muted); }
.s-pill { background: var(--bg-elevated); border: 1px solid var(--line); padding: 8px 20px; border-radius: 25px; font-size: 0.9rem; font-weight: 700; color: var(--text-main); cursor: pointer; transition: 0.2s; }
.s-pill:hover { border-color: #e74c3c; background: var(--bg-main); }

/* 4. Mood Selection View */
.mood-pill-container-centered { display: flex; flex-wrap: wrap; gap: 14px; justify-content: center; max-width: 850px; margin: 0 auto; }
.mood-pill-btn { background: var(--bg-elevated); border: 1px solid var(--line); padding: 16px 28px; border-radius: 40px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: 0.3s; }
.mood-pill-btn:hover { border-color: #e74c3c; transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.05); }
.m-pill-emoji { font-size: 1.6rem; }
.m-pill-label { font-weight: 800; color: var(--text-main); font-size: 1rem; }

/* 5. Vision Upload View */
.premium-upload-zone { background: var(--bg-elevated); border: 3px dashed var(--line); border-radius: 40px; padding: 100px 60px; text-align: center; cursor: pointer; width: 100%; max-width: 700px; transition: 0.3s; }
.premium-upload-zone:hover { border-color: #07a374; background: var(--bg-main); }
.u-icon-pulse { font-size: 6rem; margin-bottom: 24px; animation: pulse 2s infinite; }
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

/* Standard Back Button */
.btn-formatted-back { 
  background: var(--bg-elevated); border: 1px solid var(--line); padding: 12px 32px; border-radius: 16px;
  color: var(--text-main); font-weight: 800; font-size: 1rem; cursor: pointer; transition: all 0.3s; 
  margin-top: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.btn-formatted-back:hover { background: var(--bg-main); border-color: #e74c3c; transform: translateX(-4px); }

/* Analysis Card */
.analysis-glass-card { background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 32px; padding: 50px; width: 100%; box-shadow: 0 25px 60px rgba(0,0,0,0.06); text-align: left; }
.an-badge { background: var(--menu-highlight-bg); color: var(--menu-highlight-text); padding: 6px 16px; border-radius: 12px; font-size: 0.8rem; font-weight: 900; text-transform: uppercase; margin-bottom: 20px; display: inline-block; }
.an-empathy-quote { font-size: 1.5rem; font-style: italic; color: var(--text-main); margin: 32px 0; border-left: 5px solid #e74c3c; padding-left: 24px; line-height: 1.5; }
.an-details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-bottom: 40px; }
.an-detail-item label { color: var(--text-muted); font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; display: block; }
.an-detail-item.highlight { background: var(--menu-active-bg); padding: 20px; border-radius: 20px; color: var(--menu-active-text); }
.btn-reveal-recipe { background: #11263f; color: white; border: none; padding: 18px 40px; border-radius: 16px; font-weight: 800; cursor: pointer; font-size: 1.1rem; }
.an-footer-actions { margin-top: 20px; }

/* Final Recipe Display */
.premium-recipe-display { background: var(--bg-elevated); border: 1px solid var(--line); border-radius: 40px; overflow: hidden; width: 100%; box-shadow: 0 30px 80px rgba(0,0,0,0.1); text-align: left; }
.vision-bar-tags { background: #11263f; color: white; padding: 10px 40px; font-size: 0.85rem; font-weight: 600; }
.rec-header-premium { padding: 60px 60px 40px; text-align: center; background: linear-gradient(135deg, var(--bg-main) 0%, var(--bg-elevated) 100%); border-bottom: 1px solid var(--line); position: relative; }
.rec-header-badge-container { display: flex; justify-content: center; margin-bottom: 24px; }
.rec-cal-badge-pill { background: #07a374; color: white; padding: 8px 24px; border-radius: 20px; font-weight: 900; font-size: 1.2rem; box-shadow: 0 4px 12px rgba(7, 163, 116, 0.2); }
.rec-title-bold { font-size: 3rem; font-weight: 950; color: var(--text-main); margin-bottom: 16px; }
.rec-chef-message { font-style: italic; color: var(--text-muted); font-size: 1.2rem; max-width: 700px; margin: 0 auto; }

.rec-content-grid-premium { display: grid; grid-template-columns: 350px 1fr; gap: 60px; padding: 60px; }
.rec-col h4 { font-size: 1.4rem; font-weight: 900; color: var(--text-main); margin-bottom: 32px; text-transform: uppercase; }
.rec-list-styled { list-style: none; padding: 0; }
.rec-list-styled li { padding: 14px 0; border-bottom: 1px solid var(--line); color: var(--text-main); display: flex; align-items: center; gap: 12px; }
.rec-list-styled li::before { content: "•"; color: #07a374; font-weight: 900; font-size: 1.5rem; }

.rec-timeline-premium { display: flex; flex-direction: column; gap: 32px; }
.rec-step-premium { display: flex; gap: 20px; }
.rec-step-num { background: #11263f; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: 900; }
.rec-step-txt { color: var(--text-main); line-height: 1.7; font-size: 1.05rem; }

.btn-map-link-premium { width: 100%; margin-top: 32px; padding: 18px; background: var(--menu-active-bg); color: var(--menu-active-text); border: 2px dashed var(--menu-active-text); border-radius: 16px; font-weight: 900; cursor: pointer; }
.rec-final-action { padding: 40px; background: var(--bg-main); text-align: center; border-top: 1px solid var(--line); display: flex; justify-content: center; gap: 20px; }
.btn-save { background: #ff5e5e; color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; }

/* Rejection */
.rejection-card-premium { text-align: center; padding: 80px 40px; background: var(--bg-elevated); border-radius: 40px; border: 1px solid var(--line); max-width: 600px; box-shadow: 0 20px 50px rgba(0,0,0,0.05); margin: 0 auto; }
.rej-icon-large { font-size: 5rem; margin-bottom: 32px; }

/* Utils */
.spinner-dot { 
  width: 50px; 
  height: 50px; 
  border: 5px solid rgba(0,0,0,0.05); 
  border-top-color: #e74c3c; 
  border-radius: 50%; 
  animation: spin 0.8s linear infinite; 
  margin: 40px auto 20px; 
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .rec-content-grid-premium, .an-details-grid { grid-template-columns: 1fr; }
  .rec-title-bold { font-size: 2.2rem; }
}
</style>