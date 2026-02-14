<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { auth } from '@/auth'

const STORAGE_KEY = 'nutri_diary_tracking_v1'
const DEFAULT_GOAL = 1800
const mealSections = [
  { id: 'breakfast', label: 'Pequeno-almoço', icon: '🥣' },
  { id: 'lunch', label: 'Almoço', icon: '🍛' },
  { id: 'snack', label: 'Lanche', icon: '🍎' },
  { id: 'dinner', label: 'Jantar', icon: '🍽️' },
  { id: 'extras', label: 'Extras', icon: '🍫' }
]
const quickFoods = [
  { name: 'Peito de frango', calories_per_100g: 165, protein_per_100g: 31, carbs_per_100g: 0, fat_per_100g: 3.6, source: 'quick' },
  { name: 'Arroz cozido', calories_per_100g: 130, protein_per_100g: 2.7, carbs_per_100g: 28, fat_per_100g: 0.3, source: 'quick' },
  { name: 'Ovo cozido', calories_per_100g: 155, protein_per_100g: 13, carbs_per_100g: 1.1, fat_per_100g: 11, source: 'quick' },
  { name: 'Iogurte natural', calories_per_100g: 63, protein_per_100g: 5.3, carbs_per_100g: 7, fat_per_100g: 1.5, source: 'quick' },
  { name: 'Banana', calories_per_100g: 89, protein_per_100g: 1.1, carbs_per_100g: 23, fat_per_100g: 0.3, source: 'quick' },
  { name: 'Aveia', calories_per_100g: 389, protein_per_100g: 17, carbs_per_100g: 66, fat_per_100g: 7, source: 'quick' }
]

const dataByDate = ref({})
const selectedDate = ref(new Date())
const composerFor = ref('')
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
  fat: ''
})

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

const buildEmptyDay = () => ({
  goal: DEFAULT_GOAL,
  meals: {
    breakfast: [],
    lunch: [],
    snack: [],
    dinner: [],
    extras: []
  }
})

const normalizeDay = (rawDay) => {
  const day = buildEmptyDay()
  if (!rawDay || typeof rawDay !== 'object') return day

  day.goal = toNumber(rawDay.goal) > 0 ? toNumber(rawDay.goal) : DEFAULT_GOAL

  for (const section of mealSections) {
    const list = Array.isArray(rawDay.meals?.[section.id]) ? rawDay.meals[section.id] : []
    day.meals[section.id] = list.map((item) => ({
      id: item.id || `${Date.now()}-${Math.random()}`,
      name: item.name || 'Item',
      grams: toNumber(item.grams),
      calories: toNumber(item.calories),
      protein: toNumber(item.protein),
      carbs: toNumber(item.carbs),
      fat: toNumber(item.fat)
    }))
  }
  return day
}

const persist = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(dataByDate.value))
}

const ensureDay = (key) => {
  if (dataByDate.value[key]) return
  dataByDate.value = {
    ...dataByDate.value,
    [key]: buildEmptyDay()
  }
  persist()
}

const currentDay = computed(() => normalizeDay(dataByDate.value[dateKey.value]))

const updateCurrentDay = (mutator) => {
  const key = dateKey.value
  const clone = normalizeDay(dataByDate.value[key])
  mutator(clone)
  dataByDate.value = {
    ...dataByDate.value,
    [key]: clone
  }
  persist()
}

const allMealsToday = computed(() =>
  mealSections.flatMap((section) => currentDay.value.meals[section.id] || [])
)

const consumedCalories = computed(() =>
  Math.round(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.calories), 0))
)

const consumedProtein = computed(() => round1(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.protein), 0)))
const consumedCarbs = computed(() => round1(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.carbs), 0)))
const consumedFat = computed(() => round1(allMealsToday.value.reduce((acc, item) => acc + toNumber(item.fat), 0)))

const calorieGoal = computed(() => Math.max(1, toNumber(currentDay.value.goal) || DEFAULT_GOAL))
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

const isDayOnTarget = (day) => {
  const total = mealSections.reduce((sum, section) => {
    const list = day.meals?.[section.id] || []
    return sum + list.reduce((acc, item) => acc + toNumber(item.calories), 0)
  }, 0)
  if (total === 0) return false
  return total <= toNumber(day.goal || DEFAULT_GOAL)
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
    const normalized = normalizeDay(dataByDate.value[key])
    const hasMeals = mealSections.some((section) => normalized.meals[section.id]?.length)
    out.push({
      key,
      date: d,
      dayName: d.toLocaleDateString('pt-PT', { weekday: 'short' }),
      dayNum: d.getDate(),
      active: key === dateKey.value,
      hasMeals,
      onTarget: isDayOnTarget(normalized)
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

const openComposer = (sectionId) => {
  composerFor.value = composerFor.value === sectionId ? '' : sectionId
  foodSearchModalOpen.value = false
  foodSearch.value = { query: '', loading: false, error: '', results: [] }
  foodFilters.value = { source: 'all', sort: 'relevance', maxCalories: '', minProtein: '' }
  selectedFoodPer100g.value = null
  mealDraft.value = { name: '', grams: '', calories: '', protein: '', carbs: '', fat: '' }
}

const estimateMacros = (calories) => {
  const protein = round1((calories * 0.25) / 4)
  const carbs = round1((calories * 0.45) / 4)
  const fat = round1((calories * 0.3) / 9)
  return { protein, carbs, fat }
}

const addMeal = (sectionId) => {
  const name = mealDraft.value.name.trim()
  const grams = toNumber(mealDraft.value.grams)
  const calories = toNumber(mealDraft.value.calories)

  if (!name || grams <= 0 || calories <= 0) return

  let protein = toNumber(mealDraft.value.protein)
  let carbs = toNumber(mealDraft.value.carbs)
  let fat = toNumber(mealDraft.value.fat)

  if (protein === 0 && carbs === 0 && fat === 0) {
    const estimated = estimateMacros(calories)
    protein = estimated.protein
    carbs = estimated.carbs
    fat = estimated.fat
  }

  updateCurrentDay((day) => {
    day.meals[sectionId].push({
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      name,
      grams: Math.round(grams),
      calories: Math.round(calories),
      protein,
      carbs,
      fat
    })
  })

  composerFor.value = ''
  foodSearchModalOpen.value = false
  foodSearch.value = { query: '', loading: false, error: '', results: [] }
  foodFilters.value = { source: 'all', sort: 'relevance', maxCalories: '', minProtein: '' }
  selectedFoodPer100g.value = null
  mealDraft.value = { name: '', grams: '', calories: '', protein: '', carbs: '', fat: '' }
}

const openFoodSearchModal = () => {
  foodSearchModalOpen.value = true
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
  if (!toNumber(mealDraft.value.grams)) {
    mealDraft.value.grams = 100
  }
  applyFoodByGrams(food, mealDraft.value.grams)
  closeFoodSearchModal()
}

const searchFoodApi = async () => {
  const query = foodSearch.value.query.trim()
  if (!query) return

  foodSearch.value.loading = true
  foodSearch.value.error = ''
  foodSearch.value.results = []

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/foods/search?q=${encodeURIComponent(query)}&page_size=8`, {
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
  const hasQuery = foodSearch.value.query.trim().length > 0
  if (!hasQuery && filteredFoodResults.value.length === 0) return quickFoods
  if (filteredFoodResults.value.length > 0) return filteredFoodResults.value
  return []
})

const removeMeal = (sectionId, itemId) => {
  updateCurrentDay((day) => {
    day.meals[sectionId] = day.meals[sectionId].filter((item) => item.id !== itemId)
  })
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

const updateGoal = (event) => {
  const next = Math.max(1000, Math.min(6000, toNumber(event.target.value) || DEFAULT_GOAL))
  updateCurrentDay((day) => {
    day.goal = next
  })
}

onMounted(() => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (parsed && typeof parsed === 'object') dataByDate.value = parsed
    }
  } catch {
    dataByDate.value = {}
  }
  ensureDay(dateKey.value)
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
        <h2>{{ consumedCalories }} / {{ calorieGoal }} kcal</h2>
        <p v-if="deltaCalories >= 0" class="state-ok">Faltam {{ deltaCalories }} kcal para o objetivo.</p>
        <p v-else class="state-over">+{{ Math.abs(deltaCalories) }} kcal acima do objetivo.</p>
      </div>

      <label class="goal-control">
        Objetivo diário
        <input type="number" :value="calorieGoal" min="1000" max="6000" step="50" @change="updateGoal" />
      </label>

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
            <input v-model="mealDraft.name" type="text" placeholder="Nome da refeição" />
            <button type="button" class="search-food-btn" @click="openFoodSearchModal">
              Pesquisar alimento
            </button>
            <p v-if="selectedFoodPer100g" class="selected-food">
              Selecionado: <strong>{{ selectedFoodPer100g.name }}</strong>
            </p>
            <input v-model="mealDraft.grams" type="number" min="1" placeholder="Quantidade (g)" />
            <input v-model="mealDraft.calories" type="number" min="1" placeholder="kcal" />
            <div class="macro-inputs">
              <input v-model="mealDraft.protein" type="number" min="0" step="0.1" placeholder="Prot. g" />
              <input v-model="mealDraft.carbs" type="number" min="0" step="0.1" placeholder="Hidr. g" />
              <input v-model="mealDraft.fat" type="number" min="0" step="0.1" placeholder="Gord. g" />
            </div>
            <div class="composer-actions">
              <button type="button" class="save-btn" @click="addMeal(section.id)">Guardar</button>
              <button type="button" class="cancel-btn" @click="openComposer('')">Cancelar</button>
            </div>
          </div>

          <ul v-if="currentDay.meals[section.id].length" class="meal-list">
            <li v-for="item in currentDay.meals[section.id]" :key="item.id">
              <div>
                <strong>{{ item.name }}</strong>
                <small>{{ item.grams }} g · {{ item.protein }}g P · {{ item.carbs }}g H · {{ item.fat }}g G</small>
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
        <article class="side-card">
          <h3>Macros</h3>
          <div class="macro-row">
            <span>Proteínas</span>
            <strong>{{ consumedProtein }}g ({{ macroPercentages.protein }}%)</strong>
          </div>
          <div class="bar"><div class="fill protein" :style="{ width: `${macroPercentages.protein}%` }"></div></div>
          <div class="macro-row">
            <span>Hidratos</span>
            <strong>{{ consumedCarbs }}g ({{ macroPercentages.carbs }}%)</strong>
          </div>
          <div class="bar"><div class="fill carbs" :style="{ width: `${macroPercentages.carbs}%` }"></div></div>
          <div class="macro-row">
            <span>Gorduras</span>
            <strong>{{ consumedFat }}g ({{ macroPercentages.fat }}%)</strong>
          </div>
          <div class="bar"><div class="fill fat" :style="{ width: `${macroPercentages.fat}%` }"></div></div>
        </article>

        <article class="side-card streak">
          <h3>🔥 Streak</h3>
          <p><strong>{{ streakDays }}</strong> dias seguidos dentro do objetivo.</p>
        </article>

        <article class="side-card">
          <h3>Sugestões</h3>
          <ul class="insights">
            <li v-for="tip in insights" :key="tip">{{ tip }}</li>
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
            placeholder="Ex: frango, arroz, iogurte..."
            @keyup.enter="searchFoodApi"
          />
          <button type="button" class="search-food-btn" @click="searchFoodApi" :disabled="foodSearch.loading">
            {{ foodSearch.loading ? 'A procurar...' : 'Pesquisar' }}
          </button>
        </div>

        <div v-if="foodSearch.results.length" class="filter-row">
          <select v-model="foodFilters.source">
            <option value="all">Todas as fontes</option>
            <option value="usda">USDA</option>
            <option value="openfoodfacts">OpenFoodFacts</option>
          </select>
          <select v-model="foodFilters.sort">
            <option value="relevance">Mais relevantes</option>
            <option value="kcal_asc">Menos kcal/100g</option>
            <option value="kcal_desc">Mais kcal/100g</option>
            <option value="protein_desc">Mais proteína</option>
          </select>
          <input v-model="foodFilters.maxCalories" type="number" min="0" placeholder="Máx kcal/100g" />
          <input v-model="foodFilters.minProtein" type="number" min="0" placeholder="Mín Prot. g" />
        </div>

        <p v-if="foodSearch.error" class="search-error">{{ foodSearch.error }}</p>
        <p v-if="!foodSearch.query.trim()" class="search-empty">Sugestões rápidas (clique para usar):</p>
        <ul v-if="displayedFoodResults.length" class="food-suggestions">
          <li v-for="food in displayedFoodResults" :key="`${food.source}-${food.name}`">
            <button type="button" @click="chooseFoodSuggestion(food)">
              <strong>{{ food.name }}</strong>
              <small>
                {{ food.calories_per_100g }} kcal · P {{ food.protein_per_100g }}g · H {{ food.carbs_per_100g }}g · G {{ food.fat_per_100g }}g
                (100g)
              </small>
            </button>
          </li>
        </ul>
        <p v-else-if="foodSearch.results.length" class="search-empty">Sem resultados com estes filtros.</p>
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

.search-food-btn {
  border: 1px solid #14b8a6;
  background: transparent;
  color: #14b8a6;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  font-weight: 700;
}

.search-food-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.macro-inputs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
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

.side-card h3 {
  margin: 0 0 10px;
}

.macro-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 8px;
}

.bar {
  margin-top: 6px;
  width: 100%;
  height: 8px;
  background: rgba(148, 163, 184, 0.28);
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
}

.protein {
  background: #14b8a6;
}

.carbs {
  background: #3b82f6;
}

.fat {
  background: #f59e0b;
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
