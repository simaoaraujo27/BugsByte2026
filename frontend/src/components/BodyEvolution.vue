<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue'
import * as THREE from 'three'
import { useRouter } from 'vue-router'
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { useUser } from '@/store/userStore'

const router = useRouter()
const { user } = useUser()
const canvasContainer = ref(null)
const isLoading = ref(true)
const loadError = ref(null)

// Simulation State
const simState = ref({
  calories: 0,
  protein: 0,
  water: 50,
  timeframe: 6
})

// Three.js Variables
let scene, camera, renderer, controls
let characterModel
let bones = {}
let hologramMesh
let animationId

const findBoneFlexible = (object, hints) => {
  let found = null
  object.traverse((child) => {
    if (found) return
    const name = child.name.toLowerCase()
    if (hints.some(h => name.includes(h.toLowerCase()))) {
      found = child
    }
  })
  return found
}

const findAllBones = (model) => {
  return {
    hips: findBoneFlexible(model, ['Hips', 'Pelvis']),
    spine: [findBoneFlexible(model, ['Spine', 'Spine1', 'Spine2'])].filter(Boolean),
    arms: [
        findBoneFlexible(model, ['LeftArm', 'LeftArm', 'L_Arm']), 
        findBoneFlexible(model, ['RightArm', 'RightArm', 'R_Arm'])
    ].filter(Boolean),
    legs: [
        findBoneFlexible(model, ['LeftUpLeg', 'L_UpLeg']), 
        findBoneFlexible(model, ['RightUpLeg', 'R_UpLeg'])
    ].filter(Boolean),
    head: findBoneFlexible(model, ['Head'])
  }
}

const initScene = () => {
  if (!canvasContainer.value) return

  const width = canvasContainer.value.clientWidth
  const height = canvasContainer.value.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x111827)
  scene.fog = new THREE.Fog(0x111827, 5, 30)

  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(0, 1.4, 3.5)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.outputColorSpace = THREE.SRGBColorSpace
  canvasContainer.value.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.target.set(0, 1, 0)
  controls.maxPolarAngle = Math.PI / 2
  controls.minDistance = 1.5
  controls.maxDistance = 6

  const ambient = new THREE.AmbientLight(0xffffff, 1.5)
  scene.add(ambient)
  const sun = new THREE.DirectionalLight(0xffffff, 3.0)
  sun.position.set(2, 5, 5)
  sun.castShadow = true
  scene.add(sun)
  
  const gridHelper = new THREE.GridHelper(20, 20, 0x0ea5e9, 0x1e293b)
  scene.add(gridHelper)

  loadCharacter()

  const resizeObserver = new ResizeObserver(() => onResize())
  resizeObserver.observe(canvasContainer.value)
}

const loadCharacter = () => {
  const userSex = user.value?.sexo || 'M'
  const isFemale = ['f', 'feminino', 'female', 'mulher'].includes(String(userSex).toLowerCase())
  const filename = isFemale ? 'female.fbx' : 'male.fbx'
  
  console.log(`Loading Mixamo Model: ${filename}`)

  const loader = new FBXLoader()
  loader.load(
    `/models/${filename}`,
    (object) => {
        setupModel(object, isFemale)
    },
    (xhr) => {
       // Progress
    },
    (error) => {
        console.error('FBX Load Error:', error)
        createPlaceholderModel()
    }
  )
}

const setupModel = (object, isFemale) => {
    characterModel = object
    
    const box = new THREE.Box3().setFromObject(object)
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())

    object.position.x += -center.x
    object.position.z += -center.z
    object.position.y += -box.min.y

    const targetHeight = isFemale ? 1.70 : 1.80
    const scale = targetHeight / size.y
    object.scale.setScalar(scale)

    object.traverse(child => {
        if (child.isMesh) {
            child.castShadow = true
            child.receiveShadow = true
            if (child.material) {
                child.material.roughness = 0.6
                child.material.metalness = 0.1
                child.material.skinning = true
            }
        }
    })

    bones = findAllBones(object)
    scene.add(object)
    createProfileHologram() 
    isLoading.value = false
    updateBodyShape()
}

const createPlaceholderModel = () => {
    const group = new THREE.Group()
    const mat = new THREE.MeshStandardMaterial({ color: 0x0ea5e9, wireframe: false })
    
    const torso = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.6, 0.25), mat)
    torso.position.y = 1.1
    group.add(torso)
    bones.spine = [torso]

    const head = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.3, 0.25), mat)
    head.position.y = 1.65
    group.add(head)
    bones.head = head

    characterModel = group
    scene.add(group)
    createProfileHologram()
    isLoading.value = false
}

const createProfileHologram = () => {
  // Create a CIRCLE geometry for the face
  const geometry = new THREE.CircleGeometry(0.18, 32)
  const textureLoader = new THREE.TextureLoader()
  const profileImg = user.value?.profile_image || '/assets/logo.png'
  
  textureLoader.load(profileImg, (texture) => {
    // Center texture
    texture.center.set(0.5, 0.5)
    
    const material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      opacity: 0.9,
      side: THREE.DoubleSide,
      depthTest: false // Always visible on top
    })
    
    hologramMesh = new THREE.Mesh(geometry, material)
    
    // Add glowing border ring
    const frameGeo = new THREE.RingGeometry(0.18, 0.20, 32)
    const frameMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, side: THREE.DoubleSide })
    const frame = new THREE.Mesh(frameGeo, frameMat)
    hologramMesh.add(frame)
    
    // Add "Identity" line connecting to head
    const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, -0.25, 0),
        new THREE.Vector3(0, -0.18, 0)
    ])
    const lineMat = new THREE.LineBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.5 })
    const line = new THREE.Line(lineGeo, lineMat)
    hologramMesh.add(line)
    
    scene.add(hologramMesh)
    hologramMesh.renderOrder = 999
  })
}

const updateBodyShape = () => {
  if (!characterModel) return

  // TIME MULTIPLIER - More time = more pronounced changes
  // Non-linear progression: early months show less change, later months show more
  // 1 month = 0.15x, 6 months = 0.65x, 12 months = 1.0x, 24 months = 1.8x
  const timeMonths = simState.value.timeframe
  const timeFactor = Math.pow(timeMonths / 12, 0.85) * 0.9 + 0.15
  
  // 1. FAT MODIFIER (More organic)
  // Calories -> Stomach & Hips (affected by time)
  const fatFactor = (simState.value.calories / 100) * timeFactor // -0.5 to 0.5 range, scaled by time
  // Base scale is 1.0. Max fat is 1.6, min is 0.8
  const spineScale = 1 + (fatFactor * 0.6) 
  const hipsScale = 1 + (fatFactor * 0.5)
  
  if (bones.hips) {
    // Hips widen more than they grow tall
    if (Array.isArray(bones.hips)) {
        bones.hips.forEach(b => b.scale.set(hipsScale, 1, hipsScale))
    } else {
        bones.hips.scale.set(hipsScale, 1, hipsScale)
    }
  }
  
  if (bones.spine) {
      bones.spine.forEach((bone, index) => {
        // Lower spine (belly) gets more fat than upper spine
        const intensity = 1 - (index * 0.2) // Fade out effect up the spine
        const localScale = 1 + (fatFactor * 0.6 * Math.max(0, intensity))
        bone.scale.set(localScale, 1, localScale)
      })
  }

  // 2. MUSCLE MODIFIER (affected by time)
  // Protein -> Arms & Legs Thickness
  // Muscle growth requires time - scaled by timeFactor
  const muscleFactor = (simState.value.protein / 100) * timeFactor // 0 to 1, scaled by time
  const muscleScale = 1 + (muscleFactor * 0.45) // Max 45% growth with time

  if (bones.arms) {
      bones.arms.forEach(bone => {
        bone.scale.set(muscleScale, 1, muscleScale)
      })
  }
  
  if (bones.legs) {
      bones.legs.forEach(bone => {
        bone.scale.set(muscleScale, 1, muscleScale)
      })
  }

  // 3. HYDRATION MODIFIER (subtle posture/height effect)
  // Water affects overall body hydration - subtle height variation
  const waterFactor = simState.value.water / 100 // 0 to 1
  const heightScale = 0.98 + (waterFactor * 0.04) // 98% to 102% height variation
  
  if (bones.spine && bones.spine.length > 0) {
    // Apply subtle vertical stretch to simulate hydration
    bones.spine[0].scale.y = heightScale
  }
}

const resetSimulation = () => {
  simState.value = {
    calories: 0,
    protein: 0,
    water: 50,
    timeframe: 6
  }
}

watch(simState, () => {
    updateBodyShape()
}, { deep: true })

// ...

const animate = () => {
  animationId = requestAnimationFrame(animate)
  controls.update()
  
  if (hologramMesh && bones.head) {
      const headPos = new THREE.Vector3()
      if (bones.head.getWorldPosition) {
          bones.head.getWorldPosition(headPos)
      } else {
          headPos.copy(bones.head.position)
      }
      
      // Position strictly above head
      // Adjusted offset: 0.15 to be even closer to the head
      hologramMesh.position.copy(headPos).add(new THREE.Vector3(0, 0.15, 0))
      
      // Billboard behavior: Always face camera
      hologramMesh.lookAt(camera.position)
      
      // Float animation
      hologramMesh.position.y += Math.sin(Date.now() * 0.0015) * 0.015
  }

  renderer.render(scene, camera)
}

onMounted(() => {
  initScene()
  animate()
  window.addEventListener('resize', onResize)
})

const onResize = () => {
  if (!canvasContainer.value) return
  const width = canvasContainer.value.clientWidth
  const height = canvasContainer.value.clientHeight
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  cancelAnimationFrame(animationId)
  if (renderer) renderer.dispose()
})
</script>

<template>
  <div class="body-evolution-container flex flex-col bg-slate-900 text-white rounded-3xl overflow-hidden shadow-2xl border border-slate-700 h-full min-h-[600px]">
    <!-- Header -->
    <div class="p-4 bg-slate-800/50 backdrop-blur-md border-b border-slate-700 flex justify-between items-center z-10 relative">
      <div class="flex items-center gap-3">
        <div>
          <h2 class="text-lg font-black tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Evolução
          </h2>
        </div>
      </div>
      <div class="bg-blue-600/20 border border-blue-500/30 px-2 py-0.5 rounded-full text-[9px] font-bold tracking-wider text-blue-300 uppercase animate-pulse">
        Simulação
      </div>
    </div>

    <div class="flex flex-col md:flex-row flex-1 min-h-0 relative">
      
      <!-- 3D Viewport -->
      <div class="relative flex-1 bg-gradient-to-b from-slate-900 to-black" ref="canvasContainer">
        <!-- Loading State -->
        <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-slate-900/80 z-20">
          <div class="text-center">
            <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-blue-400 text-sm font-bold animate-pulse">A carregar Modelo Biométrico...</p>
            <p v-if="loadError" class="text-red-400 text-xs mt-2 max-w-xs">{{ loadError }}</p>
          </div>
        </div>

        <!-- Time Label Overlay -->
        <div v-if="simState" class="absolute top-4 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur px-4 py-2 rounded-xl border border-white/10 text-center pointer-events-none select-none">
          <div class="text-[10px] uppercase text-slate-400 font-bold tracking-widest mb-1">Previsão Temporal</div>
          <div class="text-2xl font-black text-white">+{{ simState.timeframe }} Meses</div>
        </div>
      </div>

      <!-- Controls Panel -->
      <div v-if="simState" class="w-full md:w-80 bg-slate-900/95 backdrop-blur-xl border-l border-slate-700 flex flex-col z-10 shadow-2xl">
        
        <div class="p-5 flex-1 overflow-y-auto custom-scrollbar">
            
            <!-- Header & Reset -->
            <div class="flex items-end justify-between mb-6 pb-4 border-b border-slate-700/50">
                <div>
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-100">Parâmetros</h3>
                    <p class="text-[10px] text-slate-400 mt-0.5">Ajuste em tempo real</p>
                </div>
                <button 
                    @click="resetSimulation"
                    class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-red-500/10 border border-slate-700 hover:border-red-500/30 text-[10px] font-bold uppercase tracking-wider text-slate-400 hover:text-red-400 transition-all flex items-center gap-1.5 group"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 group-hover:rotate-180 transition-transform duration-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Reset
                </button>
            </div>

            <div class="space-y-8">
                <!-- Time Travel Slider -->
                <div class="control-group">
                  <div class="flex justify-between items-center mb-3">
                    <label class="text-xs font-bold text-slate-300 flex items-center gap-2">
                        <div class="w-6 h-6 rounded-md bg-purple-500/20 flex items-center justify-center text-purple-400">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" /></svg>
                        </div>
                        Tempo
                    </label>
                    <span class="font-mono text-xs font-bold text-purple-300 bg-purple-500/10 px-2 py-1 rounded border border-purple-500/20">+{{ simState.timeframe }} meses</span>
                  </div>
                  <div class="slider-container">
                    <input type="range" v-model.number="simState.timeframe" min="1" max="24" step="1" class="styled-slider purple-slider">
                  </div>
                  <div class="flex justify-between mt-2 text-[9px] font-bold text-slate-600 uppercase tracking-widest px-1">
                    <span>Hoje</span>
                    <span>2 Anos</span>
                  </div>
                </div>

                <!-- Calories (Fat) -->
                <div class="control-group">
                  <div class="flex justify-between items-center mb-3">
                    <label class="text-xs font-bold text-slate-300 flex items-center gap-2">
                        <div class="w-6 h-6 rounded-md bg-orange-500/20 flex items-center justify-center text-orange-400">
                             <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.45-.412-1.725a1 1 0 00-1.457-.899c-.5.263-1.092.709-1.503 1.373-.787 1.275-.818 3.122-.047 5.093.593 1.517 2.052 3.037 4.542 2.712 3.15-.411 5.34-3.118 5.76-6.42.062-.489.102-.99.123-1.494.02-.49.02-1.025-.018-1.553a9.96 9.96 0 00-.317-1.85 7.152 7.152 0 00-.816-1.92 5.674 5.674 0 00-.615-.975z" clip-rule="evenodd" /></svg>
                        </div>
                        Calorias
                    </label>
                    <span class="font-mono text-xs font-bold px-2 py-1 rounded border"
                          :class="simState.calories > 0 ? 'text-orange-300 bg-orange-500/10 border-orange-500/20' : (simState.calories < 0 ? 'text-green-300 bg-green-500/10 border-green-500/20' : 'text-slate-400 bg-slate-700/50 border-slate-600')">
                      {{ simState.calories > 0 ? '+' : '' }}{{ simState.calories }}%
                    </span>
                  </div>
                  <div class="slider-container relative">
                     <input type="range" v-model.number="simState.calories" min="-50" max="50" step="1" class="styled-slider orange-slider">
                     <!-- Center Marker -->
                     <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-0.5 h-6 bg-slate-500/50 rounded-full pointer-events-none"></div>
                  </div>
                  <div class="flex justify-between mt-2 text-[9px] font-bold text-slate-600 uppercase tracking-widest px-1">
                    <span>Défice</span>
                    <span>Excesso</span>
                  </div>
                </div>

                <!-- Protein (Muscle) -->
                <div class="control-group">
                  <div class="flex justify-between items-center mb-3">
                    <label class="text-xs font-bold text-slate-300 flex items-center gap-2">
                        <div class="w-6 h-6 rounded-md bg-blue-500/20 flex items-center justify-center text-blue-400">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 2a4 4 0 00-4 4v1H5a1 1 0 00-.994.89l-1 9A1 1 0 004 18h12a1 1 0 00.994-1.11l-1-9A1 1 0 0015 7h-1V6a4 4 0 00-4-4zm2 5V6a2 2 0 10-4 0v1h4zm-6 3a1 1 0 112 0 1 1 0 01-2 0zm7-1a1 1 0 100 2 1 1 0 000-2z" clip-rule="evenodd" /></svg>
                        </div>
                        Proteína
                    </label>
                    <span class="font-mono text-xs font-bold text-blue-300 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20">{{ simState.protein }}%</span>
                  </div>
                  <div class="slider-container">
                    <input type="range" v-model.number="simState.protein" min="0" max="100" step="1" class="styled-slider blue-slider">
                  </div>
                  <p class="mt-2 text-[10px] text-slate-500 leading-tight">
                    Impacta o desenvolvimento muscular e a definição.
                  </p>
                </div>

                <!-- Water (Skin) -->
                <div class="control-group">
                  <div class="flex justify-between items-center mb-3">
                    <label class="text-xs font-bold text-slate-300 flex items-center gap-2">
                        <div class="w-6 h-6 rounded-md bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" /></svg>
                        </div>
                        Água
                    </label>
                    <span class="font-mono text-xs font-bold text-cyan-300 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/20">{{ simState.water }}%</span>
                  </div>
                  <div class="slider-container">
                    <input type="range" v-model.number="simState.water" min="0" max="100" step="1" class="styled-slider cyan-slider">
                  </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Cross-browser Slider Styling - Base */
.styled-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  background: linear-gradient(to right, rgba(30, 41, 59, 0.8), rgba(30, 41, 59, 0.5));
  border-radius: 12px;
  outline: none;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.4), 0 1px 2px rgba(255,255,255,0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.styled-slider:hover {
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.5), 0 2px 8px rgba(14, 165, 233, 0.2);
}

/* TRACK - Webkit (filled portion) */
.styled-slider::-webkit-slider-runnable-track {
  width: 100%;
  height: 8px;
  border-radius: 12px;
}

/* TRACK - Firefox */
.styled-slider::-moz-range-track {
  width: 100%;
  height: 8px;
  background: transparent;
  border-radius: 12px;
}

/* Progress Fill - Firefox */
.styled-slider::-moz-range-progress {
  height: 8px;
  border-radius: 12px 0 0 12px;
}

/* THUMB - Webkit */
.styled-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  cursor: pointer;
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(255, 255, 255, 0.1),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 12px rgba(14, 165, 233, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  margin-top: -6px;
}

.styled-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 6px rgba(255, 255, 255, 0.15),
    0 6px 12px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(14, 165, 233, 0.5);
}

.styled-slider:active::-webkit-slider-thumb {
  transform: scale(1.05);
}

/* THUMB - Firefox */
.styled-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.9);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(255, 255, 255, 0.1),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 12px rgba(14, 165, 233, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.styled-slider::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 6px rgba(255, 255, 255, 0.15),
    0 6px 12px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(14, 165, 233, 0.5);
}

/* ===== COLOR THEMES ===== */

/* Purple Slider (Time) */
.purple-slider {
  background: linear-gradient(to right, 
    rgba(168, 85, 247, 0.15) 0%, 
    rgba(30, 41, 59, 0.5) 50%,
    rgba(30, 41, 59, 0.3) 100%);
}

.purple-slider::-webkit-slider-thumb {
  background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 50%, #c084fc 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(168, 85, 247, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(168, 85, 247, 0.4);
}

.purple-slider::-moz-range-thumb {
  background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 50%, #c084fc 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(168, 85, 247, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(168, 85, 247, 0.4);
}

.purple-slider::-moz-range-progress {
  background: linear-gradient(to right, rgba(168, 85, 247, 0.4), rgba(168, 85, 247, 0.6));
}

/* Orange Slider (Calories) */
.orange-slider {
  background: linear-gradient(to right, 
    rgba(34, 197, 94, 0.15) 0%,
    rgba(30, 41, 59, 0.5) 50%,
    rgba(251, 146, 60, 0.15) 100%);
}

.orange-slider::-webkit-slider-thumb {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 50%, #fb923c 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(251, 146, 60, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(251, 146, 60, 0.4);
}

.orange-slider::-moz-range-thumb {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 50%, #fb923c 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(251, 146, 60, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(251, 146, 60, 0.4);
}

/* Blue Slider (Protein) */
.blue-slider {
  background: linear-gradient(to right, 
    rgba(59, 130, 246, 0.15) 0%,
    rgba(30, 41, 59, 0.5) 70%,
    rgba(30, 41, 59, 0.3) 100%);
}

.blue-slider::-webkit-slider-thumb {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 50%, #60a5fa 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(59, 130, 246, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(59, 130, 246, 0.4);
}

.blue-slider::-moz-range-thumb {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 50%, #60a5fa 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(59, 130, 246, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(59, 130, 246, 0.4);
}

.blue-slider::-moz-range-progress {
  background: linear-gradient(to right, rgba(59, 130, 246, 0.4), rgba(59, 130, 246, 0.6));
}

/* Cyan Slider (Water) */
.cyan-slider {
  background: linear-gradient(to right, 
    rgba(6, 182, 212, 0.15) 0%,
    rgba(30, 41, 59, 0.5) 70%,
    rgba(30, 41, 59, 0.3) 100%);
}

.cyan-slider::-webkit-slider-thumb {
  background: linear-gradient(135deg, #cffafe 0%, #67e8f9 50%, #22d3ee 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(6, 182, 212, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(6, 182, 212, 0.4);
}

.cyan-slider::-moz-range-thumb {
  background: linear-gradient(135deg, #cffafe 0%, #67e8f9 50%, #22d3ee 100%);
  box-shadow: 
    0 0 0 3px rgba(15, 23, 42, 0.95),
    0 0 0 5px rgba(6, 182, 212, 0.2),
    0 4px 8px rgba(0, 0, 0, 0.4),
    0 0 16px rgba(6, 182, 212, 0.4);
}

.cyan-slider::-moz-range-progress {
  background: linear-gradient(to right, rgba(6, 182, 212, 0.4), rgba(6, 182, 212, 0.6));
}

.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 4px;
}

/* Slider Container */
.slider-container {
  padding: 8px 0;
  position: relative;
}

/* Control Group */
.control-group {
  padding: 16px;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.control-group:hover {
  background: rgba(15, 23, 42, 0.5);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
</style>