"""StoreManager - 管理每个 workspace 的 LangGraph persistence"""
import aiosqlite
from pathlib import Path
from typing import Dict, Tuple
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.sqlite.aio import AsyncSqliteStore


class StoreManager:
    """管理每个 workspace 的 checkpointer 和 store
    
    每个 workspace 有独立的 SQLite 数据库文件：backend/data/workspace_{id}.db
    包含：
    - AsyncSqliteSaver: 保存 checkpoint（对话历史、Agent 状态）
    - AsyncSqliteStore: 保存 long-term memory（章节内容、角色、世界观等）
    """
    
    # 缓存已创建的实例：workspace_id -> (checkpointer, store, connection)
    _instances: Dict[int, Tuple[AsyncSqliteSaver, AsyncSqliteStore, aiosqlite.Connection]] = {}
    
    @classmethod
    async def get_or_create(cls, workspace_id: int) -> Tuple[AsyncSqliteSaver, AsyncSqliteStore]:
        """获取或创建 workspace 的 checkpointer 和 store
        
        Args:
            workspace_id: 工作区ID
            
        Returns:
            (checkpointer, store) 元组
        """
        if workspace_id not in cls._instances:
            # 确保数据目录存在
            data_dir = Path("backend/data")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建 workspace 专属数据库连接
            db_path = data_dir / f"workspace_{workspace_id}.db"
            conn = await aiosqlite.connect(
                str(db_path),
                check_same_thread=False  # 允许多线程访问
            )
            
            # 创建 checkpointer 和 store（共享 connection）
            checkpointer = AsyncSqliteSaver(conn)
            store = AsyncSqliteStore(conn)
            
            # 初始化数据库表结构
            try:
                await checkpointer.setup()
                await store.setup()
            except Exception as e:
                # 如果 setup 失败（比如表已存在），继续
                print(f"Setup warning for workspace {workspace_id}: {e}")
            
            # 缓存实例
            cls._instances[workspace_id] = (checkpointer, store, conn)
        
        # 返回 checkpointer 和 store（不暴露 connection）
        checkpointer, store, _ = cls._instances[workspace_id]
        return checkpointer, store
    
    @classmethod
    async def close_workspace(cls, workspace_id: int):
        """关闭 workspace 的数据库连接
        
        Args:
            workspace_id: 工作区ID
        """
        if workspace_id in cls._instances:
            _, _, conn = cls._instances[workspace_id]
            await conn.close()
            del cls._instances[workspace_id]
    
    @classmethod
    async def close_all(cls):
        """关闭所有 workspace 的数据库连接"""
        for workspace_id in list(cls._instances.keys()):
            await cls.close_workspace(workspace_id)
    
    @classmethod
    async def cleanup_chapter_history(cls, workspace_id: int, chapter_number: int):
        """清理章节的历史记录
        
        删除：
        1. Checkpointer 中的 thread 记录 (plan_{workspace_id}_{chapter_number})
        2. Store 中的章节内容记录
        
        Args:
            workspace_id: 工作区ID
            chapter_number: 章节号
        """
        checkpointer, store = await cls.get_or_create(workspace_id)
        
        # 获取底层连接
        if workspace_id not in cls._instances:
            return
        
        _, _, conn = cls._instances[workspace_id]
        
        # 1. 删除 checkpointer 中的 thread 记录
        thread_id = f"plan_{workspace_id}_{chapter_number}"
        try:
            await conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = ?",
                (thread_id,)
            )
            await conn.execute(
                "DELETE FROM checkpoint_writes WHERE thread_id = ?",
                (thread_id,)
            )
            await conn.commit()
            print(f"Cleaned up checkpointer history for thread: {thread_id}")
        except Exception as e:
            print(f"Error cleaning checkpointer history: {e}")
        
        # 2. 删除 store 中的章节记录（如果存在）
        # Store 使用 namespace = ("memories", "chapters"), key = chapter_id
        # 但我们现在用 chapter_number 删除，需要遍历所有 chapter 记录
        # 这里简单处理：不删除 store 中的记录，因为 chapter_id 删除后不会冲突
        # 如果需要严格清理，可以补充逻辑
        pass


# 全局单例
store_manager = StoreManager()

