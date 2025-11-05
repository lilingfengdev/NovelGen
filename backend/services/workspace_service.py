"""Workspace业务逻辑服务"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.workspace import Workspace
from backend.models.schemas import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    """工作区服务"""
    
    @staticmethod
    async def create_workspace(db: AsyncSession, data: WorkspaceCreate) -> Workspace:
        """创建工作区"""
        workspace = Workspace(
            title=data.title,
            description=data.description,
            genre=data.genre,
            tags=data.tags,
            config=data.config,
            plugin_states={}
        )
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)
        return workspace
    
    @staticmethod
    async def get_workspace(db: AsyncSession, workspace_id: int) -> Optional[Workspace]:
        """获取工作区"""
        result = await db.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_workspaces(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Workspace]:
        """列出工作区"""
        result = await db.execute(
            select(Workspace).offset(skip).limit(limit).order_by(Workspace.updated_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_workspace(
        db: AsyncSession, 
        workspace_id: int, 
        data: WorkspaceUpdate
    ) -> Optional[Workspace]:
        """更新工作区"""
        workspace = await WorkspaceService.get_workspace(db, workspace_id)
        if not workspace:
            return None
        
        # 更新字段
        if data.title is not None:
            workspace.title = data.title
        if data.description is not None:
            workspace.description = data.description
        if data.genre is not None:
            workspace.genre = data.genre
        if data.tags is not None:
            workspace.tags = data.tags
        if data.config is not None:
            workspace.config = data.config
        
        await db.commit()
        await db.refresh(workspace)
        return workspace
    
    @staticmethod
    async def delete_workspace(db: AsyncSession, workspace_id: int) -> bool:
        """删除工作区"""
        workspace = await WorkspaceService.get_workspace(db, workspace_id)
        if not workspace:
            return False
        
        await db.delete(workspace)
        await db.commit()
        return True

