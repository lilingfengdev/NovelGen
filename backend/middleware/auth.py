"""认证中间件"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import select
from backend.auth import verify_token
from backend.models import SystemSettings
from backend.database import AsyncSessionLocal


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件 - 检查访问密码"""
    
    # 不需要认证的路径
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",  # 登录接口
        "/api/auth/check",  # 检查是否需要密码
    }
    
    async def dispatch(self, request: Request, call_next):
        """处理每个请求"""
        path = request.url.path
        
        # 跳过 OPTIONS 请求（CORS 预检）
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # 跳过公开路径
        if path in self.PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)
        
        # 检查系统是否设置了访问密码
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
            settings = result.scalar_one_or_none()
            
            # 如果没有设置密码，直接放行
            if not settings or not settings.access_password:
                return await call_next(request)
        
        # 需要验证 token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "需要登录"},
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # 验证 token
            payload = verify_token(token)
            # 可以把用户信息附加到 request.state
            request.state.authenticated = True
        except HTTPException:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "认证令牌无效或已过期"},
            )
        
        return await call_next(request)

