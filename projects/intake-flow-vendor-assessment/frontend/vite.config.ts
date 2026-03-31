import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({
      // Use automatic JSX runtime (no React import needed)
      runtime: 'automatic',
    }),
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://192.168.10.80:8000',
        changeOrigin: true,
      },
    },
  },
})
