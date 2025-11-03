#!/bin/bash

# Novel Studio 启动脚本

echo "🚀 启动 Novel Studio..."

# 检查后端依赖
if [ ! -d "backend/venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 检查环境变量
if [ ! -f "backend/.env" ]; then
    echo "⚠️  请先配置 backend/.env 文件"
    echo "   复制 backend/.env.example 并填入你的配置"
    exit 1
fi

# 启动后端
echo "🔧 启动后端服务..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Novel Studio 已启动!"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

