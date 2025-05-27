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
      // Proxy API requests to backend server
      '/api': {
        target: 'http://localhost:3000', // Replace with your actual backend server address
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // Uncomment if your backend doesn't expect /api prefix
      }
    }
  }
})
