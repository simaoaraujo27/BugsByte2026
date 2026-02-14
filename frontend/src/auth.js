// Utilitário para gestão de autenticação
export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export const auth = {
  // Guardar token e ID do user
  saveSession(data, remember = true) {
    const storage = remember ? localStorage : sessionStorage;
    if (data?.access_token) {
      storage.setItem('token', data.access_token);
    }
    if (data?.user_id) {
      storage.setItem('user_id', String(data.user_id));
    }
    
    // If we're not remembering, make sure the other storage is clean
    if (!remember) {
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
    }
  },

  // Limpar sessão (Logout)
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user_id');
  },

  // Obter cabeçalhos com o Token para as chamadas à API
  getAuthHeaders(includeJson = true) {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    const headers = {};
    if (includeJson) headers['Content-Type'] = 'application/json';
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  },

  // Verificar se está logado
  isLoggedIn() {
    const hasLocal = !!localStorage.getItem('token');
    const hasSession = !!sessionStorage.getItem('token');
    return hasLocal || hasSession;
  },

  // Verify if token is actually valid by calling backend
  async checkAuth() {
    try {
      if (!this.isLoggedIn()) return false;
      await this.getMe();
      return true;
    } catch (e) {
      console.warn('Invalid session detected, logging out...');
      this.logout();
      return false;
    }
  },

  // Função de Login
  async login(username, password, remember = true) {
    const response = await fetch(`${API_URL}/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!response.ok) throw new Error('Credenciais inválidas');
    
    const data = await response.json();
    this.saveSession(data, remember);

    // Resolve user_id from protected endpoint
    const meResponse = await fetch(`${API_URL}/users/me`, {
      headers: this.getAuthHeaders(false)
    });
    if (meResponse.ok) {
      const me = await meResponse.json();
      this.saveSession({ user_id: me.id }, remember);
      return { ...data, user_id: me.id };
    }
    return data;
  },

  // Obter dados do utilizador atual (Rota Protegida)
  async getMe() {
    if (!this.isLoggedIn()) {
      throw new Error('Sessão não iniciada');
    }

    const response = await fetch(`${API_URL}/users/me`, {
      headers: this.getAuthHeaders(false)
    });
    if (!response.ok) {
      throw new Error('Sessão expirada');
    }
    return await response.json();
  }
};
