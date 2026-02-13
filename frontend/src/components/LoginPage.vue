<script setup>
import { ref } from 'vue'
import logo from '@/assets/logo.png'

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const calorieBudget = ref(1850)
const fileInput = ref(null)
const errorMessage = ref('')
const successMessage = ref('')

// Clear messages on input
const clearMessages = () => {
    errorMessage.value = ''
    successMessage.value = ''
}

const handleLogin = () => {
  clearMessages()
  // Basic validation logic
  if (!email.value || !password.value) {
    errorMessage.value = 'Please fill in all fields before signing in.'
    return
  }
  
  console.log('Logging in with:', { email: email.value, rememberMe: rememberMe.value })
  // Simulate API call
  successMessage.value = 'Welcome back, Chef!'
  setTimeout(() => { successMessage.value = '' }, 3000)
}

const triggerNegotiator = () => {
  clearMessages()
  // Logic to open the Negotiator modal/view
  console.log("Negotiator Mode Activated")
  successMessage.value = "Negotiator Mode Activated: Let's make a deal!"
  setTimeout(() => { successMessage.value = '' }, 3000)
}

const triggerFridge = () => {
  clearMessages()
  // Logic to trigger file upload for Fridge Raid
  fileInput.value.click()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('Uploaded:', file.name)
    successMessage.value = `Scanning ${file.name} for ingredients...`
    // Here you would send the image to the backend
    setTimeout(() => { successMessage.value = '' }, 3000)
  }
}

const handleFridgeKeydown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
        triggerFridge()
    }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-nutri-green to-nutri-orange flex items-center justify-center p-4 font-sans text-gray-900">
    <div 
        class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-transform motion-reduce:transform-none hover:scale-[1.01]"
        role="main"
        aria-labelledby="page-title"
    >
      
      <!-- Header / Logo Area -->
      <header class="bg-nutri-light p-8 text-center relative overflow-hidden">
        <!-- Decorative Top Bar -->
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-orange-400 via-red-500 to-pink-500" aria-hidden="true"></div>
        
        <!-- Logo -->
        <div class="w-24 h-24 bg-white rounded-full mx-auto flex items-center justify-center shadow-md mb-4 animate-bounce-slow motion-reduce:animate-none overflow-hidden p-2">
            <img :src="logo" alt="NutriVentures Logo" class="w-full h-full object-contain" />
        </div>
        
        <h1 id="page-title" class="text-3xl font-extrabold text-nutri-dark tracking-tight">NutriVentures</h1>
        <p class="text-gray-600 text-sm mt-1">Smart Food Negotiator</p>
        
        <!-- Calorie Dashboard Element -->
        <div 
            class="mt-6 inline-flex items-center px-3 py-1 bg-white border border-gray-300 rounded-full shadow-sm"
            role="status"
            aria-label="Current Daily Calorie Budget"
        >
            <span class="w-2 h-2 rounded-full bg-green-600 mr-2 animate-pulse motion-reduce:animate-none" aria-hidden="true"></span>
            <span class="text-xs font-bold text-gray-700 uppercase tracking-wider mr-2">Daily Budget</span>
            <span class="text-sm font-bold text-nutri-dark">{{ calorieBudget }} kcal</span>
        </div>
      </header>

      <!-- Main Form Area -->
      <div class="p-8 pt-4 space-y-6">

        <!-- Live Region for Alerts -->
        <div role="alert" aria-live="assertive" class="min-h-[1.5rem]">
            <p v-if="errorMessage" class="text-red-700 bg-red-50 border border-red-200 p-2 rounded-md text-sm font-medium flex items-center">
                <span class="mr-2" aria-hidden="true">⚠️</span> {{ errorMessage }}
            </p>
            <p v-if="successMessage" class="text-green-800 bg-green-50 border border-green-200 p-2 rounded-md text-sm font-medium flex items-center">
                <span class="mr-2" aria-hidden="true">✅</span> {{ successMessage }}
            </p>
        </div>
        
        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5" novalidate>
          <div>
            <label for="email" class="block text-sm font-bold text-gray-800 mb-1">Email Address</label>
            <input 
              v-model="email"
              @input="clearMessages"
              type="email" 
              id="email"
              name="email"
              autocomplete="email"
              required
              aria-required="true"
              class="block w-full px-4 py-3 bg-gray-50 border border-gray-400 rounded-xl focus:ring-4 focus:ring-nutri-green/50 focus:border-nutri-green text-gray-900 transition-all outline-none placeholder-gray-500"
              placeholder="chef@nutriventures.com"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-bold text-gray-800 mb-1">Password</label>
            <input 
              v-model="password"
              @input="clearMessages"
              type="password" 
              id="password"
              name="password"
              autocomplete="current-password"
              required
              aria-required="true"
              class="block w-full px-4 py-3 bg-gray-50 border border-gray-400 rounded-xl focus:ring-4 focus:ring-nutri-green/50 focus:border-nutri-green text-gray-900 transition-all outline-none placeholder-gray-500"
              placeholder="••••••••"
            />
          </div>

          <div class="flex items-center justify-between">
            <label class="flex items-center space-x-2 cursor-pointer select-none group">
              <input 
                v-model="rememberMe"
                type="checkbox" 
                class="w-5 h-5 text-nutri-green border-gray-400 rounded focus:ring-4 focus:ring-nutri-green/50 focus:ring-offset-2"
              />
              <span class="text-sm text-gray-700 group-hover:text-gray-900 font-medium">Remember me</span>
            </label>
            <a href="#" class="text-sm font-bold text-nutri-orange hover:text-red-700 hover:underline focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-nutri-orange rounded px-1 transition-colors">Forgot password?</a>
          </div>

          <button 
            type="submit" 
            class="w-full py-3 px-4 bg-nutri-dark text-white font-bold rounded-xl shadow-lg hover:bg-gray-800 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-gray-900 transform transition active:scale-95 motion-reduce:transform-none"
          >
            Sign In
          </button>
        </form>

        <!-- Divider -->
        <div class="relative py-2" role="separator">
          <div class="absolute inset-0 flex items-center" aria-hidden="true">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-600 font-medium">Hackathon Mode</span>
          </div>
        </div>

        <!-- Fun Actions -->
        <div class="space-y-3">
            <!-- The Negotiator CTA -->
            <button 
                @click="triggerNegotiator"
                class="group relative w-full flex items-center justify-center py-3 px-4 border-2 border-dashed border-nutri-orange text-sm font-bold rounded-xl text-nutri-orange hover:bg-orange-50 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-nutri-orange transition-all"
                aria-label="I'm Hungry and Want Junk Food! Activate Negotiator Mode."
            >
                <span class="mr-2 text-xl group-hover:animate-wiggle motion-reduce:animate-none" aria-hidden="true">🍔</span>
                I'm Hungry & Want Junk Food!
            </button>

            <!-- Fridge Raid Mode -->
            <!-- Using div as button requires role, tabindex, and keydown handlers -->
            <div 
              class="relative overflow-hidden rounded-xl border border-gray-300 cursor-pointer group hover:shadow-md transition-all focus-within:ring-4 focus-within:ring-nutri-green/50"
              @click="triggerFridge"
              @keydown="handleFridgeKeydown"
              role="button"
              tabindex="0"
              aria-label="Fridge Raid Mode: Upload a photo of your fridge ingredients"
            >
                <div class="absolute inset-0 bg-gradient-to-r from-teal-400/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity motion-reduce:transition-none" aria-hidden="true"></div>
                <div class="relative flex items-center justify-center p-3 space-x-2 bg-white/50 backdrop-blur-sm">
                     <span class="text-xl" aria-hidden="true">📸</span>
                     <span class="text-sm font-bold text-gray-800">Fridge Raid Mode</span>
                </div>
                 <!-- Hidden File Input -->
                <input 
                    type="file" 
                    class="hidden" 
                    ref="fileInput" 
                    @change="handleFileUpload" 
                    accept="image/*" 
                    tabindex="-1"
                    aria-hidden="true"
                />
            </div>
        </div>

      </div>
      
      <!-- Footer -->
      <footer class="bg-gray-50 p-4 text-center border-t border-gray-200">
        <router-link 
          to="/"
          class="text-sm text-gray-600 hover:text-nutri-dark hover:underline font-bold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 rounded px-2 py-1 inline-block"
          aria-label="Return to Home Page"
        >
          &larr; Back to Home
        </router-link>
        <p class="text-xs text-gray-500 mt-2">&copy; 2026 NutriVentures Hackathon Build</p>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* Custom animations that Tailwind doesn't have by default */
.animate-bounce-slow {
  animation: bounce 3s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(-5%); animation-timing-function: cubic-bezier(0.8, 0, 1, 1); }
  50% { transform: translateY(0); animation-timing-function: cubic-bezier(0, 0, 0.2, 1); }
}

@keyframes wiggle {
    0%, 100% { transform: rotate(-6deg); }
    50% { transform: rotate(6deg); }
}

.group:hover .group-hover\:animate-wiggle {
    animation: wiggle 0.4s ease-in-out infinite;
}

/* Reduced Motion Overrides */
@media (prefers-reduced-motion: reduce) {
  .animate-bounce-slow,
  .group:hover .group-hover\:animate-wiggle,
  .animate-pulse {
    animation: none !important;
  }
  
  .transform {
    transform: none !important;
  }
  
  .transition-all,
  .transition-colors,
  .transition-opacity {
    transition: none !important;
  }
}
</style>
