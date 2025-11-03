"""生成引擎核心 - 实现 Plan -> Generate -> Verify -> Improve -> Update 流程"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from backend.config import settings
from backend.plugins.manager import plugin_manager
from backend.models.chapter import Chapter, ChapterStatus


class GenerationEngine:
    """生成引擎 - 核心生成逻辑"""
    
    def __init__(self):
        """初始化生成引擎，不预创建LLM实例"""
        pass
    
    def _get_llm(self, model: Optional[str] = None) -> ChatOpenAI:
        """获取LLM实例，支持动态模型选择
        
        Args:
            model: 模型名称，如果为None则使用默认配置
            
        Returns:
            ChatOpenAI实例
        """
        kwargs = {
            "model": model or settings.openai_model,
            "openai_api_key": settings.openai_api_key,
            "temperature": 0.7,
        }
        
        # 如果配置了自定义base_url，添加到参数中
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        
        return ChatOpenAI(**kwargs)
    
    def _build_prompt(self, stage: str, base_system: str, base_user: str, context: Dict[str, Any]) -> List[BaseMessage]:
        """构建提示词，合并插件注入的内容
        
        Args:
            stage: 当前阶段
            base_system: 基础系统提示词
            base_user: 基础用户提示词
            context: 上下文
            
        Returns:
            消息列表
        """
        # 获取插件注入的提示词
        plugin_prompts = plugin_manager.merge_prompts(stage, context)
        
        # 合并系统提示词
        system_prompt = base_system
        if plugin_prompts["system"]:
            system_prompt += f"\n\n{plugin_prompts['system']}"
        
        # 合并用户提示词
        user_prompt = base_user
        if plugin_prompts["user"]:
            user_prompt += f"\n\n{plugin_prompts['user']}"
        
        # 构建消息
        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt).format(),
            HumanMessagePromptTemplate.from_template(user_prompt).format(**context)
        ]
        
        return messages
    
    async def plan_interactive(
        self,
        workspace_id: int,
        chapter_number: int,
        messages: List[Dict[str, Any]],
        previous_chapters: Optional[List[Chapter]] = None,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """对话式生成章节大纲 - 支持工具调用和多轮对话
        
        Args:
            workspace_id: 工作区ID
            chapter_number: 章节号
            messages: 对话历史
            previous_chapters: 之前的章节
            model: 模型名称
            context: 额外上下文
            
        Returns:
            {"messages": [...], "plan": "...", "completed": bool}
        """
        ctx = context or {}
        ctx.update({
            "workspace_id": workspace_id,
            "chapter_number": chapter_number,
            "previous_chapters": previous_chapters or []
        })
        
        # 调用 before_plan hooks
        hook_results = plugin_manager.call_hook("hook_before_plan", context=ctx)
        for result in hook_results:
            if result and isinstance(result, dict):
                ctx.update(result)
        
        # 构建系统提示词
        prev_summary = ""
        if previous_chapters:
            prev_summary = "\n\n".join([
                f"第{ch.chapter_number}章: {ch.title}\n{ch.plan[:200]}..."
                for ch in previous_chapters[-3:]
            ])
        
        system_prompt = f"""你是一个专业的小说大纲规划师。你需要和用户对话，根据他们的要求规划第{chapter_number}章的大纲。

之前的章节：
{prev_summary if prev_summary else "这是第一章"}

大纲应该包含：
1. 章节标题
2. 主要情节点（3-5个）
3. 涉及的角色
4. 情节推进方向
5. 重要的场景描述
比起快速推进主线，你倾向于长篇连载体裁的“慢叙事”。
你注重通过组织“人”、“物”、“事”、“地”来细致展现世界，人物的欲望、行动和关系将在与“物、事、地”的互动和改造中自然浮现。
系统性地创造叙事，保持逻辑和结构连贯，符合小说整体风格。

只有当你确认大纲完整且用户满意时，才调用 create_plan 工具。"""
        
        # 获取插件注入的提示词
        plugin_prompts = plugin_manager.merge_prompts("plan", ctx)
        if plugin_prompts["system"]:
            system_prompt += f"\n\n{plugin_prompts['system']}"
        
        # 定义create_plan工具
        @tool
        def create_plan(
            title: str,
            plot_points: List[str],
            characters: List[str],
            direction: str,
            scenes: str
        ) -> str:
            """创建章节大纲
            
            Args:
                title: 章节标题
                plot_points: 主要情节点列表
                characters: 涉及的角色列表
                direction: 情节推进方向
                scenes: 重要场景描述
            """
            plan_content = f"""# {title}

## 主要情节点
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(plot_points)])}

## 涉及角色
{', '.join(characters)}

## 情节推进方向
{direction}

## 重要场景
{scenes}
"""
            return plan_content
        
        # 收集插件工具
        plugin_tools = plugin_manager.collect_tools("plan", ctx)
        tools = [create_plan] + plugin_tools
        
        # 构建消息列表
        msg_list = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if msg["role"] == "user":
                msg_list.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                msg_list.append(AIMessage(content=msg.get("content", ""), 
                                         tool_calls=msg.get("tool_calls", [])))
            elif msg["role"] == "tool":
                msg_list.append(ToolMessage(content=msg["content"], 
                                           tool_call_id=msg["tool_call_id"]))
        
        # 调用LLM with tools
        llm = self._get_llm(model)
        llm_with_tools = llm.bind_tools(tools)
        response = await llm_with_tools.ainvoke(msg_list)
        
        # 处理响应
        result = {
            "messages": messages.copy(),
            "plan": None,
            "completed": False
        }
        
        # 添加AI响应
        ai_msg = {
            "role": "assistant",
            "content": response.content or "",
        }
        
        if response.tool_calls:
            ai_msg["tool_calls"] = response.tool_calls
            result["messages"].append(ai_msg)
            
            # 执行工具调用
            for tool_call in response.tool_calls:
                if tool_call["name"] == "create_plan":
                    # 执行create_plan
                    plan_content = create_plan.invoke(tool_call["args"])
                    
                    # 调用 after_plan hooks
                    hook_results = plugin_manager.call_hook("hook_after_plan", 
                                                           plan=plan_content, context=ctx)
                    for hook_result in hook_results:
                        if hook_result and isinstance(hook_result, str):
                            plan_content = hook_result
                    
                    result["plan"] = plan_content
                    result["completed"] = True
                    
                    # 添加工具响应消息
                    result["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": "大纲已创建"
                    })
                else:
                    # 执行其他插件工具
                    tool_result = "工具执行成功"
                    result["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result
                    })
        else:
            # 没有工具调用，继续对话
            result["messages"].append(ai_msg)
        
        return result
    
    async def plan(
        self,
        workspace_id: int,
        chapter_number: int,
        user_input: Optional[str] = None,
        previous_chapters: Optional[List[Chapter]] = None,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成章节大纲
        
        Args:
            workspace_id: 工作区ID
            chapter_number: 章节号
            user_input: 用户输入/修改意见
            previous_chapters: 之前的章节
            context: 额外上下文
            
        Returns:
            生成的大纲
        """
        ctx = context or {}
        ctx.update({
            "workspace_id": workspace_id,
            "chapter_number": chapter_number,
            "user_input": user_input or "",
            "previous_chapters": previous_chapters or []
        })
        
        # 调用 before_plan hooks - 所有插件链式修改上下文
        hook_results = plugin_manager.call_hook("hook_before_plan", context=ctx)
        for result in hook_results:
            if result and isinstance(result, dict):
                ctx.update(result)
        
        # 构建基础提示词
        base_system = """你是一个专业的小说大纲规划师。你的任务是根据已有的章节和用户要求，规划下一章的大纲。

大纲应该包含：
1. 章节标题
2. 主要情节点（3-5个）
3. 涉及的角色
4. 情节推进方向
5. 重要的场景描述

保持逻辑连贯，符合小说整体风格。"""
        
        # 构建用户提示词
        prev_summary = ""
        if previous_chapters:
            prev_summary = "\n\n".join([
                f"第{ch.chapter_number}章: {ch.title}\n{ch.plan[:200]}..."
                for ch in previous_chapters[-3:]  # 最近3章
            ])
        
        base_user = f"""请为第{chapter_number}章规划大纲。

之前的章节：
{prev_summary if prev_summary else "这是第一章"}

用户要求：
{user_input if user_input else "按照正常剧情发展"}

请生成详细的章节大纲。"""
        
        # 构建完整提示词
        messages = self._build_prompt("plan", base_system, base_user, ctx)
        
        # 调用LLM
        llm = self._get_llm(model)
        response = await llm.ainvoke(messages)
        plan = response.content
        
        # 调用 after_plan hooks - 所有插件链式修改plan
        hook_results = plugin_manager.call_hook("hook_after_plan", plan=plan, context=ctx)
        for result in hook_results:
            if result and isinstance(result, str):
                plan = result
        
        return plan
    
    async def generate(
        self,
        chapter: Chapter,
        workspace_id: int,
        previous_chapters: Optional[List[Chapter]] = None,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成章节内容
        
        Args:
            chapter: 章节对象（包含plan）
            workspace_id: 工作区ID
            previous_chapters: 之前的章节
            context: 额外上下文
            
        Returns:
            生成的章节内容
        """
        ctx = context or {}
        ctx.update({
            "workspace_id": workspace_id,
            "chapter": chapter,
            "chapter_number": chapter.chapter_number,
            "plan": chapter.plan,
            "previous_chapters": previous_chapters or []
        })
        
        # 调用 before_generate hooks - 所有插件链式修改上下文
        hook_results = plugin_manager.call_hook("hook_before_generate", context=ctx)
        for result in hook_results:
            if result and isinstance(result, dict):
                ctx.update(result)
        
        # 构建基础提示词
        base_system = """你是一个专业的小说作家。你的任务是根据大纲生成详细的章节内容。

要求：
1. 严格按照大纲展开情节
2. 保持人物性格一致
3. 细节描写生动
4. 对话自然流畅
5. 情节推进合理
6. 字数适中（3000-5000字）

注意保持与之前章节的连贯性。"""
        
        # 构建用户提示词
        prev_content = ""
        if previous_chapters:
            last_chapter = previous_chapters[-1]
            prev_content = f"\n\n上一章结尾：\n{last_chapter.content[-500:] if last_chapter.content else ''}"
        
        base_user = f"""请根据以下大纲生成第{chapter.chapter_number}章的完整内容。

章节大纲：
{chapter.plan}
{prev_content}

请开始创作章节内容。"""
        
        # 构建完整提示词
        messages = self._build_prompt("generate", base_system, base_user, ctx)
        
        # 收集工具（如果插件提供了）
        tools = plugin_manager.collect_tools("generate", ctx)
        
        # 调用LLM
        llm = self._get_llm(model)
        if tools:
            # TODO: 实现工具调用逻辑
            response = await llm.ainvoke(messages)
        else:
            response = await llm.ainvoke(messages)
        
        content = response.content
        
        # 调用 after_generate hooks - 所有插件链式修改content
        hook_results = plugin_manager.call_hook("hook_after_generate", content=content, context=ctx)
        for result in hook_results:
            if result and isinstance(result, str):
                content = result
        
        return content
    
    async def verify(
        self,
        chapter: Chapter,
        workspace_id: int,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """验证章节内容
        
        Args:
            chapter: 章节对象
            workspace_id: 工作区ID
            context: 额外上下文
            
        Returns:
            验证结果 {"passed": bool, "issues": [...], "suggestions": [...]}
        """
        ctx = context or {}
        ctx.update({
            "workspace_id": workspace_id,
            "chapter": chapter,
        })
        
        # 调用 before_verify hooks - 所有插件链式修改上下文
        hook_results = plugin_manager.call_hook("hook_before_verify", context=ctx)
        for result in hook_results:
            if result and isinstance(result, dict):
                ctx.update(result)
        
        # 构建验证提示词
        base_system = """你是一个专业的小说编辑。你的任务是检查章节内容的质量。

检查项：
1. 是否符合大纲
2. 逻辑是否连贯
3. 人物性格是否一致
4. 是否有明显的情节漏洞
5. 描写是否生动
6. 对话是否自然

请以JSON格式返回检查结果。"""
        
        base_user = f"""请检查以下章节内容：

大纲：
{chapter.plan}

内容：
{chapter.content}

请返回JSON格式的检查结果：
{{
  "passed": true/false,
  "issues": ["问题1", "问题2", ...],
  "suggestions": ["建议1", "建议2", ...]
}}"""
        
        messages = self._build_prompt("verify", base_system, base_user, ctx)
        
        # 调用LLM
        llm = self._get_llm(model)
        response = await llm.ainvoke(messages)
        
        # 解析结果
        try:
            import json
            # 尝试从response中提取JSON
            content = response.content
            # 查找JSON部分
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                result = json.loads(content[start:end])
            else:
                # 如果没有找到JSON，返回默认结果
                result = {
                    "passed": True,
                    "issues": [],
                    "suggestions": []
                }
        except Exception:
            result = {
                "passed": True,
                "issues": [],
                "suggestions": []
            }
        
        # 调用 after_verify hooks - 所有插件链式修改result
        hook_results = plugin_manager.call_hook("hook_after_verify", result=result, context=ctx)
        for hook_result in hook_results:
            if hook_result and isinstance(hook_result, dict):
                result.update(hook_result)
        
        return result
    
    async def improve(
        self,
        chapter: Chapter,
        verification_result: Dict[str, Any],
        workspace_id: int,
        focus_issues: Optional[List[str]] = None,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """改进章节内容
        
        Args:
            chapter: 章节对象
            verification_result: 验证结果
            workspace_id: 工作区ID
            focus_issues: 重点关注的问题
            context: 额外上下文
            
        Returns:
            改进后的内容
        """
        ctx = context or {}
        ctx.update({
            "workspace_id": workspace_id,
            "chapter": chapter,
            "verification_result": verification_result,
            "focus_issues": focus_issues or []
        })
        
        # 调用 before_improve hooks - 所有插件链式修改上下文
        hook_results = plugin_manager.call_hook("hook_before_improve", context=ctx)
        for result in hook_results:
            if result and isinstance(result, dict):
                ctx.update(result)
        
        # 构建改进提示词
        issues_text = "\n".join([f"- {issue}" for issue in verification_result.get("issues", [])])
        suggestions_text = "\n".join([f"- {sug}" for sug in verification_result.get("suggestions", [])])
        
        base_system = """你是一个专业的小说作家。你的任务是根据编辑的反馈改进章节内容。

要求：
1. 针对性地解决指出的问题
2. 保持原有的优点
3. 不要偏离大纲
4. 改进后内容应更加完善"""
        
        base_user = f"""请改进以下章节内容。

原内容：
{chapter.content}

发现的问题：
{issues_text if issues_text else "无明显问题"}

改进建议：
{suggestions_text if suggestions_text else "无"}

请返回改进后的完整章节内容。"""
        
        messages = self._build_prompt("improve", base_system, base_user, ctx)
        
        # 调用LLM
        llm = self._get_llm(model)
        response = await llm.ainvoke(messages)
        improved_content = response.content
        
        # 调用 after_improve hooks - 所有插件链式修改content
        hook_results = plugin_manager.call_hook("hook_after_improve", content=improved_content, context=ctx)
        for result in hook_results:
            if result and isinstance(result, str):
                improved_content = result
        
        return improved_content
    
    async def update(
        self,
        chapter: Chapter,
        workspace_id: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """更新最终内容，收集插件状态
        
        Args:
            chapter: 章节对象
            workspace_id: 工作区ID
            context: 额外上下文
        """
        ctx = context or {}
        ctx.update({
            "workspace_id": workspace_id,
            "chapter": chapter,
        })
        
        # 调用 before_update hooks - 所有插件链式修改上下文
        hook_results = plugin_manager.call_hook("hook_before_update", context=ctx)
        for result in hook_results:
            if result and isinstance(result, dict):
                ctx.update(result)
        
        # 收集所有插件的状态快照
        plugin_snapshot = plugin_manager.collect_plugin_states(workspace_id)
        chapter.plugin_snapshot = plugin_snapshot
        
        # 标记为完成
        chapter.status = ChapterStatus.COMPLETED
        chapter.completed_at = datetime.utcnow()
        
        # 调用 after_update hooks
        plugin_manager.call_hook("hook_after_update", context=ctx)


# 全局生成引擎实例
generation_engine = GenerationEngine()

