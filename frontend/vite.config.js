import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    // Enable cache busting with hash-based filenames
    rollupOptions: {
      output: {
        // Add hash to filenames for cache busting
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Generate source maps for debugging
    sourcemap: true,
    // Optimize chunk splitting
    chunkSizeWarningLimit: 1000
  },
  server: {
    // Development server configuration
    headers: {
      // Disable caching in development
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    },
    proxy: {
      // Proxy API requests to FastAPI backend server
      '/api': {
        target: 'http://localhost:5000', // FastAPI backend server
        changeOrigin: true,
        secure: false,
        // Keep /api prefix as FastAPI expects it
      }
    }
  },
  // Optimize dependencies
  optimizeDeps: {
    // Force re-optimization of dependencies
    force: true
  }
})
