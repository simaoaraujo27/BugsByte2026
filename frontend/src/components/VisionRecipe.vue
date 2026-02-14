<script setup>
import { ref } from 'vue';

const fileInput = ref(null);
const previewImage = ref(null);
const loading = ref(false);
const result = ref(null);
const error = ref(null);

const triggerFileSelect = () => {
  fileInput.value.click();
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
    uploadAndAnalyze(file);
  }
};

const uploadAndAnalyze = async (file) => {
  loading.value = true;
  error.value = null;
  result.value = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/vision/analyze', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Erro ao analisar a imagem');
    }

    result.value = await response.json();
  } catch (e) {
    error.value = e.message;
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const reset = () => {
  previewImage.value = null;
  result.value = null;
  error.value = null;
  if (fileInput.value) fileInput.value.value = '';
};
</script>

<template>
  <div class="vision-container">
    <div v-if="!previewImage" class="upload-zone" @click="triggerFileSelect">
      <div class="upload-icon">📸</div>
      <h3>Fotografa os teus ingredientes</h3>
      <p>O nosso Chef IA vai detetar o que tens e criar uma receita saudável personalizada.</p>
      <button class="btn-upload">Escolher Foto ou Tirar agora</button>
      <input 
        type="file" 
        ref="fileInput" 
        style="display: none" 
        accept="image/*" 
        @change="handleFileChange"
      />
    </div>

    <div v-else class="analysis-view">
      <div class="preview-card">
        <img :src="previewImage" class="image-preview" />
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <p>O Chef está a analisar os ingredientes...</p>
        </div>
        <button v-if="!loading" @click="reset" class="btn-reset-top">Alterar Foto</button>
      </div>

      <div v-if="error" class="error-msg">
        {{ error }}
        <button @click="reset">Tentar novamente</button>
      </div>

      <div v-if="result" class="result-content fade-in">
        <header class="analysis-header">
          <div class="ingredients-detected">
            <h4>🔎 Detetado:</h4>
            <div class="chips">
              <span v-for="ing in result.detected_ingredients" :key="ing" class="chip">{{ ing }}</span>
            </div>
          </div>
          <p class="chef-note">"{{ result.message }}"</p>
        </header>

        <div class="recipe-card">
          <div class="recipe-head">
            <span class="calories-badge">{{ result.recipe.calories }} kcal</span>
            <h2>{{ result.recipe.title }}</h2>
            <span class="time-meta">⏱️ {{ result.recipe.time_minutes }} min</span>
          </div>

          <div class="recipe-grid">
            <div class="ingredients-list">
              <h5>Ingredientes Necessários:</h5>
              <ul>
                <li v-for="ing in result.recipe.ingredients" :key="ing">{{ ing }}</li>
              </ul>
            </div>
            <div class="steps-list">
              <h5>Modo de Preparação:</h5>
              <ol>
                <li v-for="(step, i) in result.recipe.steps" :key="i">
                  <span class="step-num">{{ i + 1 }}</span>
                  <p>{{ step }}</p>
                </li>
              </ol>
            </div>
          </div>
        </div>
        
        <div class="actions">
          <button @click="reset" class="btn-finish">Fazer Nova Análise</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.vision-container {
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Sora', sans-serif;
}

.upload-zone {
  background: white;
  border: 3px dashed #edf2f7;
  border-radius: 32px;
  padding: 80px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-zone:hover {
  border-color: #07a374;
  background: #fdfdfd;
}

.upload-icon { font-size: 4rem; margin-bottom: 24px; }
.upload-zone h3 { font-size: 1.8rem; margin-bottom: 12px; color: #11263f; }
.upload-zone p { color: #54667e; margin-bottom: 32px; max-width: 500px; margin-left: auto; margin-right: auto; }

.btn-upload {
  background: #07a374;
  color: white;
  padding: 16px 32px;
  border-radius: 16px;
  border: none;
  font-weight: 700;
  font-size: 1.1rem;
}

.analysis-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.preview-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  max-height: 400px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.1);
}

.image-preview {
  width: 100%;
  height: 400px;
  object-fit: cover;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(17, 38, 63, 0.8);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255,255,255,0.1);
  border-top-color: #07a374;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.btn-reset-top {
  position: absolute;
  bottom: 20px; right: 20px;
  background: white;
  border: none;
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.analysis-header {
  text-align: center;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}

.chip {
  background: #e3f7f2;
  color: #07a374;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}

.chef-note {
  margin-top: 20px;
  font-style: italic;
  font-size: 1.1rem;
  color: #54667e;
}

.recipe-card {
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.recipe-head {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 24px;
}

.calories-badge {
  background: #07a374;
  color: white;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 0.9rem;
}

.time-meta { color: #718096; font-size: 0.9rem; font-weight: 600; }

.recipe-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 40px;
}

.ingredients-list ul {
  list-style: none;
  padding: 0;
}

.ingredients-list li {
  padding: 8px 0;
  border-bottom: 1px solid #f8fafc;
  font-size: 0.95rem;
  color: #4a5568;
}

.steps-list ol {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.steps-list li {
  display: flex;
  gap: 16px;
}

.step-num {
  background: #11263f;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.8rem;
  font-weight: 800;
}

.btn-finish {
  background: #11263f;
  color: white;
  padding: 16px 32px;
  border-radius: 16px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  align-self: center;
}

.error-msg {
  background: #fff5f5;
  color: #c53030;
  padding: 24px;
  border-radius: 16px;
  text-align: center;
}

@media (max-width: 800px) {
  .recipe-grid { grid-template-columns: 1fr; }
}
</style>