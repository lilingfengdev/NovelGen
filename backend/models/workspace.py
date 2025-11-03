"""Workspace数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship

from backend.database import Base


class Workspace(Base):
    """工作区模型 - 代表一部小说"""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="小说标题")
    description = Column(Text, nullable=True, comment="小说简介")
    
    # 元信息
    genre = Column(String(100), nullable=True, comment="类型")
    tags = Column(JSON, default=list, comment="标签列表")
    
    # 配置信息 - JSON格式存储插件配置
    config = Column(JSON, default=dict, comment="工作区配置")
    
    # 插件状态 - 当前工作区级别的插件状态
    plugin_states = Column(JSON, default=dict, comment="插件状态快照")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    chapters = relationship("Chapter", back_populates="workspace", cascade="all, delete-orphan")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "genre": self.genre,
            "tags": self.tags,
            "config": self.config,
            "plugin_states": self.plugin_states,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

