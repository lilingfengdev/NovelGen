# 前端插件系统架构

## 概述

NovelGen 前端插件系统采用基于钩子（Hooks）的设计，允许插件在特定的 UI 位置注入自定义组件和功能，无需修改核心代码。

## 设计思想

### 1. 钩子机制
类似于 WordPress 和 VSCode 的插件系统，通过预定义的钩子点，插件可以"挂载"自己的功能到应用的各个部分。

### 2. 组件化
插件返回的是 Vue 组件，可以完全访问 Vue 的响应式系统、生命周期等特性。

### 3. 松耦合
插件与核心应用通过钩子接口交互，互不影响，便于独立开发和维护。

## 核心架构

```
┌──────────────────────────────────────────────────┐
│                   Application                     │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │          Plugin Manager                    │  │
│  │  - 注册插件                                  │  │
│  │  - 管理钩子                                  │  │
│  │  - 调用钩子                                  │  │
│  └────────────────────────────────────────────┘  │
│                       │                           │
│         ┌─────────────┴─────────────┐            │
│         │                           │             │
│  ┌──────▼──────┐            ┌──────▼──────┐     │
│  │  Plugin A   │            │  Plugin B   │      │
│  │  - hooks    │            │  - hooks    │      │
│  │  - metadata │            │  - metadata │      │
│  └─────────────┘            └─────────────┘      │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │          UI Components                     │  │
│  │  - Editor.vue                              │  │
│  │  - 调用 pluginManager.callHook()           │  │
│  │  - 渲染插件返回的组件                        │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 插件生命周期

```
1. 应用启动
   ↓
2. loadPlugins() 扫描 implementations/ 目录
   ↓
3. 读取 vite.config.js 中的插件配置
   ↓
4. 动态导入插件模块
   ↓
5. 根据配置过滤禁用的插件
   ↓
6. pluginManager.register(plugin)
   ↓
7. 注册各个钩子
   ↓
8. 应用挂载 app.mount('#app')
   ↓
9. 组件渲染时调用钩子
   ↓
10. 插件钩子返回组件/数据
   ↓
11. 应用渲染插件内容
```

## 插件配置

### 在 vite.config.js 中启用/禁用插件

可以在 `vite.config.js` 中配置哪些插件启用或禁用：

```javascript
const novelGenPlugins = {
  'export': true,         // 启用导出插件
  'word-count': false,    // 禁用字数统计插件
  'my-plugin': true,      // 启用自定义插件
}
```

配置规则：
- `true`: 启用插件
- `false`: 禁用插件
- 未在配置中列出的插件默认启用

这种配置方式的好处：
1. 集中管理插件启用状态
2. 在构建时确定插件加载，无需运行时检查
3. 便于开发时快速开关插件进行调试
4. 生产环境可以选择性禁用某些插件

## 钩子系统

### 钩子定义

在 `manager.js` 中预定义所有可用的钩子：

```javascript
this.hooks = {
  'sidebar.items': [],
  'workspace.tabs': [],
  // ...
}
```

### 钩子注册

插件在 `hooks` 对象中实现钩子：

```javascript
export default {
  name: 'my-plugin',
  hooks: {
    'workspace.tabs': (context) => {
      return { /* 返回值 */ }
    }
  }
}
```

### 钩子调用

组件中调用钩子获取插件返回的内容：

```javascript
const results = pluginManager.callHook('workspace.tabs', context)
```

### 钩子返回值

钩子可以返回：
- **组件定义**: `{ component, props }`
- **操作定义**: `{ label, handler }`
- **数据**: 任何 JSON 可序列化的数据

## 上下文传递

每个钩子调用时都会传递一个 context 对象，包含当前的状态信息：

```javascript
context = {
  workspace: 当前工作空间,
  chapters: 章节列表,
  currentChapter: 当前章节,
  // ... 根据钩子类型有所不同
}
```

插件可以根据 context 决定返回什么内容。

## 组件渲染

### 动态组件

使用 Vue 的 `<component :is>` 动态渲染插件返回的组件：

```vue
<component 
  v-for="item in pluginResults" 
  :is="item.component"
  v-bind="item.props"
/>
```

### Props 传递

插件返回的 props 会传递给组件：

```javascript
{
  component: MyComponent,
  props: {
    data: someData,
    callback: handleSomething
  }
}
```

## 扩展点设计

### 位置型扩展点
在特定 UI 位置插入内容：
- `sidebar.items` - 侧边栏
- `editor.content.before/after` - 编辑器上下

### 功能型扩展点
扩展现有功能：
- `sidebar.chapter.actions` - 章节菜单
- `editor.toolbar.actions` - 工具栏按钮

### 页面型扩展点
添加新页面：
- `workspace.tabs` - 新工作区Tab
- `app.routes` - 新路由

## 错误处理

插件系统有完善的错误处理：

1. **加载时错误**: 插件加载失败不影响其他插件
2. **钩子执行错误**: 用 try-catch 包裹，记录日志但不影响应用
3. **组件渲染错误**: Vue 的 errorHandler 会捕获

```javascript
try {
  const result = handler(context)
  results.push({ pluginName, result })
} catch (error) {
  console.error(`插件 ${pluginName} 执行失败:`, error)
}
```

## 性能优化

### 1. 按需加载
使用 Vite 的 `import.meta.glob` 动态加载：

```javascript
const pluginModules = import.meta.glob('./plugins/implementations/*.js', { 
  eager: true  // 或 lazy: true 实现懒加载
})
```

### 2. 计算属性缓存
使用 Vue 的 computed 缓存插件调用结果：

```javascript
const pluginSidebarBefore = computed(() => {
  return pluginManager.callHook('sidebar.items', context)
})
```

### 3. 避免重复调用
在组件的 setup 中调用钩子，而不是在模板中直接调用。

## 与后端插件协同

### 前端插件配置
前端插件的启用/禁用配置存储在后端，通过 API 获取。

### API 调用
前端插件可以调用后端插件注册的 API：

```javascript
// 后端插件注册 API
hook_register_api_routes() {
  return [{
    router: myRouter,
    prefix: '/api/plugins/my-plugin'
  }]
}

// 前端插件调用
const result = await fetch('/api/plugins/my-plugin/action')
```

### 状态同步
某些插件可能需要前后端状态同步，通过 WebSocket 或定期轮询实现。

## 安全考虑

1. **代码注入**: 插件代码在客户端执行，需要确保来源可信
2. **XSS 防护**: 插件渲染的内容需要转义
3. **权限控制**: 某些钩子可能需要权限检查
4. **资源限制**: 防止插件占用过多资源

## 扩展方向

### 1. 热重载
开发时支持插件热重载，无需刷新页面。

### 2. 配置界面
为每个插件生成配置界面（基于 JSON Schema）。

### 3. 插件市场
支持从外部源安装插件。

### 4. 插件间通信
提供事件总线或消息机制，让插件之间可以通信。

### 5. TypeScript 支持
为钩子提供完整的类型定义。

## 最佳实践

### 插件开发者

1. **明确职责**: 一个插件只做一件事
2. **错误处理**: 所有异步操作都要有错误处理
3. **性能意识**: 避免在钩子中执行耗时操作
4. **文档完善**: 提供清晰的使用文档

### 应用开发者

1. **钩子设计**: 在合适的位置提供钩子
2. **Context 丰富**: 传递足够的上下文信息
3. **向后兼容**: 添加新钩子时保持旧钩子可用
4. **测试覆盖**: 为插件系统编写测试

## 参考资料

- [Vue 3 文档 - 动态组件](https://vuejs.org/guide/essentials/component-basics.html#dynamic-components)
- [Vite 文档 - Glob 导入](https://vitejs.dev/guide/features.html#glob-import)
- [VSCode 扩展 API](https://code.visualstudio.com/api/references/vscode-api)
- [WordPress Plugin API](https://developer.wordpress.org/plugins/)

