"""配置管理"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, Union


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI配置
    openai_api_key: str
    openai_base_url: Optional[str] = None  # 自定义API endpoint，支持代理/Azure/本地模型
    openai_model: str = "gpt-4-turbo-preview"  # 默认模型，可被前端覆盖
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./novelgen.db"
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS配置 - 可以是逗号分隔的字符串或JSON数组
    cors_origins: Union[list[str], str] = "http://localhost:5173,http://localhost:3000"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS配置 - 支持逗号分隔字符串或JSON数组"""
        if isinstance(v, str):
            # 如果是逗号分隔的字符串，split 并清理
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

