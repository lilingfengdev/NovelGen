"""生成引擎 - 基于 DeepAgent"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from backend.config import settings
from backend.models.chapter import Chapter, ChapterStatus
from backend.models.settings import SystemSettings
from backend.models.workspace import Workspace
from backend.core.store_manager import StoreManager
from backend.core.tools import create_plan_tool_factory, ToolContext
from backend.plugins.manager import plugin_manager


class GenerationEngine:
    """DeepAgent 生成引擎 - Plan Agent + Writer SubAgent"""
    
    def __init__(self):
        """初始化引擎"""
        pass
    
    async def _get_llm(
        self,
        db: AsyncSession,
        workspace_id: int,
        model: Optional[str] = None
    ) -> ChatOpenAI:
        """获取LLM实例，从workspace配置读取参数
        
        Args:
            db: 数据库会话
            workspace_id: 工作区ID
            model: 模型名称，如果为None则使用系统配置
            
        Returns:
            ChatOpenAI实例
        """
        # 从数据库读取系统设置
        result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
        sys_settings = result.scalar_one_or_none()
        if not sys_settings:
            sys_settings = SystemSettings(id=1)
        
        # 读取 workspace 配置
        ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
        workspace = ws_result.scalar_one_or_none()
        ws_config = workspace.config if workspace else {}
        
        # 基础配置
        effective_model = model or ws_config.get("model") or sys_settings.openai_model or settings.openai_model or "gpt-4-turbo-preview"
        
        # 检查 API Key
        api_key = sys_settings.openai_api_key or settings.openai_api_key
        if not api_key:
            raise ValueError("未配置 OpenAI API Key。请在系统设置中配置后再使用生成功能。")
        
        kwargs = {
            "model": effective_model,
            "openai_api_key": api_key,
        }
        
        # 只在workspace配置了生成参数时才传递
        if "temperature" in ws_config:
            kwargs["temperature"] = ws_config["temperature"]
        if "max_tokens" in ws_config:
            kwargs["max_tokens"] = ws_config["max_tokens"]
        if "top_p" in ws_config:
            kwargs["top_p"] = ws_config["top_p"]
        
        # base_url
        base_url = sys_settings.openai_base_url or settings.openai_base_url
        if base_url:
            kwargs["base_url"] = base_url
        
        return ChatOpenAI(**kwargs)
    
    async def create_plan_agent(
        self,
        db: AsyncSession,
        workspace_id: int,
        chapter_number: int,
        model: Optional[str] = None
    ):
        """创建 Plan Agent
        
        Args:
            db: 数据库会话
            workspace_id: 工作区ID
            chapter_number: 章节号
            model: 模型名称
            
        Returns:
            Plan Agent 实例
        """
        # 获取 LLM
        llm = await self._get_llm(db, workspace_id, model)
        
        # 获取 checkpointer 和 store
        checkpointer, store = await StoreManager.get_or_create(workspace_id)
        
        # 构建系统提示词
        system_prompt = f"""你是一个专业的小说大纲规划师。你需要和用户对话，根据他们的要求规划第{chapter_number}章的大纲。

其他章节存放在 `/memories/chapters/` 目录,在开始编写大纲前,请使用工具收集足够的信息

## 大纲要求

大纲应该包含：
1. 章节标题
2. 主要情节点（3-5个）
3. 涉及的角色
4. 情节推进方向
5. 重要的场景描述

你注重通过组织"人"、"物"、"事"、"地"来细致展现世界，人物的欲望、行动和关系将在与"物、事、地"的互动和改造中自然浮现。
系统性地创造叙事，保持逻辑和结构连贯，符合小说整体风格。

当大纲完整且用户满意时，**调用 create_plan 工具保存大纲** 如果用户提出修改意见，调整后再次调用 create_plan 更新

create_plan 是保存大纲的唯一方式，其他文件操作用于参考和草稿。
"""
        
        # 创建工具上下文（不传入 db，tool 内部自己创建 session）
        tool_context = ToolContext(workspace_id=workspace_id)
        
        # 创建 create_plan 工具
        create_plan = create_plan_tool_factory(tool_context)
        
        # 获取插件 middlewares
        plugin_middlewares = plugin_manager.get_middlewares(workspace_id)
        
        # Writer SubAgent 配置
        writer_subagent = {
            "name": "writer",
            "description": "专业小说作家，负责根据大纲生成章节的具体内容。擅长细节描写和对话创作。",
            "system_prompt": """你是一个专业的小说作家。你的任务是根据大纲生成详细的章节内容。

## 文件系统

- `/memories/chapters/{{id}}.md` - 历史章节内容
- `/` - 临时工作区

## 要求

1. 严格按照大纲展开情节
2. 保持人物性格一致
3. 细节描写生动
4. 对话自然流畅
5. 情节推进合理
6. 字数适中（3000-5000字）

注意保持与之前章节的连贯性。
""",
            "tools": []  # 可以访问文件系统工具
        }
        
        # 创建 Plan Agent（集成插件）
        agent = create_deep_agent(
            model=llm,
            system_prompt=system_prompt,
            tools=[create_plan],  # 只有 create_plan，其他都是内置工具
            middleware=plugin_middlewares,  # 注入插件 middleware
            backend=lambda rt: CompositeBackend(
                default=StateBackend(rt),  # /workspace/* 临时文件
                routes={
                    "/memories/": StoreBackend(rt)  # /memories/* 持久化到 Store
                }
            ),
            subagents=[writer_subagent],
            checkpointer=checkpointer,
            store=store,
        )
        
        return agent
    
    async def plan_chat(
        self,
        db: AsyncSession,
        workspace_id: int,
        chapter_number: int,
        message: str,
        thread_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Plan Agent 对话（单次调用）
        
        Args:
            db: 数据库会话
            workspace_id: 工作区ID
            chapter_number: 章节号
            message: 用户消息
            thread_id: 线程ID（用于恢复对话）
            model: 模型名称
            
        Returns:
            {
                "messages": [...],  # 完整消息历史
                "thread_id": "...",  # 线程ID
                "plan_created": bool,  # 是否创建了大纲
                "chapter_id": int | None  # 章节ID（如果创建了）
            }
        """
        # 创建 Plan Agent
        agent = await self.create_plan_agent(db, workspace_id, chapter_number, model)
        
        # 构建输入
        input_data = {
            "messages": [HumanMessage(content=message)]
        }
        
        # 配置
        config = {
            "configurable": {
                "thread_id": thread_id or f"plan_{workspace_id}_{chapter_number}",
            }
        }
        
        # 调用 Agent
        result = await agent.ainvoke(input_data, config=config)
        
        # 解析结果
        messages = result.get("messages", [])
        
        # 检查是否创建了大纲（通过检查数据库）
        chapter_result = await db.execute(
            select(Chapter).where(
                Chapter.workspace_id == workspace_id,
                Chapter.chapter_number == chapter_number
            )
        )
        chapter = chapter_result.scalar_one_or_none()
        
        plan_created = chapter is not None and chapter.plan is not None
        
        return {
            "messages": [
                {"role": m.type, "content": m.content if hasattr(m, "content") else str(m)}
                for m in messages
            ],
            "thread_id": config["configurable"]["thread_id"],
            "plan_created": plan_created,
            "chapter_id": chapter.id if chapter else None
        }
    
    async def plan_chat_stream(
        self,
        db: AsyncSession,
        workspace_id: int,
        chapter_number: int,
        message: str,
        thread_id: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Plan Agent 流式对话（用于 SSE）
        
        Args:
            db: 数据库会话
            workspace_id: 工作区ID
            chapter_number: 章节号
            message: 用户消息
            thread_id: 线程ID
            model: 模型名称
            
        Yields:
            流式事件
        """
        # 创建 Plan Agent
        agent = await self.create_plan_agent(db, workspace_id, chapter_number, model)
        
        # 构建输入
        input_data = {
            "messages": [HumanMessage(content=message)]
        }
        
        # 配置
        config = {
            "configurable": {
                "thread_id": thread_id or f"plan_{workspace_id}_{chapter_number}",
            }
        }
        
        # 流式调用
        async for event in agent.astream_events(input_data, config=config, version="v2"):
            # 只传递关键事件
            event_type = event.get("event")
            
            if event_type == "on_chat_model_stream":
                # LLM 流式输出
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield {
                        "type": "message_chunk",
                        "content": chunk.content
                    }
            
            elif event_type == "on_tool_start":
                # 工具开始调用
                tool_name = event.get("name")
                yield {
                    "type": "tool_start",
                    "tool_name": tool_name
                }
            
            elif event_type == "on_tool_end":
                # 工具调用结束
                tool_name = event.get("name")
                output = event.get("data", {}).get("output")
                
                # 确保 output 可序列化
                if output is not None:
                    # 如果是 LangChain 消息对象，提取 content
                    if hasattr(output, "content"):
                        output = output.content
                    # 如果是其他对象，转成字符串
                    elif not isinstance(output, (str, int, float, bool, list, dict, type(None))):
                        output = str(output)
                
                yield {
                    "type": "tool_end",
                    "tool_name": tool_name,
                    "output": output
                }
    
    async def generate_content(
        self,
        db: AsyncSession,
        chapter_id: int,
        workspace_id: int,
        model: Optional[str] = None
    ) -> str:
        """使用 Writer SubAgent 生成章节内容
        
        Args:
            db: 数据库会话
            chapter_id: 章节ID
            workspace_id: 工作区ID
            model: 模型名称
            
        Returns:
            生成的章节内容
        """
        # 查询章节
        chapter_result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
        chapter = chapter_result.scalar_one_or_none()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        if not chapter.plan:
            raise ValueError("章节大纲不存在，请先创建大纲")
        
        # 创建 Plan Agent（包含 Writer SubAgent）
        agent = await self.create_plan_agent(db, workspace_id, chapter.chapter_number, model)
        
        # 构建提示词，指示 Plan Agent 派发 Writer SubAgent
        prompt = f"""现在请使用 task() 工具派发 writer 子任务，生成第{chapter.chapter_number}章的内容。

章节大纲：
{chapter.plan}

要求：
1. 使用 `read_file('/memories/chapters/*.md')` 读取历史章节
2. 根据大纲生成 3000-5000 字的章节内容
3. 使用 `write_file('/memories/chapters/{chapter_id}.md', content)` 保存内容
"""
        
        # 配置 - 继续使用 plan 阶段的 thread_id，保持对话连续性
        config = {
            "configurable": {
                "thread_id": f"plan_{workspace_id}_{chapter.chapter_number}",
            }
        }
        
        # 调用 Agent，派发 Writer SubAgent
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]},
            config=config
        )
        
        # 从 Store 读取生成的内容
        _, store = await StoreManager.get_or_create(workspace_id)
        
        # 尝试从 Store 读取章节内容
        stored_chapter = await store.aget(("memories", "chapters"), str(chapter_id))
        
        if stored_chapter and stored_chapter.value:
            content = stored_chapter.value.get("content", "")
        else:
            # 如果 Store 中没有，从 Agent 结果中提取
            content = result.get("messages", [])[-1].content if result.get("messages") else ""
        
        # 更新数据库中的章节状态
        chapter.content = content[:500]  # 只存摘要
        chapter.status = ChapterStatus.GENERATING
        # 只 flush，不 commit，让外层（API）管理事务
        await db.flush()
        
        return content
    
    async def finalize_chapter(
        self,
        db: AsyncSession,
        chapter_id: int
    ):
        """最终确认章节
        
        Args:
            db: 数据库会话
            chapter_id: 章节ID
        """
        chapter_result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
        chapter = chapter_result.scalar_one_or_none()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")
        
        chapter.status = ChapterStatus.COMPLETED
        chapter.completed_at = datetime.utcnow()
        # 只 flush，不 commit，让外层（API）管理事务
        await db.flush()


# 全局引擎实例
generation_engine = GenerationEngine()


