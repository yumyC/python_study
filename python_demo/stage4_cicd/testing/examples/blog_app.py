"""
简单的博客应用

这是一个用于演示测试的简单博客应用，包含：
- 用户管理
- 文章管理
- 评论功能
"""

from datetime import datetime
from typing import List, Optional
import hashlib


class User:
    """用户类"""
    
    def __init__(self, user_id: int, username: str, email: str, password_hash: str):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == self._hash_password(password)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }


class Post:
    """文章类"""
    
    def __init__(self, post_id: int, author_id: int, title: str, content: str):
        self.id = post_id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.published = False
    
    def publish(self):
        """发布文章"""
        self.published = True
    
    def update(self, title: Optional[str] = None, content: Optional[str] = None):
        """更新文章"""
        if title:
            self.title = title
        if content:
            self.content = content
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "published": self.published,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Comment:
    """评论类"""
    
    def __init__(self, comment_id: int, post_id: int, author_id: int, content: str):
        self.id = comment_id
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "post_id": self.post_id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }


class BlogDatabase:
    """博客数据库（内存实现）"""
    
    def __init__(self):
        self.users = {}
        self.posts = {}
        self.comments = {}
        self._user_id_counter = 1
        self._post_id_counter = 1
        self._comment_id_counter = 1
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """创建用户"""
        password_hash = User._hash_password(password)
        user = User(self._user_id_counter, username, email, password_hash)
        self.users[user.id] = user
        self._user_id_counter += 1
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def create_post(self, author_id: int, title: str, content: str) -> Optional[Post]:
        """创建文章"""
        if author_id not in self.users:
            return None
        
        post = Post(self._post_id_counter, author_id, title, content)
        self.posts[post.id] = post
        self._post_id_counter += 1
        return post
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """根据 ID 获取文章"""
        return self.posts.get(post_id)
    
    def get_posts_by_author(self, author_id: int) -> List[Post]:
        """获取作者的所有文章"""
        return [post for post in self.posts.values() if post.author_id == author_id]
    
    def get_published_posts(self) -> List[Post]:
        """获取所有已发布的文章"""
        return [post for post in self.posts.values() if post.published]
    
    def delete_post(self, post_id: int) -> bool:
        """删除文章"""
        if post_id in self.posts:
            del self.posts[post_id]
            # 同时删除相关评论
            self.comments = {
                cid: comment for cid, comment in self.comments.items()
                if comment.post_id != post_id
            }
            return True
        return False
    
    def create_comment(self, post_id: int, author_id: int, content: str) -> Optional[Comment]:
        """创建评论"""
        if post_id not in self.posts or author_id not in self.users:
            return None
        
        comment = Comment(self._comment_id_counter, post_id, author_id, content)
        self.comments[comment.id] = comment
        self._comment_id_counter += 1
        return comment
    
    def get_comments_by_post(self, post_id: int) -> List[Comment]:
        """获取文章的所有评论"""
        return [comment for comment in self.comments.values() if comment.post_id == post_id]


class BlogService:
    """博客服务"""
    
    def __init__(self, database: BlogDatabase):
        self.db = database
    
    def register_user(self, username: str, email: str, password: str) -> dict:
        """注册用户"""
        # 验证用户名
        if len(username) < 3:
            raise ValueError("用户名至少需要 3 个字符")
        
        # 检查用户名是否已存在
        if self.db.get_user_by_username(username):
            raise ValueError(f"用户名 {username} 已存在")
        
        # 验证邮箱
        if "@" not in email:
            raise ValueError("邮箱格式无效")
        
        # 验证密码
        if len(password) < 6:
            raise ValueError("密码至少需要 6 个字符")
        
        # 创建用户
        user = self.db.create_user(username, email, password)
        return user.to_dict()
    
    def login(self, username: str, password: str) -> Optional[dict]:
        """用户登录"""
        user = self.db.get_user_by_username(username)
        if user and user.check_password(password):
            return user.to_dict()
        return None
    
    def create_post(self, author_id: int, title: str, content: str) -> dict:
        """创建文章"""
        # 验证标题
        if not title or len(title) < 5:
            raise ValueError("标题至少需要 5 个字符")
        
        # 验证内容
        if not content or len(content) < 10:
            raise ValueError("内容至少需要 10 个字符")
        
        # 创建文章
        post = self.db.create_post(author_id, title, content)
        if not post:
            raise ValueError("用户不存在")
        
        return post.to_dict()
    
    def publish_post(self, post_id: int, author_id: int) -> dict:
        """发布文章"""
        post = self.db.get_post_by_id(post_id)
        if not post:
            raise ValueError("文章不存在")
        
        if post.author_id != author_id:
            raise ValueError("只有作者可以发布文章")
        
        post.publish()
        return post.to_dict()
    
    def update_post(self, post_id: int, author_id: int, title: Optional[str] = None, 
                   content: Optional[str] = None) -> dict:
        """更新文章"""
        post = self.db.get_post_by_id(post_id)
        if not post:
            raise ValueError("文章不存在")
        
        if post.author_id != author_id:
            raise ValueError("只有作者可以编辑文章")
        
        post.update(title, content)
        return post.to_dict()
    
    def delete_post(self, post_id: int, author_id: int) -> bool:
        """删除文章"""
        post = self.db.get_post_by_id(post_id)
        if not post:
            raise ValueError("文章不存在")
        
        if post.author_id != author_id:
            raise ValueError("只有作者可以删除文章")
        
        return self.db.delete_post(post_id)
    
    def get_user_posts(self, author_id: int) -> List[dict]:
        """获取用户的所有文章"""
        posts = self.db.get_posts_by_author(author_id)
        return [post.to_dict() for post in posts]
    
    def get_published_posts(self) -> List[dict]:
        """获取所有已发布的文章"""
        posts = self.db.get_published_posts()
        return [post.to_dict() for post in posts]
    
    def add_comment(self, post_id: int, author_id: int, content: str) -> dict:
        """添加评论"""
        if not content or len(content) < 1:
            raise ValueError("评论内容不能为空")
        
        comment = self.db.create_comment(post_id, author_id, content)
        if not comment:
            raise ValueError("文章或用户不存在")
        
        return comment.to_dict()
    
    def get_post_comments(self, post_id: int) -> List[dict]:
        """获取文章的所有评论"""
        comments = self.db.get_comments_by_post(post_id)
        return [comment.to_dict() for comment in comments]
    
    def search_posts(self, keyword: str) -> List[dict]:
        """搜索文章"""
        keyword_lower = keyword.lower()
        results = []
        
        for post in self.db.get_published_posts():
            if (keyword_lower in post.title.lower() or 
                keyword_lower in post.content.lower()):
                results.append(post.to_dict())
        
        return results
