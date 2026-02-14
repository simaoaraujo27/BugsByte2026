import { computed, ref } from 'vue'
import { auth } from '@/auth'

const user = ref(null)

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
    fetchUser,
    setUser
  }
}
