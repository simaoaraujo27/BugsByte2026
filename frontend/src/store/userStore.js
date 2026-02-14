import { computed, ref, watch } from 'vue'
import { auth } from '@/auth'

const user = ref(null)

const customMacroPercents = ref({
  protein: 30,
  carbs: 45,
  fat: 25
})

// Sync customMacroPercents when user data is loaded
watch(user, (newUser) => {
  if (newUser) {
    customMacroPercents.value = {
      protein: newUser.macro_protein_percent ?? 30,
      carbs: newUser.macro_carbs_percent ?? 45,
      fat: newUser.macro_fat_percent ?? 25
    }
  }
}, { immediate: true })

const saveMacroPercents = async (percents) => {
  try {
    const { API_URL } = await import('@/auth')
    const { auth } = await import('@/auth')
    
    await fetch(`${API_URL}/users/me`, {
      method: 'PUT',
      headers: auth.getAuthHeaders(),
      body: JSON.stringify({
        macro_protein_percent: percents.protein,
        macro_carbs_percent: percents.carbs,
        macro_fat_percent: percents.fat
      })
    })
  } catch (e) {
    console.error('Error saving macro percents to server:', e)
  }
}

const toDisplayName = (profile) => {
  if (!profile) return 'Utilizador'
  const fullName = (profile.full_name || '').trim()
  if (fullName) return fullName

  const username = (profile.username || '').trim()
  if (!username) return 'Utilizador'

  const localPart = username.split('@')[0] || username
  return localPart
    .replace(/[._-]+/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ') || 'Utilizador'
}

const displayName = computed(() => toDisplayName(user.value))

const bmr = computed(() => {
  const profile = user.value
  if (!profile?.peso || !profile?.altura || !profile?.idade) return null

  const weight = Number(profile.peso)
  const height = Number(profile.altura)
  const age = Number(profile.idade)
  const gender = (profile.sexo || '').toLowerCase()

  if (gender === 'male') return 10 * weight + 6.25 * height - 5 * age + 5
  if (gender === 'female') return 10 * weight + 6.25 * height - 5 * age - 161
  return 10 * weight + 6.25 * height - 5 * age - 78
})

const activityFactor = computed(() => {
  const level = (user.value?.activity_level || '').toLowerCase()
  if (level === 'sedentary') return 1.2
  if (level === 'light') return 1.375
  if (level === 'moderate') return 1.55
  if (level === 'high') return 1.725
  return 1.2
})

const tdee = computed(() => {
  if (!bmr.value) return null
  return bmr.value * activityFactor.value
})

const targetCalories = computed(() => {
  if (user.value?.target_calories) {
    return user.value.target_calories
  }

  if (!tdee.value) return 1800 
  const goal = (user.value?.goal || '').toLowerCase()
  if (goal === 'lose') return Math.round(tdee.value - 500)
  if (goal === 'gain') return Math.round(tdee.value + 300)
  return Math.round(tdee.value)
})

const fetchUser = async () => {
  const profile = await auth.getMe()
  user.value = profile
  return profile
}

const setUser = (profile) => {
  user.value = profile
}

export function useUser() {
  return {
    user,
    displayName,
    bmr,
    tdee,
    targetCalories,
    customMacroPercents,
    saveMacroPercents,
    fetchUser,
    setUser
  }
}
