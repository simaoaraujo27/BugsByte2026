<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUser } from '@/store/userStore'
import SidebarNav from './SidebarNav.vue'
import DashboardHome from './DashboardHome.vue'
import Negotiator from './Negotiator.vue'
import ShopFinder from './ShopFinder.vue'
import ProfilePanel from './ProfilePanel.vue'
import DiaryTracking from './DiaryTracking.vue'
import VisionRecipe from './VisionRecipe.vue'
import VolumeComparison from './VolumeComparison.vue'
import YourRecipesPage from './YourRecipesPage.vue'
import SettingsPage from './SettingsPage.vue'
import CasinoGame from './CasinoGame.vue'
import NutritionQuiz from './NutritionQuiz.vue'
import UnitConverter from './UnitConverter.vue'
import FastingTimer from './FastingTimer.vue'
import { auth, API_URL } from '@/auth'
import chatbotImg from '@/assets/chatbot.png'

const { fetchUser } = useUser()

// Water Logic
const waterLiters = ref(0)
const dashboardKey = ref(0)
const showWaterReminder = ref(false)
const nextWaterTime = ref(null)
let waterInterval = null
const WATER_REMINDER_INTERVAL_MS = 30 * 60 * 1000
const WATER_SNOOZE_MS = 30 * 1000

// Chat Assistant Logic
const isChatOpen = ref(false)
const chatInput = ref('')
const isChatLoading = ref(false)
const isListening = ref(false)
const isVoiceEnabled = ref(false)
const diaryKey = ref(0) // Used to refresh diary if needed
const chatMessages = ref([
  { role: 'assistant', content: 'Olá! Eu sou a Nutra. Estou aqui para te ajudar a tirar o máximo partido da NutriVentures. O que precisas de saber?' }
])

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
}

// Voice Synthesis (TTS)
const speak = (text) => {
  if (!isVoiceEnabled.value) return
  if (!window.speechSynthesis) return

  // Cancel any ongoing speech
  window.speechSynthesis.cancel()
  
  // Wait a tiny bit for the cancel to take effect in some browsers
  setTimeout(() => {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'pt-PT'
    utterance.rate = 1.0
    utterance.pitch = 1.0
    
    const voices = window.speechSynthesis.getVoices()
    // Detailed search for a female Portuguese voice
    const femaleVoice = voices.find(v => 
      (v.lang.includes('pt-PT') || v.lang.includes('pt-BR')) && 
      (v.name.includes('Maria') || v.name.includes('Helena') || v.name.includes('Joana') || v.name.includes('Raquel') || v.name.includes('Google português'))
    )
    
    if (femaleVoice) {
      utterance.voice = femaleVoice
    } else {
      const anyPt = voices.find(v => v.lang.startsWith('pt'))
      if (anyPt) utterance.voice = anyPt
    }
    
    window.speechSynthesis.speak(utterance)
  }, 50)
}

// Ensure voices are loaded (for Chrome/Edge)
if (typeof window !== 'undefined' && window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices()
  }
}

// Function to "unlock" audio (browsers require user gesture)
const toggleVoiceAndUnlock = () => {
  isVoiceEnabled.value = !isVoiceEnabled.value
  if (isVoiceEnabled.value) {
    // Speak a tiny silent or very short greeting to unlock the context
    const unlockUtterance = new SpeechSynthesisUtterance('')
    unlockUtterance.volume = 0
    window.speechSynthesis.speak(unlockUtterance)
    
    // Also trigger the welcome message if it's the start
    if (chatMessages.value.length === 1) {
      speak(chatMessages.value[0].content)
    }
  }
}

// Voice Recognition (STT)
const startListening = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    alert('O seu navegador não suporta reconhecimento de voz.')
    return
  }
  
  const recognition = new SpeechRecognition()
  recognition.lang = 'pt-PT'
  recognition.onstart = () => { isListening.value = true }
  recognition.onend = () => { isListening.value = false }
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    chatInput.value = transcript
    sendChatMessage()
  }
  recognition.start()
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || isChatLoading.value) return
  
  const userText = chatInput.value.trim()
  chatMessages.value.push({ role: 'user', content: userText })
  chatInput.value = ''
  isChatLoading.value = true

  try {
    const res = await fetch(`${API_URL}/assistant/chat`, {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ messages: chatMessages.value })
    })
    
    if (res.ok) {
      const data = await res.json()
      chatMessages.value.push({ role: 'assistant', content: data.content })
      speak(data.content) // Speak the response
      if (data.action) {
        executeNutraAction(data.action)
      }
    } else {
      const errText = 'Desculpa, tive um problema ao processar a tua mensagem.'
      chatMessages.value.push({ role: 'assistant', content: errText })
      speak(errText)
    }
  } catch (e) {
    const errText = 'Erro de ligação com o servidor.'
    chatMessages.value.push({ role: 'assistant', content: errText })
    speak(errText)
  } finally {
    isChatLoading.value = false
    // Scroll to bottom
    setTimeout(() => {
      const box = document.querySelector('.chat-messages-box')
      if (box) box.scrollTop = box.scrollHeight
    }, 100)
  }
}

const executeNutraAction = async (action) => {
  console.log('Executing Nutra Action:', action)
  const { type, value, section } = action

  switch (type) {
    case 'ADD_MEAL':
      try {
        // 1. Analyze nutrition
        const anaRes = await fetch(`${API_URL}/negotiator/nutrition`, {
          method: 'POST',
          headers: auth.getAuthHeaders(),
          body: JSON.stringify({ food_text: value })
        })
        if (!anaRes.ok) throw new Error('Falha na análise')
        const data = await anaRes.json()

        // 2. Add to diary
        const today = new Date().toISOString().split('T')[0]
        const mealSection = section || 'lunch'
        await fetch(`${API_URL}/diary/${today}/meals`, {
          method: 'POST',
          headers: auth.getAuthHeaders(),
          body: JSON.stringify({
            section: mealSection,
            name: data.name,
            grams: data.estimated_grams,
            calories: data.calories,
            protein: data.protein,
            carbs: data.carbs,
            fat: data.fat
          })
        })
        
        // Refresh dashboard and diary if active
        if (activeSection.value === 'inicio') dashboardKey.value++
        if (activeSection.value === 'diario') diaryKey.value++
      } catch (e) {
        console.error('Add meal via Nutra failed', e)
      }
      break
    case 'START_NEGOTIATION':
      globalCraving.value = value
      negotiatorRouteMode.value = 'desejo'
      selectSection('tenho-fome')
      break
    case 'NAVIGATE':
      const sectionId = sectionSlugToId[value] || value
      if (sections.some(s => s.id === sectionId)) {
        selectSection(sectionId)
      }
      break
    case 'SET_THEME':
      if (value === 'dark' && !isDarkMode.value) toggleTheme()
      if (value === 'light' && isDarkMode.value) toggleTheme()
      break
    case 'ADD_WATER':
      addWaterGlobal()
      break
    case 'REMOVE_WATER':
      removeWaterGlobal()
      break
    case 'SET_COLOR_MODE':
      updateColorBlindness(value)
      break
    case 'OPEN_CASINO':
      chatMessages.value.push({ 
        role: 'assistant', 
        type: 'casino',
        content: 'Bora lá! Tenta a tua sorte na nossa Slot Machine saudável. Clica em "Girar"!' 
      })
      break
    case 'OPEN_QUIZ':
      chatMessages.value.push({ 
        role: 'assistant', 
        type: 'quiz',
        content: 'Vamos testar os teus conhecimentos nutricionais? Responde às perguntas abaixo!' 
      })
      break
    case 'OPEN_CONVERTER':
      chatMessages.value.push({ 
        role: 'assistant', 
        type: 'converter',
        content: 'Aqui tens a ferramenta de conversão para te ajudar a medir as porções corretamente.' 
      })
      break
    case 'OPEN_FASTING_TIMER':
      chatMessages.value.push({ 
        role: 'assistant', 
        type: 'timer',
        content: 'Configura aqui o teu cronómetro de jejum intermitente.' 
      })
      break
    case 'CLEAR_MEALS':
      try {
        const today = new Date().toISOString().split('T')[0]
        await fetch(`${API_URL}/diary/${today}/meals`, {
          method: 'DELETE',
          headers: auth.getAuthHeaders()
        })
        if (activeSection.value === 'inicio') dashboardKey.value++
        if (activeSection.value === 'diario') diaryKey.value++
      } catch (e) {
        console.error('Clear meals failed', e)
      }
      break
    case 'LOG_WEIGHT':
      try {
        const today = new Date().toISOString().split('T')[0]
        await fetch(`${API_URL}/users/me/weight`, {
          method: 'POST',
          headers: auth.getAuthHeaders(),
          body: JSON.stringify({ weight: parseFloat(value), date: today })
        })
        if (activeSection.value === 'inicio') dashboardKey.value++
      } catch (e) {
        console.error('Weight log failed', e)
      }
      break
    case 'OPEN_FOOD_SEARCH':
      selectSection('diario')
      // Wait for navigation
      setTimeout(() => {
        const btn = document.querySelector('.search-food-btn')
        if (btn) btn.click()
      }, 300)
      break
    case 'LOGOUT':
      auth.logout()
      router.push('/login')
      break
    default:
      console.warn('Unknown action type:', type)
  }
}

const fetchWaterIntake = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await fetch(`${API_URL}/diary/${today}`, {
      headers: auth.getAuthHeaders()
    })
    if (res.ok) {
      const day = await res.json()
      waterLiters.value = day.water_liters || 0
    }
  } catch (e) {
    console.error("Failed to fetch water", e)
  }
}

const addWaterGlobal = async () => {
  const newAmount = Number((waterLiters.value + 0.25).toFixed(2))
  waterLiters.value = newAmount
  try {
    const today = new Date().toISOString().split('T')[0]
    await fetch(`${API_URL}/diary/${today}/water`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ water_liters: newAmount })
    })
    resetWaterTimer()
    // Refresh dashboard if active
    if (activeSection.value === 'inicio') {
      dashboardKey.value++
    }
  } catch (e) {
    console.error("Water update failed", e)
  }
}

const removeWaterGlobal = async () => {
  if (waterLiters.value <= 0) return
  const newAmount = Number((waterLiters.value - 0.25).toFixed(2))
  waterLiters.value = newAmount
  try {
    const today = new Date().toISOString().split('T')[0]
    await fetch(`${API_URL}/diary/${today}/water`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ water_liters: newAmount })
    })
    resetWaterTimer()
    // Refresh dashboard if active
    if (activeSection.value === 'inicio') {
      dashboardKey.value++
    }
  } catch (e) {
    console.error("Water update failed", e)
  }
}

const startWaterTimer = () => {
  nextWaterTime.value = new Date(Date.now() + WATER_REMINDER_INTERVAL_MS)
  waterInterval = setInterval(() => {
    if (nextWaterTime.value && Date.now() >= nextWaterTime.value.getTime()) {
      showWaterReminder.value = true
    }
  }, 10000)
}

const resetWaterTimer = () => {
  showWaterReminder.value = false
  nextWaterTime.value = new Date(Date.now() + WATER_REMINDER_INTERVAL_MS)
}

const snoozeWaterReminder = () => {
  showWaterReminder.value = false
  nextWaterTime.value = new Date(Date.now() + WATER_SNOOZE_MS)
}

const sections = [
  { id: 'inicio', label: 'Início', icon: '🏠' },
  { id: 'tenho-fome', label: 'Tenho Fome', icon: '🍔' },
  { id: 'gerar-receita', label: 'Visão do Chef', icon: '📸' },
  { id: 'visualizador', label: 'Volume das Calorias', icon: '🥗' },
  { id: 'supermercados', label: 'Supermercados & Compras', icon: '🛒' },
  { id: 'diario', label: 'Diário / Tracking', icon: '📊' },
  { id: 'tuas-receitas', label: 'Tuas Receitas', icon: '📚' },
  { id: 'perfil', label: 'Perfil', icon: '👤' },
  { id: 'definicoes', label: 'Definições', icon: '⚙️' }
]

const route = useRoute()
const router = useRouter()

const activeSection = ref('inicio')
const isDarkMode = ref(false)
const colorBlindnessMode = ref('none')

// State for ShopFinder parameters
const shopParams = ref({
  ingredients: '',
  mode: 'shop',
  term: ''
})
const negotiatorRouteMode = ref('')
const globalCraving = ref('')

const sectionIdToSlug = {
  inicio: 'inicio',
  'tenho-fome': 'tenhofome',
  'visualizador': 'volumecalorias',
  supermercados: 'supermercados',
  diario: 'diario',
  'tuas-receitas': 'tuasreceitas',
  perfil: 'perfil',
  definicoes: 'definicoes',
  'gerar-receita': 'gerarreceita'
}

const sectionSlugToId = Object.fromEntries(
  Object.entries(sectionIdToSlug).map(([id, slug]) => [slug, id])
)

const negotiatorModeToSubSlug = {
  '': '',
  desejo: 'desejo',
  estadoalma: 'estadoalma',
  visaochef: 'visaochef'
}

const negotiatorSubSlugToMode = Object.fromEntries(
  Object.entries(negotiatorModeToSubSlug).map(([mode, slug]) => [slug, mode])
)

const resolveSectionFromRoute = (routeSection) => {
  if (!routeSection) return 'inicio'
  if (routeSection === 'favoritos' || routeSection === 'historico') return 'tuas-receitas'
  return sectionSlugToId[routeSection] || 'inicio'
}

const syncRouteWithSection = (id, replace = false, subsection = '') => {
  const slug = sectionIdToSlug[id] || sectionIdToSlug.inicio
  const sub = id === 'tenho-fome' && subsection ? `/${subsection}` : ''
  const target = `/dashboard/${slug}${sub}`
  if (route.path === target) return
  if (replace) {
    router.replace(target)
  } else {
    router.push(target)
  }
}

const handleNegotiationChoice = (choice) => {
  if (choice.type === 'diy') {
    shopParams.value = {
      ingredients: choice.ingredients,
      mode: 'shop',
      term: ''
    }
    selectSection('supermercados')
  }
}

// When manually clicking supermarket or restaurant, maybe reset params?
// Or keep them. Usually better to reset if not coming from Negotiator.
const selectSection = (target) => {
  const id = typeof target === 'string' ? target : target?.id
  if (!id) return

  activeSection.value = id
  if (id !== 'tenho-fome') {
    negotiatorRouteMode.value = ''
  } else if (typeof target === 'object' && target?.subsection) {
    negotiatorRouteMode.value = negotiatorSubSlugToMode[target.subsection] || ''
  }
  syncRouteWithSection(id, false, id === 'tenho-fome' ? negotiatorModeToSubSlug[negotiatorRouteMode.value] : '')
}

const handleNegotiatorModeChange = (mode) => {
  if (activeSection.value !== 'tenho-fome') return
  const normalized = negotiatorModeToSubSlug[mode] !== undefined ? mode : ''
  negotiatorRouteMode.value = normalized
  syncRouteWithSection('tenho-fome', false, negotiatorModeToSubSlug[normalized])
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
}

const updateColorBlindness = (mode) => {
  colorBlindnessMode.value = mode
  localStorage.setItem('colorBlindnessMode', mode)
}

const sectionContent = {
  inicio: {
    title: 'Painel Inicial',
    subtitle: 'Calorias do dia, streak e o atalho para "Tenho Fome".'
  },
  'tenho-fome': {
    title: 'Tenho Fome (Intelligent Assistant)',
    subtitle: 'Escolhe como queres decidir a tua próxima refeição saudável.'
  },
  'gerar-receita': {
    title: 'Visão do Chef',
    subtitle: 'Tira uma foto aos teus ingredientes e deixa a IA criar a receita perfeita.'
  },
  supermercados: {
    title: 'Supermercados & Compras',
    subtitle: 'Lista automática de compras e ingredientes necessários.'
  },
  diario: {
    title: 'Diário / Tracking',
    subtitle: 'Acompanha as tuas calorias, o histórico semanal e o teu progresso.'
  },
  'tuas-receitas': {
    title: 'Tuas Receitas',
    subtitle: 'Favoritos e histórico de receitas numa única página.'
  },
  perfil: {
    title: 'Perfil',
    subtitle: 'Dados físicos, objetivo, dieta, alergénios e localização.'
  },
  definicoes: {
    title: 'Definições',
    subtitle: 'Preferências da conta, notificações e opções da aplicação.'
  }
}

const containerStyle = computed(() => {
  if (colorBlindnessMode.value === 'none') return {}
  return { filter: `url(#${colorBlindnessMode.value})` }
})

onMounted(() => {
  console.log('SiteHomePage onMounted')
  fetchUser().catch(err => console.error('fetchUser failed in SiteHomePage:', err))
  fetchWaterIntake()
  startWaterTimer()
  
  const initialSection = resolveSectionFromRoute(route.params.section)
  const initialSubsection = typeof route.params.subsection === 'string' ? route.params.subsection : ''
  activeSection.value = initialSection
  if (initialSection === 'tenho-fome') {
    negotiatorRouteMode.value = negotiatorSubSlugToMode[initialSubsection] || ''
  } else {
    negotiatorRouteMode.value = ''
  }
  syncRouteWithSection(
    initialSection,
    true,
    initialSection === 'tenho-fome' ? negotiatorModeToSubSlug[negotiatorRouteMode.value] : ''
  )

  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
  } else {
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  const savedColorMode = localStorage.getItem('colorBlindnessMode')
  if (savedColorMode) {
    colorBlindnessMode.value = savedColorMode
  }
})

watch(isDarkMode, (value) => {
  localStorage.setItem('theme', value ? 'dark' : 'light')
  if (value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})

watch(
  () => [route.params.section, route.params.subsection],
  ([sectionSlug, subsection]) => {
    const nextSection = resolveSectionFromRoute(sectionSlug)
    const normalizedSubsection = typeof subsection === 'string' ? subsection : ''

    if (nextSection !== activeSection.value) {
      activeSection.value = nextSection
    }

    if (nextSection === 'tenho-fome') {
      negotiatorRouteMode.value = negotiatorSubSlugToMode[normalizedSubsection] || ''
    } else {
      negotiatorRouteMode.value = ''
    }

    const expectedSection = sectionIdToSlug[nextSection]
    const expectedSub = nextSection === 'tenho-fome'
      ? negotiatorModeToSubSlug[negotiatorRouteMode.value]
      : ''

    if (sectionSlug !== expectedSection || normalizedSubsection !== expectedSub) {
      syncRouteWithSection(nextSection, true, expectedSub)
    }
  }
)

onUnmounted(() => {
  if (waterInterval) clearInterval(waterInterval)
})
</script>

<template>
  <!-- SVG Filters for Color Blindness -->
  <svg style="position: absolute; width: 0; height: 0; overflow: hidden;" aria-hidden="true">
    <defs>
      <filter id="protanopia">
        <feColorMatrix type="matrix" values="0.567, 0.433, 0, 0, 0 0.558, 0.442, 0, 0, 0 0, 0.242, 0.758, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
      <filter id="deuteranopia">
        <feColorMatrix type="matrix" values="0.625, 0.375, 0, 0, 0 0.7, 0.3, 0, 0, 0 0, 0.3, 0.7, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
      <filter id="tritanopia">
        <feColorMatrix type="matrix" values="0.95, 0.05, 0, 0, 0 0, 0.433, 0.567, 0, 0 0, 0.475, 0.525, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
      <filter id="achromatopsia">
        <feColorMatrix type="matrix" values="0.299, 0.587, 0.114, 0, 0 0.299, 0.587, 0.114, 0, 0 0.299, 0.587, 0.114, 0, 0 0, 0, 0, 1, 0"/>
      </filter>
    </defs>
  </svg>

  <!-- Water Reminder Toast (Global) -->
  <div v-if="showWaterReminder" class="water-toast-global">
    <div class="water-content">
      <span class="water-icon">💧</span>
      <div>
        <h4>Hora de beber água!</h4>
        <p>Mantém-te hidratado. Já passaram 30 minutos.</p>
      </div>
    </div>
    <div class="water-actions">
      <button @click="removeWaterGlobal" class="btn-snooze" style="border-color: #0891b2; color: #0891b2;">Remover (-250ml)</button>
      <button @click="addWaterGlobal" class="btn-drink">Beber (+250ml)</button>
      <button @click="snoozeWaterReminder" class="btn-snooze">Agora não</button>
    </div>
  </div>

  <div class="site-layout" :class="{ 'theme-dark': isDarkMode }" :style="containerStyle">
    <SidebarNav :sections="sections" :active-section="activeSection" @select="selectSection" />

    <main class="content">
      <div v-if="activeSection === 'inicio'">
        <DashboardHome 
          :key="dashboardKey"
          @navigate="selectSection" 
          @update-water="fetchWaterIntake"
        />
      </div>

      <div v-else-if="activeSection === 'tenho-fome'">
        <Negotiator
          :route-mode="negotiatorRouteMode"
          :initial-craving="globalCraving"
          @choice="handleNegotiationChoice"
          @route-mode-change="handleNegotiatorModeChange"
          @navigate="selectSection"
          @negotiated="globalCraving = ''"
        />
      </div>
      
      <div v-else-if="activeSection === 'gerar-receita'">
        <VisionRecipe />
      </div>

      <div v-else-if="activeSection === 'visualizador'" class="full-height-section">
        <VolumeComparison :is-dark-mode="isDarkMode" />
      </div>

      <div v-else-if="activeSection === 'supermercados'">
        <ShopFinder 
          :initial-ingredients="shopParams.ingredients" 
          mode="shop" 
        />
      </div>

      <div v-else-if="activeSection === 'diario'">
        <DiaryTracking :key="diaryKey" />
      </div>
      
      <div v-else-if="activeSection === 'tuas-receitas'">
        <YourRecipesPage @navigate="selectSection" />
      </div>

      <div v-else-if="activeSection === 'definicoes'">
        <SettingsPage 
          :is-dark-mode="isDarkMode" 
          :color-blindness-mode="colorBlindnessMode"
          @toggle-theme="toggleTheme" 
          @update-color-blindness="updateColorBlindness"
        />
      </div>

      <div v-else-if="activeSection === 'perfil'">
        <ProfilePanel />
      </div>

      <div v-else>
        <h1>{{ sectionContent[activeSection].title }}</h1>
        <p>{{ sectionContent[activeSection].subtitle }}</p>
      </div>
    </main>

    <!-- Assistant Chat FAB -->
    <button class="chat-fab" @click="toggleChat" :class="{ 'chat-fab-open': isChatOpen }">
      <span v-if="!isChatOpen">💬</span>
      <span v-else>✕</span>
    </button>

    <!-- Assistant Chat Window -->
    <div v-if="isChatOpen" class="chat-assistant-window fade-in">
      <header class="chat-assistant-header">
        <div class="chat-header-info">
          <div class="bot-photo-container">
            <img :src="chatbotImg" alt="Nutra" class="bot-photo" />
            <span class="online-status"></span>
          </div>
          <div>
            <h4>Nutra</h4>
            <p>Assistente Inteligente</p>
          </div>
        </div>
        <button 
          class="voice-toggle-btn" 
          @click="toggleVoiceAndUnlock"
          :class="{ 'voice-active': isVoiceEnabled }"
          title="Ativar/Desativar Voz"
        >
          {{ isVoiceEnabled ? '🔊' : '🔈' }}
        </button>
      </header>
      
      <div class="chat-messages-box">
        <div 
          v-for="(msg, idx) in chatMessages" 
          :key="idx" 
          class="chat-bubble-wrap"
          :class="msg.role"
        >
          <div class="chat-bubble">
            {{ msg.content }}
            <CasinoGame v-if="msg.type === 'casino'" />
            <NutritionQuiz v-if="msg.type === 'quiz'" />
            <UnitConverter v-if="msg.type === 'converter'" />
            <FastingTimer v-if="msg.type === 'timer'" />
          </div>
        </div>
        <div v-if="isChatLoading" class="chat-bubble-wrap assistant">
          <div class="chat-bubble loading-bubble">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <form class="chat-input-area" @submit.prevent="sendChatMessage">
        <button 
          type="button" 
          class="mic-btn" 
          @click="startListening" 
          :class="{ 'mic-listening': isListening }"
        >
          🎤
        </button>
        <input 
          v-model="chatInput" 
          placeholder="Pergunta como fazer algo..." 
          autofocus
        />
        <button type="submit" :disabled="isChatLoading || !chatInput.trim()">
          Enviar
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.site-layout {
  --bg-main: #f2f6f9;
  --bg-elevated: #ffffff;
  --text-main: #11263f;
  --text-muted: #54667e;
  --line: #dbe3eb;
  --sidebar-bg: #ffffff;
  --sidebar-text: #54667e;
  --menu-hover-bg: #f3f7fb;
  --menu-active-bg: #e3f7f2;
  --menu-active-text: #0a705d;
  --menu-highlight-bg: #fff1e7;
  --menu-highlight-hover-bg: #ffe5d2;
  --menu-highlight-active-bg: #ffd9bd;
  --menu-highlight-text: #9a3412;
  --menu-highlight-active-text: #7c2d12;

  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
  background: linear-gradient(160deg, #f8fbff 0%, var(--bg-main) 100%);
  color: var(--text-main);
  font-family: Sora, 'Segoe UI', Tahoma, sans-serif;
}

.site-layout.theme-dark {
  --bg-main: #06090f;
  --bg-elevated: #0f172a;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --line: #1e293b;
  --sidebar-bg: #020617;
  --sidebar-text: #ffffff;
  --menu-hover-bg: #1e293b;
  --menu-active-bg: #064e3b;
  --menu-active-text: #34d399;
  --menu-highlight-bg: #451a03;
  --menu-highlight-hover-bg: #78350f;
  --menu-highlight-active-bg: #92400e;
  --menu-highlight-text: #fed7aa;
  --menu-highlight-active-text: #ffedd5;
  background: radial-gradient(circle at 0% 0%, #0f172a 0%, #06090f 50%, #020617 100%);
}

.content {
  padding: 44px;
}

.content h1 {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.content p {
  margin-top: 12px;
  max-width: 60ch;
  color: var(--text-muted);
  font-size: 1.02rem;
}

.full-height-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
}

.site-layout.theme-dark :deep(.shop-finder .location-setup),
.site-layout.theme-dark :deep(.shop-finder .controls),
.site-layout.theme-dark :deep(.shop-finder .shop-item),
.site-layout.theme-dark :deep(.negotiator-container .option-card),
.site-layout.theme-dark :deep(.negotiator-container input) {
  background: var(--bg-elevated);
  border-color: var(--line);
  color: var(--text-main);
}

.site-layout.theme-dark :deep(.shop-finder input),
.site-layout.theme-dark :deep(.shop-finder .search-wrapper input) {
  background: #0f1728;
  border-color: var(--line);
  color: var(--text-main);
}

.site-layout.theme-dark :deep(.shop-finder label),
.site-layout.theme-dark :deep(.shop-finder .radius-control),
.site-layout.theme-dark :deep(.shop-finder .location-label),
.site-layout.theme-dark :deep(.negotiator-container .recipe-content ul),
.site-layout.theme-dark :deep(.negotiator-container .btn-back) {
  color: var(--text-muted);
}

.site-layout.theme-dark :deep(.shop-finder .suggestions),
.site-layout.theme-dark :deep(.shop-finder .suggestions li) {
  background: var(--bg-elevated);
  color: var(--text-main);
  border-color: var(--line);
}

@media (max-width: 860px) {
  .site-layout {
    grid-template-columns: 1fr;
  }
}

/* Water Toast Global Styles */
.water-toast-global {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: var(--bg-elevated);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(8, 145, 178, 0.25);
  border: 1px solid var(--line);
  z-index: 2000;
  width: 320px;
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.water-content {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.water-icon {
  font-size: 2rem;
  background: #ecfeff;
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.water-content h4 {
  margin: 0 0 4px;
  font-size: 1.1rem;
  color: var(--text-main);
}

.water-content p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.water-actions {
  display: flex;
  gap: 10px;
}

.btn-drink {
  flex: 1;
  background: #0891b2;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.btn-drink:hover { background: #0e7490; }

.btn-snooze {
  flex: 1;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--text-muted);
  padding: 10px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.btn-snooze:hover { background: var(--bg-main); }

/* Assistant Chat Styles */
.chat-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--menu-active-text);
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(10, 112, 93, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2100;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: fabPulse 2s infinite;
  overflow: hidden;
  padding: 0;
}

@keyframes fabPulse {
  0% { box-shadow: 0 0 0 0 rgba(10, 112, 93, 0.4); }
  70% { box-shadow: 0 0 0 15px rgba(10, 112, 93, 0); }
  100% { box-shadow: 0 0 0 0 rgba(10, 112, 93, 0); }
}

.chat-fab:hover {
  transform: scale(1.1) rotate(5deg);
}

.chat-fab-open {
  background: #ef4444;
  box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3);
}

.chat-assistant-window {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 380px;
  height: 550px;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.15);
  z-index: 2100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-assistant-header {
  background: var(--menu-active-text);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.voice-toggle-btn {
  background: rgba(255,255,255,0.15);
  border: none;
  font-size: 1.2rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-toggle-btn:hover { background: rgba(255,255,255,0.25); }
.voice-toggle-btn.voice-active { background: white; }

.chat-header-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.bot-photo-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.bot-photo {
  width: 100%;
  height: 100%;
  border-radius: 14px;
  object-fit: cover;
  border: 2px solid rgba(255,255,255,0.3);
}

.online-status {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #22c55e;
  border: 2px solid var(--menu-active-text);
  border-radius: 50%;
}

.chat-header-info h4 { margin: 0; font-size: 1.15rem; font-weight: 800; }
.chat-header-info p { margin: 0; font-size: 0.85rem; opacity: 0.9; }

.chat-messages-box {
  flex: 1;
  padding: 24px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.02));
}

.chat-bubble-wrap {
  display: flex;
  width: 100%;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-bubble-wrap.user { justify-content: flex-end; }
.chat-bubble-wrap.assistant { justify-content: flex-start; }

.chat-bubble {
  max-width: 85%;
  padding: 12px 18px;
  border-radius: 20px;
  font-size: 0.95rem;
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.user .chat-bubble {
  background: linear-gradient(135deg, var(--menu-active-text), #0d9488);
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant .chat-bubble {
  background: var(--bg-elevated);
  color: var(--text-main);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--line);
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid var(--line);
  display: flex;
  gap: 10px;
  background: var(--bg-elevated);
}

.mic-btn {
  background: var(--bg-main);
  border: 1.5px solid var(--line);
  border-radius: 14px;
  width: 46px;
  height: 46px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mic-btn:hover { background: var(--line); }
.mic-listening {
  background: #fee2e2 !important;
  border-color: #ef4444 !important;
  animation: micPulse 1.5s infinite;
}

@keyframes micPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.chat-input-area input {
  flex: 1;
  border: 1.5px solid var(--line);
  background: var(--bg-main);
  color: var(--text-main);
  padding: 12px 18px;
  border-radius: 14px;
  outline: none;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.chat-input-area input:focus {
  border-color: var(--menu-active-text);
}

.chat-input-area button {
  background: var(--menu-active-text);
  color: white;
  border: none;
  padding: 0 20px;
  border-radius: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-input-area button:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

.chat-input-area button:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-bubble {
  display: flex;
  gap: 4px;
  padding: 12px 20px !important;
}

.loading-bubble span {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.loading-bubble span:nth-child(1) { animation-delay: -0.32s; }
.loading-bubble span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@media (max-width: 450px) {
  .chat-assistant-window {
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
}
</style>
