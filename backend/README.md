# Novel Studio Backend

强大的小说生成器后端服务

## 安装

```bash
cd backend
pip install -r requirements.txt
```

## 配置

OpenAI API Key 等模型配置在前端界面的系统设置中配置，无需配置 .env 文件。

如需自定义数据库路径、API端口等服务器配置，可创建 `.env` 文件：

```bash
# 可选配置项
DATABASE_URL=sqlite+aiosqlite:///./novelgen.db
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 运行

```bash
python -m uvicorn main:app --reload
```

或者：

```bash
python main.py
```

访问 http://localhost:8000/docs 查看API文档。

## 架构

- `core/` - 核心生成引擎
- `plugins/` - 插件系统（基于Pluggy）
- `models/` - 数据模型
- `services/` - 业务逻辑
- `api/` - API路由

