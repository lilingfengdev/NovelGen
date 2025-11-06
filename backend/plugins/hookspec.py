"""插件 Hook 规范定义 - 融合 Pluggy + AgentMiddleware"""
import pluggy
from typing import Dict, Any, List, Optional
from langchain.agents.middleware import AgentMiddleware

hookspec = pluggy.HookspecMarker("novelgen")


class NovelGenHookSpec:
    """NovelGen 插件 Hook 规范
    
    融合架构：
    - 使用 Pluggy 管理插件生命周期和配置
    - 使用 AgentMiddleware 进行运行时集成
    """
    
    # ============ 核心接口（必须实现）============
    
    @hookspec
    def hook_get_middleware(self) -> Optional[AgentMiddleware]:
        """返回插件的 AgentMiddleware 实例
        
        这是核心接口，插件通过返回 AgentMiddleware 来注入：
        - Tools（通过 middleware.tools）
        - State（通过 middleware.state_schema）
        - System Prompt（通过 middleware.modify_model_request）
        
        Returns:
            AgentMiddleware 实例，返回 None 表示插件不参与 Agent 运行时
        """
        pass
    
    @hookspec
    def hook_get_metadata(self) -> Dict[str, Any]:
        """返回插件元信息
        
        Returns:
            {
                "name": str,
                "version": str,
                "description": str,
                "author": str,
                "config_schema": dict  # JSON Schema
            }
        """
        pass
    
    # ============ 配置管理 ============
    
    @hookspec
    def hook_validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否合法
        
        Args:
            config: 配置字典
            
        Returns:
            是否合法
        """
        pass
    
    # ============ 生命周期 ============
    
    @hookspec
    def hook_on_workspace_init(self, workspace_id: int):
        """工作区初始化时调用
        
        Args:
            workspace_id: 工作区ID
        """
        pass
    
    @hookspec
    def hook_on_plugin_enabled(self, workspace_id: int):
        """插件启用时调用
        
        Args:
            workspace_id: 工作区ID
        """
        pass
    
    @hookspec
    def hook_on_plugin_disabled(self, workspace_id: int):
        """插件禁用时调用
        
        Args:
            workspace_id: 工作区ID
        """
        pass
    
    # ============ 扩展接口（可选）============
    
    @hookspec
    def hook_register_api_routes(self) -> List[Dict[str, Any]]:
        """注册插件自定义 API 路由
        
        Returns:
            [
                {
                    "router": APIRouter实例,
                    "prefix": "/api/plugins/<name>",
                    "tags": ["plugins", "<name>"]
                }
            ]
        """
        pass
    
    @hookspec
    def hook_extend_create_plan_params(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """扩展 create_plan 工具的参数
        
        插件可以返回额外的参数定义，这些参数会被合并到 create_plan 工具中。
        
        Args:
            context: 上下文信息
            
        Returns:
            {
                "param_name": {
                    "type": type,  # Python 类型
                    "description": "参数描述",
                    "required": True/False
                }
            }
        """
        pass

