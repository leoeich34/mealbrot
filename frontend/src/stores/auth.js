import { defineStore } from 'pinia';
import { api } from '../api/client';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loaded: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user),
    isAdmin: (state) => state.user?.role === 'admin'
  },
  actions: {
    async fetchMe() {
      try {
        this.user = await api.get('/auth/me');
      } catch {
        this.user = null;
      } finally {
        this.loaded = true;
      }
    },
    async login(payload) {
      this.user = await api.post('/auth/login', payload);
      this.loaded = true;
    },
    async register(payload) {
      this.user = await api.post('/auth/register', payload);
      this.loaded = true;
    },
    async logout() {
      await api.post('/auth/logout', {});
      this.user = null;
      this.loaded = true;
    }
  }
});
