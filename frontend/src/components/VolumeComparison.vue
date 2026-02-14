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
 * Broccoli: 34 kcal/100g -> 1470g (7.9x burger → ∛7.9 = 2.0x visual scale)
 * Apple: 52 kcal/100g -> 960g (5.2x burger → ∛5.2 = 1.73x visual scale)
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
  // junkScene.background = new THREE.Color(props.isDarkMode ? 0x020617 : 0xf0f4f8)
  
  healthyScene = new THREE.Scene()
  // healthyScene.background = new THREE.Color(props.isDarkMode ? 0x020617 : 0xf0f4f8)

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

  // Add simple circular plate geometry instead of loading model
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

watch(() => props.isDarkMode, () => {
  /*
  if (junkScene && healthyScene) {
    junkScene.background = new THREE.Color(props.isDarkMode ? 0x020617 : 0xf0f4f8)
    healthyScene.background = new THREE.Color(props.isDarkMode ? 0x020617 : 0xf0f4f8)
  }
  */
})

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
  <div class="visualizer-wrapper" :class="{ 'theme-dark': isDarkMode }">
    <div class="ui-header">
      <div class="badge">Ajuste Manual de Volume</div>
      <h1>A Escala Real das Calorias</h1>
      <p>Compare o espaço físico ocupado por <strong>{{ calorieBudget }} kcal</strong></p>
    </div>

    <div class="canvas-box" ref="canvasContainer">
      <div class="controls-header-box">
        <div class="control-group">
          <span class="type">Ultra-Processado</span>
          <div class="name">{{ junkModels[currentJunkIndex].name }}</div>
          <button @click="cycle('junk')" class="btn-swap">🔄 Trocar</button>
        </div>
        
        <div class="vs-divider"></div>
        
        <div class="control-group">
          <span class="type">Natural</span>
          <div class="name">{{ healthyModels[currentHealthyIndex].name }}</div>
          <button @click="cycle('healthy')" class="btn-swap">🔄 Trocar</button>
        </div>
      </div>
    </div>

    <div class="ui-footer">
      <div class="slider-card">
        <div class="slider-header">
          <label>Orçamento: <strong>{{ calorieBudget }} kcal</strong></label>
          <span class="ratio" v-if="!isNaN(satietyMultiplier)">
            {{ satietyMultiplier.toFixed(1) }}x mais volume
          </span>
        </div>
        <input type="range" v-model.number="calorieBudget" min="100" max="2000" step="50" class="custom-slider">
      </div>
      
      <div class="insight-box">
        <div class="icon">🥗</div>
        <p>
          O volume físico é o que sinaliza a saciedade. Alimentos naturais preenchem o seu estômago 
          enquanto ultra-processados são apenas calorias vazias em espaços minúsculos.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.visualizer-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 88px);
  background: #ffffff;
  border-radius: 24px;
  overflow: hidden;
  color: #1e293b;
  transition: background 0.3s, color 0.3s;
}

.visualizer-wrapper.theme-dark {
  background: #020617;
  color: white;
}

.visualizer-wrapper.theme-dark h1,
.visualizer-wrapper.theme-dark .name,
.visualizer-wrapper.theme-dark label {
  color: white;
}

.visualizer-wrapper.theme-dark .canvas-box {
  background: #0f172a;
}

.ui-header { position: absolute; top: 0; left: 0; right: 0; padding: 30px; text-align: center; z-index: 10; pointer-events: none; }
.badge { display: inline-block; background: #3b82f6; color: white; padding: 4px 12px; border-radius: 99px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }
h1 { font-size: 1.8rem; margin: 0; font-weight: 700; color: #1e293b; }

.canvas-box { 
  flex: 1; 
  position: relative; 
  cursor: grab;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  margin: 0 24px 24px;
  overflow: hidden;
  transition: background 0.3s;
}

.viewport-box {
  position: absolute;
  top: 100px;
  bottom: 20px;
  width: calc(50% - 12px);
  background: transparent;
  border: 2px solid rgba(59, 130, 246, 0.15);
  border-radius: 20px;
  pointer-events: none;
  box-shadow: none;
  transition: border-color 0.3s;
}

.viewport-box.left-viewport {
  left: 20px;
}

.viewport-box.right-viewport {
  right: 20px;
}

.theme-dark .viewport-box {
  background: transparent;
  border-color: rgba(71, 85, 105, 0.2);
  box-shadow: none;
}30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: auto;
  min-width: 500px;
  background: transparent;
  padding: 15px 40px
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.5);
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  backdrop-filter: blur(8px);
  z-index: 20;
  transition: all 0.3s ease;
}

.theme-dark .controls-header-box {
  background: rgba(30, 41, 59, 0.95);
  border-color: rgba(255,255,255,0.05);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3); 
}
transparent;
  border: none;
  box-shadow: none;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-width: 150px;
}

.vs-divider {
  width: 1px;
  height: 60px;
  background: #e2e8f0;
  margin: 0 30px;
}

.theme-dark .vs-divider {
  background: #334155;
}

.type { color: #3b82f6; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.name { font-size: 1.2rem; font-weight: 700; margin: 0 0 10px; color: #1e293b; }
.btn-swap { background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; width: 100%; font-size: 0.9em; transition: 0.2s; }
.btn-swap:hover { background: #2563eb; transform: scale(1.02); }

.ui-footer { position: absolute; bottom: 0; left: 0; right: 0; padding: 30px; display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; pointer-events: none; z-index: 10; }
.slider-card, .insight-box { background: rgba(255, 255, 255, 0.98); padding: 24px; border-radius: 24px; border: 2px solid #e2e8f0; pointer-events: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.08); transition: background 0.3s, border-color 0.3s; }

.theme-dark .slider-card,
.theme-dark .insight-box {
  background: rgba(30, 41, 59, 0.98);
  border-color: #334155;
}

.slider-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; color: #1e293b; transition: color 0.3s; }
.ratio { color: #10b981; font-weight: 800; font-size: 0.95rem; }

.theme-dark .slider-header {
  color: white;
}

.custom-slider { -webkit-appearance: none; width: 100%; height: 10px; background: #e2e8f0; border-radius: 5px; cursor: pointer; outline: none; transition: background 0.3s; }
.custom-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 24px; height: 24px; background: #3b82f6; border-radius: 50%; border: 3px solid white; cursor: pointer; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3); }

.theme-dark .custom-slider {
  background: #1e293b;
}

.insight-box { display: flex; align-items: center; gap: 15px; color: #64748b; font-size: 0.95rem; line-height: 1.6; transition: color 0.3s; }

.theme-dark .insight-box {
  color: #94a3b8;
}
.insight-box .icon { font-size: 1.8rem; }

@media (max-width: 900px) {
  .ui-footer { grid-template-columns: 1fr; }
  .controls-overlay { top: auto; bottom: 350px; }
}
</style>
