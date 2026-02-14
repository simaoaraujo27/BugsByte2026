<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

// Props
const props = defineProps({
  isDarkMode: {
    type: Boolean,
    default: false
  }
})

// Reactive state
const canvasContainer = ref(null)
const calorieBudget = ref(500)
const isLoading = ref(false)

const junkModels = [
  { name: 'Hambúrguer', file: 'burger.glb', baseScale: 0.15, caloriesPerGram: 2.5, unitGrams: 180 },
  { name: 'Pizza', file: 'pizza.glb', baseScale: 0.23, caloriesPerGram: 2.7, unitGrams: 120 },
  { name: 'Refrigerante', file: 'soda.glb', baseScale: 0.08, caloriesPerGram: 0.41, unitGrams: 330 }
]

const healthyModels = [
  { name: 'Salada', file: 'salad.glb', baseScale: 1.2, caloriesPerGram: 0.45, unitGrams: 250 },
  { name: 'Brócolos', file: 'broccoli.glb', baseScale: 0.8, caloriesPerGram: 0.34, unitGrams: 90 },
  { name: 'Maçã', file: 'apple.glb', baseScale: 0.10, caloriesPerGram: 0.52, unitGrams: 150 }
]

const CONFIG = {
  plate: {
    scale: 3.0,
    y: -0.5
  }
}

const currentJunkIndex = ref(0)
const currentHealthyIndex = ref(0)

const currentJunkConfig = computed(() => junkModels[currentJunkIndex.value])
const currentHealthyConfig = computed(() => healthyModels[currentHealthyIndex.value])

const junkGrams = computed(() => {
  const grams = calorieBudget.value / currentJunkConfig.value.caloriesPerGram
  return Number.isFinite(grams) ? Math.round(grams) : 0
})

const healthyGrams = computed(() => {
  const grams = calorieBudget.value / currentHealthyConfig.value.caloriesPerGram
  return Number.isFinite(grams) ? Math.round(grams) : 0
})

const junkUnits = computed(() => getItemCount(junkGrams.value, currentJunkConfig.value.unitGrams))
const healthyUnits = computed(() => getItemCount(healthyGrams.value, currentHealthyConfig.value.unitGrams))

const satietyMultiplier = computed(() => {
  const junkConfig = currentJunkConfig.value
  const healthyConfig = currentHealthyConfig.value
  const junkGrams = calorieBudget.value / junkConfig.caloriesPerGram
  const healthyGrams = calorieBudget.value / healthyConfig.caloriesPerGram
  const ratio = healthyGrams / junkGrams
  return isNaN(ratio) ? 1.0 : ratio
})

const uiTheme = computed(() => {
  if (props.isDarkMode) {
    return {
      title: 'text-white',
      subtitle: 'text-slate-400',
      stage: 'bg-slate-900 border-slate-800 shadow-none',
      viewport: 'from-gray-900 via-slate-900 to-black',
      card: 'bg-slate-800/90 border-slate-700/50',
      cardTitle: 'text-white',
      cardMeta: 'text-slate-300',
      cardBtn: 'text-slate-200 bg-slate-700/50 hover:bg-slate-700 border-slate-600',
      divider: 'border-white/10',
      vs: 'bg-slate-700 outline-slate-800/50',
      footer: 'bg-slate-950 border-slate-900',
      sliderTrack: 'bg-slate-800',
      sliderHint: 'text-slate-500',
      satietyBadge: 'bg-emerald-500/10 border-emerald-500/20 hover:bg-emerald-500/15',
      satietySub: 'text-slate-400',
      satietyText: 'text-white'
    }
  }

  return {
    title: 'text-slate-800',
    subtitle: 'text-slate-600',
    stage: 'bg-white border-slate-200 shadow-2xl shadow-slate-200/70',
    viewport: 'from-slate-50 via-white to-slate-100',
    card: 'bg-white/92 border-slate-200/80',
    cardTitle: 'text-slate-800',
    cardMeta: 'text-slate-500',
    cardBtn: 'text-slate-600 bg-slate-50 hover:bg-slate-100 border-slate-200',
    divider: 'border-slate-300/70',
    vs: 'bg-slate-800 outline-slate-200',
    footer: 'bg-white border-slate-200',
    sliderTrack: 'bg-slate-200',
    sliderHint: 'text-slate-500',
    satietyBadge: 'bg-emerald-50 border-emerald-200 hover:bg-emerald-100/60',
    satietySub: 'text-slate-500',
    satietyText: 'text-slate-800'
  }
})

let junkScene, healthyScene, junkCamera, healthyCamera, renderer
let junkTemplate, healthyTemplate
let junkGroup, healthyGroup
let junkPlate, healthyPlate

const initScene = () => {
  junkScene = new THREE.Scene()
  healthyScene = new THREE.Scene()

  const aspect = (canvasContainer.value.clientWidth / 2) / canvasContainer.value.clientHeight
  
  junkCamera = new THREE.PerspectiveCamera(40, aspect, 0.1, 1000)
  junkCamera.position.set(0, 5, 8)
  junkCamera.lookAt(0, 0, 0)
  
  healthyCamera = new THREE.PerspectiveCamera(40, aspect, 0.1, 1000)
  healthyCamera.position.set(0, 5, 8)
  healthyCamera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  canvasContainer.value.appendChild(renderer.domElement)

  const setupLights = (scene) => {
    const ambient = new THREE.AmbientLight(0xffffff, 2.0)
    scene.add(ambient)
    const sun = new THREE.DirectionalLight(0xffffff, 1.5)
    sun.position.set(5, 10, 5)
    scene.add(sun)
  }
  
  setupLights(junkScene)
  setupLights(healthyScene)

  const plateGeometry = new THREE.CylinderGeometry(2, 2, 0.1, 32)
  const plateMaterial = new THREE.MeshStandardMaterial({ color: 0xf8f8f8 })
  
  junkPlate = new THREE.Mesh(plateGeometry, plateMaterial)
  junkPlate.position.y = CONFIG.plate.y
  junkScene.add(junkPlate)
  
  healthyPlate = new THREE.Mesh(plateGeometry, plateMaterial.clone())
  healthyPlate.position.y = CONFIG.plate.y
  healthyScene.add(healthyPlate)

  junkGroup = new THREE.Group()
  healthyGroup = new THREE.Group()
  junkScene.add(junkGroup)
  healthyScene.add(healthyGroup)
}

const getItemCount = (grams, unitGrams) => {
  if (!grams || !unitGrams) return 1
  return Math.max(1, Math.min(12, Math.round(grams / unitGrams)))
}

const clearGroup = (group) => {
  if (!group) return
  while (group.children.length) {
    const child = group.children.pop()
    if (child) group.remove(child)
  }
}

const getSlotPosition = (index, total) => {
  if (total <= 1) return { x: 0, z: 0 }
  if (total <= 4) {
    const spacing = 1.1
    const row = Math.floor(index / 2)
    const col = index % 2
    return { x: (col - 0.5) * spacing, z: (row - 0.5) * spacing }
  }

  const ringIndex = index % 6
  const ring = index < 6 ? 1 : 2
  const radius = ring === 1 ? 1.0 : 1.5
  const angle = (Math.PI * 2 * ringIndex) / 6
  return { x: Math.cos(angle) * radius, z: Math.sin(angle) * radius }
}

const renderFoodCopies = (type) => {
  const isJunk = type === 'junk'
  const template = isJunk ? junkTemplate : healthyTemplate
  const group = isJunk ? junkGroup : healthyGroup
  const config = isJunk ? currentJunkConfig.value : currentHealthyConfig.value
  const grams = isJunk ? junkGrams.value : healthyGrams.value

  if (!template || !group || !config) return

  const copies = getItemCount(grams, config.unitGrams)
  clearGroup(group)

  for (let i = 0; i < copies; i += 1) {
    const copy = template.clone(true)
    const { x, z } = getSlotPosition(i, copies)
    const yOffset = copies > 7 ? (i % 2) * 0.08 : 0
    copy.position.set(x, yOffset, z)
    copy.rotation.y = Math.PI / 4 + i * 0.25
    copy.scale.setScalar(config.baseScale)
    group.add(copy)
  }
}

const loadFood = async (type) => {
  isLoading.value = true
  const list = type === 'junk' ? junkModels : healthyModels
  const index = type === 'junk' ? currentJunkIndex.value : currentHealthyIndex.value
  const filename = list[index].file
  const loader = new GLTFLoader()

  try {
    const gltf = await new Promise((res, rej) => {
      loader.load(`/models/${filename}`, res, undefined, rej)
    })
    
    const model = gltf.scene

    if (type === 'junk') {
      junkTemplate = model
      renderFoodCopies('junk')
    } else {
      healthyTemplate = model
      renderFoodCopies('healthy')
    }
  } catch (err) {
    console.error("Load error:", filename)
  } finally {
    isLoading.value = false
    updateScales()
  }
}

const updateScales = () => {
  renderFoodCopies('junk')
  renderFoodCopies('healthy')
}

const cycle = (type) => {
  if (type === 'junk') currentJunkIndex.value = (currentJunkIndex.value + 1) % junkModels.length
  else currentHealthyIndex.value = (currentHealthyIndex.value + 1) % healthyModels.length
  loadFood(type)
}

const animate = () => {
  requestAnimationFrame(animate)
  if (junkGroup) junkGroup.rotation.y += 0.0035
  if (healthyGroup) healthyGroup.rotation.y += 0.0035
  
  if (renderer) {
    const width = canvasContainer.value.clientWidth
    const height = canvasContainer.value.clientHeight
    
    renderer.setViewport(0, 0, width / 2, height)
    renderer.setScissor(0, 0, width / 2, height)
    renderer.setScissorTest(true)
    renderer.render(junkScene, junkCamera)
    
    renderer.setViewport(width / 2, 0, width / 2, height)
    renderer.setScissor(width / 2, 0, width / 2, height)
    renderer.render(healthyScene, healthyCamera)
    
    renderer.setScissorTest(false)
  }
}

watch(calorieBudget, updateScales)

onMounted(() => {
  initScene()
  loadFood('junk')
  loadFood('healthy')
  animate()
  
  window.addEventListener('resize', () => {
    if (!canvasContainer.value) return
    const width = canvasContainer.value.clientWidth
    const height = canvasContainer.value.clientHeight
    const aspect = (width / 2) / height
    
    junkCamera.aspect = aspect
    junkCamera.updateProjectionMatrix()
    
    healthyCamera.aspect = aspect
    healthyCamera.updateProjectionMatrix()
    
    renderer.setSize(width, height)
  })
})
</script>

<template>
  <div class="flex flex-col h-full max-h-[calc(100vh-120px)] overflow-hidden">
    <!-- Header: Minimal & Clean -->
    <header class="mb-6 text-center">
      <span class="px-4 py-1 text-[10px] font-extrabold tracking-[0.2em] text-white uppercase bg-blue-600 rounded-full shadow-lg shadow-blue-500/20">
        Laboratório de Saciedade
      </span>
      <h1 class="mt-4 text-3xl font-black tracking-tight md:text-4xl" :class="uiTheme.title">
        A Ilusão das Calorias
      </h1>
      <p class="mt-1 text-sm font-semibold" :class="uiTheme.subtitle">
        Visualize como <span class="font-bold underline decoration-2 underline-offset-4" :class="props.isDarkMode ? 'text-blue-400' : 'text-blue-600'">{{ calorieBudget }} kcal</span> ocupam o espaço real.
      </p>
    </header>

    <!-- Main Stage: Unified Dashboard Card (Apple Health / Clinical Look) -->
    <div class="relative flex-1 min-h-0 rounded-[2.5rem] border flex flex-col overflow-hidden" :class="uiTheme.stage">
      
      <!-- 3D Viewport with Contrast-Enhancing Radial Gradient -->
      <div class="relative flex-1 w-full min-h-0 cursor-grab active:cursor-grabbing bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))]" :class="uiTheme.viewport" ref="canvasContainer">
        
        <!-- Overlays: Left Food Info (Glassmorphism Pill) -->
        <div class="absolute z-20 flex flex-col items-center p-4 transition-all transform top-6 left-6 rounded-[1.5rem] backdrop-blur-sm shadow-lg border min-w-[140px]" :class="uiTheme.card">
          <span class="text-[9px] font-black text-rose-500 uppercase tracking-widest mb-1.5">Ultra-Processado</span>
          <div class="text-base font-extrabold" :class="uiTheme.cardTitle">{{ currentJunkConfig.name }}</div>
          <div class="mt-1 text-[11px] font-semibold" :class="uiTheme.cardMeta">
            {{ junkGrams }}g · {{ junkUnits }} un.
          </div>
          <button @click="cycle('junk')" class="mt-3 px-4 py-2 text-[11px] font-bold rounded-xl transition-all flex items-center gap-2 border" :class="uiTheme.cardBtn">
            <span>Trocar</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 opacity-60" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
          </button>
        </div>

        <!-- VS Badge Center -->
        <div class="absolute z-20 transform -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
           <div class="flex items-center justify-center w-12 h-12 font-black text-white rounded-full shadow-2xl outline outline-[6px] text-xs italic tracking-tighter" :class="uiTheme.vs">VS</div>
        </div>

        <div class="absolute inset-y-0 z-10 hidden border-l border-dashed left-1/2 md:block" :class="uiTheme.divider"></div>

        <!-- Overlays: Right Food Info (Glassmorphism Pill) -->
        <div class="absolute z-20 flex flex-col items-center p-4 transition-all transform top-6 right-6 rounded-[1.5rem] backdrop-blur-sm shadow-lg border min-w-[140px]" :class="uiTheme.card">
          <span class="text-[9px] font-black text-emerald-500 uppercase tracking-widest mb-1.5">Densidade Baixa</span>
          <div class="text-base font-extrabold" :class="uiTheme.cardTitle">{{ currentHealthyConfig.name }}</div>
          <div class="mt-1 text-[11px] font-semibold" :class="uiTheme.cardMeta">
            {{ healthyGrams }}g · {{ healthyUnits }} un.
          </div>
          <button @click="cycle('healthy')" class="mt-3 px-4 py-2 text-[11px] font-bold rounded-xl transition-all flex items-center gap-2 border" :class="uiTheme.cardBtn">
            <span>Trocar</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 opacity-60" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
          </button>
        </div>

        <div v-if="isLoading" class="absolute inset-0 z-30 grid place-items-center bg-slate-950/25 backdrop-blur-[2px]">
          <div class="px-4 py-2 text-xs font-bold text-white rounded-xl bg-slate-900/80">
            A carregar modelo...
          </div>
        </div>
      </div>

      <!-- Anchored Footer Controls (Dark Slate for Contrast) -->
      <footer class="p-8 border-t rounded-b-3xl" :class="uiTheme.footer">
        <div class="flex flex-col items-center gap-8 md:flex-row md:justify-between">
          
          <!-- Slider Control -->
          <div class="flex-1 w-full max-w-xl">
            <div class="flex items-center justify-between mb-4">
              <label class="text-[10px] font-black tracking-[0.2em] uppercase" :class="uiTheme.sliderHint">Ajuste de Orçamento</label>
              <div class="flex items-baseline gap-1.5">
                <span class="text-3xl font-black tabular-nums" :class="uiTheme.satietyText">{{ calorieBudget }}</span>
                <span class="text-xs font-bold uppercase" :class="uiTheme.sliderHint">kcal</span>
              </div>
            </div>
            <input type="range" v-model.number="calorieBudget" min="100" max="2000" step="50" class="w-full h-2 rounded-lg appearance-none cursor-pointer accent-blue-500 focus:outline-none" :class="uiTheme.sliderTrack">
            <div class="flex justify-between mt-2 text-[10px] font-semibold" :class="uiTheme.sliderHint">
              <span>100 kcal</span>
              <span>2000 kcal</span>
            </div>
          </div>

          <!-- Satiety Insight Badge -->
          <div class="flex items-center gap-5 px-6 py-5 rounded-[2rem] border md:max-w-xs transition-all" :class="uiTheme.satietyBadge">
            <div class="flex items-center justify-center w-12 h-12 text-2xl rounded-2xl bg-emerald-500/20 shadow-inner">🥗</div>
            <div>
              <div class="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-0.5">Fator de Saciedade</div>
              <div class="text-xl font-black" :class="uiTheme.satietyText">
                {{ satietyMultiplier.toFixed(1) }}x <span class="text-sm font-medium" :class="uiTheme.satietySub">mais volume</span>
              </div>
            </div>
          </div>

        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* High-End Range Input Styling */
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 28px;
  width: 28px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 5px solid white;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

input[type=range]::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  background: #2563eb;
}

input[type=range]::-moz-range-thumb {
  height: 28px;
  width: 28px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 5px solid white;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3);
  transition: all 0.2s ease;
}
</style>
