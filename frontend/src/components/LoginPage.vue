<script setup>
import { ref } from 'vue'
import logo from '@/assets/logo.png'

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const calorieBudget = ref(1850)
const showNegotiator = ref(false)
const showFridge = ref(false)
const fileInput = ref(null)

const handleLogin = () => {
  // Basic validation logic
  if (!email.value || !password.value) {
    alert('Please fill in all fields!')
    return
  }
  console.log('Logging in with:', { email: email.value, rememberMe: rememberMe.value })
  // Simulate API call
  alert('Welcome back, Chef!')
}

const triggerNegotiator = () => {
  // Logic to open the Negotiator modal/view
  console.log("Negotiator Mode Activated")
  alert("Negotiator Mode Activated: Let's make a deal!")
  showNegotiator.value = true
}

const triggerFridge = () => {
  // Logic to trigger file upload for Fridge Raid
  fileInput.value.click()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('Uploaded:', file.name)
    alert(`Scanning ${file.name} for ingredients...`)
    // Here you would send the image to the backend
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-nutri-green to-nutri-orange flex items-center justify-center p-4 font-sans">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all hover:scale-[1.01]">
      
      <!-- Header / Logo Area -->
      <div class="bg-nutri-light p-8 text-center relative overflow-hidden">
        <!-- Decorative Top Bar -->
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-orange-400 via-red-500 to-pink-500"></div>
        
        <!-- Logo Placeholder -->
        <div class="w-24 h-24 bg-white rounded-full mx-auto flex items-center justify-center shadow-md mb-4 animate-bounce-slow overflow-hidden p-2">
            <img :src="logo" alt="NutriVentures Logo" class="w-full h-full object-contain" />
        </div>
        
        <h1 class="text-3xl font-extrabold text-nutri-dark tracking-tight">NutriVentures</h1>
        <p class="text-gray-500 text-sm mt-1">Smart Food Negotiator</p>
        
        <!-- Calorie Dashboard Element (Subtle) -->
        <div class="mt-6 inline-flex items-center px-3 py-1 bg-white border border-gray-200 rounded-full shadow-sm">
            <span class="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider mr-2">Daily Budget</span>
            <span class="text-sm font-bold text-nutri-dark">{{ calorieBudget }} kcal</span>
        </div>
      </div>

      <!-- Main Form Area -->
      <div class="p-8 pt-4 space-y-6">
        
        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <input 
              v-model="email"
              type="email" 
              id="email" 
              required
              class="block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-nutri-green focus:border-transparent transition-all outline-none placeholder-gray-400"
              placeholder="chef@nutriventures.com"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              v-model="password"
              type="password" 
              id="password" 
              required
              class="block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-nutri-green focus:border-transparent transition-all outline-none placeholder-gray-400"
              placeholder="••••••••"
            />
          </div>

          <div class="flex items-center justify-between">
            <label class="flex items-center space-x-2 cursor-pointer select-none">
              <input 
                v-model="rememberMe"
                type="checkbox" 
                class="w-4 h-4 text-nutri-green border-gray-300 rounded focus:ring-nutri-green"
              />
              <span class="text-sm text-gray-600">Remember me</span>
            </label>
            <a href="#" class="text-sm font-medium text-nutri-orange hover:text-red-600 transition-colors">Forgot password?</a>
          </div>

          <button 
            type="submit" 
            class="w-full py-3 px-4 bg-nutri-dark text-white font-bold rounded-xl shadow-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 transform transition active:scale-95"
          >
            Sign In
          </button>
        </form>

        <!-- Divider -->
        <div class="relative py-2">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500 font-medium">Hackathon Mode</span>
          </div>
        </div>

        <!-- Fun Actions -->
        <div class="space-y-3">
            <!-- The Negotiator CTA -->
            <button 
                @click="triggerNegotiator"
                class="group relative w-full flex items-center justify-center py-3 px-4 border-2 border-dashed border-nutri-orange text-sm font-bold rounded-xl text-nutri-orange hover:bg-orange-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-nutri-orange transition-all"
            >
                <span class="mr-2 text-xl group-hover:animate-wiggle">🍔</span>
                I'm Hungry & Want Junk Food!
            </button>

            <!-- Fridge Raid Mode -->
            <div 
              class="relative overflow-hidden rounded-xl border border-gray-200 cursor-pointer group hover:shadow-md transition-all"
              @click="triggerFridge"
            >
                <div class="absolute inset-0 bg-gradient-to-r from-teal-400/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div class="relative flex items-center justify-center p-3 space-x-2 bg-white/50 backdrop-blur-sm">
                     <span class="text-xl">📸</span>
                     <span class="text-sm font-medium text-gray-700">Fridge Raid Mode</span>
                </div>
                 <!-- Hidden File Input for demo -->
                <input type="file" class="hidden" ref="fileInput" @change="handleFileUpload" accept="image/*" />
            </div>
        </div>

      </div>
      
      <!-- Footer -->
      <div class="bg-gray-50 p-4 text-center border-t border-gray-100">
        <p class="text-xs text-gray-400">&copy; 2026 NutriVentures Hackathon Build</p>
      </div>
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
</style>
