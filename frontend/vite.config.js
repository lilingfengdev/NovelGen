import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// NovelGen 插件配置
// 设置为 false 禁用插件，true 启用插件
// 不在列表中的插件默认启用
const novelGenPlugins = {
  'export': true,         // 导出插件
  'word-count': false,     // 字数统计插件
  // 添加更多插件配置...
}

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

