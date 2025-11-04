"""认证 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import bcrypt

from backend.database import get_db
from backend.models import SystemSettings
from backend.auth import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求"""
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"


class AuthCheckResponse(BaseModel):
    """认证检查响应"""
    requires_password: bool


@router.get("/check", response_model=AuthCheckResponse)
async def check_auth_requirement(db: AsyncSession = Depends(get_db)):
    """检查系统是否需要密码认证"""
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalar_one_or_none()
    
    return AuthCheckResponse(
        requires_password=bool(settings and settings.access_password)
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """登录 - 验证密码并返回 token"""
    # 获取系统设置
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalar_one_or_none()
    
    # 如果没有设置密码，不允许登录
    if not settings or not settings.access_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统未设置访问密码"
        )
    
    # 用 bcrypt 验证密码
    if not bcrypt.checkpw(
        request.password.encode('utf-8'),
        settings.access_password.encode('utf-8')
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )
    
    # 生成 token
    access_token = create_access_token(
        data={"authenticated": True}
    )
    
    return LoginResponse(access_token=access_token)

