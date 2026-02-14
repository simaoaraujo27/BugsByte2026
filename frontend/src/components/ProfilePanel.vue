<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { auth, API_URL } from '@/auth'
import { useUser } from '@/store/userStore'

const { user: userProfile, fetchUser, setUser, displayName } = useUser()

const toNumber = (val) => {
  const n = parseFloat(val)
  return isNaN(n) ? 0 : n
}

const loading = ref(false)
const errorMessage = ref('')
const passwordMessage = ref('')
const passwordLoading = ref(false)
const isEditing = ref(false)
const editForm = ref({
  username: '',
  full_name: '',
  peso: 0,
  altura: 0,
  idade: 0,
  sexo: '',
  goal: '',
  activity_level: ''
})
const isSaving = ref(false)
const showImageMenu = ref(false)
const profileImageInput = ref(null)
const profileCameraInput = ref(null)
const videoRef = ref(null)
const canvasRef = ref(null)
const isCameraActive = ref(false)
const stream = ref(null)

// Local directive for clicking outside
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      // Check if the click was outside the element AND its children
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('mousedown', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('mousedown', el.clickOutsideEvent)
  }
}

const toggleImageMenu = (e) => {
  e.stopPropagation();
  showImageMenu.value = !showImageMenu.value;
  console.log('Menu toggled:', showImageMenu.value);
};

const startCamera = async () => {
  console.log('Starting camera...');
  showImageMenu.value = false
  // On mobile, try to use native camera interface first for better reliability
  if (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)) {
    profileCameraInput.value.click();
    return;
  }

  isCameraActive.value = true
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'user' } 
    });
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
    }
  } catch (err) {
    console.error("Error accessing camera:", err);
    alert("Não foi possível aceder à câmara.");
    isCameraActive.value = false;
  }
};

const stopCamera = () => {
  console.log('Stopping camera...');
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  isCameraActive.value = false;
};

const capturePhoto = () => {
  console.log('Capturing photo...');
  const video = videoRef.value;
  const canvas = canvasRef.value;
  if (video && canvas) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const base64Image = canvas.toDataURL('image/jpeg', 0.8);
    uploadProfileImage(base64Image);
    stopCamera();
  }
};

const uploadProfileImage = async (base64Image) => {
  console.log('Uploading image (base64 length):', base64Image.length);
  try {
    const res = await fetch(`${API_URL}/users/me`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ profile_image: base64Image })
    })

    if (!res.ok) {
      const errorData = await res.json();
      console.error('Upload failed:', errorData);
      throw new Error('Falha ao carregar imagem')
    }
    
    const updatedUser = await res.json()
    console.log('Upload success, updated user');
    setUser(updatedUser)
  } catch (err) {
    console.error('Upload error:', err);
    alert(err.message)
  }
};

const formatGender = (value) => {
  const normalized = (value || '').toLowerCase()
  if (normalized === 'male') return 'Masculino'
  if (normalized === 'female') return 'Feminino'
  if (normalized === 'other') return 'Outro'
  return value || 'N/A'
}

const formatGoal = (value) => {
  const normalized = (value || '').toLowerCase()
  if (normalized === 'lose') return 'Perder Peso'
  if (normalized === 'maintain') return 'Manter Peso'
  if (normalized === 'gain') return 'Ganhar Massa Muscular'
  return value || 'N/A'
}

const formatActivityLevel = (value) => {
  const normalized = (value || '').toLowerCase()
  if (normalized === 'sedentary') return 'Sedentário'
  if (normalized === 'light') return 'Ligeiro'
  if (normalized === 'moderate') return 'Moderado'
  if (normalized === 'high') return 'Elevado'
  return value || 'N/A'
}

const bmi = computed(() => {
  if (!userProfile.value?.altura || !userProfile.value?.peso) return null
  const heightM = Number(userProfile.value.altura) / 100
  if (!heightM) return null
  return Number(userProfile.value.peso) / (heightM * heightM)
})

const bmr = computed(() => {
  const profile = userProfile.value
  if (!profile?.peso || !profile?.altura || !profile?.idade) return null

  const weight = Number(profile.peso)
  const height = Number(profile.altura)
  const age = Number(profile.idade)
  const gender = (profile.sexo || '').toLowerCase()

  if (gender === 'male') return 10 * weight + 6.25 * height - 5 * age + 5
  if (gender === 'female') return 10 * weight + 6.25 * height - 5 * age - 161
  return 10 * weight + 6.25 * height - 5 * age - 78
})

const activityFactor = computed(() => {
  const level = (userProfile.value?.activity_level || '').toLowerCase()
  if (level === 'sedentary') return 1.2
  if (level === 'light') return 1.375
  if (level === 'moderate') return 1.55
  if (level === 'high') return 1.725
  return 1.2
})

const tdee = computed(() => {
  if (!bmr.value) return null
  return bmr.value * activityFactor.value
})

const bmiCategory = computed(() => {
  if (!bmi.value) return 'N/A'
  if (bmi.value < 18.5) return 'Abaixo do peso'
  if (bmi.value < 25) return 'Peso normal'
  if (bmi.value < 30) return 'Excesso de peso'
  return 'Obesidade'
})

const allergiesText = computed(() => {
  if (!userProfile.value?.allergens?.length) return 'Nenhum'
  return userProfile.value.allergens.map((item) => item.name).join(', ')
})

const fetchProfileData = async () => {
  if (userProfile.value) {
    syncEditForm()
    return
  }
  
  loading.value = true
  errorMessage.value = ''

  try {
    await fetchUser()
    
    if (!userProfile.value) {
      errorMessage.value = 'Não existe nenhum perfil disponível.'
    } else {
      syncEditForm()
    }
  } catch (error) {
    errorMessage.value = error.message || 'Erro ao obter o perfil.'
  } finally {
    loading.value = false
  }
}

const syncEditForm = () => {
  if (!userProfile.value) return
  editForm.value = {
    username: userProfile.value.username || '',
    full_name: userProfile.value.full_name || '',
    peso: toNumber(userProfile.value.peso),
    altura: toNumber(userProfile.value.altura),
    idade: toNumber(userProfile.value.idade),
    sexo: userProfile.value.sexo || 'other',
    goal: userProfile.value.goal || 'maintain',
    activity_level: userProfile.value.activity_level || 'sedentary'
  }
}

const toggleEdit = () => {
  if (!isEditing.value) {
    syncEditForm()
  }
  isEditing.value = !isEditing.value
}

watch(userProfile, (newVal) => {
  if (newVal && !isEditing.value) {
    syncEditForm()
  }
}, { deep: true })

const saveProfile = async () => {
  isSaving.value = true
  try {
    const res = await fetch(`${API_URL}/users/me`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify(editForm.value)
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Falha ao atualizar perfil')
    }

    const updatedUser = await res.json()
    setUser(updatedUser)
    isEditing.value = false
    alert('Perfil atualizado com sucesso!')
  } catch (err) {
    alert(err.message)
  } finally {
    isSaving.value = false
  }
}

const triggerImageUpload = () => {
  showImageMenu.value = false
  profileImageInput.value.click()
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Basic validation
  if (!file.type.startsWith('image/')) {
    alert('Por favor, selecione uma imagem.')
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    alert('A imagem deve ter no máximo 2MB.')
    return
  }

  const reader = new FileReader()
  reader.onload = async (e) => {
    uploadProfileImage(e.target.result);
  }
  reader.readAsDataURL(file)
}

const requestPasswordChange = async () => {
  if (!userProfile.value?.username || passwordLoading.value) return

  passwordLoading.value = true
  passwordMessage.value = ''

  try {
    const response = await fetch(`${API_URL}/forgot-password/`, {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ username: userProfile.value.username })
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data?.detail || 'Não foi possível iniciar a alteração da palavra-passe.')
    }

    passwordMessage.value = data.message || 'Pedido enviado.'
  } catch (error) {
    passwordMessage.value = error instanceof TypeError
      ? 'Backend indisponível para alterar a palavra-passe.'
      : (error.message || 'Erro ao iniciar a alteração da palavra-passe.')
  } finally {
    passwordLoading.value = false
  }
}

onMounted(fetchProfileData)
</script>

<template>
  <section class="profile-panel">
    <header class="panel-header">
      <div class="header-content">
        <div>
          <h1>Perfil</h1>
          <p>Informação da conta e métricas de saúde</p>
        </div>
        <button class="edit-toggle-btn" @click="toggleEdit">
          {{ isEditing ? 'Cancelar' : '📝 Editar Perfil' }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="status-card">A carregar perfil...</div>
    <div v-else-if="errorMessage" class="status-card error">{{ errorMessage }}</div>

    <template v-else-if="userProfile">
      <!-- Camera Modal/Overlay -->
      <div v-if="isCameraActive" class="camera-overlay">
        <div class="camera-modal">
          <video ref="videoRef" autoplay playsinline class="profile-video"></video>
          <canvas ref="canvasRef" style="display: none"></canvas>
          <div class="camera-actions">
            <button @click="stopCamera" class="btn-cancel-cam">Cancelar</button>
            <button @click="capturePhoto" class="btn-capture-profile"></button>
            <div style="width: 80px;"></div>
          </div>
        </div>
      </div>

      <article class="hero-card">
        <div class="hero-content">
          <div class="avatar-group">
            <div class="avatar-container" @click="toggleImageMenu">
              <img v-if="userProfile.profile_image" :src="userProfile.profile_image" class="avatar-img" />
              <div v-else class="avatar-tile" aria-hidden="true">👤</div>
              <div class="avatar-overlay">
                <span>Mudar</span>
              </div>
            </div>
            
            <div v-if="showImageMenu" class="image-menu" v-click-outside="() => showImageMenu = false">
              <button @click="triggerImageUpload">📁 Da Galeria</button>
              <button @click="startCamera">📷 Usar Câmara</button>
            </div>
            
            <input type="file" ref="profileImageInput" style="display: none" accept="image/*" @change="handleImageUpload" />
            <input type="file" ref="profileCameraInput" style="display: none" accept="image/*" capture="user" @change="handleImageUpload" />
          </div>
          <div>
            <h2>{{ displayName }}</h2>
            <p class="hero-email">✉ {{ userProfile.username }}</p>
          </div>
        </div>
      </article>

      <div class="grid">
        <article class="card details-card">
          <div class="card-header">
            <h3><span class="badge green">●</span> Dados Pessoais</h3>
          </div>
          
          <div v-if="isEditing" class="edit-grid">
            <div class="form-group">
              <label>Nome Completo</label>
              <input v-model="editForm.full_name" type="text" placeholder="O seu nome" />
            </div>
            <div class="form-group">
              <label>Utilizador (Email)</label>
              <input v-model="editForm.username" type="text" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Idade</label>
                <input v-model.number="editForm.idade" type="number" />
              </div>
              <div class="form-group">
                <label>Género</label>
                <select v-model="editForm.sexo">
                  <option value="male">Masculino</option>
                  <option value="female">Feminino</option>
                  <option value="other">Outro</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Altura (cm)</label>
                <input v-model.number="editForm.altura" type="number" />
              </div>
              <div class="form-group">
                <label>Peso (kg)</label>
                <input v-model.number="editForm.peso" type="number" step="0.1" />
              </div>
            </div>
            <div class="form-group">
              <label>Objetivo</label>
              <select v-model="editForm.goal">
                <option value="lose">Perder Peso</option>
                <option value="maintain">Manter Peso</option>
                <option value="gain">Ganhar Massa Muscular</option>
              </select>
            </div>
            <div class="form-group">
              <label>Nível de Atividade</label>
              <select v-model="editForm.activity_level">
                <option value="sedentary">Sedentário</option>
                <option value="light">Ligeiro</option>
                <option value="moderate">Moderado</option>
                <option value="high">Elevado</option>
              </select>
            </div>
            <button class="save-btn" @click="saveProfile" :disabled="isSaving">
              {{ isSaving ? 'A guardar...' : 'Guardar Alterações' }}
            </button>
          </div>

          <ul v-else class="detail-list">
            <li>
              <span>Género</span>
              <strong>{{ formatGender(userProfile.sexo) }}</strong>
            </li>
            <li>
              <span>Idade</span>
              <strong>{{ userProfile.idade }} anos</strong>
            </li>
            <li>
              <span>Altura</span>
              <strong>{{ userProfile.altura }} cm</strong>
            </li>
            <li>
              <span>Peso</span>
              <strong>{{ userProfile.peso }} kg</strong>
            </li>
            <li>
              <span>Objetivo</span>
              <strong>{{ formatGoal(userProfile.goal) }}</strong>
            </li>
            <li>
              <span>Nível de Atividade</span>
              <strong>{{ formatActivityLevel(userProfile.activity_level) }}</strong>
            </li>
            <li>
              <span>Alergénios</span>
              <strong>{{ allergiesText }}</strong>
            </li>
          </ul>
        </article>

        <article class="card metrics-card">
          <h3><span class="badge rose">●</span> Métricas de Saúde</h3>
          <div class="metric-box">
            <p>Índice de Massa Corporal</p>
            <strong>{{ bmi ? bmi.toFixed(1) : '-' }} kg/m²</strong>
            <small>{{ bmiCategory }}</small>
          </div>
          <div class="metric-box">
            <p>Taxa Metabólica Basal</p>
            <strong>{{ bmr ? Math.round(bmr) : '-' }} kcal/dia</strong>
          </div>
          <div class="metric-box">
            <p>Kcal normais (TDEE)</p>
            <strong>{{ tdee ? Math.round(tdee) : '-' }} kcal/dia</strong>
            <small>Manutenção diária com base no nível de atividade.</small>
          </div>
        </article>

        <article class="card full">
          <h3>Segurança</h3>
          <p class="muted">Altere a sua palavra-passe enviando um link de recuperação para o seu email.</p>
          <button type="button" class="btn" :disabled="passwordLoading" @click="requestPasswordChange">
            {{ passwordLoading ? 'A enviar...' : '📧 Enviar link de alteração' }}
          </button>
          <p v-if="passwordMessage" class="password-message">{{ passwordMessage }}</p>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.profile-panel {
  max-width: 980px;
}

.panel-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.panel-header h1 {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.panel-header p {
  margin-top: 6px;
  color: var(--text-muted);
}

.edit-toggle-btn {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.2s;
}

.edit-toggle-btn:hover {
  background: var(--bg-main);
  border-color: #0ea5a0;
}

.status-card {
  margin-top: 24px;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 12px;
  padding: 16px;
  color: var(--text-main);
}

.status-card.error {
  border-color: #dc2626;
  color: #dc2626;
}

.hero-card {
  background: linear-gradient(105deg, #19b88a 0%, #20c4b3 55%, #28a8cf 100%);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: visible;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.hero-content {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-group {
  position: relative;
}

.image-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 100;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  min-width: 190px;
  white-space: nowrap;
}

.image-menu button {
  background: transparent;
  border: none;
  padding: 10px 14px;
  text-align: left;
  color: var(--text-main);
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.image-menu button:hover {
  background: var(--bg-main);
}

.camera-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 2000;
  display: grid;
  place-items: center;
  padding: 20px;
}

.camera-modal {
  width: 100%;
  max-width: 500px;
  background: #000;
  border-radius: 32px;
  overflow: hidden;
  position: relative;
  aspect-ratio: 1/1;
}

.profile-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-cancel-cam {
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(8px);
}

.btn-capture-profile {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: white;
  border: 4px solid rgba(255,255,255,0.3);
  cursor: pointer;
  position: relative;
}

.btn-capture-profile::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  border: 2px solid #000;
}

.avatar-container {
  position: relative;
  width: 90px;
  height: 90px;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  background: #f7fbff;
  border: 2px solid rgba(255,255,255,0.3);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-tile {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 2.5rem;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-overlay span {
  color: white;
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.hero-content h2 {
  margin: 0;
  font-size: 2.2rem;
  line-height: 1.15;
  color: #f6fffe;
  font-weight: 800;
}

.hero-email {
  margin-top: 4px;
  color: rgba(236, 255, 252, 0.9);
  font-weight: 500;
}

.grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.card {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.card.full {
  grid-column: 1 / -1;
}

.card h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.badge {
  font-size: 0.8rem;
  vertical-align: middle;
  margin-right: 8px;
}

.badge.green { color: #10b981; }
.badge.rose { color: #f43f5e; }

.detail-list {
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.detail-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
}

.detail-list li:last-child {
  border-bottom: 0;
}

.detail-list li span {
  color: var(--text-muted);
  font-weight: 500;
}

.detail-list li strong {
  color: var(--text-main);
  text-align: right;
  font-weight: 700;
}

.metrics-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-box {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px;
  background: rgba(148, 163, 184, 0.08);
  transition: transform 0.2s;
}

.metric-box:hover {
  transform: translateY(-2px);
}

.metric-box p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  font-weight: 600;
}

.metric-box strong {
  display: block;
  margin-top: 8px;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
}

.metric-box small {
  display: inline-block;
  margin-top: 6px;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Edit Form Styles */
.edit-grid {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
}

.form-group input, 
.form-group select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--bg-main);
  color: var(--text-main);
  font-family: inherit;
  font-size: 0.95rem;
}

.save-btn {
  margin-top: 10px;
  background: #0ea5a0;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover {
  background: #0b8f8b;
  transform: translateY(-2px);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn {
  margin-top: 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--bg-main);
  color: var(--text-main);
  font-weight: 700;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  background: var(--menu-hover-bg);
  border-color: #0ea5a0;
}

.password-message {
  margin-top: 12px;
  padding: 10px;
  border-radius: 8px;
  background: var(--bg-main);
  font-size: 0.9rem;
  color: #0ea5a0;
  font-weight: 600;
}

:global(.theme-dark) .hero-card,
:global(.theme-dark) .card {
  box-shadow: 0 10px 22px rgba(3, 8, 18, 0.35);
}

:global(.theme-dark) .avatar-container {
  background: #0f1a2b;
  border-color: #30415e;
}

:global(.theme-dark) .metric-box {
  background: rgba(15, 23, 40, 0.55);
}

@media (max-width: 860px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .hero-content h2 {
    font-size: 1.8rem;
  }
}
</style>
