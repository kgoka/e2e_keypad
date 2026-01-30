// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // '/api'로 시작하는 요청을 백엔드(5000)로 토스해라!
      '/api': {
        target: 'http://127.0.0.1:5000', 
        changeOrigin: true,
        secure: false,
      },
    },
  },
})