# Novel Studio

强大的小说生成器，高扩展性的 AI 辅助写作系统

## 特性

- 🚀 **完整生成流程**: Plan → Generate → Verify → Improve → Update
- 🔌 **插件化架构**: 基于 Pluggy 的强大插件系统
- 📦 **状态快照**: 每个章节保存完整的插件状态，支持自由回退
- 🎨 **现代化UI**: Vue 3 + Naive UI 打造的优雅界面
- 🔄 **实时协作**: 前后端分离，API 优先设计

## 技术栈

### 后端
- **FastAPI**: 高性能异步 Web 框架
- **LangChain**: AI 编排框架
- **Pluggy**: 插件系统
- **SQLAlchemy**: 异步 ORM
- **SQLite**: 轻量级数据库

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Naive UI**: 高质量 Vue 3 组件库
- **Pinia**: 状态管理
- **Vue Router**: 路由管理

## 快速开始

### 1. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key

# 启动后端
python main.py
```

后端将运行在 `http://localhost:8000`

API 文档: `http://localhost:8000/docs`

### 2. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:5173`

## 架构设计

### 生成流程

```
Plan (计划生成大纲)
  ↓
用户确认/修改 (可选)
  ↓
Generate (生成章节内容)
  ↓
Verify (检查逻辑/设定)
  ↓
├─ 通过 → Update (更新最终状态) → 完成
└─ 不通过 → Improve (改进内容) → 重新 Verify
```

### 插件系统

插件通过 Hook 机制扩展系统功能：

- **提示词注入**: `hook_inject_system_prompt`, `hook_inject_user_prompt`
- **工具注入**: `hook_inject_tools`
- **内容修改**: `hook_modify_generation`
- **流程拦截**: `hook_before_*/hook_after_*`
- **状态管理**: `hook_get_plugin_state`, `hook_set_plugin_state`

插件示例见 `backend/plugins/implementations/example_plugin.py`

### Chapter 快照机制

每个 Chapter 不仅包含文本内容，还保存：
- 生成时所有插件的状态
- 生成历史记录
- 验证结果
- 元信息

这使得可以：
- 回退到任意章节
- 恢复当时的完整状态
- 追踪生成过程

## 项目结构

```
NovelGen/
├── backend/              # 后端
│   ├── core/            # 核心生成引擎
│   ├── plugins/         # 插件系统
│   │   ├── hookspec.py # Hook 规范
│   │   ├── manager.py  # 插件管理器
│   │   └── implementations/ # 插件实现
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   ├── api/             # API 路由
│   ├── database.py      # 数据库配置
│   ├── config.py        # 配置管理
│   └── main.py          # 应用入口
│
└── frontend/            # 前端
    ├── src/
    │   ├── views/       # 页面组件
    │   ├── stores/      # Pinia 状态管理
    │   ├── services/    # API 服务
    │   ├── router/      # 路由配置
    │   └── App.vue      # 根组件
    └── package.json
```

## 开发指南

### 创建插件

1. 在 `backend/plugins/implementations/` 创建插件文件
2. 实现 Hook 方法（使用 `@hookimpl` 装饰器）
3. 插件会自动加载

```python
from backend.plugins import hookimpl

class MyPlugin:
    @hookimpl
    def hook_inject_system_prompt(self, stage, context):
        if stage == "plan":
            return "<my-plugin>插件提示词</my-plugin>"
        return None
```

### API 使用示例

```bash
# 创建工作区
curl -X POST http://localhost:8000/api/workspace \
  -H "Content-Type: application/json" \
  -d '{"title": "我的小说", "genre": "玄幻"}'

# 生成大纲
curl -X POST http://localhost:8000/api/plan \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": 1, "chapter_number": 1}'

# 生成内容
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"chapter_id": 1}'
```

## 扩展想法

- **Writer 插件**: 控制写作风格、视角、节奏
- **Role 插件**: 角色管理、关系图谱、RAG知识库
- **WorldView 插件**: 世界观设定、魔法体系、地理信息
- **Plot 插件**: 情节管理、伏笔追踪
- **Continuity 插件**: 连续性检查、矛盾检测

## License

MIT

## 作者

Built with ❤️ using AI-assisted development

