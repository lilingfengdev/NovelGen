/**
 * 前端插件管理器
 * 
 * 负责加载、注册和调用前端插件
 */

class PluginManager {
  constructor() {
    this.plugins = new Map()
    this.hooks = {
      // 侧边栏钩子
      'sidebar.items': [],           // 侧边栏章节列表上方/下方的自定义内容
      'sidebar.chapter.actions': [], // 章节右键菜单扩展
      'sidebar.header.actions': [],  // 侧边栏头部额外按钮
      
      // 编辑器钩子
      'editor.toolbar.actions': [],  // 编辑器工具栏按钮
      'editor.content.before': [],   // 编辑器内容区上方
      'editor.content.after': [],    // 编辑器内容区下方
      'editor.contextmenu': [],      // 编辑器右键菜单
      
      // 工作区钩子
      'workspace.tabs': [],          // 工作区新增Tab页（编辑器/插件/设置之外）
      'workspace.settings.tabs': [], // 设置页面的新增Tab
      
      // 章节钩子
      'chapter.actions': [],         // 章节操作按钮扩展
      'chapter.view.sections': [],   // 章节视图区域扩展
      
      // 全局钩子
      'app.routes': [],              // 注册新路由
      'app.stores': [],              // 注册新的 Pinia store
    }
  }

  /**
   * 注册插件
   * @param {Object} plugin - 插件对象
   * @param {string} plugin.name - 插件名称
   * @param {string} plugin.version - 插件版本
   * @param {Object} plugin.hooks - 插件钩子实现
   * @param {boolean} enabled - 插件是否启用
   */
  register(plugin, enabled = true) {
    if (!plugin.name) {
      console.error('插件必须有名称')
      return false
    }

    if (this.plugins.has(plugin.name)) {
      console.warn(`插件 ${plugin.name} 已经注册过了`)
      return false
    }

    // 保存插件信息（包括启用状态）
    this.plugins.set(plugin.name, { ...plugin, enabled })
    
    // 只有启用的插件才注册钩子
    if (enabled && plugin.hooks) {
      Object.keys(plugin.hooks).forEach(hookName => {
        if (this.hooks[hookName]) {
          this.hooks[hookName].push({
            pluginName: plugin.name,
            handler: plugin.hooks[hookName]
          })
        } else {
          console.warn(`未知的钩子: ${hookName}`)
        }
      })
    }

    console.log(`${enabled ? '✓' : '⊗'} 加载前端插件: ${plugin.name}`)
    return true
  }

  /**
   * 调用钩子并收集结果
   * @param {string} hookName - 钩子名称
   * @param {Object} context - 上下文数据
   * @returns {Array} 所有插件的返回值
   */
  callHook(hookName, context = {}) {
    const hookHandlers = this.hooks[hookName] || []
    const results = []

    for (const { pluginName, handler } of hookHandlers) {
      try {
        const result = handler(context)
        if (result !== undefined && result !== null) {
          results.push({
            pluginName,
            result
          })
        }
      } catch (error) {
        console.error(`插件 ${pluginName} 的钩子 ${hookName} 执行失败:`, error)
      }
    }

    return results
  }

  /**
   * 调用钩子，返回第一个非空结果
   */
  callHookFirst(hookName, context = {}) {
    const results = this.callHook(hookName, context)
    return results.length > 0 ? results[0].result : null
  }

  /**
   * 获取所有已注册的插件
   */
  getPlugins() {
    return Array.from(this.plugins.values())
  }

  /**
   * 获取特定插件
   */
  getPlugin(name) {
    return this.plugins.get(name)
  }

  /**
   * 检查插件是否已注册
   */
  hasPlugin(name) {
    return this.plugins.has(name)
  }

  /**
   * 移除插件（热重载时使用）
   */
  unregister(name) {
    if (!this.plugins.has(name)) return false

    // 从所有钩子中移除该插件
    Object.keys(this.hooks).forEach(hookName => {
      this.hooks[hookName] = this.hooks[hookName].filter(
        h => h.pluginName !== name
      )
    })

    this.plugins.delete(name)
    console.log(`✓ 卸载前端插件: ${name}`)
    return true
  }
}

// 导出单例
export const pluginManager = new PluginManager()
export default pluginManager

