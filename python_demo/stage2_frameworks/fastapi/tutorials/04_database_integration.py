"""
FastAPI 数据库集成示例

演示如何配置数据库连接、创建会话和使用依赖注入管理数据库会话。
本示例使用 SQLite 数据库，便于学习和测试。

运行方式:
    uvicorn 04_database_integration:app --reload

访问文档:
    http://127.0.0.1:8000/docs

注意: 首次运行会自动创建数据库和表
"""

from typing import Generator
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

# ============ 1. 数据库配置 ============

# SQLite 数据库 URL
# 使用相对路径创建数据库文件
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 创建数据库引擎
# connect_args={"check_same_thread": False} 是 SQLite 特有的配置
# 允许多线程访问（仅用于 SQLite）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit=False: 需要手动提交事务
# autoflush=False: 需要手动刷新
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# ============ 2. 数据库模型 ============

class UserDB(Base):
    """
    用户数据库模型
    
    这是 SQLAlchemy ORM 模型，定义数据库表结构
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


# 创建所有表
# 如果表已存在则不会重复创建
Base.metadata.create_all(bind=engine)


# ============ 3. Pydantic 模型（API 模型）============

class UserCreate(BaseModel):
    """创建用户的请求模型"""
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # 允许从 ORM 模型创建


class UserUpdate(BaseModel):
    """更新用户的请求模型"""
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


# ============ 4. 依赖注入 - 数据库会话 ============

def get_db() -> Generator[Session, None, None]:
    """
    数据库会话依赖
    
    这是一个生成器函数，用于创建和管理数据库会话
    - 每个请求创建一个新的会话
    - 请求结束后自动关闭会话
    - 使用 yield 确保会话正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ 5. 创建 FastAPI 应用 ============

app = FastAPI(
    title="数据库集成示例 API",
    description="演示 FastAPI 与 SQLAlchemy 的集成",
    version="1.0.0"
)


# ============ 6. API 端点 ============

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    
    db 参数通过依赖注入自动获取数据库会话
    """
    # 检查用户名是否已存在
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被使用"
        )
    
    # 创建新用户
    # 实际应用中应该对密码进行哈希处理
    db_user = UserDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=f"hashed_{user.password}",  # 简化示例，实际应使用 bcrypt
        is_active=True,
        created_at=datetime.now()
    )
    
    # 添加到数据库
    db.add(db_user)
    db.commit()  # 提交事务
    db.refresh(db_user)  # 刷新对象以获取数据库生成的值（如 ID）
    
    return db_user


@app.get("/users", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    
    支持分页
    """
    users = db.query(UserDB).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    通过 ID 获取用户
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    return user


@app.get("/users/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    通过用户名获取用户
    """
    user = db.query(UserDB).filter(UserDB.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户名 '{username}' 不存在"
        )
    
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    # 查找用户
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 检查用户名冲突
    if "username" in update_data:
        existing = db.query(UserDB).filter(
            UserDB.username == update_data["username"],
            UserDB.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 检查邮箱冲突
    if "email" in update_data:
        existing = db.query(UserDB).filter(
            UserDB.email == update_data["email"],
            UserDB.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 应用更新
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户
    """
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    db.delete(db_user)
    db.commit()
    
    return None


@app.get("/users/search/", response_model=list[UserResponse])
def search_users(
    q: str,
    db: Session = Depends(get_db)
):
    """
    搜索用户
    
    在用户名和全名中搜索
    """
    users = db.query(UserDB).filter(
        (UserDB.username.contains(q)) | (UserDB.full_name.contains(q))
    ).all()
    
    return users


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    获取统计信息
    """
    total_users = db.query(UserDB).count()
    active_users = db.query(UserDB).filter(UserDB.is_active == True).count()
    inactive_users = total_users - active_users
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users
    }


"""
学习要点:

1. 数据库配置
   - create_engine(): 创建数据库引擎
   - sessionmaker(): 创建会话工厂
   - declarative_base(): 创建 ORM 基类

2. SQLAlchemy ORM 模型
   - 继承 Base 类
   - __tablename__: 指定表名
   - Column: 定义列
   - 数据类型: Integer, String, Boolean, DateTime 等
   - 约束: primary_key, unique, index, nullable

3. 依赖注入
   - Depends() 用于注入依赖
   - get_db() 生成器函数管理会话生命周期
   - 每个请求获得独立的数据库会话
   - 自动处理会话关闭

4. 数据库操作
   - db.query(): 创建查询
   - .filter(): 添加过滤条件
   - .first(): 获取第一条记录
   - .all(): 获取所有记录
   - .offset() 和 .limit(): 分页
   - db.add(): 添加对象
   - db.commit(): 提交事务
   - db.refresh(): 刷新对象
   - db.delete(): 删除对象

5. 查询操作
   - 相等: UserDB.id == user_id
   - 包含: UserDB.username.contains(q)
   - 或条件: (条件1) | (条件2)
   - 与条件: (条件1) & (条件2)

6. 事务管理
   - 默认不自动提交
   - 需要显式调用 db.commit()
   - 发生错误时可以回滚

7. Pydantic 与 ORM 集成
   - from_attributes = True: 允许从 ORM 对象创建 Pydantic 模型
   - 自动转换 ORM 对象为 JSON

8. 最佳实践
   - 使用依赖注入管理数据库会话
   - 每个请求使用独立的会话
   - 请求结束后关闭会话
   - 使用索引提高查询性能
   - 对敏感数据（如密码）进行哈希处理

实践练习:
1. 添加更多字段到用户模型（如头像、电话号码）
2. 创建一个文章模型，与用户建立关系
3. 实现用户和文章的关联查询
4. 添加软删除功能（不真正删除，只标记为已删除）
5. 实现更复杂的搜索和过滤功能
6. 添加数据库迁移（使用 Alembic）

注意事项:
- 本示例使用 SQLite 便于学习，生产环境建议使用 PostgreSQL 或 MySQL
- 密码应该使用 bcrypt 等库进行哈希处理
- 考虑使用连接池优化性能
- 添加适当的错误处理和日志记录
"""
