"""Chapter API路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_db
from backend.models.schemas import ChapterResponse
from backend.services.chapter_service import ChapterService

router = APIRouter()


class CreateChapterRequest(BaseModel):
    workspace_id: int
    chapter_number: int
    title: Optional[str] = None


@router.post("/chapters", response_model=ChapterResponse)
async def create_chapter(
    request: CreateChapterRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建新章节"""
    chapter = await ChapterService.create_chapter(
        db=db,
        workspace_id=request.workspace_id,
        chapter_number=request.chapter_number,
        title=request.title
    )
    return chapter.to_dict()


@router.get("/workspace/{workspace_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    workspace_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取工作区的章节列表"""
    chapters = await ChapterService.list_chapters(db, workspace_id, skip, limit)
    return [ch.to_dict() for ch in chapters]


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取章节详情"""
    chapter = await ChapterService.get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter.to_dict()


@router.delete("/chapters/{chapter_id}", status_code=204)
async def delete_chapter(
    chapter_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除章节"""
    success = await ChapterService.delete_chapter(db, chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return None


@router.post("/workspace/{workspace_id}/rollback/{chapter_id}")
async def rollback_to_chapter(
    workspace_id: int,
    chapter_id: int,
    db: AsyncSession = Depends(get_db)
):
    """回退到指定章节（删除之后的章节，恢复插件状态）"""
    success = await ChapterService.rollback_to_chapter(db, workspace_id, chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chapter not found or invalid")
    return {"message": f"Rolled back to chapter {chapter_id}"}

