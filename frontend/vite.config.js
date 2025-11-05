import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'fs'
import { resolve } from 'path'

// 从 plugins.json 读取插件配置
function loadPluginsConfig() {
  try {
    const configPath = resolve(__dirname, 'plugins.json')
    const configContent = readFileSync(configPath, 'utf-8')
    const config = JSON.parse(configContent)
    return config.plugins || {}
  } catch (error) {
    console.warn('无法读取 plugins.json，使用默认配置:', error.message)
    return {}
  }
}

const novelGenPlugins = loadPluginsConfig()

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  define: {
    // 注入插件配置到运行时
    __NOVELGEN_PLUGINS_CONFIG__: JSON.stringify(novelGenPlugins)
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vue 核心库单独打包
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // Naive UI 单独打包，这玩意儿很大
          'naive-ui': ['naive-ui'],
          // 图标库单独打包
          'icons': ['@vicons/ionicons5'],
          // axios 单独打包
          'utils': ['axios']
        }
      }
    },
    // 把 chunk size 警告阈值设为 1000KB，但这不意味着你可以偷懒
    chunkSizeWarningLimit: 1000
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

