import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue'
// path import is not needed if using fileURLToPath
// import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      // Proxy API requests to FastAPI backend server
      '/api': {
        target: 'http://localhost:8000', // FastAPI backend server
        changeOrigin: true,
        secure: false,
        // Keep /api prefix as FastAPI expects it
      }
    }
  }
})
