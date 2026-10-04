import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    basicSsl() // 加上剛安裝的 SSL 外掛
  ],
  server: {
    https: true, // 開啟 HTTPS
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://localhost:8001', // 指向後端 API 地址
        changeOrigin: true,
        secure: false // 允許開發環境自簽憑證
      }
    }
  }
})