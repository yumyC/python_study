"""
FastAPI ORM 模型和关系示例

演示如何使用 SQLAlchemy 定义复杂的数据模型、建立表关系、
以及执行关联查询。

运行方式:
    uvicorn 05_orm_models:app --reload

访问文档:
    http://127.0.0.1:8000/docs

本示例创建一个简单的博客系统，包含用户、文章、分类和标签。
"""

from typing import Generator, List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr

# ============ 1. 数据库配置 ============

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============ 2. 多对多关系的关联表 ============

# 文章-标签关联表（多对多）
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


# ============ 3. ORM 模型定义 ============

class UserDB(Base):
    """
    用户模型
    
    一个用户可以有多篇文章（一对多关系）
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系：一个用户有多篇文章
    # back_populates 创建双向关系
    # cascade 定义级联操作
    posts = relationship(
        "PostDB",
        back_populates="author",
        cascade="all, delete-orphan"
    )


class CategoryDB(Base):
    """
    分类模型
    
    一个分类可以有多篇文章（一对多关系）
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系：一个分类有多篇文章
    posts = relationship("PostDB", back_populates="category")


class TagDB(Base):
    """
    标签模型
    
    标签和文章是多对多关系
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系：多对多关系通过关联表
    posts = relationship(
        "PostDB",
        secondary=post_tags,
        back_populates="tags"
    )


class PostDB(Base):
    """
    文章模型
    
    - 多对一关系：多篇文章属于一个用户
    - 多对一关系：多篇文章属于一个分类
    - 多对多关系：一篇文章可以有多个标签
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    is_published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 外键
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # 关系
    author = relationship("UserDB", back_populates="posts")
    category = relationship("CategoryDB", back_populates="posts")
    tags = relationship(
        "TagDB",
        secondary=post_tags,
        back_populates="posts"
    )


# 创建所有表
Base.metadata.create_all(bind=engine)


# ============ 4. Pydantic 模型 ============

# 标签模型
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 分类模型
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 用户模型
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# 文章模型
class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    is_published: bool = False
    category_id: Optional[int] = None


class PostCreate(PostBase):
    tag_ids: List[int] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class Post(PostBase):
    id: int
    author_id: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    author: User
    category: Optional[Category] = None
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True


# ============ 5. 依赖注入 ============

def get_db() -> Generator[Session, None, None]:
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ 6. FastAPI 应用 ============

app = FastAPI(
    title="博客系统 API",
    description="演示 ORM 模型和关系的完整示例",
    version="1.0.0"
)


# ============ 7. 用户端点 ============

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    # 检查用户名
    if db.query(UserDB).filter(UserDB.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    db_user = UserDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=f"hashed_{user.password}"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户"""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@app.get("/users/{user_id}/posts", response_model=List[Post])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的所有文章
    
    演示一对多关系查询
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user.posts


# ============ 8. 分类端点 ============

@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建分类"""
    if db.query(CategoryDB).filter(CategoryDB.name == category.name).first():
        raise HTTPException(status_code=400, detail="分类已存在")
    
    db_category = CategoryDB(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get("/categories", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    return db.query(CategoryDB).all()


# ============ 9. 标签端点 ============

@app.post("/tags", response_model=Tag, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    if db.query(TagDB).filter(TagDB.name == tag.name).first():
        raise HTTPException(status_code=400, detail="标签已存在")
    
    db_tag = TagDB(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get("/tags", response_model=List[Tag])
def get_tags(db: Session = Depends(get_db)):
    """获取所有标签"""
    return db.query(TagDB).all()


# ============ 10. 文章端点 ============

@app.post("/users/{user_id}/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(
    user_id: int,
    post: PostCreate,
    db: Session = Depends(get_db)
):
    """
    创建文章
    
    演示如何创建带关系的对象
    """
    # 验证用户存在
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证分类存在
    if post.category_id:
        category = db.query(CategoryDB).filter(CategoryDB.id == post.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
    
    # 创建文章
    db_post = PostDB(
        title=post.title,
        content=post.content,
        summary=post.summary,
        is_published=post.is_published,
        author_id=user_id,
        category_id=post.category_id
    )
    
    # 添加标签（多对多关系）
    if post.tag_ids:
        tags = db.query(TagDB).filter(TagDB.id.in_(post.tag_ids)).all()
        if len(tags) != len(post.tag_ids):
            raise HTTPException(status_code=404, detail="部分标签不存在")
        db_post.tags = tags
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts", response_model=List[Post])
def get_posts(
    skip: int = 0,
    limit: int = 10,
    published_only: bool = False,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取文章列表
    
    支持多种过滤条件
    """
    query = db.query(PostDB)
    
    # 过滤已发布
    if published_only:
        query = query.filter(PostDB.is_published == True)
    
    # 按分类过滤
    if category_id:
        query = query.filter(PostDB.category_id == category_id)
    
    # 按标签过滤
    if tag_id:
        query = query.join(PostDB.tags).filter(TagDB.id == tag_id)
    
    posts = query.offset(skip).limit(limit).all()
    return posts


@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    获取文章详情
    
    自动加载关联的作者、分类和标签
    """
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加浏览次数
    post.view_count += 1
    db.commit()
    
    return post


@app.put("/posts/{post_id}", response_model=Post)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db)
):
    """更新文章"""
    db_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    update_data = post_update.model_dump(exclude_unset=True)
    
    # 处理标签更新
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(TagDB).filter(TagDB.id.in_(tag_ids)).all()
            db_post.tags = tags
    
    # 更新其他字段
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db_post.updated_at = datetime.now()
    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """删除文章"""
    db_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(db_post)
    db.commit()
    return None


"""
学习要点:

1. 表关系类型
   - 一对多 (One-to-Many): 用户 -> 文章
   - 多对一 (Many-to-One): 文章 -> 用户
   - 多对多 (Many-to-Many): 文章 <-> 标签

2. 外键 (Foreign Key)
   - ForeignKey("表名.列名") 定义外键
   - 建立表之间的引用关系
   - 确保数据完整性

3. 关系 (Relationship)
   - relationship() 定义 ORM 级别的关系
   - back_populates: 创建双向关系
   - cascade: 定义级联操作
   - secondary: 多对多关系的关联表

4. 关联表 (Association Table)
   - 用于多对多关系
   - 使用 Table() 定义
   - 包含两个外键

5. 级联操作 (Cascade)
   - all: 所有操作都级联
   - delete: 删除时级联
   - delete-orphan: 删除孤儿对象
   - save-update: 保存更新时级联

6. 关系查询
   - 通过关系属性访问: user.posts
   - join() 连接查询
   - filter() 过滤关联数据
   - 自动加载关联对象

7. 多对多关系操作
   - 添加: post.tags = [tag1, tag2]
   - 追加: post.tags.append(tag)
   - 删除: post.tags.remove(tag)
   - 清空: post.tags = []

8. 查询优化
   - 使用索引提高查询性能
   - 避免 N+1 查询问题
   - 使用 joinedload 预加载关系
   - 合理使用分页

实践练习:
1. 添加评论模型，建立文章和评论的一对多关系
2. 实现用户关注功能（用户之间的多对多关系）
3. 添加文章点赞功能
4. 实现文章收藏功能
5. 创建文章草稿箱功能
6. 实现文章版本历史
7. 添加文章搜索功能（全文搜索）

注意事项:
- 合理设计表关系，避免过度复杂
- 注意循环引用问题
- 使用索引优化查询性能
- 考虑使用软删除而不是物理删除
- 添加适当的数据验证
- 处理并发更新问题
"""
