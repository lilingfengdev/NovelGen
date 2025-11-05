# 插件系统架构设计

## 概述

NovelGen 插件系统采用基于钩子（Hooks）的设计，分为前端插件和后端插件两部分，允许开发者在不修改核心代码的情况下扩展功能。

## 设计理念

### 1. 钩子机制

类似于 WordPress 和 VSCode 的插件系统，通过预定义的钩子点，插件可以"挂载"自己的功能到应用的各个部分。

**核心思想**：
- **扩展点明确**: 在代码的关键位置预留钩子
- **调用统一**: 通过插件管理器统一调用
- **返回值处理**: 钩子可以返回数据、组件或修改输入

### 2. 松耦合

插件与核心应用通过钩子接口交互，互不影响，便于独立开发和维护。

- 插件不直接依赖核心代码
- 核心代码不需要知道具体插件实现
- 插件之间原则上互不依赖

### 3. 前后端协同

前端插件负责 UI 扩展，后端插件负责逻辑扩展，两者可以通过 API 进行通信。

## 前端插件架构

### 核心架构图

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

### 组件化设计

插件返回的是 Vue 组件，可以完全访问 Vue 的响应式系统、生命周期等特性。

**好处**：
- 使用标准的 Vue 开发方式
- 可以使用 Composition API
- 支持响应式数据
- 集成 Vue 生态系统

### 插件生命周期

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

### 钩子系统

#### 钩子定义

在 `manager.js` 中预定义所有可用的钩子：

```javascript
this.hooks = {
  'sidebar.items': [],
  'workspace.tabs': [],
  'editor.toolbar.actions': [],
  // ...
}
```

#### 钩子注册

插件在 `hooks` 对象中实现钩子：

```javascript
export default {
  name: 'my-plugin',
  hooks: {
    'workspace.tabs': (context) => {
      return { component, props }
    }
  }
}
```

#### 钩子调用

组件中调用钩子获取插件返回的内容：

```javascript
const results = pluginManager.callHook('workspace.tabs', context)
```

#### 钩子返回值

钩子可以返回：
- **组件定义**: `{ component, props }`
- **操作定义**: `{ label, handler }`
- **数据**: 任何 JSON 可序列化的数据

### 上下文传递

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

### 组件渲染

#### 动态组件

使用 Vue 的 `<component :is>` 动态渲染插件返回的组件：

```vue
<component 
  v-for="item in pluginResults" 
  :is="item.component"
  v-bind="item.props"
/>
```

#### Props 传递

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

### 插件配置

#### 在 vite.config.js 中启用/禁用插件

可以在 `vite.config.js` 中配置哪些插件启用或禁用：

```javascript
const novelGenPlugins = {
  'export': true,         // 启用导出插件
  'word-count': false,    // 禁用字数统计插件
  'my-plugin': true,      // 启用自定义插件
}
```

**配置规则**：
- `true`: 启用插件
- `false`: 禁用插件
- 未在配置中列出的插件默认启用

**好处**：
1. 集中管理插件启用状态
2. 在构建时确定插件加载，无需运行时检查
3. 便于开发时快速开关插件进行调试
4. 生产环境可以选择性禁用某些插件

### 扩展点设计

#### 位置型扩展点
在特定 UI 位置插入内容：
- `sidebar.items` - 侧边栏
- `editor.content.before/after` - 编辑器上下

#### 功能型扩展点
扩展现有功能：
- `sidebar.chapter.actions` - 章节菜单
- `editor.toolbar.actions` - 工具栏按钮

#### 页面型扩展点
添加新页面：
- `workspace.tabs` - 新工作区 Tab
- `app.routes` - 新路由

## 后端插件架构

### 核心架构图

```
┌──────────────────────────────────────────────────┐
│              FastAPI Application                  │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │       Pluggy Plugin Manager                │  │
│  │  - 注册插件                                  │  │
│  │  - 管理钩子规范                              │  │
│  │  - 调用钩子方法                              │  │
│  └────────────────────────────────────────────┘  │
│                       │                           │
│         ┌─────────────┴─────────────┐            │
│         │                           │             │
│  ┌──────▼──────┐            ┌──────▼──────┐     │
│  │  Plugin A   │            │  Plugin B   │      │
│  │  - @hookimpl│            │  - @hookimpl│      │
│  │  - metadata │            │  - metadata │      │
│  └─────────────┘            └─────────────┘      │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │       Generation Engine / API              │  │
│  │  - 调用 pm.hook.xxx()                       │  │
│  │  - 处理返回值                                │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### Pluggy 框架

后端插件基于 [Pluggy](https://pluggy.readthedocs.io/) 框架，这是 pytest 使用的插件系统。

**核心概念**：
- **HookSpec**: 定义钩子规范（接口）
- **HookImpl**: 插件实现钩子（实现）
- **PluginManager**: 管理插件和调用钩子

### 钩子规范定义

在 `hookspec.py` 中使用 `@hookspec` 定义钩子规范：

```python
from pluggy import HookspecMarker

hookspec = HookspecMarker("novelgen")

class NovelGenHookSpec:
    @hookspec
    def hook_inject_system_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        """注入系统提示词"""
        pass
    
    @hookspec
    def hook_extend_create_plan_params(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """扩展 create_plan 工具参数"""
        pass
```

### 插件实现钩子

插件使用 `@hookimpl` 实现钩子：

```python
from pluggy import HookimplMarker

hookimpl = HookimplMarker("novelgen")

class MyPlugin:
    @hookimpl
    def hook_inject_system_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        if stage == "plan":
            return "我的提示词"
        return None
```

### 钩子调用

在生成引擎或 API 中调用钩子：

```python
# 获取所有插件的返回值
results = pm.hook.hook_inject_system_prompt(stage="plan", context=context)

# 过滤 None 值并拼接
prompts = [r for r in results if r]
additional_prompt = "\n\n".join(prompts)
```

### 钩子类型

#### 1. 注入型钩子
在特定位置注入内容：
- `hook_inject_system_prompt` - 注入系统提示词
- `hook_inject_user_prompt` - 注入用户提示词

#### 2. 扩展型钩子
扩展现有功能：
- `hook_extend_create_plan_params` - 扩展工具参数
- `hook_register_api_routes` - 注册 API 路由

#### 3. 处理型钩子
处理数据：
- `hook_before_plan` - plan 生成前
- `hook_after_plan` - plan 生成后
- `hook_before_chapter` - 章节生成前
- `hook_after_chapter` - 章节生成后

## 性能优化

### 前端优化

#### 1. 按需加载

使用 Vite 的 `import.meta.glob` 动态加载：

```javascript
const pluginModules = import.meta.glob('./plugins/implementations/*.js', { 
  eager: true  // 或 lazy: true 实现懒加载
})
```

#### 2. 计算属性缓存

使用 Vue 的 computed 缓存插件调用结果：

```javascript
const pluginSidebarBefore = computed(() => {
  return pluginManager.callHook('sidebar.items', context)
})
```

#### 3. 避免重复调用

在组件的 setup 中调用钩子，而不是在模板中直接调用。

### 后端优化

#### 1. 钩子结果缓存

对于不变的结果，可以缓存：

```python
@lru_cache(maxsize=128)
def get_system_prompt(stage: str):
    results = pm.hook.hook_inject_system_prompt(stage=stage, context={})
    return "\n\n".join([r for r in results if r])
```

#### 2. 异步钩子

对于耗时操作，使用异步钩子：

```python
@hookspec
async def hook_process_chapter(self, chapter: str) -> Optional[str]:
    pass

# 调用
results = await pm.hook.hook_process_chapter(chapter=text)
```

## 前后端协同

### 前端插件配置

前端插件的启用/禁用配置存储在后端，通过 API 获取。

```javascript
// 前端获取插件配置
const config = await fetch('/api/plugins/config')
```

### API 调用

前端插件可以调用后端插件注册的 API：

```javascript
// 前端插件调用
const result = await fetch('/api/plugins/my-plugin/action')
```

```python
# 后端插件注册 API
@hookimpl
def hook_register_api_routes(self):
    return [{
        'router': my_router,
        'prefix': '/api/plugins/my-plugin'
    }]
```

### 状态同步

某些插件可能需要前后端状态同步，通过 WebSocket 或定期轮询实现。

## 错误处理

### 前端错误处理

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

### 后端错误处理

```python
try:
    results = pm.hook.hook_inject_system_prompt(stage=stage, context=context)
except Exception as e:
    logger.error(f"插件钩子调用失败: {e}")
    results = []
```

## 安全考虑

### 前端安全

1. **代码注入**: 插件代码在客户端执行，需要确保来源可信
2. **XSS 防护**: 插件渲染的内容需要转义
3. **权限控制**: 某些钩子可能需要权限检查
4. **资源限制**: 防止插件占用过多资源

### 后端安全

1. **代码执行**: 只加载可信的插件代码
2. **API 权限**: 插件注册的 API 需要权限验证
3. **资源限制**: 限制插件的计算资源
4. **数据隔离**: 插件数据应该隔离存储

