<script setup>
import { ref } from 'vue';
import { auth } from '@/auth';

const fileInput = ref(null);
const videoRef = ref(null);
const canvasRef = ref(null);
const previewImage = ref(null);
const isCameraActive = ref(false);
const stream = ref(null);
const loading = ref(false);
const saving = ref(false);
const result = ref(null);
const error = ref(null);

const triggerFileSelect = () => {
  fileInput.value.click();
};

const startCamera = async () => {
  isCameraActive.value = true;
  error.value = null;
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    });
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
    }
  } catch (err) {
    console.error("Error accessing camera:", err);
    error.value = "Não foi possível aceder à câmara. Verifique as permissões.";
    isCameraActive.value = false;
  }
};

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  isCameraActive.value = false;
};

const capturePhoto = () => {
  console.log("VisionRecipe: Attempting capture...");
  const video = videoRef.value;
  const canvas = canvasRef.value;
  if (video && canvas) {
    try {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob((blob) => {
        if (blob) {
          console.log("VisionRecipe: Blob created, size:", blob.size);
          const file = new File([blob], "captured_ingredients.jpg", { type: "image/jpeg" });
          previewImage.value = URL.createObjectURL(blob);
          uploadAndAnalyze(file);
          stopCamera();
        } else {
          console.error("VisionRecipe: Failed to create blob");
          error.value = "Erro ao processar imagem capturada.";
        }
      }, 'image/jpeg', 0.8);
    } catch (err) {
      console.error("VisionRecipe: Capture error:", err);
      error.value = "Erro na captura: " + err.message;
    }
  }
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    console.log("VisionRecipe: File selected via input:", file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
    uploadAndAnalyze(file);
  }
};

const uploadAndAnalyze = async (file) => {
  console.log("VisionRecipe: Starting uploadAndAnalyze...");
  loading.value = true;
  error.value = null;
  result.value = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    console.log("VisionRecipe: Fetching from:", `${apiUrl}/vision/analyze`);
    
    const response = await fetch(`${apiUrl}/vision/analyze`, {
      method: 'POST',
      headers: auth.getAuthHeaders(false),
      body: formData,
    });

    console.log("VisionRecipe: Response status:", response.status);
    if (!response.ok) {
      const errText = await response.text();
      console.error("VisionRecipe: API Error:", errText);
      throw new Error('Erro ao analisar a imagem');
    }

    result.value = await response.json();
    console.log("VisionRecipe: Analysis success");
  } catch (e) {
    console.error("VisionRecipe: uploadAndAnalyze error:", e);
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

const saveRecipe = async () => {
  if (!result.value || !result.value.recipe) return;
  saving.value = true;

  try {
    // 1. Create the recipe
    const recipeData = {
      name: result.value.recipe.title,
      ingredients: result.value.recipe.ingredients.join(', '),
      instructions: result.value.recipe.steps.join('\n')
    };

    const createResponse = await fetch('' + (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/recipes/', {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify(recipeData)
    });

    if (!createResponse.ok) throw new Error('Failed to create recipe');
    const createdRecipe = await createResponse.json();

    // 2. Add to favorites
    const favResponse = await fetch(`' + (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/users/me/favorites/recipes/${createdRecipe.id}`, {
      method: 'POST',
      headers: auth.getAuthHeaders()
    });

    if (!favResponse.ok) throw new Error('Failed to add to favorites');

    alert('Receita guardada com sucesso!');
  } catch (err) {
    console.error('Error saving recipe:', err);
    alert('Erro ao guardar a receita.');
  } finally {
    saving.value = false;
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
    <div v-if="!previewImage && !isCameraActive" class="upload-zone">
      <div class="upload-icon">📸</div>
      <h3>Fotografe os seus ingredientes</h3>
      <p>O nosso Chef IA vai detetar o que tem e criar uma receita saudável personalizada.</p>
      <div class="upload-actions">
        <button class="btn-upload" @click="triggerFileSelect">Escolher da Galeria</button>
        <button class="btn-camera" @click="startCamera">Abrir Câmara</button>
      </div>
      <input 
        type="file" 
        ref="fileInput" 
        style="display: none" 
        accept="image/*" 
        @change="handleFileChange"
      />
    </div>

    <!-- Camera View -->
    <div v-if="isCameraActive" class="camera-view fade-in">
      <div class="camera-container">
        <video ref="videoRef" autoplay playsinline class="camera-video"></video>
        <canvas ref="canvasRef" style="display: none"></canvas>
        <div class="camera-controls">
          <button @click="stopCamera" class="btn-cancel">Cancelar</button>
          <button @click="capturePhoto" class="btn-capture">
            <div class="capture-inner"></div>
          </button>
          <div class="spacer"></div>
        </div>
      </div>
    </div>

    <div v-if="previewImage && !isCameraActive" class="analysis-view">
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
          <button @click="saveRecipe" class="btn-save" :disabled="saving">
            {{ saving ? 'A guardar...' : '❤️ Guardar Receita' }}
          </button>
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
  background: var(--bg-elevated);
  border: 3px dashed var(--line);
  border-radius: 32px;
  padding: 80px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-zone:hover {
  border-color: #07a374;
  background: var(--bg-main);
}

.upload-icon { font-size: 4rem; margin-bottom: 24px; }
.upload-zone h3 { font-size: 1.8rem; margin-bottom: 12px; color: var(--text-main); }
.upload-zone p { color: var(--text-muted); margin-bottom: 32px; max-width: 500px; margin-left: auto; margin-right: auto; }

.upload-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-upload, .btn-camera {
  padding: 16px 32px;
  border-radius: 16px;
  border: none;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-upload {
  background: #07a374;
  color: white;
}

.btn-camera {
  background: var(--text-main);
  color: var(--bg-main);
}

.btn-upload:hover, .btn-camera:hover {
  transform: translateY(-2px);
}

.camera-view {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.camera-container {
  position: relative;
  background: #000;
  border-radius: 32px;
  overflow: hidden;
  aspect-ratio: 3/4;
  display: flex;
  flex-direction: column;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 30px;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-capture {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: white;
  border: 4px solid rgba(255,255,255,0.3);
  padding: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-capture:active {
  transform: scale(0.9);
}

.capture-inner {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 50%;
  border: 2px solid #000;
}

.btn-cancel {
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.spacer { width: 80px; }

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
  border: 1px solid var(--line);
}

.image-preview {
  width: 100%;
  height: 400px;
  object-fit: cover;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(17, 38, 63, 0.85);
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
  background: var(--bg-elevated);
  color: var(--text-main);
  border: 1px solid var(--line);
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
  background: var(--menu-active-bg);
  color: var(--menu-active-text);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}

.chef-note {
  margin-top: 20px;
  font-style: italic;
  font-size: 1.1rem;
  color: var(--text-muted);
}

.recipe-card {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  border: 1px solid var(--line);
}

.recipe-head {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 1px solid var(--line);
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

.time-meta { color: var(--text-muted); font-size: 0.9rem; font-weight: 600; }

.recipe-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 40px;
}

.ingredients-list h5, .steps-list h5 {
  color: var(--text-main);
  margin-top: 0;
}

.ingredients-list ul {
  list-style: none;
  padding: 0;
}

.ingredients-list li {
  padding: 8px 0;
  border-bottom: 1px solid var(--line);
  font-size: 0.95rem;
  color: var(--text-main);
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
  background: var(--text-main);
  color: var(--bg-main);
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

.steps-list p {
  color: var(--text-main);
  margin: 0;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.btn-save {
  background: #ff5e5e;
  color: white;
  padding: 16px 32px;
  border-radius: 16px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-save:hover { opacity: 0.9; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-finish {
  background: var(--text-main);
  color: var(--bg-main);
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