"""插件Hook规范定义"""
import pluggy
from typing import Dict, Any, List, Optional

hookspec = pluggy.HookspecMarker("novelgen")


class NovelGenHookSpec:
    """Novel Studio插件Hook规范
    
    插件通过实现这些hooks来扩展系统功能
    """
    
    # ============ 提示词注入 ============
    
    @hookspec
    def hook_inject_system_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        """注入系统提示词
        
        Args:
            stage: 当前阶段 (plan/generate/verify/improve)
            context: 上下文信息 (workspace, chapter, etc.)
            
        Returns:
            要注入的系统提示词，返回None则不注入
        """
        pass
    
    @hookspec
    def hook_inject_user_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        """注入用户提示词
        
        Args:
            stage: 当前阶段
            context: 上下文信息
            
        Returns:
            要注入的用户提示词
        """
        pass
    
    # ============ 工具注入 ============
    
    @hookspec
    def hook_inject_tools(self, stage: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """注入工具调用（LangChain tools）
        
        Args:
            stage: 当前阶段
            context: 上下文信息
            
        Returns:
            工具定义列表
        """
        pass
    
    @hookspec
    def hook_extend_create_plan_params(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """扩展 create_plan 工具的参数
        
        插件可以返回额外的参数定义，这些参数会被合并到 create_plan 工具中。
        返回的字典格式：
        {
            "param_name": {
                "type": type,  # Python 类型
                "description": "参数描述",
                "required": True/False  # 可选，默认 False
            }
        }
        
        Args:
            context: 上下文信息
            
        Returns:
            额外参数定义字典，返回 None 则不扩展
        """
        pass
    
    # ============ 内容修改 ============
    
    @hookspec
    def hook_modify_generation(self, stage: str, content: str, context: Dict[str, Any]) -> str:
        """修改生成的内容
        
        Args:
            stage: 当前阶段
            content: 生成的原始内容
            context: 上下文信息
            
        Returns:
            修改后的内容
        """
        pass
    
    # ============ 流程拦截 ============
    
    @hookspec
    def hook_before_plan(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Plan阶段前的拦截
        
        Args:
            context: 上下文信息
            
        Returns:
            修改后的上下文，或None保持不变
        """
        pass
    
    @hookspec
    def hook_after_plan(self, plan: str, context: Dict[str, Any]) -> Optional[str]:
        """Plan阶段后的拦截
        
        Args:
            plan: 生成的大纲
            context: 上下文信息
            
        Returns:
            修改后的大纲，或None保持不变
        """
        pass
    
    @hookspec
    def hook_before_generate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate阶段前的拦截"""
        pass
    
    @hookspec
    def hook_after_generate(self, content: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate阶段后的拦截"""
        pass
    
    @hookspec
    def hook_before_verify(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verify阶段前的拦截"""
        pass
    
    @hookspec
    def hook_after_verify(self, result: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verify阶段后的拦截"""
        pass
    
    @hookspec
    def hook_before_improve(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Improve阶段前的拦截"""
        pass
    
    @hookspec
    def hook_after_improve(self, content: str, context: Dict[str, Any]) -> Optional[str]:
        """Improve阶段后的拦截"""
        pass
    
    @hookspec
    def hook_before_update(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update阶段前的拦截"""
        pass
    
    @hookspec
    def hook_after_update(self, context: Dict[str, Any]) -> None:
        """Update阶段后的拦截"""
        pass

    # ============ 配置与状态 ============
    
    @hookspec
    def hook_get_config_schema(self) -> Optional[Dict[str, Any]]:
        """返回插件配置的JSON Schema定义
        
        Returns:
            JSON Schema 字典，None 表示无配置
        """
        pass
    
    @hookspec
    def hook_get_plugin_state(self, workspace_id: int) -> Optional[Dict[str, Any]]:
        """返回插件在指定工作区的可序列化状态
        
        Args:
            workspace_id: 工作区ID
        
        Returns:
            状态字典，None 表示无状态
        """
        pass
    
    @hookspec
    def hook_set_plugin_state(self, workspace_id: int, state: Dict[str, Any]) -> None:
        """恢复插件在指定工作区的状态"""
        pass

    # ============ API 路由注册 ============
    
    @hookspec
    def hook_register_api_routes(self) -> List[Dict[str, Any]]:
        """注册插件自定义API路由
        
        约定返回格式：
            [
              {"router": APIRouter实例, "prefix": "/api/plugins/<name>", "tags": ["<name>"]},
              ...
            ]
        
        Returns:
            路由定义列表
        """
        pass
    
    # ============ 插件状态管理 ============
    
    @hookspec
    def hook_get_plugin_state(self, workspace_id: int) -> Dict[str, Any]:
        """获取插件状态（用于序列化到Chapter）
        
        Args:
            workspace_id: 工作区ID
            
        Returns:
            插件当前状态的字典
        """
        pass
    
    @hookspec
    def hook_set_plugin_state(self, workspace_id: int, state: Dict[str, Any]) -> None:
        """恢复插件状态（从Chapter反序列化）
        
        Args:
            workspace_id: 工作区ID
            state: 要恢复的状态
        """
        pass
    
    # ============ 插件配置 ============
    
    @hookspec
    def hook_get_config_schema(self) -> Dict[str, Any]:
        """获取插件配置Schema（JSON Schema格式）
        
        Returns:
            配置Schema，用于前端动态生成配置表单
        """
        pass
    
    @hookspec
    def hook_validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否合法
        
        Args:
            config: 配置字典
            
        Returns:
            是否合法
        """
        pass

