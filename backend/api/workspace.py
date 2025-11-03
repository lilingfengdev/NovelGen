"""Workspace API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from backend.services.workspace_service import WorkspaceService

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    data: WorkspaceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新的工作区（小说）"""
    workspace = await WorkspaceService.create_workspace(db, data)
    return workspace.to_dict()


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取工作区列表"""
    workspaces = await WorkspaceService.list_workspaces(db, skip, limit)
    return [ws.to_dict() for ws in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取工作区详情"""
    workspace = await WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace.to_dict()


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新工作区"""
    workspace = await WorkspaceService.update_workspace(db, workspace_id, data)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace.to_dict()


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除工作区"""
    success = await WorkspaceService.delete_workspace(db, workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return None

