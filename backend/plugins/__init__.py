"""插件系统模块"""
from backend.plugins.hookspec import NovelGenHookSpec, hookspec
from backend.plugins.manager import PluginManager, plugin_manager, hookimpl

__all__ = ["NovelGenHookSpec", "hookspec", "PluginManager", "plugin_manager", "hookimpl"]
