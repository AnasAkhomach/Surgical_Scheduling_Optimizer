import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    deps: {
      inline: ['vue-router'] // Ensure vue-router is processed by Vitest
    },
    moduleNameMapper: {
      '^.+\.svg$': '<rootDir>/__mocks__/svgMock.js' // Or a simple string like 'svg-mock'
    }
  },
})