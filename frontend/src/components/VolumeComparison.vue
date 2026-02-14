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

/**
 * CALORIC DENSITY (kcal per 100g):
 * At 500 kcal reference point:
 * Burger: 270 kcal/100g -> 185g (REFERENCE: scale = 1.0)
 * Pizza: 265 kcal/100g -> 189g (1.02x burger)
 * Soda: 42 kcal/100ml -> 1190g (6.4x burger)
 * Salad: 20 kcal/100g -> 2500g (13.5x burger → ∛13.5 = 2.38x visual scale)
 * Broccoli: 34 kcal/100g -> 1470g (7.9x burger → ∛13.5 = 2.0x visual scale)
 * Apple: 52 kcal/100g -> 960g (5.2x burger → ∛13.5 = 1.73x visual scale)
 */
const junkModels = [
  { name: 'Hambúrguer', file: 'burger.glb', baseScale: 0.15, caloriesPerGram: 2.7 },
  { name: 'Pizza', file: 'pizza.glb', baseScale: 0.23, caloriesPerGram: 2.65 },
  { name: 'Refrigerante', file: 'soda.glb', baseScale: 0.08, caloriesPerGram: 0.42 }
]

const healthyModels = [
  { name: 'Salada', file: 'salad.glb', baseScale: 1.2, caloriesPerGram: 0.20 },
  { name: 'Brócolos', file: 'broccoli.glb', baseScale: 0.8, caloriesPerGram: 0.34 },
  { name: 'Maçã', file: 'apple.glb', baseScale: 0.20, caloriesPerGram: 0.52 }
]

const CONFIG = {
  plate: {
    scale: 3.0,
    y: -0.5
  }
}

const currentJunkIndex = ref(0)
const currentHealthyIndex = ref(0)

const satietyMultiplier = computed(() => {
  const junkConfig = junkModels[currentJunkIndex.value]
  const healthyConfig = healthyModels[currentHealthyIndex.value]
  const junkGrams = calorieBudget.value / junkConfig.caloriesPerGram
  const healthyGrams = calorieBudget.value / healthyConfig.caloriesPerGram
  const ratio = healthyGrams / junkGrams
  return isNaN(ratio) ? 1.0 : ratio
})

let junkScene, healthyScene, junkCamera, healthyCamera, renderer
let junkModel, healthyModel
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
    model.rotation.y = Math.PI / 4
    model.position.set(0, 0, 0)

    if (type === 'junk') {
      if (junkModel) junkScene.remove(junkModel)
      junkModel = model
      junkScene.add(junkModel)
    } else {
      if (healthyModel) healthyScene.remove(healthyModel)
      healthyModel = model
      healthyScene.add(healthyModel)
    }
  } catch (err) {
    console.error("Load error:", filename)
  } finally {
    isLoading.value = false
    updateScales()
  }
}

const updateScales = () => {
  const referenceGrams = 185
  
  if (junkModel) {
    const config = junkModels[currentJunkIndex.value]
    const grams = calorieBudget.value / config.caloriesPerGram
    const volumeRatio = grams / referenceGrams
    const linearScale = Math.pow(volumeRatio, 1/3)
    const s = config.baseScale * linearScale
    junkModel.scale.set(s, s, s)
    junkModel.position.set(0, 0, 0)
  }
  
  if (healthyModel) {
    const config = healthyModels[currentHealthyIndex.value]
    const grams = calorieBudget.value / config.caloriesPerGram
    const volumeRatio = grams / referenceGrams
    const linearScale = Math.pow(volumeRatio, 1/3)
    const s = config.baseScale * linearScale
    healthyModel.scale.set(s, s, s)
    healthyModel.position.set(0, 0, 0)
  }
}

const cycle = (type) => {
  if (type === 'junk') currentJunkIndex.value = (currentJunkIndex.value + 1) % junkModels.length
  else currentHealthyIndex.value = (currentHealthyIndex.value + 1) % healthyModels.length
  loadFood(type)
}

const animate = () => {
  requestAnimationFrame(animate)
  if (junkModel) junkModel.rotation.y += 0.005
  if (healthyModel) healthyModel.rotation.y += 0.005
  
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
  <div class="flex flex-col h-full max-h-[calc(100vh-120px)] overflow-hidden" :class="{ 'dark': isDarkMode }">
    <!-- Header: Minimal & Clean -->
    <header class="mb-6 text-center">
      <span class="px-4 py-1 text-[10px] font-extrabold tracking-[0.2em] text-white uppercase bg-blue-600 rounded-full shadow-lg shadow-blue-500/20">
        Laboratório de Saciedade
      </span>
      <h1 class="mt-4 text-3xl font-black tracking-tight text-slate-800 dark:text-white md:text-4xl">
        A Ilusão das Calorias
      </h1>
      <p class="mt-1 text-sm font-semibold text-slate-500 dark:text-slate-400">
        Visualize como <span class="text-blue-600 dark:text-blue-400 font-bold underline decoration-2 underline-offset-4">{{ calorieBudget }} kcal</span> ocupam o espaço real.
      </p>
    </header>

    <!-- Main Stage: Unified Dashboard Card (Apple Health / Clinical Look) -->
    <div class="relative flex-1 min-h-0 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-2xl shadow-slate-200/50 dark:shadow-none flex flex-col overflow-hidden">
      
      <!-- 3D Viewport with Contrast-Enhancing Radial Gradient -->
      <div class="relative flex-1 w-full min-h-0 cursor-grab active:cursor-grabbing bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white via-slate-50 to-slate-200 dark:from-gray-900 dark:to-black" ref="canvasContainer">
        
        <!-- Overlays: Left Food Info (Glassmorphism Pill) -->
        <div class="absolute z-20 flex flex-col items-center p-4 transition-all transform top-6 left-6 rounded-[1.5rem] bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-lg border border-white/50 dark:border-slate-700/50 min-w-[140px]">
          <span class="text-[9px] font-black text-rose-500 uppercase tracking-widest mb-1.5">Ultra-Processado</span>
          <div class="text-base font-extrabold text-slate-800 dark:text-white">{{ junkModels[currentJunkIndex].name }}</div>
          <button @click="cycle('junk')" class="mt-3 px-4 py-2 text-[11px] font-bold text-slate-600 dark:text-slate-200 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-all flex items-center gap-2 border border-slate-100 dark:border-slate-600">
            <span>Trocar</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 opacity-60" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
          </button>
        </div>

        <!-- VS Badge Center -->
        <div class="absolute z-20 transform -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
           <div class="flex items-center justify-center w-12 h-12 font-black text-white rounded-full shadow-2xl bg-slate-900 dark:bg-slate-700 outline outline-[6px] outline-white/30 dark:outline-slate-800/50 text-xs italic tracking-tighter">VS</div>
        </div>

        <!-- Overlays: Right Food Info (Glassmorphism Pill) -->
        <div class="absolute z-20 flex flex-col items-center p-4 transition-all transform top-6 right-6 rounded-[1.5rem] bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-lg border border-white/50 dark:border-slate-700/50 min-w-[140px]">
          <span class="text-[9px] font-black text-emerald-500 uppercase tracking-widest mb-1.5">Densidade Baixa</span>
          <div class="text-base font-extrabold text-slate-800 dark:text-white">{{ healthyModels[currentHealthyIndex].name }}</div>
          <button @click="cycle('healthy')" class="mt-3 px-4 py-2 text-[11px] font-bold text-slate-600 dark:text-slate-200 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-all flex items-center gap-2 border border-slate-100 dark:border-slate-600">
            <span>Trocar</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 opacity-60" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
          </button>
        </div>
      </div>

      <!-- Anchored Footer Controls (Dark Slate for Contrast) -->
      <footer class="p-8 bg-slate-900 dark:bg-slate-950 border-t border-slate-800 dark:border-slate-900 rounded-b-3xl">
        <div class="flex flex-col items-center gap-8 md:flex-row md:justify-between">
          
          <!-- Slider Control -->
          <div class="flex-1 w-full max-w-xl">
            <div class="flex items-center justify-between mb-4">
              <label class="text-[10px] font-black tracking-[0.2em] uppercase text-slate-400">Ajuste de Orçamento</label>
              <div class="flex items-baseline gap-1.5">
                <span class="text-3xl font-black text-white tabular-nums">{{ calorieBudget }}</span>
                <span class="text-xs font-bold text-slate-500 uppercase">kcal</span>
              </div>
            </div>
            <input type="range" v-model.number="calorieBudget" min="100" max="2000" step="50" class="w-full h-2 rounded-lg appearance-none cursor-pointer bg-slate-800 accent-blue-500 focus:outline-none">
          </div>

          <!-- Satiety Insight Badge -->
          <div class="flex items-center gap-5 px-6 py-5 bg-white/5 dark:bg-emerald-500/10 rounded-[2rem] border border-white/10 dark:border-emerald-500/20 md:max-w-xs transition-all hover:bg-white/10">
            <div class="flex items-center justify-center w-12 h-12 text-2xl rounded-2xl bg-emerald-500/20 shadow-inner">🥗</div>
            <div>
              <div class="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-0.5">Fator de Saciedade</div>
              <div class="text-xl font-black text-white">
                {{ satietyMultiplier.toFixed(1) }}x <span class="text-sm font-medium text-slate-400">mais volume</span>
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
