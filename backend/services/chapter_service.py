"""Chapter业务逻辑服务"""
from typing import Optional, List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chapter import Chapter, ChapterStatus
from backend.core.generation_engine import generation_engine
from backend.plugins.manager import plugin_manager


class ChapterService:
    """章节服务"""
    
    @staticmethod
    async def create_chapter(
        db: AsyncSession,
        workspace_id: int,
        chapter_number: int,
        title: Optional[str] = None
    ) -> Chapter:
        """创建章节"""
        chapter = Chapter(
            workspace_id=workspace_id,
            chapter_number=chapter_number,
            title=title,
            status=ChapterStatus.PLANNING,
            plugin_snapshot={},
            generation_history=[]
        )
        db.add(chapter)
        await db.commit()
        await db.refresh(chapter)
        return chapter
    
    @staticmethod
    async def get_chapter(db: AsyncSession, chapter_id: int) -> Optional[Chapter]:
        """获取章节"""
        result = await db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_chapters(
        db: AsyncSession,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Chapter]:
        """列出章节"""
        result = await db.execute(
            select(Chapter)
            .where(Chapter.workspace_id == workspace_id)
            .order_by(Chapter.chapter_number)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_previous_chapters(
        db: AsyncSession,
        workspace_id: int,
        chapter_number: int,
        limit: int = 5
    ) -> List[Chapter]:
        """获取之前的章节（用于上下文）"""
        result = await db.execute(
            select(Chapter)
            .where(Chapter.workspace_id == workspace_id)
            .where(Chapter.chapter_number < chapter_number)
            .order_by(Chapter.chapter_number.desc())
            .limit(limit)
        )
        chapters = list(result.scalars().all())
        return list(reversed(chapters))  # 按正序返回
    
    @staticmethod
    async def delete_chapter(db: AsyncSession, chapter_id: int) -> bool:
        """删除章节"""
        chapter = await ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return False
        
        await db.delete(chapter)
        await db.commit()
        return True
    
    @staticmethod
    async def rollback_to_chapter(
        db: AsyncSession,
        workspace_id: int,
        chapter_id: int
    ) -> bool:
        """回退到指定章节（删除之后的所有章节，恢复插件状态）"""
        chapter = await ChapterService.get_chapter(db, chapter_id)
        if not chapter or chapter.workspace_id != workspace_id:
            return False
        
        # 删除之后的所有章节
        result = await db.execute(
            select(Chapter)
            .where(Chapter.workspace_id == workspace_id)
            .where(Chapter.chapter_number > chapter.chapter_number)
        )
        later_chapters = result.scalars().all()
        for ch in later_chapters:
            await db.delete(ch)
        
        # 恢复插件状态
        if chapter.plugin_snapshot:
            plugin_manager.restore_plugin_states(workspace_id, chapter.plugin_snapshot)
        
        await db.commit()
        return True


class GenerationService:
    """生成流程服务 - 封装完整的生成流程"""
    
    @staticmethod
    async def execute_plan_interactive(
        db: AsyncSession,
        workspace_id: int,
        chapter_number: int,
        messages: List[Dict],
        model: Optional[str] = None
    ) -> Dict:
        """执行对话式Plan生成"""
        # 获取之前的章节
        previous_chapters = await ChapterService.get_previous_chapters(
            db, workspace_id, chapter_number
        )
        
        # 第一次调用时就创建章节（如果不存在）
        from sqlalchemy import select
        query = select(Chapter).where(
            Chapter.workspace_id == workspace_id,
            Chapter.chapter_number == chapter_number
        )
        db_result = await db.execute(query)
        chapter = db_result.scalar_one_or_none()
        
        if not chapter:
            chapter = await ChapterService.create_chapter(
                db, workspace_id, chapter_number,
                title=f"第{chapter_number}章（创建中...）"
            )
        
        # 对话式生成大纲
        result = await generation_engine.plan(
            db=db,
            workspace_id=workspace_id,
            chapter_number=chapter_number,
            messages=messages,
            previous_chapters=previous_chapters,
            model=model
        )
        
        # 保存对话历史（每次都保存）
        chapter.plan_chat_messages = result["messages"]
        
        # 更新章节的 plan 和 plan_data
        if result.get("plan"):
            chapter.plan = result["plan"]
            chapter.plan_data = result.get("plan_data")  # 保存结构化数据
            chapter.status = ChapterStatus.PLANNING
            if result["completed"]:
                # 完成时更新标题并记录历史
                chapter.title = None  # 清除"创建中"标记
                chapter.add_history_entry("plan", {"plan": result["plan"]})
        
        await db.commit()
        await db.refresh(chapter)
        
        result["chapter_id"] = chapter.id
        
        return result
    
    @staticmethod
    async def execute_generate(
        db: AsyncSession,
        chapter_id: int,
        regenerate: bool = False,
        model: Optional[str] = None
    ) -> Chapter:
        """执行Generate阶段"""
        chapter = await ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        if not chapter.plan:
            raise ValueError("Chapter must have a plan before generating content")
        
        # 获取之前的章节
        previous_chapters = await ChapterService.get_previous_chapters(
            db, chapter.workspace_id, chapter.chapter_number
        )
        
        # 生成内容
        chapter.status = ChapterStatus.GENERATING
        await db.commit()
        
        content = await generation_engine.generate(
            db=db,
            chapter=chapter,
            workspace_id=chapter.workspace_id,
            previous_chapters=previous_chapters,
            model=model
        )
        
        chapter.content = content
        chapter.add_history_entry("generate", {"content": content})
        
        await db.commit()
        await db.refresh(chapter)
        return chapter
    
    @staticmethod
    async def execute_verify(
        db: AsyncSession,
        chapter_id: int,
        model: Optional[str] = None
    ) -> dict:
        """执行Verify阶段"""
        chapter = await ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        if not chapter.content:
            raise ValueError("Chapter must have content before verification")
        
        # 验证内容
        chapter.status = ChapterStatus.VERIFYING
        await db.commit()
        
        result = await generation_engine.verify(
            db=db,
            chapter=chapter,
            workspace_id=chapter.workspace_id,
            model=model
        )
        
        chapter.verification_result = result
        chapter.verification_passed = 1 if result.get("passed") else -1
        chapter.add_history_entry("verify", {"result": result})
        
        await db.commit()
        await db.refresh(chapter)
        return result
    
    @staticmethod
    async def execute_improve(
        db: AsyncSession,
        chapter_id: int,
        focus_issues: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> Chapter:
        """执行Improve阶段"""
        chapter = await ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        if not chapter.verification_result:
            raise ValueError("Chapter must be verified before improvement")
        
        # 改进内容
        chapter.status = ChapterStatus.IMPROVING
        await db.commit()
        
        improved_content = await generation_engine.improve(
            db=db,
            chapter=chapter,
            verification_result=chapter.verification_result,
            workspace_id=chapter.workspace_id,
            focus_issues=focus_issues,
            model=model
        )
        
        # 保存旧内容到历史
        chapter.add_history_entry("improve", {
            "old_content": chapter.content,
            "new_content": improved_content
        })
        
        chapter.content = improved_content
        # 重置验证状态，需要重新验证
        chapter.verification_passed = 0
        chapter.verification_result = None
        
        await db.commit()
        await db.refresh(chapter)
        return chapter
    
    @staticmethod
    async def execute_update(db: AsyncSession, chapter_id: int) -> Chapter:
        """执行Update阶段（最终确认）"""
        chapter = await ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        if chapter.verification_passed != 1:
            raise ValueError("Chapter must pass verification before finalization")
        
        # 更新最终状态
        await generation_engine.update(
            chapter=chapter,
            workspace_id=chapter.workspace_id
        )
        
        await db.commit()
        await db.refresh(chapter)
        return chapter

