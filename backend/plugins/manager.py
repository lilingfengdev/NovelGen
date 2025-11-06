"""插件管理器 - 融合 Pluggy + AgentMiddleware"""
import pluggy
import importlib
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain.agents.middleware import AgentMiddleware

from backend.plugins.hookspec import NovelGenHookSpec

hookimpl = pluggy.HookimplMarker("novelgen")


class PluginManager:
    """插件管理器 - 融合 Pluggy + AgentMiddleware
    
    架构：
    - 使用 Pluggy 管理插件发现、配置、生命周期
    - 使用 AgentMiddleware 进行运行时集成
    """
    
    def __init__(self):
        # Pluggy 管理器
        self.pm = pluggy.PluginManager("novelgen")
        self.pm.add_hookspecs(NovelGenHookSpec)
        
        # 插件实例缓存
        self._plugins: Dict[str, Any] = {}
        
        # 工作空间配置缓存
        self._workspace_configs: Dict[int, Dict[str, Any]] = {}
        
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
                        if any(hasattr(getattr(attr, method, None), 'novelgen_impl') 
                               for method in dir(attr) if not method.startswith('_')):
                            plugin_instance = attr()
                            self.pm.register(plugin_instance, name=attr_name)
                            self._plugins[attr_name] = plugin_instance
                            print(f"✓ 加载插件: {attr_name}")
            except Exception as e:
                print(f"✗ 加载插件失败 {file.name}: {e}")
                import traceback
                traceback.print_exc()
    
    def get_plugins(self) -> Dict[str, Any]:
        """获取所有已加载的插件"""
        return self._plugins
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取单个插件的详细信息
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件信息字典
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return None
        
        # 调用 hook_get_metadata
        try:
            metadata_results = self.pm.hook.hook_get_metadata()
            # 找到对应插件的 metadata
            for result in metadata_results:
                if result and result.get("name") == plugin_name:
                    return result
        except Exception:
            pass
        
        # 回退：从插件属性获取
        return {
            "name": getattr(plugin, "name", plugin_name),
            "description": getattr(plugin, "description", "无描述"),
            "version": getattr(plugin, "version", "1.0.0"),
            "author": getattr(plugin, "author", "Unknown"),
            "config_schema": {}
        }
    
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
    
    # ============ 运行时集成 - AgentMiddleware ============
    
    def get_middlewares(self, workspace_id: Optional[int] = None) -> List[AgentMiddleware]:
        """获取所有插件的 AgentMiddleware 实例
        
        Args:
            workspace_id: 工作空间ID，如果提供则过滤禁用的插件
            
        Returns:
            AgentMiddleware 列表
        """
        middlewares = []
        middleware_results = self.pm.hook.hook_get_middleware()
        
        for plugin_name, middleware in zip(self._plugins.keys(), middleware_results):
            if middleware is None:
                continue
            
            # 检查插件是否启用
            if workspace_id is not None and not self.is_plugin_enabled(workspace_id, plugin_name):
                continue
            
            middlewares.append(middleware)
        
        return middlewares
    
    # ============ 扩展功能 ============
    
    def collect_api_routers(self) -> List[Dict[str, Any]]:
        """收集所有插件注册的 API 路由
        
        Returns:
            路由定义列表
        """
        router_defs = self.pm.hook.hook_register_api_routes()
        all_routes: List[Dict[str, Any]] = []
        
        for item in router_defs:
            if isinstance(item, list):
                for r in item:
                    if isinstance(r, dict) and "router" in r:
                        all_routes.append(r)
            elif isinstance(item, dict) and "router" in item:
                all_routes.append(item)
        
        return all_routes
    
    def extend_create_plan_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """收集所有插件扩展的 create_plan 参数
        
        Args:
            context: 上下文信息
            
        Returns:
            合并后的参数定义
        """
        all_params = {}
        param_defs = self.pm.hook.hook_extend_create_plan_params(context=context)
        
        for params in param_defs:
            if isinstance(params, dict):
                all_params.update(params)
        
        return all_params
    
    def call_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """调用 Hook 并收集所有插件的返回值
        
        Args:
            hook_name: Hook名称
            **kwargs: Hook参数
            
        Returns:
            所有插件返回值的列表
        """
        hook = getattr(self.pm.hook, hook_name, None)
        if hook is None:
            return []
        
        results = hook(**kwargs)
        return [r for r in results if r is not None]
    
    def call_hook_first(self, hook_name: str, **kwargs) -> Optional[Any]:
        """调用 Hook 并返回第一个非 None 结果
        
        Args:
            hook_name: Hook名称
            **kwargs: Hook参数
            
        Returns:
            第一个非None的返回值
        """
        results = self.call_hook(hook_name, **kwargs)
        return results[0] if results else None


# 全局插件管理器实例
plugin_manager = PluginManager()

