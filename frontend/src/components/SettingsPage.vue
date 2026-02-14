<template>
  <div class="settings-panel">
    <h1>Definições</h1>
    <p>Preferências da conta, notificações e opções da aplicação.</p>

    <div class="settings-card">
      <div>
        <h3>Modo Escuro</h3>
        <small>Ativa um tema mais confortavel para ambientes com pouca luz.</small>
      </div>
      <button
        type="button"
        class="theme-toggle"
        :class="{ active: isDarkMode }"
        @click="$emit('toggle-theme')"
        :aria-pressed="isDarkMode"
      >
        <span class="toggle-knob"></span>
      </button>
    </div>

    <div class="settings-card">
      <div>
        <h3>Modo Daltonismo</h3>
        <small>Ajusta as cores da aplicação para melhorar a visibilidade.</small>
      </div>
      <select 
        :value="colorBlindnessMode" 
        @change="$emit('update-color-blindness', $event.target.value)"
        class="mode-select"
      >
        <option value="none">Nenhum (Padrão)</option>
        <option value="protanopia">Protanopia (Vermelho)</option>
        <option value="deuteranopia">Deuteranopia (Verde)</option>
        <option value="tritanopia">Tritanopia (Azul)</option>
        <option value="achromatopsia">Acromatopsia (Monocromático)</option>
      </select>
    </div>

    <div class="settings-card profile-section">
      <div style="width: 100%;">
        <h3>Editar Perfil</h3>
        <small>Altere o seu nome de utilizador ou palavra-passe.</small>
        
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label>Novo Nome de Utilizador</label>
            <input v-model="profileData.username" type="text" placeholder="Utilizador" />
          </div>
          <div class="form-group">
            <label>Nova Palavra-passe</label>
            <input v-model="profileData.password" type="password" placeholder="••••••••" />
          </div>
          <button type="submit" class="save-btn" :disabled="isSaving">
            {{ isSaving ? 'A guardar...' : 'Guardar Alterações' }}
          </button>
        </form>
        <p v-if="message" :class="['message', message.type]">{{ message.text }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { auth, API_URL } from '@/auth'

export default {
  props: {
    isDarkMode: {
      type: Boolean,
      required: true
    },
    colorBlindnessMode: {
      type: String,
      default: 'none'
    }
  },
  emits: ['toggle-theme', 'update-color-blindness'],
  data() {
    return {
      profileData: {
        username: '',
        password: ''
      },
      isSaving: false,
      message: null
    }
  },
  methods: {
    async updateProfile() {
      if (!this.profileData.username && !this.profileData.password) return
      
      this.isSaving = true
      this.message = null
      
      try {
        const body = {}
        if (this.profileData.username) body.username = this.profileData.username
        if (this.profileData.password) body.password = this.profileData.password
        
        const res = await fetch(`${API_URL}/users/me`, {
          method: 'PUT',
          headers: auth.getAuthHeaders(),
          body: JSON.stringify(body)
        })
        
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.detail || 'Falha ao atualizar perfil')
        }
        
        this.message = { type: 'success', text: 'Perfil atualizado com sucesso!' }
        this.profileData.password = ''
      } catch (err) {
        this.message = { type: 'error', text: err.message }
      } finally {
        this.isSaving = false
      }
    }
  },
  async mounted() {
    try {
      const me = await auth.getMe()
      if (me) this.profileData.username = me.username
    } catch (err) {
      console.error('Error loading profile:', err)
    }
  }
};
</script>

<style scoped>
.settings-panel {
  max-width: 760px;
}

.profile-section {
  flex-direction: column;
  align-items: flex-start;
}

.profile-form {
  margin-top: 20px;
  display: grid;
  gap: 16px;
  width: 100%;
  max-width: 400px;
}

.form-group {
  display: grid;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
}

.form-group input {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--bg-main);
  color: var(--text-main);
}

.save-btn {
  padding: 12px;
  border-radius: 10px;
  border: none;
  background: #07a374;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  margin-top: 16px;
  font-size: 0.9rem;
  font-weight: 600;
}

.message.success { color: #07a374; }
.message.error { color: #e74c3c; }

.settings-card {
  margin-top: 26px;
  border: 1px solid var(--line);
  background: var(--bg-elevated);
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.settings-card h3 {
  margin: 0;
  font-size: 1.02rem;
}

.settings-card small {
  display: block;
  margin-top: 6px;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.theme-toggle {
  width: 56px;
  height: 32px;
  border-radius: 99px;
  border: 1px solid var(--line);
  background: #d6dee8;
  padding: 3px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: background 0.2s ease, border-color 0.2s ease;
}

/* Note: Global theme styles are handled in SiteHomePage, but we can target specific local styles if needed */
:global(.theme-dark) .theme-toggle {
  background: #23314a;
}

.theme-toggle.active {
  background: #07a374;
  border-color: #07a374;
}

.toggle-knob {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ffffff;
  transition: transform 0.2s ease;
}

.theme-toggle.active .toggle-knob {
  transform: translateX(24px);
}

.mode-select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--bg-main);
  color: var(--text-main);
  font-family: inherit;
  font-size: 0.95rem;
  cursor: pointer;
}
</style>
