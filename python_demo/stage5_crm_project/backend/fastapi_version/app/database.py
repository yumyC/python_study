"""
数据库配置和连接管理

这个模块负责：
1. 数据库连接配置
2. SQLAlchemy 引擎和会话管理
3. 数据库初始化
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./crm_fastapi.db"  # 默认使用 SQLite 数据库
)

# 创建数据库引擎
# 对于 SQLite，我们需要一些特殊配置
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 特殊配置
        poolclass=StaticPool,  # 使用静态连接池
        echo=True  # 开发环境下打印 SQL 语句
    )
else:
    # PostgreSQL 或其他数据库
    engine = create_engine(DATABASE_URL, echo=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    
    这个函数用于 FastAPI 的依赖注入系统，
    确保每个请求都有独立的数据库会话，
    并在请求结束后正确关闭会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    创建所有数据表
    
    这个函数会根据模型定义创建数据库表。
    通常在应用启动时调用。
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    删除所有数据表
    
    这个函数主要用于开发和测试环境，
    可以重置数据库结构。
    """
    Base.metadata.drop_all(bind=engine)