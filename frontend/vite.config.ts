import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Django backend
        changeOrigin: false,
        secure: false,
      },
      '/recommend': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false,
        secure: false,
      },
    },
  },
})
