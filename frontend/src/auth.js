// Utilitário para gestão de autenticação
export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export const auth = {
  // Guardar token e ID do user
  saveSession(data) {
    if (data?.access_token) {
      localStorage.setItem('token', data.access_token);
    }
    if (data?.user_id) {
      localStorage.setItem('user_id', String(data.user_id));
    }
  },

  // Limpar sessão (Logout)
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
  },

  // Obter cabeçalhos com o Token para as chamadas à API
  getAuthHeaders(includeJson = true) {
    const token = localStorage.getItem('token');
    const headers = {};
    if (includeJson) headers['Content-Type'] = 'application/json';
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  },

  // Verificar se está logado
  isLoggedIn() {
    return !!localStorage.getItem('token');
  },

  // Função de Login
  async login(username, password) {
    const response = await fetch(`${API_URL}/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!response.ok) throw new Error('Credenciais inválidas');
    
    const data = await response.json();
    this.saveSession(data);

    // Resolve user_id from protected endpoint for components that still depend on it
    const meResponse = await fetch(`${API_URL}/users/me`, {
      headers: this.getAuthHeaders(false)
    });
    if (meResponse.ok) {
      const me = await meResponse.json();
      this.saveSession({ user_id: me.id });
      return { ...data, user_id: me.id };
    }
    return data;
  },

  // Obter dados do utilizador atual (Rota Protegida)
  async getMe() {
    if (!localStorage.getItem('token')) {
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
