import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/answer': 'http://127.0.0.1:8000',
      '/next-question': 'http://127.0.0.1:8000',
      '/mastery': 'http://127.0.0.1:8000',
      '/class-heatmap': 'http://127.0.0.1:8000',
      '/misconceptions': 'http://127.0.0.1:8000',
      '/concepts': 'http://127.0.0.1:8000',
      '/students': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
})
