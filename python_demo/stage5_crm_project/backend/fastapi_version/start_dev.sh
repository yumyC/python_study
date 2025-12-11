#!/bin/bash
# 开发环境启动脚本

set -e

echo "🚀 启动 CRM 系统开发环境..."

# 检查是否存在 .env 文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置数据库和 Redis 连接信息"
fi

# 启动依赖服务
echo "🐳 启动 Redis 和数据库服务..."
docker-compose -f docker-compose.dev.yml up -d redis

# 等待 Redis 启动
echo "⏳ 等待 Redis 启动..."
sleep 5

# 检查 Redis 连接
if ! docker-compose -f docker-compose.dev.yml exec redis redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis 连接失败，请检查 Docker 服务"
    exit 1
fi

echo "✅ Redis 服务已启动"

# 安装依赖（如果需要）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
fi

echo "📦 激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库
echo "🗄️ 初始化数据库..."
python -c "from app.database import create_tables; create_tables()"
python -c "from app.init_db import init_database; init_database()"

echo "🎉 开发环境准备完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 启动 FastAPI 服务器: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "2. 启动 Celery Worker: python celery_worker.py"
echo "3. 访问 API 文档: http://localhost:8000/docs"
echo "4. Redis 管理界面: http://localhost:8081"
echo ""
echo "🔧 有用的命令："
echo "- 查看 Redis 状态: docker-compose -f docker-compose.dev.yml ps"
echo "- 停止服务: docker-compose -f docker-compose.dev.yml down"
echo "- 查看日志: docker-compose -f docker-compose.dev.yml logs -f"