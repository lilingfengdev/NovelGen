# Novel Studio Backend

强大的小说生成器后端服务

## 安装

```bash
cd backend
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 到 `.env` 并配置你的 OpenAI API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置。

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

