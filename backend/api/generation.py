"""Generation API路由 - 生成流程相关接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import (
    PlanInteractiveRequest, PlanInteractiveResponse,
    GenerateRequest, GenerateResponse,
    VerifyRequest, VerifyResponse,
    ImproveRequest, ImproveResponse
)
from backend.services.chapter_service import GenerationService

router = APIRouter()


@router.post("/plan/interactive", response_model=PlanInteractiveResponse)
async def create_plan_interactive(
    data: PlanInteractiveRequest,
    db: AsyncSession = Depends(get_db)
):
    """对话式生成章节大纲 - 支持多轮对话和修改"""
    try:
        result = await GenerationService.execute_plan_interactive(
            db=db,
            workspace_id=data.workspace_id,
            chapter_number=data.chapter_number,
            messages=data.messages,
            model=data.model
        )
        
        return {
            "messages": result["messages"],
            "plan": result.get("plan"),
            "plan_data": result.get("plan_data"),
            "completed": result["completed"],
            "chapter_id": result.get("chapter_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    data: GenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """生成章节内容（Generate阶段）"""
    try:
        chapter = await GenerationService.execute_generate(
            db=db,
            chapter_id=data.chapter_id,
            regenerate=data.regenerate,
            model=data.model
        )
        
        return {
            "chapter_id": chapter.id,
            "content": chapter.content,
            "status": chapter.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=VerifyResponse)
async def verify_content(
    data: VerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """验证章节内容（Verify阶段）"""
    try:
        result = await GenerationService.execute_verify(
            db=db,
            chapter_id=data.chapter_id,
            model=data.model
        )
        
        return {
            "chapter_id": data.chapter_id,
            "passed": result.get("passed", False),
            "issues": result.get("issues", []),
            "suggestions": result.get("suggestions", [])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve", response_model=ImproveResponse)
async def improve_content(
    data: ImproveRequest,
    db: AsyncSession = Depends(get_db)
):
    """改进章节内容（Improve阶段）"""
    try:
        chapter = await GenerationService.execute_improve(
            db=db,
            chapter_id=data.chapter_id,
            focus_issues=data.focus_issues,
            model=data.model
        )
        
        return {
            "chapter_id": chapter.id,
            "improved_content": chapter.content,
            "status": chapter.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalize/{chapter_id}")
async def finalize_chapter(
    chapter_id: int,
    db: AsyncSession = Depends(get_db)
):
    """最终确认章节（Update阶段）"""
    try:
        chapter = await GenerationService.execute_update(
            db=db,
            chapter_id=chapter_id
        )
        
        return {
            "chapter_id": chapter.id,
            "status": chapter.status.value,
            "message": "Chapter finalized successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

