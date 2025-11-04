"""系统设置模型"""
from sqlalchemy import Column, String, Integer
from backend.database import Base


class SystemSettings(Base):
    """系统设置表 - 单例模式，只有一条记录"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, default=1)  # 固定ID=1
    
    # AI模型配置
    openai_api_key = Column(String, nullable=True)
    openai_base_url = Column(String, nullable=True)
    openai_model = Column(String, default="gpt-4-turbo-preview")
    
    # 安全配置
    access_password = Column(String, nullable=True)  # 访问密码，为空表示不启用

