"""示例插件 - 展示插件如何实现"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter
from backend.plugins import hookimpl


class ExamplePlugin:
    """示例插件 - 展示基本的Hook实现"""
    
    # 插件元数据
    name = "ExamplePlugin"
    description = "这是一个示例插件，展示如何实现Novel Studio的插件系统"
    version = "1.0.0"
    author = "Novel Studio"
    
    def __init__(self):
        # 插件可以维护自己的状态
        self._states: Dict[int, Dict[str, Any]] = {}
    
    @hookimpl
    def hook_inject_system_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        """在系统提示词中注入示例内容"""
        if stage == "plan":
            return "<example-plugin>\n这是一个示例插件注入的系统提示词\n</example-plugin>"
        return None
    
    @hookimpl
    def hook_before_plan(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Plan前的处理"""
        print(f"[{self.name}] Plan阶段开始")
        return None
    
    @hookimpl
    def hook_after_plan(self, plan: str, context: Dict[str, Any]) -> Optional[str]:
        """Plan后的处理"""
        print(f"[{self.name}] Plan生成完成，长度: {len(plan)}")
        return None
    
    @hookimpl
    def hook_get_plugin_state(self, workspace_id: int) -> Dict[str, Any]:
        """获取插件状态"""
        return self._states.get(workspace_id, {})
    
    @hookimpl
    def hook_set_plugin_state(self, workspace_id: int, state: Dict[str, Any]) -> None:
        """恢复插件状态"""
        self._states[workspace_id] = state
    
    @hookimpl
    def hook_get_config_schema(self) -> Dict[str, Any]:
        """返回插件配置Schema"""
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
        # 简单验证
        if "max_length" in config:
            if not (100 <= config["max_length"] <= 5000):
                return False
        if "style" in config:
            if config["style"] not in ["formal", "casual", "poetic"]:
                return False
        return True

    @hookimpl
    def hook_register_api_routes(self) -> List[Dict[str, Any]]:
        """注册示例插件的API路由"""
        router = APIRouter()

        @router.get("/hello")
        async def hello():
            return {"plugin": self.name, "message": "hello from example plugin"}

        return [{
            "router": router,
            "prefix": "/api/plugins/example",
            "tags": ["plugins", self.name]
        }]

