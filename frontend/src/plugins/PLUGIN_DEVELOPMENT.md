# 前端插件开发指南

## 概述

NovelGen 前端插件系统允许你通过钩子机制扩展 UI 功能，在各个位置插入自定义组件和功能。

## 插件结构

一个最简单的前端插件：

```javascript
export default {
  name: 'my-plugin',
  version: '1.0.0',
  description: '我的第一个插件',
  author: 'Your Name',
  
  hooks: {
    // 在侧边栏头部添加按钮
    'sidebar.header.actions': (context) => {
      return {
        component: MyButtonComponent,
        props: { ... }
      }
    },
    
    // 添加工作区Tab
    'workspace.tabs': (context) => {
      return {
        key: 'my-tab',
        label: '我的功能',
        icon: MyIconComponent,
        component: MyContentComponent
      }
    }
  }
}
```

## 可用钩子

### 1. 侧边栏钩子

#### `sidebar.items`
在章节列表上方或下方插入自定义内容

**Context:**
- `workspace` - 当前工作空间
- `chapters` - 章节列表
- `currentChapter` - 当前选中章节
- `position` - 'before' | 'after'

**返回值:**
```javascript
{
  component: YourComponent,  // Vue 组件
  props: { ... },            // 组件 props
  order: 10                  // 显示顺序（可选）
}
```

#### `sidebar.chapter.actions`
扩展章节右键菜单

**Context:**
- `chapter` - 章节对象
- `workspace` - 工作空间

**返回值:**
```javascript
{
  label: '我的操作',
  key: 'my-action',
  icon: IconComponent,       // 可选
  handler: (chapter) => {
    // 处理逻辑
  }
}
```

#### `sidebar.header.actions`
在侧边栏头部添加额外按钮

**Context:**
- `workspace` - 当前工作空间

**返回值:**
```javascript
{
  component: ButtonComponent,
  props: { ... }
}
```

### 2. 编辑器钩子

#### `editor.toolbar.actions`
在编辑器工具栏添加按钮

**Context:**
- `chapter` - 当前章节
- `workspace` - 工作空间

**返回值:**
```javascript
{
  label: '我的工具',
  icon: IconComponent,
  handler: () => { ... },
  order: 10
}
```

#### `editor.content.before` / `editor.content.after`
在编辑器内容区上方/下方插入组件

**Context:**
- `chapter` - 当前章节

**返回值:**
```javascript
{
  component: YourComponent,
  props: { chapter, ... }
}
```

#### `editor.contextmenu`
扩展编辑器右键菜单

**Context:**
- `chapter` - 当前章节
- `selection` - 选中的文本（如果有）

**返回值:**
```javascript
{
  label: '我的菜单',
  handler: (context) => { ... }
}
```

### 3. 工作区钩子

#### `workspace.tabs`
添加新的工作区Tab（与编辑器、插件、设置平级）

**Context:**
- `workspace` - 当前工作空间

**返回值:**
```javascript
{
  key: 'my-workspace',
  label: '我的工作区',
  icon: IconComponent,       // SVG 组件
  component: ContentComponent,
  tooltip: '提示文本',       // 可选
  order: 100                 // 显示顺序
}
```

#### `workspace.settings.tabs`
在设置页面添加新的Tab

**Context:**
- `workspace` - 当前工作空间

**返回值:**
```javascript
{
  name: 'my-settings',
  tab: '我的设置',
  component: SettingsComponent
}
```

### 4. 章节钩子

#### `chapter.actions`
扩展章节操作按钮

**Context:**
- `chapter` - 章节对象

**返回值:**
```javascript
{
  label: '我的操作',
  type: 'primary' | 'default',
  handler: async (chapter) => { ... }
}
```

#### `chapter.view.sections`
在章节视图中添加新区域

**Context:**
- `chapter` - 章节对象

**返回值:**
```javascript
{
  title: '我的区域',
  component: SectionComponent,
  props: { chapter },
  order: 10
}
```

### 5. 全局钩子

#### `app.routes`
注册新路由

**Context:**
- `router` - Vue Router 实例

**返回值:**
```javascript
{
  path: '/my-page',
  name: 'MyPage',
  component: PageComponent
}
```

#### `app.stores`
注册新的 Pinia store

**Context:**
- `pinia` - Pinia 实例

**返回值:**
```javascript
{
  name: 'myStore',
  store: defineStore('myStore', { ... })
}
```

## 完整示例

参见 `implementations/word-count-plugin.js`

## 最佳实践

1. **插件命名**: 使用清晰的名称，避免与其他插件冲突
2. **错误处理**: 钩子函数中应该处理所有可能的错误，避免影响主应用
3. **性能**: 避免在钩子中执行耗时操作，使用异步加载
4. **样式隔离**: 使用 scoped 样式或 CSS Modules
5. **响应式**: 合理使用 Vue 的响应式 API（ref、reactive 等）

## 与后端插件协同

前端插件可以通过 API 与后端插件通信：

```javascript
import { pluginAPI } from '@/services/api'

// 调用后端插件接口
const result = await pluginAPI.call('my-plugin', 'my-method', { params })
```

后端插件可以通过 `hook_register_api_routes` 注册自己的 API 路由供前端调用。

