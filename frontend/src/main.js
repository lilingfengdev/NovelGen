import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { pluginManager } from './plugins/manager'

// 获取插件配置
function getPluginConfig() {
  // 从 vite.config.js 注入的配置
  if (typeof __NOVELGEN_PLUGINS_CONFIG__ !== 'undefined') {
    return __NOVELGEN_PLUGINS_CONFIG__
  }
  return {}
}

// 检查插件是否启用
function isPluginEnabled(pluginName) {
  const config = getPluginConfig()
  // 如果配置中没有该插件，默认启用
  if (config.hasOwnProperty(pluginName)) {
    return config[pluginName] === true
  }
  return true
}

// 加载前端插件
async function loadPlugins() {
  const config = getPluginConfig()
  console.log('插件配置:', config)
  
  // 动态导入所有插件
  const pluginModules = import.meta.glob('./plugins/implementations/*.js', { eager: true })
  
  let enabledCount = 0
  let disabledCount = 0
  
  for (const [path, module] of Object.entries(pluginModules)) {
    try {
      const plugin = module.default
      if (plugin && plugin.name) {
        // 检查插件是否启用
        const enabled = isPluginEnabled(plugin.name)
        // 注册插件（无论启用还是禁用都注册，但只有启用的才会注册钩子）
        pluginManager.register(plugin, enabled)
        
        if (enabled) {
          enabledCount++
        } else {
          disabledCount++
        }
      }
    } catch (error) {
      console.error(`加载插件失败 ${path}:`, error)
    }
  }
  
  console.log(`前端插件加载完成: ${enabledCount} 个启用, ${disabledCount} 个禁用`)
}

// 初始化应用
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 加载插件后再挂载应用
loadPlugins().then(() => {
  app.mount('#app')
  console.log('前端插件系统初始化完成')
})

