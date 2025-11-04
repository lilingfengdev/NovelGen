# 前端插件系统

## 目录结构

```
plugins/
├── manager.js              # 插件管理器
├── PLUGIN_DEVELOPMENT.md   # 插件开发文档
├── README.md               # 本文件
└── implementations/        # 插件实现
    ├── word-count-plugin.js    # 示例：字数统计插件
    └── export-plugin.js        # 示例：导出插件
```

## 快速开始

### 1. 创建插件

在 `implementations/` 目录下创建新的 `.js` 文件：

```javascript
// my-plugin.js
export default {
  name: 'my-plugin',
  version: '1.0.0',
  description: '我的插件',
  author: 'Your Name',
  
  hooks: {
    'workspace.tabs': (context) => {
      return {
        key: 'my-tab',
        label: '我的功能',
        icon: MyIcon,
        component: MyComponent
      }
    }
  }
}
```

### 2. 插件会自动加载

重启前端开发服务器，插件会自动被加载。

### 3. 调试插件

打开浏览器控制台，查看插件加载日志。

## 可用钩子

详见 [PLUGIN_DEVELOPMENT.md](./PLUGIN_DEVELOPMENT.md)

## 内置示例插件

### word-count-plugin
字数统计插件，展示如何：
- 在侧边栏插入自定义内容
- 添加新的工作区Tab
- 使用响应式数据

### export-plugin
导出插件，展示如何：
- 添加工作区Tab
- 扩展章节右键菜单
- 与后端API交互

## 启用/禁用插件

### 方法一：在 vite.config.js 中配置（推荐）

在 `vite.config.js` 中配置插件的启用状态：

```javascript
const novelGenPlugins = {
  'export': true,         // 启用导出插件
  'word-count': false,    // 禁用字数统计插件
}
```

这种方式的好处：
- 配置集中管理
- 在构建时确定，更高效
- 便于环境切换

### 插件列表显示

前端插件会在插件管理界面中显示，但标记为"内置"且不能禁用。这样可以统一查看所有插件的信息，包括：
- 插件名称和版本
- 插件描述
- 启用状态（内置插件始终启用）

## 插件通信

### 前端插件之间通信

使用 `pluginManager` 的事件系统（需要扩展）或 Pinia store。

### 前端插件与后端插件通信

通过标准的 HTTP API：

```javascript
import { pluginAPI } from '@/services/api'

// 调用后端插件接口
const result = await pluginAPI.call('plugin-name', 'method', params)
```

## 最佳实践

1. **命名规范**: 插件名使用 kebab-case，如 `word-count`
2. **错误处理**: 所有钩子函数都应该有 try-catch
3. **性能优化**: 避免在钩子中执行耗时操作
4. **样式隔离**: 使用 scoped 样式或内联样式
5. **类型安全**: 使用 JSDoc 或 TypeScript 定义类型

## 常见问题

### Q: 插件没有加载？
A: 检查：
1. 文件是否在 `implementations/` 目录下
2. 文件名是否以 `.js` 结尾
3. 是否 export default 了插件对象
4. 插件对象是否有 `name` 属性
5. 控制台是否有错误信息

### Q: 如何传递数据给插件组件？
A: 通过钩子返回的 `props` 字段：

```javascript
'workspace.tabs': (context) => {
  return {
    component: MyComponent,
    props: {
      data: context.workspace,
      customProp: 'value'
    }
  }
}
```

### Q: 如何访问 Vue Router 或 Pinia？
A: 在组件的 setup 函数中使用：

```javascript
import { useRouter } from 'vue-router'
import { useWorkspaceStore } from '@/stores/workspace'

setup() {
  const router = useRouter()
  const workspaceStore = useWorkspaceStore()
  // ...
}
```

## 贡献插件

如果你开发了有用的插件，欢迎提交 PR 分享给社区！

