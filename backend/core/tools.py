"""自定义 Tools - 供 DeepAgent 使用"""
from typing import List, Optional
from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.chapter import Chapter, ChapterStatus
from backend.models.workspace import Workspace


class ToolContext:
    """工具上下文 - 注入数据库会话等依赖"""
    
    def __init__(self, db: AsyncSession, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id


def create_plan_tool_factory(context: ToolContext):
    """创建 create_plan 工具的工厂函数
    
    Args:
        context: 工具上下文（包含 db session 和 workspace_id）
        
    Returns:
        create_plan 工具实例
    """
    
    @tool
    async def create_plan(
        title: str,
        plot_points: List[str],
        characters: List[str],
        direction: str,
        scenes: List[str],
        chapter_number: Optional[int] = None
    ) -> str:
        """创建或更新章节大纲
        
        当你规划好章节大纲后，调用此工具保存大纲到数据库。
        
        Args:
            title: 章节标题
            plot_points: 主要情节点列表（3-5个）
            characters: 涉及的角色列表
            direction: 情节推进方向
            scenes: 重要场景描述列表
            chapter_number: 章节号（可选，自动推断）
            
        Returns:
            确认消息，包含章节ID
        """
        # 构建纯文本大纲
        plan_text = f"""# {title}

## 主要情节点
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(plot_points)])}

## 涉及角色
{', '.join(characters)}

## 情节推进方向
{direction}

## 重要场景
{chr(10).join([f"{i+1}. {s}" for i, s in enumerate(scenes)])}
"""
        
        # 结构化数据
        plan_data = {
            "title": title,
            "plot_points": plot_points,
            "characters": characters,
            "direction": direction,
            "scenes": scenes
        }
        
        # 查询 workspace
        ws_result = await context.db.execute(
            select(Workspace).where(Workspace.id == context.workspace_id)
        )
        workspace = ws_result.scalar_one_or_none()
        if not workspace:
            raise ValueError(f"Workspace {context.workspace_id} not found")
        
        # 确定章节号
        if chapter_number is None:
            # 查询当前最大章节号
            chapters_result = await context.db.execute(
                select(Chapter).where(Chapter.workspace_id == context.workspace_id)
            )
            existing_chapters = chapters_result.scalars().all()
            chapter_number = len(existing_chapters) + 1
        
        # 检查章节是否已存在
        existing_result = await context.db.execute(
            select(Chapter).where(
                Chapter.workspace_id == context.workspace_id,
                Chapter.chapter_number == chapter_number
            )
        )
        existing_chapter = existing_result.scalar_one_or_none()
        
        if existing_chapter:
            # 更新现有章节
            existing_chapter.title = title
            existing_chapter.plan = plan_text
            existing_chapter.plan_data = plan_data
            existing_chapter.status = ChapterStatus.PLANNING
            chapter_id = existing_chapter.id
            action = "updated"
        else:
            # 创建新章节
            new_chapter = Chapter(
                workspace_id=context.workspace_id,
                chapter_number=chapter_number,
                title=title,
                plan=plan_text,
                plan_data=plan_data,
                status=ChapterStatus.PLANNING
            )
            context.db.add(new_chapter)
            await context.db.flush()  # 获取 ID
            chapter_id = new_chapter.id
            action = "created"
        
        await context.db.commit()
        
        return f"大纲已{action}！章节ID: {chapter_id}, 章节号: {chapter_number}, 标题: {title}"
    
    return create_plan


# 导出工厂函数
__all__ = ["create_plan_tool_factory", "ToolContext"]

