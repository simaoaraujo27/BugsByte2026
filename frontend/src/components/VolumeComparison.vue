<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

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
  { name: 'Hambúrguer', file: 'burger.glb', baseScale: 0.15, caloriesPerGram: 2.5, unitGrams: 180, surfaceOffsetY: 0 },
  { name: 'Pizza', file: 'pizza.glb', baseScale: 0.23, caloriesPerGram: 2.7, unitGrams: 120, surfaceOffsetY: 0 },
  { name: 'Refrigerante', file: 'soda.glb', baseScale: 0.08, caloriesPerGram: 0.41, unitGrams: 330, surfaceOffsetY: 0 }
]

const healthyModels = [
  { name: 'Salada', file: 'salad.glb', baseScale: 1.2, caloriesPerGram: 0.45, unitGrams: 250, surfaceOffsetY: 0.22 },
  { name: 'Brócolos', file: 'broccoli.glb', baseScale: 0.8, caloriesPerGram: 0.34, unitGrams: 90, surfaceOffsetY: 0 },
  { name: 'Maçã', file: 'apple.glb', baseScale: 0.10, caloriesPerGram: 0.52, unitGrams: 150, surfaceOffsetY: 0 }
]

const CONFIG = {
  plate: {
    scale: 3.0,
    y: -0.5,
    height: 0.1
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
let junkControls, healthyControls
let handleWindowResize
let handlePointerMove
let handlePointerLeave
let handlePointerDown

const isVertical = ref(false)

const updateCameraFrames = () => {
  if (!junkCamera || !healthyCamera || !canvasContainer.value) return
  
  const width = canvasContainer.value.clientWidth
  const height = canvasContainer.value.clientHeight
  isVertical.value = width < 768

  const aspect = isVertical.value 
    ? width / (height / 2)
    : (width / 2) / height

  junkCamera.aspect = aspect
  healthyCamera.aspect = aspect

  // Optimized camera distance and angle for each orientation
  if (isVertical.value) {
    junkCamera.position.set(0, 7, 10)
    healthyCamera.position.set(0, 7, 10)
  } else {
    junkCamera.position.set(0, 5, 8)
    healthyCamera.position.set(0, 5, 8)
  }
  
  const targetY = CONFIG.plate.y
  junkCamera.lookAt(0, targetY, 0)
  healthyCamera.lookAt(0, targetY, 0)
  
  if (junkControls) junkControls.target.set(0, targetY, 0)
  if (healthyControls) healthyControls.target.set(0, targetY, 0)
  
  junkCamera.updateProjectionMatrix()
  healthyCamera.updateProjectionMatrix()
}

const initScene = () => {
  if (!canvasContainer.value) return
  
  junkScene = new THREE.Scene()
  healthyScene = new THREE.Scene()

  const width = canvasContainer.value.clientWidth
  const height = canvasContainer.value.clientHeight
  
  junkCamera = new THREE.PerspectiveCamera(40, 1, 0.1, 1000)
  healthyCamera = new THREE.PerspectiveCamera(40, 1, 0.1, 1000)
  
  updateCameraFrames()

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  canvasContainer.value.appendChild(renderer.domElement)

  junkControls = new OrbitControls(junkCamera, renderer.domElement)
  junkControls.enableDamping = true
  junkControls.dampingFactor = 0.07
  junkControls.enablePan = false
  junkControls.minDistance = 4
  junkControls.maxDistance = 14
  junkControls.target.set(0, CONFIG.plate.y, 0)
  junkControls.enabled = false

  healthyControls = new OrbitControls(healthyCamera, renderer.domElement)
  healthyControls.enableDamping = true
  healthyControls.dampingFactor = 0.07
  healthyControls.enablePan = false
  healthyControls.minDistance = 4
  healthyControls.maxDistance = 14
  healthyControls.target.set(0, CONFIG.plate.y, 0)
  healthyControls.enabled = false

  handlePointerMove = (event) => {
    if (!renderer) return
    const rect = renderer.domElement.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    if (isVertical.value) {
      const topHalf = y < rect.height / 2
      junkControls.enabled = topHalf
      healthyControls.enabled = !topHalf
    } else {
      const leftHalf = x < rect.width / 2
      junkControls.enabled = leftHalf
      healthyControls.enabled = !leftHalf
    }
  }

  handlePointerLeave = () => {
    junkControls.enabled = false
    healthyControls.enabled = false
  }

  handlePointerDown = (event) => {
    handlePointerMove(event)
  }

  renderer.domElement.addEventListener('pointermove', handlePointerMove)
  renderer.domElement.addEventListener('pointerleave', handlePointerLeave)
  renderer.domElement.addEventListener('pointerdown', handlePointerDown)

  const setupLights = (scene) => {
    const ambient = new THREE.AmbientLight(0xffffff, 1.2)
    scene.add(ambient)
    const sun = new THREE.DirectionalLight(0xffffff, 1.0)
    sun.position.set(5, 10, 5)
    scene.add(sun)
  }
  
  setupLights(junkScene)
  setupLights(healthyScene)

  const plateGeometry = new THREE.CylinderGeometry(2, 2, 0.1, 32)
  const plateMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xf0f0f0,
    roughness: 0.3,
    metalness: 0.1
  })
  
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
  if (!grams || !unitGrams) return 0
  return Math.max(0, Math.min(12, Math.floor(grams / unitGrams)))
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

const getPizzaSliceLayout = (index, total) => {
  const slicesPerPizza = 8
  const pizzaIndex = Math.floor(index / slicesPerPizza)
  const sliceIndex = index % slicesPerPizza
  const slicesInThisPizza = Math.min(slicesPerPizza, total - (pizzaIndex * slicesPerPizza))

  const centerX = total > slicesPerPizza ? (pizzaIndex === 0 ? -0.85 : 0.85) : 0
  const centerZ = 0
  const angleStep = (Math.PI * 2) / Math.max(slicesInThisPizza, 2)
  const angle = sliceIndex * angleStep
  const radius = slicesInThisPizza <= 1 ? 0 : 0.38

  return {
    x: centerX + Math.cos(angle) * radius,
    z: centerZ + Math.sin(angle) * radius,
    rotationY: (-angle + Math.PI / 2),
    scaleMultiplier: 1.45
  }
}

const normalizeModelToGround = (model) => {
  const bounds = new THREE.Box3().setFromObject(model)
  const center = bounds.getCenter(new THREE.Vector3())
  const minY = bounds.min.y

  model.position.x -= center.x
  model.position.z -= center.z
  model.position.y -= minY
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
  const plateTopY = CONFIG.plate.y + (CONFIG.plate.height / 2)

  for (let i = 0; i < copies; i += 1) {
    const copy = template.clone(true)
    const isPizza = config.name === 'Pizza'
    const slot = isPizza ? getPizzaSliceLayout(i, copies) : getSlotPosition(i, copies)
    const { x, z } = slot
    const yOffset = copies > 7 ? (i % 2) * 0.08 : 0
    copy.position.set(x, plateTopY + yOffset + (config.surfaceOffsetY || 0), z)
    copy.rotation.y = isPizza ? slot.rotationY : (Math.PI / 4 + i * 0.25)
    const scaleMultiplier = isPizza ? (slot.scaleMultiplier || 1) : 1
    copy.scale.setScalar(config.baseScale * scaleMultiplier)
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
    normalizeModelToGround(model)

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
  if (junkControls) junkControls.update()
  if (healthyControls) healthyControls.update()
  
  if (renderer && canvasContainer.value) {
    const width = renderer.domElement.clientWidth
    const height = renderer.domElement.clientHeight
    
    if (isVertical.value) {
      // Top half (Junk)
      renderer.setViewport(0, height / 2, width, height / 2)
      renderer.setScissor(0, height / 2, width, height / 2)
      renderer.setScissorTest(true)
      renderer.render(junkScene, junkCamera)
      
      // Bottom half (Healthy)
      renderer.setViewport(0, 0, width, height / 2)
      renderer.setScissor(0, 0, width, height / 2)
      renderer.render(healthyScene, healthyCamera)
    } else {
      // Left half (Junk)
      renderer.setViewport(0, 0, width / 2, height)
      renderer.setScissor(0, 0, width / 2, height)
      renderer.setScissorTest(true)
      renderer.render(junkScene, junkCamera)
      
      // Right half (Healthy)
      renderer.setViewport(width / 2, 0, width / 2, height)
      renderer.setScissor(width / 2, 0, width / 2, height)
      renderer.render(healthyScene, healthyCamera)
    }
    
    renderer.setScissorTest(false)
  }
}

watch(calorieBudget, updateScales)

onMounted(() => {
  initScene()
  loadFood('junk')
  loadFood('healthy')
  animate()
  
  handleWindowResize = () => {
    if (!canvasContainer.value || !renderer) return
    const width = canvasContainer.value.clientWidth
    const height = canvasContainer.value.clientHeight
    
    renderer.setSize(width, height)
    updateCameraFrames()
  }

  window.addEventListener('resize', handleWindowResize)
  // Ensure initial frame is perfect
  setTimeout(handleWindowResize, 100)
})

onBeforeUnmount(() => {
  if (renderer?.domElement) {
    renderer.domElement.removeEventListener('pointermove', handlePointerMove)
    renderer.domElement.removeEventListener('pointerleave', handlePointerLeave)
    renderer.domElement.removeEventListener('pointerdown', handlePointerDown)
  }
  if (handleWindowResize) {
    window.removeEventListener('resize', handleWindowResize)
  }
  junkControls?.dispose()
  healthyControls?.dispose()
  renderer?.dispose()
})
</script>

<template>
  <div class="volume-comparison flex flex-col h-full max-h-[calc(100vh-80px)] md:max-h-[calc(100vh-120px)] overflow-hidden">
    <!-- Header: Minimal & Clean -->
    <header class="mb-4 text-center md:mb-6">
      <span class="px-3 py-1 md:px-4 text-[9px] md:text-[10px] font-extrabold tracking-[0.2em] text-white uppercase bg-blue-600 rounded-full shadow-lg shadow-blue-500/20">
        Laboratório de Saciedade
      </span>
      <h1 class="mt-2 text-2xl font-black tracking-tight md:mt-4 md:text-4xl" :class="uiTheme.title">
        A Ilusão das Calorias
      </h1>
      <p class="mt-1 text-xs font-semibold md:text-sm" :class="uiTheme.subtitle">
        Visualize como <span class="font-bold underline decoration-2 underline-offset-4" :class="props.isDarkMode ? 'text-blue-400' : 'text-blue-600'">{{ calorieBudget }} kcal</span> ocupam o espaço real.
      </p>
    </header>

    <!-- Main Stage -->
    <div class="volume-stage relative flex-1 min-h-0 rounded-[2rem] md:rounded-[2.5rem] border flex flex-col overflow-hidden" :class="uiTheme.stage">
      
      <!-- 3D Viewport -->
      <div class="volume-viewport relative flex-1 w-full min-h-0 cursor-grab active:cursor-grabbing bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))]" :class="uiTheme.viewport" ref="canvasContainer">
        
        <!-- Overlays: Junk Food Info -->
        <div class="food-card absolute z-20 flex flex-col items-center p-4 md:p-5 transition-all transform rounded-[1.2rem] md:rounded-[1.5rem] backdrop-blur-sm shadow-lg border min-w-[170px] md:min-w-[220px]" 
             :class="[uiTheme.card, isVertical ? 'top-3 left-1/2 -translate-x-1/2 w-[calc(100%-24px)] max-w-[340px]' : 'top-6 left-6']">
          <span class="text-[10px] md:text-[11px] font-black text-rose-500 uppercase tracking-[0.18em] mb-1.5">Ultra-Processado</span>
          <div class="text-lg md:text-2xl font-extrabold leading-tight text-center" :class="uiTheme.cardTitle">{{ currentJunkConfig.name }}</div>
          <div class="mt-1 text-sm md:text-base font-semibold" :class="uiTheme.cardMeta">
            {{ junkGrams }}g<span v-if="junkUnits > 0"> · {{ junkUnits }} un.</span>
          </div>
          <button @click="cycle('junk')" class="mt-3 md:mt-4 px-4 py-2 md:px-5 md:py-2.5 text-xs md:text-sm font-bold rounded-xl transition-all flex items-center gap-2 border" :class="uiTheme.cardBtn">
            <span>Trocar</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 md:w-3.5 h-3 md:h-3.5 opacity-60" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
          </button>
        </div>

        <!-- VS Badge Center -->
        <div class="absolute z-20 transform -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
           <div class="flex items-center justify-center w-10 h-10 md:w-12 md:h-12 font-black text-white rounded-full shadow-2xl outline outline-[4px] md:outline-[6px] text-[10px] md:text-xs italic tracking-tighter" :class="uiTheme.vs">VS</div>
        </div>

        <!-- Split Lines -->
        <div v-if="!isVertical" class="absolute inset-y-0 z-10 hidden border-l border-dashed left-1/2 md:block" :class="uiTheme.divider"></div>
        <div v-else class="absolute inset-x-0 z-10 border-t border-dashed top-1/2" :class="uiTheme.divider"></div>

        <!-- Overlays: Healthy Food Info -->
        <div class="food-card absolute z-20 flex flex-col items-center p-4 md:p-5 transition-all transform rounded-[1.2rem] md:rounded-[1.5rem] backdrop-blur-sm shadow-lg border min-w-[170px] md:min-w-[220px]" 
             :class="[uiTheme.card, isVertical ? 'bottom-3 left-1/2 -translate-x-1/2 w-[calc(100%-24px)] max-w-[340px]' : 'top-6 right-6']">
          <span class="text-[10px] md:text-[11px] font-black text-emerald-500 uppercase tracking-[0.18em] mb-1.5">Densidade Baixa</span>
          <div class="text-lg md:text-2xl font-extrabold leading-tight text-center" :class="uiTheme.cardTitle">{{ currentHealthyConfig.name }}</div>
          <div class="mt-1 text-sm md:text-base font-semibold" :class="uiTheme.cardMeta">
            {{ healthyGrams }}g<span v-if="healthyUnits > 0"> · {{ healthyUnits }} un.</span>
          </div>
          <button @click="cycle('healthy')" class="mt-3 md:mt-4 px-4 py-2 md:px-5 md:py-2.5 text-xs md:text-sm font-bold rounded-xl transition-all flex items-center gap-2 border" :class="uiTheme.cardBtn">
            <span>Trocar</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 md:w-3.5 h-3 md:h-3.5 opacity-60" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" /></svg>
          </button>
        </div>

        <div v-if="isLoading" class="absolute inset-0 z-30 grid place-items-center bg-slate-950/25 backdrop-blur-[2px]">
          <div class="px-4 py-2 text-xs font-bold text-white rounded-xl bg-slate-900/80">
            A carregar modelo...
          </div>
        </div>
      </div>

      <!-- Anchored Footer Controls -->
      <footer class="p-4 border-t md:p-8 rounded-b-3xl" :class="uiTheme.footer">
        <div class="flex flex-col items-center gap-4 md:gap-8 md:flex-row md:justify-between">
          
          <!-- Slider Control -->
          <div class="flex-1 w-full max-w-xl">
            <div class="flex items-center justify-between mb-2 md:mb-4">
              <label class="text-[9px] md:text-[10px] font-black tracking-[0.2em] uppercase" :class="uiTheme.sliderHint">Orçamento de Calorias</label>
              <div class="flex items-baseline gap-1.5">
                <span class="text-2xl font-black md:text-3xl tabular-nums" :class="uiTheme.satietyText">{{ calorieBudget }}</span>
                <span class="text-[10px] md:text-xs font-bold uppercase" :class="uiTheme.sliderHint">kcal</span>
              </div>
            </div>
            <input type="range" v-model.number="calorieBudget" min="100" max="2000" step="50" class="w-full h-2 rounded-lg appearance-none cursor-pointer accent-blue-500 focus:outline-none" :class="uiTheme.sliderTrack">
            <div class="flex justify-between mt-1 md:mt-2 text-[9px] md:text-[10px] font-semibold" :class="uiTheme.sliderHint">
              <span>100 kcal</span>
              <span>2000 kcal</span>
            </div>
          </div>

          <!-- Satiety Insight Badge -->
          <div class="flex items-center w-full gap-4 px-4 py-3 border md:w-auto md:gap-5 md:px-6 md:py-5 rounded-2xl md:rounded-[2rem] transition-all" :class="uiTheme.satietyBadge">
            <div class="flex items-center justify-center w-10 h-10 text-xl rounded-xl md:w-12 md:h-12 md:text-2xl md:rounded-2xl bg-emerald-500/20 shadow-inner">🥗</div>
            <div>
              <div class="text-[9px] md:text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-0.5">Fator de Saciedade</div>
              <div class="text-lg font-black md:text-xl" :class="uiTheme.satietyText">
                {{ satietyMultiplier.toFixed(1) }}x <span class="text-xs md:text-sm font-medium" :class="uiTheme.satietySub">mais volume</span>
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

@media (max-width: 768px) {
  .volume-comparison {
    max-height: none !important;
    overflow: visible !important;
  }

  .volume-stage {
    min-height: 760px;
  }

  .volume-viewport {
    min-height: 520px;
  }

  .food-card {
    min-width: 0 !important;
    padding: 12px !important;
  }

  .food-card button {
    width: 100%;
    justify-content: center;
  }
}
</style>
