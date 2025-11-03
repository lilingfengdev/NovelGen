"""FastAPI应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.plugins.manager import plugin_manager
from backend.api import workspace, generation, chapter, plugins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()
    plugin_manager.load_plugins()
    # 挂载插件自定义API路由
    try:
        plugin_routes = plugin_manager.collect_api_routers()
        for rd in plugin_routes:
            router = rd.get("router")
            prefix = rd.get("prefix", "")
            tags = rd.get("tags")
            if router is not None:
                if tags is not None:
                    app.include_router(router, prefix=prefix, tags=tags)
                else:
                    app.include_router(router, prefix=prefix)
        if plugin_routes:
            print(f"✓ 已挂载 {len(plugin_routes)} 个插件路由")
    except Exception as e:
        print(f"✗ 挂载插件路由失败: {e}")
    print("✓ 数据库初始化完成")
    print(f"✓ 已加载 {len(plugin_manager.get_plugins())} 个插件")
    
    yield
    
    # 关闭时清理
    print("✓ 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Novel Studio API",
    description="强大的小说生成器后端API",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])
app.include_router(generation.router, prefix="/api", tags=["generation"])
app.include_router(chapter.router, prefix="/api", tags=["chapter"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "Novel Studio API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

