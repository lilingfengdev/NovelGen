"""插件API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.schemas import PluginInfo, PluginConfigUpdate, PluginToggleRequest
from backend.plugins.manager import plugin_manager
from backend.services.workspace_service import WorkspaceService

router = APIRouter()


@router.get("/", response_model=List[PluginInfo])
async def list_plugins():
    """获取所有已加载插件的信息"""
    plugins_list = plugin_manager.get_plugins_list()
    return plugins_list


@router.get("/{workspace_id}/config")
async def get_workspace_plugin_config(
    workspace_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取工作空间的插件配置"""
    workspace = await WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # 从workspace.config中获取plugins配置
    plugins_config = workspace.config.get("plugins", {})
    
    # 同步到插件管理器缓存
    plugin_manager.set_workspace_config(workspace_id, plugins_config)
    
    return {"plugins": plugins_config}


@router.put("/{workspace_id}/config")
async def update_workspace_plugin_config(
    workspace_id: int,
    data: PluginConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新工作空间的插件配置"""
    workspace = await WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # 验证插件配置
    for plugin_name, plugin_config in data.plugins.items():
        plugin = plugin_manager.get_plugins().get(plugin_name)
        if not plugin:
            raise HTTPException(
                status_code=400, 
                detail=f"Plugin '{plugin_name}' not found"
            )
        
        # 调用插件的验证hook
        is_valid = plugin_manager.call_hook_first(
            "hook_validate_config",
            config=plugin_config
        )
        if is_valid is False:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid configuration for plugin '{plugin_name}'"
            )
    
    # 更新workspace.config
    new_config = workspace.config.copy()
    new_config["plugins"] = data.plugins
    
    # 保存到数据库
    from backend.models.schemas import WorkspaceUpdate
    updated_workspace = await WorkspaceService.update_workspace(
        db, 
        workspace_id, 
        WorkspaceUpdate(config=new_config)
    )
    
    # 更新插件管理器缓存
    plugin_manager.set_workspace_config(workspace_id, data.plugins)
    
    return {"plugins": data.plugins}


@router.put("/{workspace_id}/{plugin_name}/toggle")
async def toggle_plugin(
    workspace_id: int,
    plugin_name: str,
    data: PluginToggleRequest,
    db: AsyncSession = Depends(get_db)
):
    """启用/禁用特定插件"""
    workspace = await WorkspaceService.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # 检查插件是否存在
    if plugin_name not in plugin_manager.get_plugins():
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    
    # 更新配置
    new_config = workspace.config.copy()
    plugins_config = new_config.get("plugins", {})
    
    if plugin_name not in plugins_config:
        plugins_config[plugin_name] = {}
    
    plugins_config[plugin_name]["enabled"] = data.enabled
    new_config["plugins"] = plugins_config
    
    # 保存到数据库
    from backend.models.schemas import WorkspaceUpdate
    await WorkspaceService.update_workspace(
        db,
        workspace_id,
        WorkspaceUpdate(config=new_config)
    )
    
    # 更新插件管理器缓存
    plugin_manager.set_workspace_config(workspace_id, plugins_config)
    
    return {
        "plugin_name": plugin_name,
        "enabled": data.enabled
    }

