"""Generation API"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from backend.database import get_db, AsyncSessionLocal
from backend.core.generation_engine import generation_engine
from backend.models.chapter import Chapter
from backend.core.store_manager import StoreManager

router = APIRouter()


# ========== Request/Response Models ==========

class PlanChatRequest(BaseModel):
    """Plan Agent 对话请求"""
    workspace_id: int
    chapter_number: int
    message: str
    thread_id: Optional[str] = None
    model: Optional[str] = None


class PlanChatResponse(BaseModel):
    """Plan Agent 对话响应"""
    messages: List[Dict[str, Any]]
    thread_id: str
    plan_created: bool
    chapter_id: Optional[int] = None


class PlanConfirmRequest(BaseModel):
    """确认 Plan 请求"""
    chapter_id: int


class GenerateRequest(BaseModel):
    """生成内容请求"""
    chapter_id: int
    workspace_id: int
    model: Optional[str] = None


class GenerateResponse(BaseModel):
    """生成内容响应"""
    chapter_id: int
    content_preview: str
    status: str


# ========== API Endpoints ==========

@router.post("/plan/chat", response_model=PlanChatResponse)
async def plan_chat(
        request: PlanChatRequest,
        db: AsyncSession = Depends(get_db)
):
    """Plan Agent 对话（非流式）

    用于简单的对话交互
    """
    try:
        result = await generation_engine.plan_chat(
            db=db,
            workspace_id=request.workspace_id,
            chapter_number=request.chapter_number,
            message=request.message,
            thread_id=request.thread_id,
            model=request.model
        )

        return PlanChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan/chat/stream")
async def plan_chat_stream(
        request: PlanChatRequest,
        db: AsyncSession = Depends(get_db)
):
    """Plan Agent 流式对话（SSE）

    用于实时显示 Agent 思考过程
    """

    async def event_generator():
        """生成 SSE 事件流"""
        async with AsyncSessionLocal() as stream_db:
            try:
                async for event in generation_engine.plan_chat_stream(
                        db=stream_db,
                        workspace_id=request.workspace_id,
                        chapter_number=request.chapter_number,
                        message=request.message,
                        thread_id=request.thread_id,
                        model=request.model
                ):
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                # 检查是否创建了 Plan
                chapter_result = await stream_db.execute(
                    select(Chapter).where(
                        Chapter.workspace_id == request.workspace_id,
                        Chapter.chapter_number == request.chapter_number
                    )
                )
                chapter = chapter_result.scalar_one_or_none()

                if chapter and chapter.plan:
                    yield f"data: {json.dumps({'type': 'plan_created', 'chapter_id': chapter.id}, ensure_ascii=False)}\n\n"

                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/plan/confirm")
async def confirm_plan(
        request: PlanConfirmRequest,
        db: AsyncSession = Depends(get_db)
):
    """确认 Plan，标记为可生成状态

    用户确认大纲后调用
    """
    try:
        chapter_result = await db.execute(
            select(Chapter).where(Chapter.id == request.chapter_id)
        )
        chapter = chapter_result.scalar_one_or_none()

        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        if not chapter.plan:
            raise HTTPException(status_code=400, detail="Plan not created yet")

        # 标记为已规划，可以进入生成阶段
        from backend.models.chapter import ChapterStatus
        chapter.status = ChapterStatus.PLANNING
        await db.commit()

        return {
            "chapter_id": chapter.id,
            "status": chapter.status.value,
            "message": "Plan confirmed"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
        request: GenerateRequest,
        db: AsyncSession = Depends(get_db)
):
    """生成章节内容（使用 Writer SubAgent）"""
    try:
        content = await generation_engine.generate_content(
            db=db,
            chapter_id=request.chapter_id,
            workspace_id=request.workspace_id,
            model=request.model
        )

        # 查询更新后的章节
        chapter_result = await db.execute(
            select(Chapter).where(Chapter.id == request.chapter_id)
        )
        chapter = chapter_result.scalar_one_or_none()

        return GenerateResponse(
            chapter_id=request.chapter_id,
            content_preview=content[:200] + "..." if len(content) > 200 else content,
            status=chapter.status.value if chapter else "unknown"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalize/{chapter_id}")
async def finalize_chapter(
        chapter_id: int,
        db: AsyncSession = Depends(get_db)
):
    """最终确认章节"""
    try:
        await generation_engine.finalize_chapter(db=db, chapter_id=chapter_id)

        return {
            "chapter_id": chapter_id,
            "status": "completed",
            "message": "Chapter finalized successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chapter/{chapter_id}/content")
async def get_chapter_content(
        chapter_id: int,
        workspace_id: int,
        db: AsyncSession = Depends(get_db)
):
    """从 Store 获取章节完整内容

    Args:
        chapter_id: 章节ID
        workspace_id: 工作区ID
    """
    try:
        # 获取 Store
        _, store = await StoreManager.get_or_create(workspace_id)

        # 从 Store 读取章节
        stored_chapter = await store.aget(("memories", "chapters"), str(chapter_id))

        if not stored_chapter or not stored_chapter.value:
            raise HTTPException(status_code=404, detail="Chapter content not found in store")

        content = stored_chapter.value.get("content", "")

        return {
            "chapter_id": chapter_id,
            "content": content
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan/history")
async def get_plan_history(
        workspace_id: int,
        chapter_number: int,
        thread_id: Optional[str] = None
):
    """获取 Plan Agent 的对话历史

    Args:
        workspace_id: 工作区ID
        chapter_number: 章节号
        thread_id: 线程ID（可选，不传则用默认）

    Returns:
        对话历史消息列表
    """
    try:
        # 获取 checkpointer
        checkpointer, _ = await StoreManager.get_or_create(workspace_id)

        # 构建 thread_id
        effective_thread_id = thread_id or f"plan_{workspace_id}_{chapter_number}"

        # 从 checkpointer 读取历史
        config = {
            "configurable": {
                "thread_id": effective_thread_id
            }
        }

        # 获取最新状态
        state = await checkpointer.aget_tuple(config)

        if not state or not state.checkpoint:
            # 没有历史记录
            return {
                "thread_id": effective_thread_id,
                "messages": []
            }

        # 提取消息
        messages = state.checkpoint.get("channel_values", {}).get("messages", [])

        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            # 根据消息类型判断角色
            msg_type = msg.__class__.__name__

            if msg_type == "HumanMessage":
                role = "user"
            elif msg_type in ["AIMessage", "AIMessageChunk"]:
                role = "assistant"
            elif msg_type == "SystemMessage":
                role = "system"
            elif msg_type == "ToolMessage":
                # 工具消息可以跳过或者标记
                continue
            else:
                role = "unknown"

            content = getattr(msg, "content", str(msg))

            formatted_messages.append({
                "role": role,
                "content": content
            })

        return {
            "thread_id": effective_thread_id,
            "messages": formatted_messages
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")

