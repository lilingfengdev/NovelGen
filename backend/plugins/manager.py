"""插件管理器"""
import pluggy
import importlib
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.plugins.hookspec import NovelGenHookSpec

hookimpl = pluggy.HookimplMarker("novelgen")


class PluginManager:
    """插件管理器 - 负责加载、注册和调用插件"""
    
    def __init__(self):
        self.pm = pluggy.PluginManager("novelgen")
        self.pm.add_hookspecs(NovelGenHookSpec)
        self._plugins: Dict[str, Any] = {}
        self._workspace_configs: Dict[int, Dict[str, Any]] = {}  # 工作空间配置缓存
        
    def load_plugins(self, plugin_dir: Optional[str] = None):
        """加载插件
        
        Args:
            plugin_dir: 插件目录路径，默认为 backend/plugins/implementations
        """
        if plugin_dir is None:
            plugin_dir = os.path.join(os.path.dirname(__file__), "implementations")
        
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            plugin_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ 创建插件目录: {plugin_dir}")
            return
        
        # 扫描插件目录
        for file in plugin_path.glob("*.py"):
            if file.name.startswith("_"):
                continue
                
            module_name = f"backend.plugins.implementations.{file.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # 查找实现了插件接口的类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, '__dict__'):
                        # 检查是否有 hookimpl 装饰的方法
                        if any(hasattr(getattr(attr, method), 'novelgen_impl') 
                               for method in dir(attr) if not method.startswith('_')):
                            plugin_instance = attr()
                            self.pm.register(plugin_instance, name=attr_name)
                            self._plugins[attr_name] = plugin_instance
                            print(f"✓ 加载插件: {attr_name}")
            except Exception as e:
                print(f"✗ 加载插件失败 {file.name}: {e}")
    
    def get_plugins(self) -> Dict[str, Any]:
        """获取所有已加载的插件"""
        return self._plugins
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取单个插件的详细信息
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件信息字典，包含name, description, version, config_schema等
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return None
        
        # 从插件类获取元数据
        metadata = {
            "name": getattr(plugin, "name", plugin_name),
            "description": getattr(plugin, "description", "无描述"),
            "version": getattr(plugin, "version", "1.0.0"),
            "author": getattr(plugin, "author", "Unknown"),
        }
        
        # 获取配置schema
        config_schema = self.call_hook_first(
            "hook_get_config_schema",
        )
        if config_schema:
            metadata["config_schema"] = config_schema
        
        return metadata
    
    def get_plugins_list(self) -> List[Dict[str, Any]]:
        """获取所有插件的信息列表
        
        Returns:
            插件信息列表
        """
        plugins_info = []
        for plugin_name in self._plugins.keys():
            info = self.get_plugin_info(plugin_name)
            if info:
                plugins_info.append(info)
        return plugins_info
    
    def set_workspace_config(self, workspace_id: int, config: Dict[str, Any]):
        """设置工作空间的插件配置
        
        Args:
            workspace_id: 工作空间ID
            config: 配置字典
        """
        self._workspace_configs[workspace_id] = config
    
    def get_workspace_config(self, workspace_id: int) -> Dict[str, Any]:
        """获取工作空间的插件配置
        
        Args:
            workspace_id: 工作空间ID
            
        Returns:
            配置字典
        """
        return self._workspace_configs.get(workspace_id, {})
    
    def is_plugin_enabled(self, workspace_id: int, plugin_name: str) -> bool:
        """检查插件是否在指定工作空间中启用
        
        Args:
            workspace_id: 工作空间ID
            plugin_name: 插件名称
            
        Returns:
            是否启用
        """
        config = self.get_workspace_config(workspace_id)
        plugin_config = config.get(plugin_name, {})
        return plugin_config.get("enabled", True)  # 默认启用
    
    def call_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """调用Hook并收集所有插件的返回值
        
        Args:
            hook_name: Hook名称
            **kwargs: Hook参数
            
        Returns:
            所有插件返回值的列表
        """
        hook = getattr(self.pm.hook, hook_name, None)
        if hook is None:
            return []
        
        # 检查是否有workspace_id参数，如果有则过滤禁用的插件
        workspace_id = kwargs.get('context', {}).get('workspace_id') if 'context' in kwargs else None
        
        results = hook(**kwargs)
        
        # 如果有workspace_id，过滤掉被禁用的插件返回值
        if workspace_id is not None:
            filtered_results = []
            for plugin_name, result in zip(self._plugins.keys(), results):
                if self.is_plugin_enabled(workspace_id, plugin_name):
                    filtered_results.append(result)
            results = filtered_results
        
        # 过滤掉None值
        return [r for r in results if r is not None]
    
    def call_hook_first(self, hook_name: str, **kwargs) -> Optional[Any]:
        """调用Hook并返回第一个非None结果
        
        Args:
            hook_name: Hook名称
            **kwargs: Hook参数
            
        Returns:
            第一个非None的返回值
        """
        results = self.call_hook(hook_name, **kwargs)
        return results[0] if results else None
    
    def merge_prompts(self, stage: str, context: Dict[str, Any]) -> Dict[str, str]:
        """合并所有插件注入的提示词
        
        Args:
            stage: 当前阶段
            context: 上下文信息
            
        Returns:
            {"system": "...", "user": "..."}
        """
        system_prompts = self.call_hook("hook_inject_system_prompt", stage=stage, context=context)
        user_prompts = self.call_hook("hook_inject_user_prompt", stage=stage, context=context)
        
        return {
            "system": "\n\n".join(system_prompts) if system_prompts else "",
            "user": "\n\n".join(user_prompts) if user_prompts else ""
        }
    
    def collect_tools(self, stage: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """收集所有插件注入的工具
        
        Args:
            stage: 当前阶段
            context: 上下文信息
            
        Returns:
            工具列表
        """
        tools_lists = self.call_hook("hook_inject_tools", stage=stage, context=context)
        # 扁平化工具列表
        all_tools = []
        for tools in tools_lists:
            if isinstance(tools, list):
                all_tools.extend(tools)
        return all_tools
    
    def collect_api_routers(self) -> List[Dict[str, Any]]:
        """收集所有插件注册的API路由
        
        Returns:
            路由定义列表，每项包含：{"router": APIRouter, "prefix": str, "tags": List[str]}
        """
        router_defs = self.call_hook("hook_register_api_routes")
        all_routes: List[Dict[str, Any]] = []
        for item in router_defs:
            if isinstance(item, list):
                for r in item:
                    if isinstance(r, dict) and "router" in r:
                        all_routes.append(r)
            elif isinstance(item, dict) and "router" in item:
                all_routes.append(item)
        return all_routes
    
    def collect_plugin_states(self, workspace_id: int) -> Dict[str, Any]:
        """收集所有插件的状态（用于保存到Chapter）
        
        Args:
            workspace_id: 工作区ID
            
        Returns:
            {"plugin_name": state_dict, ...}
        """
        states = {}
        for plugin_name, plugin in self._plugins.items():
            state = self.call_hook_first("hook_get_plugin_state", workspace_id=workspace_id)
            if state:
                states[plugin_name] = state
        return states
    
    def restore_plugin_states(self, workspace_id: int, states: Dict[str, Any]):
        """恢复所有插件的状态（从Chapter加载）
        
        Args:
            workspace_id: 工作区ID
            states: 状态字典
        """
        for plugin_name, state in states.items():
            if plugin_name in self._plugins:
                self.call_hook("hook_set_plugin_state", workspace_id=workspace_id, state=state)


# 全局插件管理器实例
plugin_manager = PluginManager()

