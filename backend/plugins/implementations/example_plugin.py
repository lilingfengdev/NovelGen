"""示例插件 - 融合 Pluggy + AgentMiddleware"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter
from langchain.agents.middleware import AgentMiddleware
from langchain_core.tools import tool

from backend.plugins import hookimpl


# ============ AgentMiddleware 实现 ============

class ExampleAgentMiddleware(AgentMiddleware):
    """示例 Middleware - 运行时功能"""
    
    # 注入工具
    tools = []  # 通过 __init__ 动态设置
    
    def __init__(self):
        super().__init__()
        
        # 定义工具
        @tool
        def example_tool(query: str) -> str:
            """示例工具 - 演示插件如何注入工具
            
            Args:
                query: 查询内容
                
            Returns:
                示例响应
            """
            return f"示例插件收到查询: {query}"
        
        self.tools = [example_tool]
    
    def modify_model_request(self, request):
        """修改模型请求 - 注入系统提示词"""
        # 在系统提示词中添加插件指令
        plugin_prompt = """

## 示例插件提示

这是示例插件注入的系统提示词。在规划时请注意：
- 保持情节张力
- 注重角色成长
- 考虑世界观一致性
"""
        # 修改第一条消息（通常是系统提示词）
        if request.messages and len(request.messages) > 0:
            first_msg = request.messages[0]
            if hasattr(first_msg, 'content'):
                first_msg.content = first_msg.content + plugin_prompt
        
        return request


# ============ Pluggy 插件类 ============

class ExamplePlugin:
    """示例插件 - 展示完整的插件实现
    
    功能：
    1. 提供自定义工具（通过 AgentMiddleware）
    2. 注入系统提示词（通过 AgentMiddleware）
    3. 扩展 create_plan 参数
    4. 提供配置 Schema
    5. 注册自定义 API 路由
    """
    
    # 插件元数据
    name = "ExamplePlugin"
    description = "示例插件 - 展示 Pluggy + AgentMiddleware 融合架构"
    version = "2.0.0"
    author = "NovelGen Team"
    
    def __init__(self):
        # 创建 Middleware 实例
        self.middleware = ExampleAgentMiddleware()
    
    # ============ 核心接口 ============
    
    @hookimpl
    def hook_get_middleware(self) -> AgentMiddleware:
        """返回 AgentMiddleware 实例"""
        return self.middleware
    
    @hookimpl
    def hook_get_metadata(self) -> Dict[str, Any]:
        """返回插件元信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "config_schema": self.hook_get_config_schema()
        }
    
    # ============ 配置管理 ============
    
    def hook_get_config_schema(self) -> Dict[str, Any]:
        """返回插件配置 Schema"""
        return {
            "type": "object",
            "title": "示例插件配置",
            "description": "配置示例插件的行为",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "title": "启用插件",
                    "description": "是否启用此插件",
                    "default": True
                },
                "example_option": {
                    "type": "string",
                    "title": "示例文本选项",
                    "description": "一个简单的文本配置选项",
                    "default": "default_value"
                },
                "max_length": {
                    "type": "number",
                    "title": "最大长度",
                    "description": "生成内容的最大长度限制",
                    "default": 1000,
                    "minimum": 100,
                    "maximum": 5000
                },
                "style": {
                    "type": "string",
                    "title": "写作风格",
                    "description": "选择写作风格",
                    "enum": ["formal", "casual", "poetic"],
                    "enumNames": ["正式", "随意", "诗意"],
                    "default": "casual"
                }
            },
            "required": ["enabled"]
        }
    
    @hookimpl
    def hook_validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否合法"""
        if "max_length" in config:
            if not (100 <= config["max_length"] <= 5000):
                return False
        if "style" in config:
            if config["style"] not in ["formal", "casual", "poetic"]:
                return False
        return True
    
    # ============ 扩展功能 ============
    
    @hookimpl
    def hook_extend_create_plan_params(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """扩展 create_plan 工具的参数
        
        示例：添加世界观相关的参数
        """
        return {
            "world_setting": {
                "type": str,
                "description": "世界观设定",
                "required": False
            },
            "key_items": {
                "type": List[str],
                "description": "本章出现的关键物品",
                "required": False
            },
            "location": {
                "type": str,
                "description": "主要场景地点",
                "required": False
            },
            "chapter_tags": {
                "type": List[str],
                "description": "章节标签（如：战斗、日常、转折）",
                "required": False
            }
        }
    
    @hookimpl
    def hook_register_api_routes(self) -> List[Dict[str, Any]]:
        """注册示例插件的 API 路由"""
        router = APIRouter()

        @router.get("/hello")
        async def hello():
            return {
                "plugin": self.name,
                "message": "Hello from Example Plugin!",
                "version": self.version
            }
        
        @router.get("/status")
        async def status():
            return {
                "plugin": self.name,
                "status": "running",
                "features": [
                    "AgentMiddleware integration",
                    "Custom tools",
                    "System prompt injection",
                    "create_plan extension",
                    "API routes"
                ]
            }

        return [{
            "router": router,
            "prefix": "/api/plugins/example",
            "tags": ["plugins", self.name]
        }]
    
    # ============ 生命周期 ============
    
    @hookimpl
    def hook_on_workspace_init(self, workspace_id: int):
        """工作区初始化时调用"""
        print(f"[{self.name}] 工作区 {workspace_id} 初始化")
    
    @hookimpl
    def hook_on_plugin_enabled(self, workspace_id: int):
        """插件启用时调用"""
        print(f"[{self.name}] 在工作区 {workspace_id} 中启用")
    
    @hookimpl
    def hook_on_plugin_disabled(self, workspace_id: int):
        """插件禁用时调用"""
        print(f"[{self.name}] 在工作区 {workspace_id} 中禁用")
