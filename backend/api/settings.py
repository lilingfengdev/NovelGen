"""系统设置API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from backend.database import get_db
from backend.models import SystemSettings
from backend.models.schemas import (
    SystemSettingsResponse,
    SystemSettingsUpdate,
    SystemSettingsPublic
)

router = APIRouter()


async def get_or_create_settings(db: AsyncSession) -> SystemSettings:
    """获取或创建系统设置（单例模式）"""
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        # 首次运行，创建默认设置
        settings = SystemSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


@router.get("/public", response_model=SystemSettingsPublic)
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    """获取公开的系统设置信息（不包含敏感数据）"""
    settings = await get_or_create_settings(db)
    
    return SystemSettingsPublic(
        openai_base_url=settings.openai_base_url,
        openai_model=settings.openai_model or "gpt-4-turbo-preview",
        has_password=bool(settings.access_password),
        has_api_key=bool(settings.openai_api_key)
    )


@router.get("", response_model=SystemSettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """获取系统设置（不返回敏感数据）
    
    敏感数据（API Key、密码）会被掩码
    """
    settings = await get_or_create_settings(db)
    
    # 返回设置但隐藏敏感信息
    return SystemSettingsResponse(
        openai_api_key=None,  # 不返回API Key
        openai_base_url=settings.openai_base_url,
        openai_model=settings.openai_model or "gpt-4-turbo-preview",
        access_password=None  # 不返回密码
    )


@router.put("", response_model=SystemSettingsResponse)
async def update_settings(
    update_data: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新系统设置
    
    注意：实际使用时应该加上权限验证
    """
    settings = await get_or_create_settings(db)
    
    # 只更新提供的字段
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # 如果有密码字段，需要加密
    if 'access_password' in update_dict:
        password = update_dict['access_password']
        if password:
            # 用 bcrypt 加密密码
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_dict['access_password'] = hashed.decode('utf-8')
        # 如果密码为空字符串，存 None
        else:
            update_dict['access_password'] = None
    
    for key, value in update_dict.items():
        setattr(settings, key, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return SystemSettingsResponse.model_validate(settings)


@router.post("/reset")
async def reset_settings(db: AsyncSession = Depends(get_db)):
    """重置系统设置到默认值
    
    注意：实际使用时应该加上权限验证
    """
    settings = await get_or_create_settings(db)
    
    # 重置到默认值
    settings.openai_api_key = None
    settings.openai_base_url = None
    settings.openai_model = "gpt-4-turbo-preview"
    settings.access_password = None
    
    await db.commit()
    await db.refresh(settings)
    
    return {"message": "设置已重置"}

