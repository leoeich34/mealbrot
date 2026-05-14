import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/catalog': 'http://localhost:8000',
      '/inventory': 'http://localhost:8000',
      '/recipes': 'http://localhost:8000',
      '/planner': 'http://localhost:8000',
      '/shopping-list': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  },
  test: {
    environment: 'jsdom',
    globals: true
  }
});
