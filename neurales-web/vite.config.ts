import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

const host = process.env.TAURI_DEV_HOST
const isTauri = !!process.env.TAURI_ENV_PLATFORM
const webPort = Number(process.env.VITE_PORT || 5173)

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  clearScreen: false,
  server: {
    port: isTauri ? 1420 : webPort,
    strictPort: isTauri,
    host: host || false,
    hmr: host
      ? {
          protocol: 'ws',
          host,
          port: 1421,
        }
      : undefined,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
})
