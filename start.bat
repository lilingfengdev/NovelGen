@echo off
chcp 65001 >nul
echo 🚀 启动 Novel Studio...
echo.

REM 检查后端依赖
if not exist "backend\venv" (
    echo 📦 创建 Python 虚拟环境...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo 📦 安装前端依赖...
    cd frontend
    call npm install
    cd ..
)

REM 检查环境变量
if not exist "backend\.env" (
    echo ⚠️  请先配置 backend\.env 文件
    echo    复制 backend\.env.example 并填入你的配置
    pause
    exit /b 1
)

REM 启动后端
echo 🔧 启动后端服务...
cd backend
start "NovelGen Backend" cmd /k "venv\Scripts\activate && python main.py"
cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🎨 启动前端服务...
cd frontend
start "NovelGen Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ✅ Novel Studio 已启动!
echo    前端: http://localhost:5173
echo    后端: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo.
pause

