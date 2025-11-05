# NovelGen 插件系统

## 概述

NovelGen 提供了强大的插件系统，支持前端和后端扩展。插件系统采用基于钩子（Hooks）的设计，允许开发者在不修改核心代码的情况下扩展功能。

## 核心特性

- **前端插件**: 基于 Vue 3，通过钩子机制扩展 UI
- **后端插件**: 基于 Pluggy，扩展生成引擎和 API
- **松耦合设计**: 插件与核心应用解耦，互不影响
- **热插拔**: 支持动态启用/禁用插件
- **完整生态**: 提供丰富的钩子和示例插件

## 文档结构

- [插件架构设计](./architecture.md) - 深入理解插件系统的设计理念和技术架构
- [前端插件开发指南](./frontend-development.md) - 如何开发前端插件
- [后端插件开发指南](./backend-development.md) - 如何开发后端插件

## 快速开始

### 前端插件

1. **创建插件文件**

在 `frontend/src/plugins/implementations/` 目录下创建新的 `.js` 文件：

```javascript
// my-plugin.js
export default {
  name: 'my-plugin',
  version: '1.0.0',
  description: '我的第一个插件',
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

2. **配置插件**

在 `frontend/vite.config.js` 中启用插件：

```javascript
const novelGenPlugins = {
  'my-plugin': true,
}
```

3. **重启开发服务器**

插件会自动加载。

### 后端插件

1. **创建插件类**

在 `backend/plugins/implementations/` 目录下创建新的 `.py` 文件：

```python
from typing import Dict, Any, Optional
from backend.plugins import hookimpl

class MyPlugin:
    name = "MyPlugin"
    description = "我的插件"
    version = "1.0.0"
    
    @hookimpl
    def hook_inject_system_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        if stage == "plan":
            return "这是我注入的提示词"
        return None
```

2. **注册插件**

在 `backend/plugins/__init__.py` 中导入并注册：

```python
from .implementations.my_plugin import MyPlugin
```

3. **重启后端服务器**

插件会自动加载。

## 内置示例插件

### 前端插件

- **export-plugin**: 导出插件，展示如何添加工作区 Tab、扩展右键菜单和与后端 API 交互

### 后端插件

- **example_plugin**: 示例插件，展示如何扩展 create_plan 工具参数和注入系统提示词

## 目录结构

```
NovelGen/
├── frontend/
│   └── src/
│       └── plugins/
│           ├── manager.js              # 前端插件管理器
│           └── implementations/        # 前端插件实现
│               ├── word-count-plugin.js
│               └── export-plugin.js
│
├── backend/
│   └── plugins/
│       ├── manager.py                  # 后端插件管理器
│       ├── hookspec.py                 # 钩子规范定义
│       └── implementations/            # 后端插件实现
│           └── example_plugin.py
│
└── docs/
    └── plugins/
        ├── README.md                   # 本文件
        ├── architecture.md             # 架构设计
        ├── frontend-development.md     # 前端开发指南
        └── backend-development.md      # 后端开发指南
```

## 启用/禁用插件

### 前端插件

在 `frontend/vite.config.js` 中配置：

```javascript
const novelGenPlugins = {
  'export': true,         // 启用导出插件
  'word-count': false,    // 禁用字数统计插件
}
```

配置规则：
- `true`: 启用插件
- `false`: 禁用插件
- 未列出的插件默认启用

### 后端插件

后端插件的启用/禁用配置存储在数据库中，可通过前端的插件管理界面配置。

## 插件通信

### 前端插件调用后端 API

```javascript
import { pluginAPI } from '@/services/api'

// 调用后端插件接口
const result = await pluginAPI.call('plugin-name', 'method', params)
```

### 后端插件注册 API 路由

```python
@hookimpl
def hook_register_api_routes(self) -> Optional[List[Dict[str, Any]]]:
    return [{
        'router': my_router,
        'prefix': '/api/plugins/my-plugin'
    }]
```

