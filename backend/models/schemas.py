"""Pydantic Schema定义"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ Workspace Schemas ============

class WorkspaceCreate(BaseModel):
    """创建工作区请求"""
    title: str = Field(..., min_length=1, max_length=500, description="小说标题")
    description: Optional[str] = Field(None, description="小说简介")
    genre: Optional[str] = Field(None, description="类型")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置")


class WorkspaceUpdate(BaseModel):
    """更新工作区请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    """工作区响应"""
    id: int
    title: str
    description: Optional[str]
    genre: Optional[str]
    tags: List[str]
    config: Dict[str, Any]
    plugin_states: Dict[str, Any]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# ============ Chapter Schemas ============

class ChapterResponse(BaseModel):
    """章节响应"""
    id: int
    workspace_id: int
    chapter_number: int
    title: Optional[str]
    plan: Optional[str]
    content: Optional[str]
    verification_result: Optional[Dict[str, Any]]
    verification_passed: int
    status: str
    plugin_snapshot: Dict[str, Any]
    generation_history: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    
    class Config:
        from_attributes = True


# ============ Generation Schemas ============

class PlanRequest(BaseModel):
    """生成大纲请求"""
    workspace_id: int
    chapter_number: int
    user_input: Optional[str] = Field(None, description="用户额外输入/修改意见")
    model: Optional[str] = Field(None, description="使用的模型，如gpt-4-turbo-preview")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外上下文")


class PlanResponse(BaseModel):
    """生成大纲响应"""
    chapter_id: int
    plan: str
    status: str


class PlanInteractiveRequest(BaseModel):
    """对话式Plan生成请求"""
    workspace_id: int
    chapter_number: int
    messages: List[Dict[str, Any]] = Field(..., description="对话历史")
    model: Optional[str] = Field(None, description="使用的模型")


class PlanInteractiveResponse(BaseModel):
    """对话式Plan生成响应"""
    messages: List[Dict[str, Any]] = Field(..., description="更新后的对话历史")
    plan: Optional[str] = Field(None, description="生成的大纲（完成时才有）")
    completed: bool = Field(..., description="是否完成大纲创建")
    chapter_id: Optional[int] = Field(None, description="章节ID（完成时才有）")


class GenerateRequest(BaseModel):
    """生成章节请求"""
    chapter_id: int
    regenerate: bool = Field(False, description="是否重新生成")
    model: Optional[str] = Field(None, description="使用的模型")


class GenerateResponse(BaseModel):
    """生成章节响应"""
    chapter_id: int
    content: str
    status: str


class VerifyRequest(BaseModel):
    """验证章节请求"""
    chapter_id: int
    model: Optional[str] = Field(None, description="使用的模型")


class VerifyResponse(BaseModel):
    """验证章节响应"""
    chapter_id: int
    passed: bool
    issues: List[Dict[str, Any]]
    suggestions: List[str]


class ImproveRequest(BaseModel):
    """改进章节请求"""
    chapter_id: int
    focus_issues: Optional[List[str]] = Field(None, description="重点关注的问题")
    model: Optional[str] = Field(None, description="使用的模型")


class ImproveResponse(BaseModel):
    """改进章节响应"""
    chapter_id: int
    improved_content: str
    status: str


# ============ Plugin Schemas ============

class PluginInfo(BaseModel):
    """插件信息"""
    name: str = Field(..., description="插件名称")
    description: str = Field(..., description="插件描述")
    version: str = Field(..., description="插件版本")
    author: str = Field(..., description="插件作者")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="配置Schema")


class PluginConfigUpdate(BaseModel):
    """插件配置更新请求"""
    plugins: Dict[str, Dict[str, Any]] = Field(..., description="插件配置字典")


class PluginToggleRequest(BaseModel):
    """插件启用/禁用请求"""
    enabled: bool = Field(..., description="是否启用")


# ============ System Settings Schemas ============

class SystemSettingsResponse(BaseModel):
    """系统设置响应 - 用于前端显示"""
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key")
    openai_base_url: Optional[str] = Field(None, description="OpenAI Base URL")
    openai_model: str = Field("gpt-4-turbo-preview", description="默认模型")
    access_password: Optional[str] = Field(None, description="访问密码")
    
    class Config:
        from_attributes = True


class SystemSettingsUpdate(BaseModel):
    """系统设置更新请求"""
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key")
    openai_base_url: Optional[str] = Field(None, description="OpenAI Base URL")
    openai_model: Optional[str] = Field(None, description="默认模型")
    access_password: Optional[str] = Field(None, description="访问密码，留空则不启用")


class SystemSettingsPublic(BaseModel):
    """系统设置公开信息 - 不包含敏感信息"""
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    has_password: bool = False  # 是否设置了访问密码
    has_api_key: bool = False  # 是否设置了 API Key

