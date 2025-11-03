"""Chapter数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class ChapterStatus(str, enum.Enum):
    """章节状态"""
    PLANNING = "planning"      # 计划中
    GENERATING = "generating"  # 生成中
    VERIFYING = "verifying"    # 验证中
    IMPROVING = "improving"    # 改进中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


class Chapter(Base):
    """章节模型 - 不是简单的文字，包含生成时的完整状态快照"""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    
    # 章节信息
    chapter_number = Column(Integer, nullable=False, comment="章节号")
    title = Column(String(500), nullable=True, comment="章节标题")
    
    # 生成过程数据
    plan = Column(Text, nullable=True, comment="章节大纲/计划")
    content = Column(Text, nullable=True, comment="章节内容")
    
    # 验证结果
    verification_result = Column(JSON, nullable=True, comment="验证结果")
    verification_passed = Column(Integer, default=0, comment="验证是否通过 0=未验证 1=通过 -1=未通过")
    
    # 状态
    status = Column(Enum(ChapterStatus), default=ChapterStatus.PLANNING, comment="章节状态")
    
    # 插件状态快照 - 这一章生成完成时所有插件的状态
    plugin_snapshot = Column(JSON, default=dict, comment="插件状态快照")
    
    # 生成历史 - 记录每次improve的历史版本
    generation_history = Column(JSON, default=list, comment="生成历史记录")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关系
    workspace = relationship("Workspace", back_populates="chapters")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "chapter_number": self.chapter_number,
            "title": self.title,
            "plan": self.plan,
            "content": self.content,
            "verification_result": self.verification_result,
            "verification_passed": self.verification_passed,
            "status": self.status.value if self.status else None,
            "plugin_snapshot": self.plugin_snapshot,
            "generation_history": self.generation_history,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def add_history_entry(self, entry_type: str, data: dict):
        """添加历史记录"""
        if self.generation_history is None:
            self.generation_history = []
        
        self.generation_history.append({
            "type": entry_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        })

