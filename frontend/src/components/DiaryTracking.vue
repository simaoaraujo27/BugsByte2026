<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { auth, API_URL } from '@/auth'
import { useUser } from '@/store/userStore'

const { 
  targetCalories, 
  customMacroPercents, 
  saveMacroPercents 
} = useUser()

// Auto-save changes to server with a slight delay to avoid spamming
let saveTimeout = null
watch(customMacroPercents, (newVal) => {
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(() => {
    saveMacroPercents(newVal)
  }, 1000)
}, { deep: true })

const DEFAULT_GOAL = computed(() => targetCalories.value || 1800)
const mealSections = [
  { id: 'breakfast', label: 'Pequeno-almoço', icon: '🥣' },
  { id: 'lunch', label: 'Almoço', icon: '🍛' },
  { id: 'snack', label: 'Lanche', icon: '🍎' },
  { id: 'dinner', label: 'Jantar', icon: '🍽️' },
  { id: 'extras', label: 'Extras', icon: '🍫' }
]

const dataByDate = ref({})
const selectedDate = ref(new Date())
const isLoading = ref(false)
const composerFor = ref('')
const composerMode = ref('manual') // 'manual' or 'auto'
const autoLoading = ref(false)

const foodSearch = ref({
  query: '',
  loading: false,
  error: '',
  results: []
})
const foodSearchModalOpen = ref(false)
const foodFilters = ref({
  source: 'all',
  sort: 'relevance',
  maxCalories: '',
  minProtein: ''
})
const selectedFoodPer100g = ref(null)
let foodSearchDebounce = null
const mealDraft = ref({
  name: '',
  grams: '',
  calories: '',
  protein: '',
  carbs: '',
  fat: '',
  source: 'manual'
})
const autoDraft = ref({
  text: ''
})
const isListening = ref(false)
let recognitionInstance = null

const toggleListening = async () => {
  if (isListening.value) {
    if (recognitionInstance) {
      recognitionInstance.stop()
    }
    return
  }

  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('O seu navegador não suporta reconhecimento de voz. Use Chrome, Edge ou Safari.')
    return
  }

  try {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognitionInstance = new Recognition()
    
    // Explicitly set language to Portuguese (Portugal)
    recognitionInstance.lang = 'pt-PT'
    recognitionInstance.continuous = false
    recognitionInstance.interimResults = true
    recognitionInstance.maxAlternatives = 1
    
    // Some browsers might need the lang property set on the prototype or early
    if ('lang' in recognitionInstance) {
      recognitionInstance.lang = 'pt-PT'
    }
    
    recognitionInstance.onstart = () => {
      console.log('Speech recognition started')
      isListening.value = true
    }
    
    recognitionInstance.onresult = (event) => {
      console.log('Speech recognition onresult triggered', event)
      let transcript = ''
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          transcript += result[0].transcript + ' '
        } else {
          transcript += result[0].transcript
        }
      }
      
      if (transcript.trim()) {
        autoDraft.value.text = transcript.trim()
      }
    }
    
    recognitionInstance.onerror = (event) => {
      console.error('Speech recognition error:', event.error, event)
      
      if (event.error === 'not-allowed' || event.error === 'permission-denied') {
        alert('Permissão de microfone negada. Clique no ícone de cadeado na barra de endereço.')
      } else if (event.error === 'audio-capture') {
        alert('Erro ao capturar áudio. Verifique se o microfone correto está selecionado nas definições do sistema e do browser.')
      } else if (event.error === 'no-speech') {
        console.log('Nenhuma fala detectada')
      } else if (event.error === 'network') {
        alert('Erro de rede. O reconhecimento de voz requer conexão à internet.')
      } else if (event.error !== 'aborted') {
        alert('Erro: ' + event.error)
      }
      
      stopListening()
    }
    
    recognitionInstance.onend = () => {
      console.log('Speech recognition ended')
      stopListening()
    }
    
    recognitionInstance.start()
    console.log('Speech recognition start() called')
  } catch (err) {
    console.error('Failed to start speech recognition:', err)
    stopListening()
    alert('Erro ao iniciar: ' + err.message)
  }
}

const stopListening = () => {
  isListening.value = false
  if (recognitionInstance) {
    try { recognitionInstance.stop() } catch (e) {}
    recognitionInstance = null
  }
}

const today = new Date()
today.setHours(12, 0, 0, 0)

const toDateKey = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const fromDateKey = (key) => {
  const [y, m, d] = key.split('-').map(Number)
  return new Date(y, m - 1, d, 12, 0, 0, 0)
}

const fetchDay = async (key) => {
  if (dataByDate.value[key]) return
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/diary/${key}`, {
      headers: auth.getAuthHeaders()
    })
    if (!res.ok) throw new Error('Falha ao carregar diário')
    const day = await res.json()
    dataByDate.value[key] = day
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const dateKey = computed(() => toDateKey(selectedDate.value))

const dayLabel = computed(() => {
  const dt = selectedDate.value
  return dt.toLocaleDateString('pt-PT', {
    weekday: 'long',
    day: '2-digit',
    month: 'long'
  })
})

const toNumber = (value) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

const round1 = (value) => Math.round(value * 10) / 10
const formatMealGrams = (value) => {
  const grams = toNumber(value)
  return grams > 0 ? `${round1(grams)} g` : '-- g'
}
const formatMacro = (value) => `${round1(toNumber(value))}g`

const buildEmptyDay = () => ({
  goal: DEFAULT_GOAL.value,
  meals: {
    breakfast: [],
    lunch: [],
    snack: [],
    dinner: [],
    extras: []
  }
})

const ensureDay = (key) => {
  fetchDay(key)
}

const currentDay = computed(() => {
  const day = dataByDate.value[dateKey.value]
  if (!day) return buildEmptyDay()
  
  const normalized = {
    goal: day.goal,
    meals: {
      breakfast: day.meals.filter(m => m.section === 'breakfast'),
      lunch: day.meals.filter(m => m.section === 'lunch'),
      snack: day.meals.filter(m => m.section === 'snack'),
      dinner: day.meals.filter(m => m.section === 'dinner'),
      extras: day.meals.filter(m => m.section === 'extras')
    }
  }
  return normalized
})

const allMealsToday = computed(() => {
  const mealsObj = currentDay.value.meals
  return Object.values(mealsObj).flat()
})

const consumedCalories = computed(() =>
  Math.round(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.calories), 0))
)

const consumedProtein = computed(() => round1(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.protein), 0)))
const consumedCarbs = computed(() => round1(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.carbs), 0)))
const consumedFat = computed(() => round1(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.fat), 0)))

const calorieGoal = computed(() => Math.max(1, DEFAULT_GOAL.value || toNumber(currentDay.value.goal)))
const deltaCalories = computed(() => calorieGoal.value - consumedCalories.value)

const progressPercent = computed(() => {
  if (!calorieGoal.value) return 0
  return Math.min(100, Math.round((consumedCalories.value / calorieGoal.value) * 100))
})

const exceededPercent = computed(() => {
  if (deltaCalories.value >= 0) return 0
  return Math.min(100, Math.round((Math.abs(deltaCalories.value) / calorieGoal.value) * 100))
})

const sectionTotal = (sectionId) =>
  Math.round((currentDay.value.meals[sectionId] || []).reduce((acc, item) => acc + toNumber(item.calories), 0))

const mealCount = computed(() => allMealsToday.value.length)

const macroCalories = computed(() => ({
  protein: consumedProtein.value * 4,
  carbs: consumedCarbs.value * 4,
  fat: consumedFat.value * 9
}))

const macroTotalCalories = computed(() =>
  macroCalories.value.protein + macroCalories.value.carbs + macroCalories.value.fat
)

const macroPercentages = computed(() => {
  if (!macroTotalCalories.value) return { protein: 0, carbs: 0, fat: 0 }
  return {
    protein: Math.round((macroCalories.value.protein / macroTotalCalories.value) * 100),
    carbs: Math.round((macroCalories.value.carbs / macroTotalCalories.value) * 100),
    fat: Math.round((macroCalories.value.fat / macroTotalCalories.value) * 100)
  }
})

const totalMacroPercent = computed(() => 
  toNumber(customMacroPercents.value.protein) + 
  toNumber(customMacroPercents.value.carbs) + 
  toNumber(customMacroPercents.value.fat)
)

const macroGoals = computed(() => {
  const total = calorieGoal.value
  const p = toNumber(customMacroPercents.value.protein) / 100
  const c = toNumber(customMacroPercents.value.carbs) / 100
  const f = toNumber(customMacroPercents.value.fat) / 100
  
  return {
    protein: Math.round((total * p) / 4),
    carbs: Math.round((total * c) / 4),
    fat: Math.round((total * f) / 9)
  }
})

const macroProgress = computed(() => ({
  protein: Math.min(100, Math.round((consumedProtein.value / (macroGoals.value.protein || 1)) * 100)),
  carbs: Math.min(100, Math.round((consumedCarbs.value / (macroGoals.value.carbs || 1)) * 100)),
  fat: Math.min(100, Math.round((consumedFat.value / (macroGoals.value.fat || 1)) * 100))
}))

const isDayOnTarget = (day) => {
  const mealsList = Array.isArray(day.meals) ? day.meals : []
  const total = mealsList.reduce((acc, item) => acc + toNumber(item.calories), 0)
  if (total === 0) return false
  return total <= toNumber(day.goal || DEFAULT_GOAL.value)
}

const weeklyDays = computed(() => {
  const cursor = new Date(selectedDate.value)
  const day = cursor.getDay()
  const mondayOffset = day === 0 ? -6 : 1 - day
  cursor.setDate(cursor.getDate() + mondayOffset)
  cursor.setHours(12, 0, 0, 0)

  const out = []
  for (let i = 0; i < 7; i += 1) {
    const d = new Date(cursor)
    d.setDate(cursor.getDate() + i)
    const key = toDateKey(d)
    const dayData = dataByDate.value[key] || buildEmptyDay()
    const hasMeals = Array.isArray(dayData.meals) ? dayData.meals.length > 0 : false
    out.push({
      key,
      date: d,
      dayName: d.toLocaleDateString('pt-PT', { weekday: 'short' }),
      dayNum: d.getDate(),
      active: key === dateKey.value,
      hasMeals,
      onTarget: isDayOnTarget(dayData)
    })
  }
  return out
})

const streakDays = computed(() => {
  let streak = 0
  const cursor = new Date(today)

  for (let i = 0; i < 365; i += 1) {
    const key = toDateKey(cursor)
    const day = normalizeDay(dataByDate.value[key])
    const hasMeals = mealSections.some((section) => day.meals[section.id]?.length)

    if (!hasMeals || !isDayOnTarget(day)) break
    streak += 1
    cursor.setDate(cursor.getDate() - 1)
  }

  return streak
})

const weeklyStats = computed(() => {
  const stats = { onTarget: 0, deficit: 0, daysWithData: 0 }
  const cursor = new Date(today)

  for (let i = 0; i < 7; i += 1) {
    const key = toDateKey(cursor)
    const day = normalizeDay(dataByDate.value[key])
    const total = mealSections.reduce((sum, section) => {
      const list = day.meals[section.id] || []
      return sum + list.reduce((acc, item) => acc + toNumber(item.calories), 0)
    }, 0)

    if (total > 0) {
      stats.daysWithData += 1
      if (total <= day.goal) {
        stats.onTarget += 1
        stats.deficit += day.goal - total
      }
    }

    cursor.setDate(cursor.getDate() - 1)
  }

  return stats
})

const insights = computed(() => {
  const list = []

  if (mealCount.value === 0) {
    list.push('Comece por adicionar a primeira refeição de hoje para acompanhar o progresso.')
    return list
  }

  if (deltaCalories.value >= 0) {
    if (deltaCalories.value <= 200) {
      list.push('Está muito perto do objetivo diário. Falta um ajuste pequeno.')
    } else {
      list.push(`Ainda tem ${deltaCalories.value} kcal disponíveis hoje.`)
    }
  } else {
    list.push(`Hoje já excedeu ${Math.abs(deltaCalories.value)} kcal. Amanhã pode compensar de forma ligeira.`)
  }

  if (macroPercentages.value.protein > 0 && macroPercentages.value.protein < 18) {
    list.push('A sua percentagem de proteína está baixa. Considere incluir uma fonte proteica no próximo prato.')
  }

  if (weeklyStats.value.daysWithData >= 4) {
    list.push(`Boa consistência: ${weeklyStats.value.onTarget} de ${weeklyStats.value.daysWithData} dias esta semana ficaram dentro do objetivo.`)
  }

  if (weeklyStats.value.deficit > 0) {
    const weeklyKg = weeklyStats.value.deficit / 7700
    const projection = (weeklyKg * 6).toFixed(1)
    list.push(`Se mantiver este ritmo, poderá variar cerca de ${projection} kg em 6 semanas.`)
  }

  return list.slice(0, 3)
})

const foodHistory = ref([])

const fetchFoodHistory = async () => {
  try {
    const res = await fetch(`${API_URL}/users/me/food-history?limit=20`, {
      headers: auth.getAuthHeaders()
    })
    if (!res.ok) throw new Error('Falha ao carregar histórico')
    foodHistory.value = await res.json()
  } catch (err) {
    console.error(err)
  }
}

const saveFoodHistory = async (food) => {
  try {
    await fetch(`${API_URL}/users/me/food-history`, {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({
        name: food.name,
        calories_per_100g: toNumber(food.calories_per_100g),
        protein_per_100g: toNumber(food.protein_per_100g),
        carbs_per_100g: toNumber(food.carbs_per_100g),
        fat_per_100g: toNumber(food.fat_per_100g),
        source: food.source || 'search'
      })
    })
    // Refresh history silently
    fetchFoodHistory()
  } catch (err) {
    console.error(err)
  }
}

const mergedHistory = computed(() => {
  const uniqueMap = new Map()

  // 1. Add API history first (presumed most recent/relevant if sorted by date desc)
  for (const item of foodHistory.value) {
    const key = item.name.trim().toLowerCase()
    uniqueMap.set(key, item)
  }

  // 2. Add local history from current visible days (if not already present)
  // We iterate backwards through days to get recent stuff
  const allDays = Object.values(dataByDate.value)
  for (const day of allDays) {
    if (!day || !day.meals) continue
    const flatMeals = mealSections.flatMap(s => day.meals[s.id] || [])
    
    // Reverse to process later items (if array is ordered by time added) ?? 
    // Actually day.meals order depends on array. Let's just process.
    for (const meal of flatMeals) {
      const grams = toNumber(meal.grams)
      if (!meal.name || grams <= 0) continue

      const key = meal.name.trim().toLowerCase()
      // If we already have this from API, skip (API source is preferred for accuracy)
      // OR overwrite if we prefer local? Let's stick with API preference for consistency.
      if (!uniqueMap.has(key)) {
        uniqueMap.set(key, {
          name: meal.name,
          source: 'recente',
          calories_per_100g: Math.round((toNumber(meal.calories) / grams) * 100),
          protein_per_100g: round1((toNumber(meal.protein) / grams) * 100),
          carbs_per_100g: round1((toNumber(meal.carbs) / grams) * 100),
          fat_per_100g: round1((toNumber(meal.fat) / grams) * 100),
        })
      }
    }
  }

  // Convert map to array
  return Array.from(uniqueMap.values()).slice(0, 30)
})

const openComposer = (sectionId) => {
  composerFor.value = composerFor.value === sectionId ? '' : sectionId
  foodSearchModalOpen.value = false
  foodSearch.value = { query: '', loading: false, error: '', results: [] }
  foodFilters.value = { source: 'all', sort: 'relevance', maxCalories: '', minProtein: '' }
  selectedFoodPer100g.value = null
  mealDraft.value = { name: '', grams: '', calories: '', protein: '', carbs: '', fat: '', source: 'manual' }
  autoDraft.value = { text: '' }
}

const estimateMacros = (calories) => {
  const protein = round1((calories * 0.25) / 4)
  const carbs = round1((calories * 0.45) / 4)
  const fat = round1((calories * 0.3) / 9)
  return { protein, carbs, fat }
}

const startListening = () => {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('O seu navegador não suporta reconhecimento de voz.')
    return
  }
  
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
  const recognition = new Recognition()
  
  recognition.lang = 'pt-PT'
  recognition.interimResults = false
  recognition.maxAlternatives = 1
  
  recognition.onstart = () => {
    isListening.value = true
  }
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    autoDraft.value.text = transcript
  }
  
  recognition.onerror = (event) => {
    console.error('Speech recognition error', event.error)
    isListening.value = false
  }
  
  recognition.onend = () => {
    isListening.value = false
  }
  
  recognition.start()
}

const calculateNutrition = async () => {
  if (!autoDraft.value.text.trim()) return
  autoLoading.value = true
  
  try {
    const res = await fetch(`${API_URL}/negotiator/nutrition`, {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ food_text: autoDraft.value.text })
    })
    
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Falha ao calcular.')
    
    // Populate manual fields with result
    mealDraft.value.name = data.name
    mealDraft.value.grams = data.estimated_grams
    mealDraft.value.calories = data.calories
    mealDraft.value.protein = data.protein
    mealDraft.value.carbs = data.carbs
    mealDraft.value.fat = data.fat
    mealDraft.value.source = 'IA'
    
    // Save directly and stay in auto mode
    await addMeal(composerFor.value, false)
    autoDraft.value.text = ''
  } catch (err) {
    console.error(err)
    alert(err.message)
  } finally {
    autoLoading.value = false
  }
}

const addMeal = async (sectionId, closeAfter = true) => {
  const name = mealDraft.value.name.trim()
  const grams = toNumber(mealDraft.value.grams)
  const calories = toNumber(mealDraft.value.calories)
  const source = mealDraft.value.source || 'manual'

  // Only name and calories are strictly required now
  if (!name || calories <= 0) {
    alert('Por favor, preencha o nome e as calorias.')
    return
  }

  let protein = toNumber(mealDraft.value.protein)
  let carbs = toNumber(mealDraft.value.carbs)
  let fat = toNumber(mealDraft.value.fat)

  if (protein === 0 && carbs === 0 && fat === 0) {
    const estimated = estimateMacros(calories)
    protein = estimated.protein
    carbs = estimated.carbs
    fat = estimated.fat
  }

  try {
    const res = await fetch(`${API_URL}/diary/${dateKey.value}/meals`, {
      method: 'POST',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({
        section: sectionId,
        name,
        grams: Math.round(grams),
        calories: Math.round(calories),
        protein,
        carbs,
        fat
      })
    })
    if (!res.ok) throw new Error('Falha ao adicionar refeição')
    const updatedDay = await res.json()
    dataByDate.value[dateKey.value] = updatedDay

    if (closeAfter) {
      composerFor.value = ''
      foodSearchModalOpen.value = false
    }
    foodSearch.value = { query: '', loading: false, error: '', results: [] }
    foodFilters.value = { source: 'all', sort: 'relevance', maxCalories: '', minProtein: '' }
    selectedFoodPer100g.value = null
    mealDraft.value = { name: '', grams: '', calories: '', protein: '', carbs: '', fat: '', source: 'manual' }

    // Save to history for future suggestions
    // Calculate per 100g
    if (grams > 0) {
      const ratio = 100 / grams
      saveFoodHistory({
        name,
        source: 'manual',
        calories_per_100g: calories * ratio,
        protein_per_100g: protein * ratio,
        carbs_per_100g: carbs * ratio,
        fat_per_100g: fat * ratio
      })
    }
  } catch (err) {
    console.error(err)
    alert('Erro ao adicionar refeição.')
  }
}

const removeMeal = async (sectionId, itemId) => {
  try {
    const res = await fetch(`${API_URL}/diary/meals/${itemId}`, {
      method: 'DELETE',
      headers: auth.getAuthHeaders()
    })
    if (!res.ok) throw new Error('Falha ao remover refeição')
    const updatedDay = await res.json()
    dataByDate.value[dateKey.value] = updatedDay
  } catch (err) {
    console.error(err)
    alert('Erro ao remover refeição.')
  }
}

const shiftDay = (delta) => {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() + delta)
  d.setHours(12, 0, 0, 0)
  selectedDate.value = d
}

const setSelectedDay = (dateObj) => {
  const d = new Date(dateObj)
  d.setHours(12, 0, 0, 0)
  selectedDate.value = d
}

const updateGoal = async (event) => {
  const next = Math.max(1000, Math.min(6000, toNumber(event.target.value) || DEFAULT_GOAL.value))
  try {
    const res = await fetch(`${API_URL}/diary/${dateKey.value}/goal`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({ goal: next })
    })
    if (!res.ok) throw new Error('Falha ao atualizar meta')
    const updatedDay = await res.json()
    dataByDate.value[dateKey.value] = updatedDay
  } catch (err) {
    console.error(err)
    alert('Erro ao atualizar meta.')
  }
}

const openFoodSearchModal = () => {
  foodSearchModalOpen.value = true
  fetchFoodHistory()
}

const closeFoodSearchModal = () => {
  foodSearchModalOpen.value = false
}

const applyFoodByGrams = (foodPer100g, gramsInput) => {
  const grams = toNumber(gramsInput)
  if (!foodPer100g || grams <= 0) return
  const ratio = grams / 100
  mealDraft.value.calories = Math.round(foodPer100g.calories_per_100g * ratio)
  mealDraft.value.protein = round1(foodPer100g.protein_per_100g * ratio)
  mealDraft.value.carbs = round1(foodPer100g.carbs_per_100g * ratio)
  mealDraft.value.fat = round1(foodPer100g.fat_per_100g * ratio)
}

const chooseFoodSuggestion = (food) => {
  selectedFoodPer100g.value = food
  mealDraft.value.name = food.name
  mealDraft.value.source = food.source
  if (!toNumber(mealDraft.value.grams)) {
    mealDraft.value.grams = 100
  }
  applyFoodByGrams(food, mealDraft.value.grams)
  saveFoodHistory(food)
  closeFoodSearchModal()
}

const searchFoodApi = async () => {
  const query = foodSearch.value.query.trim()
  if (!query) return

  foodSearch.value.loading = true
  foodSearch.value.error = ''
  foodSearch.value.results = []

  try {
    const res = await fetch(`${API_URL}/foods/search?q=${encodeURIComponent(query)}&page_size=8`, {
      headers: auth.getAuthHeaders()
    })
    if (!res.ok) throw new Error('Falha na pesquisa de alimentos')
    const data = await res.json()
    foodSearch.value.results = Array.isArray(data) ? data : []
    if (foodSearch.value.results.length === 0) {
      foodSearch.value.error = 'Sem resultados para esse alimento.'
    }
  } catch (error) {
    foodSearch.value.error = error instanceof TypeError
      ? 'Servidor indisponível para pesquisa.'
      : (error.message || 'Erro ao pesquisar alimentos.')
  } finally {
    foodSearch.value.loading = false
  }
}

const filteredFoodResults = computed(() => {
  const source = foodFilters.value.source
  const maxCalories = toNumber(foodFilters.value.maxCalories)
  const minProtein = toNumber(foodFilters.value.minProtein)
  const sort = foodFilters.value.sort

  let list = [...foodSearch.value.results]

  if (source !== 'all') {
    list = list.filter((item) => item.source === source)
  }
  if (maxCalories > 0) {
    list = list.filter((item) => toNumber(item.calories_per_100g) <= maxCalories)
  }
  if (minProtein > 0) {
    list = list.filter((item) => toNumber(item.protein_per_100g) >= minProtein)
  }

  if (sort === 'kcal_asc') {
    list.sort((a, b) => toNumber(a.calories_per_100g) - toNumber(b.calories_per_100g))
  } else if (sort === 'kcal_desc') {
    list.sort((a, b) => toNumber(b.calories_per_100g) - toNumber(a.calories_per_100g))
  } else if (sort === 'protein_desc') {
    list.sort((a, b) => toNumber(b.protein_per_100g) - toNumber(a.protein_per_100g))
  }

  return list
})

const displayedFoodResults = computed(() => {
  const hasQuery = foodSearch.value.query.trim().length > 0;

  // If user is actively searching, show API results
  if (hasQuery) {
    return filteredFoodResults.value;
  }

  // Otherwise, show merged history
  return mergedHistory.value;
})

onMounted(() => {
  ensureDay(dateKey.value)
})

onUnmounted(() => {
  stopListening()
})

watch(dateKey, (key) => {
  ensureDay(key)
})

watch(
  () => mealDraft.value.grams,
  (grams) => {
    if (selectedFoodPer100g.value) {
      applyFoodByGrams(selectedFoodPer100g.value, grams)
    }
  }
)

watch(
  () => foodSearch.value.query,
  (query) => {
    const term = query.trim()
    if (foodSearchDebounce) clearTimeout(foodSearchDebounce)
    if (term.length < 2) return

    foodSearchDebounce = setTimeout(() => {
      searchFoodApi()
    }, 400)
  }
)
</script>

<template>
  <section class="diary-page">
    <header class="diary-header">
      <div>
        <h1>Diário / Tracking</h1>
        <p class="sub">Acompanhe as suas calorias, refeições e consistência diária.</p>
      </div>

      <div class="date-nav">
        <button type="button" class="nav-btn" @click="shiftDay(-1)">◀</button>
        <strong>{{ dayLabel }}</strong>
        <button type="button" class="nav-btn" @click="shiftDay(1)">▶</button>
      </div>
    </header>

    <article class="summary-card">
      <div class="summary-main">
        <h2>Objetivo diário:  {{ consumedCalories }} / {{ calorieGoal }} kcal</h2>
        <p v-if="deltaCalories >= 0" class="state-ok">Faltam {{ deltaCalories }} kcal para o objetivo.</p>
        <p v-else class="state-over">+{{ Math.abs(deltaCalories) }} kcal acima do objetivo.</p>
      </div>

      <div class="progress-wrap" aria-label="Progresso calórico">
        <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        <div v-if="exceededPercent > 0" class="progress-over" :style="{ width: `${exceededPercent}%` }"></div>
      </div>
    </article>

    <div class="weekly-strip">
      <button
        v-for="day in weeklyDays"
        :key="day.key"
        type="button"
        class="week-day"
        :class="{ active: day.active, good: day.hasMeals && day.onTarget, over: day.hasMeals && !day.onTarget }"
        @click="setSelectedDay(day.date)"
      >
        <span>{{ day.dayName }}</span>
        <strong>{{ day.dayNum }}</strong>
      </button>
    </div>

    <div class="grid">
      <section class="meals-column">
        <article v-for="section in mealSections" :key="section.id" class="meal-card">
          <header class="meal-head">
            <h3>{{ section.icon }} {{ section.label }}</h3>
            <button type="button" class="add-btn" @click="openComposer(section.id)">+ adicionar</button>
          </header>

          <div v-if="composerFor === section.id" class="composer">
            <div class="composer-tabs">
              <button 
                :class="{ active: composerMode === 'manual' }" 
                @click="composerMode = 'manual'"
              >
                Manual
              </button>
              <button 
                :class="{ active: composerMode === 'auto' }" 
                @click="composerMode = 'auto'"
              >
                ✨ Automático (IA)
              </button>
              <button type="button" class="search-food-btn" @click="openFoodSearchModal">
                🔍 Histórico
              </button>
            </div>

            <div v-if="composerMode === 'manual'" class="mode-manual">
              <div class="form-group-diary">
                <label>Alimento</label>
                <input v-model="mealDraft.name" type="text" placeholder="Ex: Frango Grelhado" />
              </div>

              <p v-if="selectedFoodPer100g" class="selected-food">
                ✅ Selecionado: <strong>{{ selectedFoodPer100g.name }}</strong>
              </p>

              <div class="manual-grid-diary">
                <div class="form-group-diary">
                  <label>Peso (g)</label>
                  <input v-model="mealDraft.grams" type="number" min="1" placeholder="g" />
                </div>
                <div class="form-group-diary">
                  <label>Calorias (kcal)</label>
                  <input v-model="mealDraft.calories" type="number" min="1" placeholder="kcal" />
                </div>
              </div>

              <div class="macro-inputs-diary">
                <div class="form-group-diary">
                  <label>Prot. (g)</label>
                  <input v-model="mealDraft.protein" type="number" min="0" step="0.1" placeholder="g" />
                </div>
                <div class="form-group-diary">
                  <label>Hidr. (g)</label>
                  <input v-model="mealDraft.carbs" type="number" min="0" step="0.1" placeholder="g" />
                </div>
                <div class="form-group-diary">
                  <label>Gord. (g)</label>
                  <input v-model="mealDraft.fat" type="number" min="0" step="0.1" placeholder="g" />
                </div>
              </div>

              <div class="composer-actions">
                <button type="button" class="save-btn" @click="addMeal(section.id)">Guardar Refeição</button>
                <button type="button" class="cancel-btn" @click="openComposer('')">Cancelar</button>
              </div>
            </div>

            <div v-else class="mode-auto">
              <p class="helper-text">Descreva o que comeu e a quantidade. A IA calculará os macros.</p>
              <div class="voice-input-wrapper">
                <input 
                  v-model="autoDraft.text" 
                  type="text" 
                  placeholder="Ex: 1 banana média e 200ml de leite" 
                  @keyup.enter="calculateNutrition"
                />
                <button 
                  type="button" 
                  class="mic-btn" 
                  :class="{ active: isListening }"
                  :title="isListening ? 'Clique para parar a gravação' : 'Clique para falar'"
                  @click="toggleListening"
                >
                  🎤
                </button>
              </div>
              <div class="composer-actions">
                <button type="button" class="save-btn" :disabled="autoLoading" @click="calculateNutrition">
                  {{ autoLoading ? 'A calcular...' : '✨ Calcular Macros' }}
                </button>
                <button type="button" class="cancel-btn" @click="openComposer('')">Cancelar</button>
              </div>
            </div>
          </div>

          <ul v-if="currentDay.meals[section.id].length" class="meal-list">
            <li v-for="item in currentDay.meals[section.id]" :key="item.id">
              <div>
                <strong>{{ item.name }}</strong>
                <small>{{ formatMealGrams(item.grams) }} total · {{ formatMacro(item.fat) }} G · {{ formatMacro(item.protein) }} P · {{ formatMacro(item.carbs) }} H</small>
              </div>
              <div class="right">
                <span>{{ item.calories }} kcal</span>
                <button type="button" class="delete-btn" @click="removeMeal(section.id, item.id)">apagar</button>
              </div>
            </li>
          </ul>
          <p v-else class="empty">Ainda sem registos neste bloco.</p>

          <footer class="meal-total">Total {{ section.label }}: <strong>{{ sectionTotal(section.id) }} kcal</strong></footer>
        </article>
      </section>

      <aside class="stats-column">
        <article class="side-card macro-panel">
          <h3>Metas de Macros</h3>
          
          <div class="macro-item">
            <div class="macro-row">
              <span class="macro-label">Proteínas</span>
              <strong class="macro-val">{{ consumedProtein }}g <small>/ {{ macroGoals.protein }}g</small></strong>
            </div>
            <div class="bar-outer">
              <div class="fill-inner protein" :style="{ width: `${macroProgress.protein}%` }"></div>
            </div>
          </div>

          <div class="macro-item">
            <div class="macro-row">
              <span class="macro-label">Hidratos</span>
              <strong class="macro-val">{{ consumedCarbs }}g <small>/ {{ macroGoals.carbs }}g</small></strong>
            </div>
            <div class="bar-outer">
              <div class="fill-inner carbs" :style="{ width: `${macroProgress.carbs}%` }"></div>
            </div>
          </div>

          <div class="macro-item">
            <div class="macro-row">
              <span class="macro-label">Gorduras</span>
              <strong class="macro-val">{{ consumedFat }}g <small>/ {{ macroGoals.fat }}g</small></strong>
            </div>
            <div class="bar-outer">
              <div class="fill-inner fat" :style="{ width: `${macroProgress.fat}%` }"></div>
            </div>
          </div>
        </article>

        <article class="side-card customize-macros">
          <h3>Personalizar Percentagens</h3>
          <p class="sub-text">Ajuste a distribuição calórica dos seus macros.</p>
          
          <div class="macro-edit-grid">
            <div class="form-group-diary">
              <label>Proteína (%)</label>
              <input v-model.number="customMacroPercents.protein" type="number" min="0" max="100" />
            </div>
            <div class="form-group-diary">
              <label>Hidratos (%)</label>
              <input v-model.number="customMacroPercents.carbs" type="number" min="0" max="100" />
            </div>
            <div class="form-group-diary">
              <label>Gordura (%)</label>
              <input v-model.number="customMacroPercents.fat" type="number" min="0" max="100" />
            </div>
          </div>

          <div class="total-checker" :class="{ error: totalMacroPercent !== 100 }">
            Total: <strong>{{ totalMacroPercent }}%</strong>
            <span v-if="totalMacroPercent !== 100"> (Deve somar 100%)</span>
            <span v-else class="success-text"> ✅</span>
          </div>
        </article>

        <article class="side-card">
          <h3>Sugestões</h3>
          <ul class="insights">
            <li v-if="mealCount === 0">Comece por adicionar a primeira refeição de hoje.</li>
            <li v-else-if="deltaCalories >= 0">Ainda tem {{ deltaCalories }} kcal disponíveis hoje.</li>
            <li v-else>Hoje já excedeu {{ Math.abs(deltaCalories) }} kcal.</li>
          </ul>
        </article>
      </aside>
    </div>

    <div v-if="foodSearchModalOpen" class="food-modal-overlay" @click.self="closeFoodSearchModal">
      <div class="food-modal">
        <div class="food-modal-head">
          <h3>Pesquisar alimento</h3>
          <button type="button" class="modal-close" @click="closeFoodSearchModal">✕</button>
        </div>

        <div class="food-search-row">
          <input
            v-model="foodSearch.query"
            type="text"
            placeholder="Procurar alimento..."
          />
        </div>

        <p v-if="foodSearch.error" class="search-error">{{ foodSearch.error }}</p>
        
        <div v-if="!foodSearch.error">
          <p v-if="!foodSearch.query.trim()" class="search-empty">Sugestões do seu histórico:</p>
          
          <ul v-if="displayedFoodResults.length > 0" class="food-suggestions">
            <li v-for="food in displayedFoodResults" :key="`${food.source}-${food.name}`">
              <button type="button" @click="chooseFoodSuggestion(food)">
                <div class="food-info">
                  <strong>{{ food.name }}</strong>
                  <span class="food-source-badge">{{ food.source === 'manual' ? 'recente' : food.source }}</span>
                </div>
                <small>{{ food.calories_per_100g }} kcal · P {{ food.protein_per_100g }}g · H {{ food.carbs_per_100g }}g · G {{ food.fat_per_100g }}g (100g)</small>
              </button>
            </li>
          </ul>
          <p v-else-if="foodSearch.query.trim() && !foodSearch.loading" class="search-empty">
            Sem resultados para a sua pesquisa.
          </p>
        </div>
        </div>
    </div>
  </section>
</template>

<style scoped>
.diary-page {
  max-width: 1200px;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.diary-header h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
}

.sub {
  margin-top: 6px;
  color: var(--text-muted);
}

.date-nav {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 12px;
  padding: 8px 12px;
}

.date-nav strong {
  text-transform: capitalize;
}

.nav-btn {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 8px;
  width: 30px;
  height: 30px;
  cursor: pointer;
}

.summary-card {
  margin-top: 18px;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 14px;
  padding: 18px;
}

.summary-main h2 {
  margin: 0;
  font-size: clamp(1.3rem, 2.5vw, 1.9rem);
}

.summary-main p {
  margin: 4px 0 0;
}

.state-ok {
  color: #0ea372;
}

.state-over {
  color: #e85d5d;
}

.goal-control {
  margin-top: 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.goal-control input {
  width: 96px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: transparent;
  color: var(--text-main);
  padding: 6px 8px;
  /* Remove arrows */
  -moz-appearance: textfield;
  appearance: textfield;
}

.goal-control input::-webkit-outer-spin-button,
.goal-control input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.progress-wrap {
  margin-top: 14px;
  position: relative;
  height: 12px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.25);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #22c5a5);
}

.progress-over {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(90deg, #fb7185, #ef4444);
}

.weekly-strip {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.week-day {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  color: var(--text-main);
  border-radius: 10px;
  padding: 8px 6px;
  cursor: pointer;
  display: grid;
  gap: 2px;
  justify-items: center;
  text-transform: capitalize;
}

.week-day span {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.week-day.active {
  border-color: #14b8a6;
  box-shadow: 0 0 0 1px #14b8a6 inset;
}

.week-day.good {
  background: rgba(16, 185, 129, 0.16);
}

.week-day.over {
  background: rgba(244, 63, 94, 0.14);
}

.grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
}

.meals-column {
  display: grid;
  gap: 12px;
}

.meal-card {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 12px;
  padding: 14px;
}

.meal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.meal-head h3 {
  margin: 0;
  font-size: 1.03rem;
}

.add-btn {
  border: 1px solid #14b8a6;
  background: transparent;
  color: #14b8a6;
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
  font-weight: 700;
}

.composer {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}

.composer input {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 8px;
  padding: 8px 10px;
}

.food-search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.filter-row select,
.filter-row input {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 8px;
  padding: 8px 10px;
}

.selected-food {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.search-error {
  margin: 0;
  color: #ef5b74;
  font-size: 0.9rem;
}

.search-empty {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.food-suggestions {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 6px;
  max-height: 190px;
  overflow: auto;
}

.food-suggestions li button {
  width: 100%;
  text-align: left;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 8px;
  padding: 8px 9px;
  cursor: pointer;
}

.food-suggestions li button:hover {
  border-color: #14b8a6;
}

.food-suggestions strong {
  display: block;
}

.food-suggestions small {
  color: var(--text-muted);
}

.food-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.food-source-badge {
  font-size: 0.75rem;
  background: rgba(20, 184, 166, 0.1);
  color: #14b8a6;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.food-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 10, 20, 0.62);
  display: grid;
  place-items: center;
  z-index: 50;
  padding: 16px;
}

.food-modal {
  width: min(880px, 100%);
  max-height: 82vh;
  overflow: auto;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 14px;
  padding: 14px;
  display: grid;
  gap: 10px;
}

.food-modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.food-modal-head h3 {
  margin: 0;
}

.modal-close {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
}

.composer-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.composer-tabs button {
  flex: 1;
  padding: 8px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.composer-tabs button.active {
  background: rgba(20, 184, 166, 0.1);
  border-color: #14b8a6;
  color: #14b8a6;
}

.composer-tabs button.search-food-btn:hover {
  background: rgba(20, 184, 166, 0.05);
  border-color: #14b8a6;
  color: #14b8a6;
}

.mode-manual, .mode-auto {
  display: grid;
  gap: 12px;
}

.input-with-action {
  display: flex;
  gap: 8px;
}

.input-with-action input {
  flex: 1;
}

.ai-estimate-btn {
  background: rgba(20, 184, 166, 0.1);
  border: 1px solid #14b8a6;
  color: #14b8a6;
  border-radius: 8px;
  padding: 0 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.ai-estimate-btn:hover:not(:disabled) {
  background: #14b8a6;
  color: white;
}

.ai-estimate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: var(--line);
  color: var(--text-muted);
}

.form-group-diary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group-diary label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.manual-grid-diary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.macro-inputs-diary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.voice-input-wrapper {
  display: flex;
  gap: 8px;
}

.voice-input-wrapper input {
  flex: 1;
}

.mic-btn {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--bg-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.mic-btn.active {
  background: #ef5b74;
  color: white;
  border-color: #ef5b74;
  animation: pulse-mic 1.5s infinite;
}

@keyframes pulse-mic {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.helper-text {
  margin: 0 0 4px;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.composer-actions {
  display: flex;
  gap: 8px;
}

.save-btn,
.cancel-btn {
  border: 0;
  border-radius: 8px;
  padding: 7px 10px;
  cursor: pointer;
  font-weight: 700;
}

.save-btn {
  background: #14b8a6;
  color: #f8fffe;
}

.cancel-btn {
  background: rgba(148, 163, 184, 0.24);
  color: var(--text-main);
}

.meal-list {
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.meal-list li {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.meal-list strong {
  display: block;
}

.meal-list small {
  color: var(--text-muted);
}

.right {
  text-align: right;
  min-width: 110px;
}

.right span {
  display: block;
  font-weight: 700;
}

.delete-btn {
  margin-top: 3px;
  border: 0;
  background: transparent;
  color: #ef5b74;
  cursor: pointer;
  font-size: 0.82rem;
  text-decoration: underline;
}

.empty {
  margin-top: 10px;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.meal-total {
  margin-top: 10px;
  color: var(--text-muted);
}

.stats-column {
  display: grid;
  gap: 12px;
  align-content: start;
}

.side-card {
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 12px;
  padding: 14px;
}

.customize-macros h3 {
  margin: 0 0 4px;
  font-size: 1.1rem;
}

.sub-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.macro-edit-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.macro-edit-grid input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--bg-main);
  color: var(--text-main);
}

.total-checker {
  font-size: 0.9rem;
  padding: 8px;
  border-radius: 8px;
  background: rgba(148, 163, 184, 0.1);
  text-align: center;
}

.total-checker.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.success-text {
  color: #10b981;
}

.macro-panel h3 {
  margin: 0 0 16px;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
}

.macro-item {
  margin-bottom: 18px;
}

.macro-item:last-child {
  margin-bottom: 6px;
}

.macro-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 6px;
}

.macro-label {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-main);
}

.macro-val {
  font-size: 1rem;
  color: var(--text-main);
}

.macro-val small {
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.85rem;
}

.bar-outer {
  width: 100%;
  height: 10px;
  background: rgba(148, 163, 184, 0.15);
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
}

.fill-inner {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fill-inner.protein {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
}

.fill-inner.carbs {
  background: linear-gradient(90deg, #10b981, #34d399);
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.fill-inner.fat {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.streak p {
  margin: 0;
  color: var(--text-muted);
}

.insights {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
  color: var(--text-muted);
}

@media (max-width: 1060px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 740px) {
  .diary-header {
    flex-direction: column;
  }

  .weekly-strip {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .macro-inputs {
    grid-template-columns: 1fr;
  }

  .filter-row {
    grid-template-columns: 1fr;
  }
}
</style>
