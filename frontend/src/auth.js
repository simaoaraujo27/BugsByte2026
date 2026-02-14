// Utilitário para gestão de autenticação
const API_URL = 'http://localhost:8000';

export const auth = {
  // Guardar token e ID do user
  saveSession(data) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user_id', data.user_id);
  },

  // Limpar sessão (Logout)
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    window.location.reload();
  },

  // Obter cabeçalhos com o Token para as chamadas à API
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
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
    return data;
  },

  // Obter dados do utilizador atual (Rota Protegida)
  async getMe() {
    const response = await fetch(`${API_URL}/users/me`, {
      headers: this.getAuthHeaders()
    });
    if (!response.ok) {
      this.logout();
      throw new Error('Sessão expirada');
    }
    return await response.json();
  }
};
