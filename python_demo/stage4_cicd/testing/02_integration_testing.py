"""
集成测试示例

本模块演示如何编写集成测试，包括：
- API 端点测试
- 数据库集成测试
- 测试客户端的使用
- 端到端流程测试

运行测试：
    pytest 02_integration_testing.py -v
"""

import pytest
from typing import List, Optional
from datetime import datetime


# ============================================================================
# 模拟的应用代码（通常在单独的模块中）
# ============================================================================

class Database:
    """模拟数据库"""
    
    def __init__(self):
        self.users = []
        self.posts = []
        self._user_id_counter = 1
        self._post_id_counter = 1
    
    def create_user(self, username: str, email: str) -> dict:
        """创建用户"""
        user = {
            "id": self._user_id_counter,
            "username": username,
            "email": email,
            "created_at": datetime.now()
        }
        self.users.append(user)
        self._user_id_counter += 1
        return user
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """获取用户"""
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        for user in self.users:
            if user["username"] == username:
                return user
        return None
    
    def update_user(self, user_id: int, **kwargs) -> Optional[dict]:
        """更新用户"""
        user = self.get_user(user_id)
        if user:
            user.update(kwargs)
            return user
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user(user_id)
        if user:
            self.users.remove(user)
            return True
        return False
    
    def create_post(self, user_id: int, title: str, content: str) -> Optional[dict]:
        """创建文章"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        post = {
            "id": self._post_id_counter,
            "user_id": user_id,
            "title": title,
            "content": content,
            "created_at": datetime.now()
        }
        self.posts.append(post)
        self._post_id_counter += 1
        return post
    
    def get_posts_by_user(self, user_id: int) -> List[dict]:
        """获取用户的所有文章"""
        return [post for post in self.posts if post["user_id"] == user_id]
    
    def clear(self):
        """清空数据库"""
        self.users = []
        self.posts = []
        self._user_id_counter = 1
        self._post_id_counter = 1


class UserService:
    """用户服务"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def register_user(self, username: str, email: str) -> dict:
        """注册用户"""
        # 检查用户名是否已存在
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"用户名 {username} 已存在")
        
        # 验证邮箱格式
        if "@" not in email:
            raise ValueError("邮箱格式无效")
        
        return self.db.create_user(username, email)
    
    def get_user_profile(self, user_id: int) -> Optional[dict]:
        """获取用户资料"""
        return self.db.get_user(user_id)
    
    def update_user_email(self, user_id: int, new_email: str) -> Optional[dict]:
        """更新用户邮箱"""
        if "@" not in new_email:
            raise ValueError("邮箱格式无效")
        return self.db.update_user(user_id, email=new_email)


class PostService:
    """文章服务"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create_post(self, user_id: int, title: str, content: str) -> dict:
        """创建文章"""
        if not title or not content:
            raise ValueError("标题和内容不能为空")
        
        post = self.db.create_post(user_id, title, content)
        if not post:
            raise ValueError(f"用户 {user_id} 不存在")
        
        return post
    
    def get_user_posts(self, user_id: int) -> List[dict]:
        """获取用户的所有文章"""
        return self.db.get_posts_by_user(user_id)


# ============================================================================
# 集成测试
# ============================================================================

class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库"""
        database = Database()
        yield database
        # 测试后清理
        database.clear()
    
    def test_create_and_get_user(self, db):
        """测试创建和获取用户"""
        # 创建用户
        user = db.create_user("testuser", "test@example.com")
        
        # 验证返回的用户数据
        assert user["id"] == 1
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert "created_at" in user
        
        # 获取用户
        retrieved_user = db.get_user(1)
        assert retrieved_user == user
    
    def test_update_user(self, db):
        """测试更新用户"""
        # 创建用户
        user = db.create_user("testuser", "test@example.com")
        user_id = user["id"]
        
        # 更新用户
        updated_user = db.update_user(user_id, email="newemail@example.com")
        
        # 验证更新
        assert updated_user["email"] == "newemail@example.com"
        assert updated_user["username"] == "testuser"  # 其他字段不变
    
    def test_delete_user(self, db):
        """测试删除用户"""
        # 创建用户
        user = db.create_user("testuser", "test@example.com")
        user_id = user["id"]
        
        # 删除用户
        result = db.delete_user(user_id)
        assert result is True
        
        # 验证用户已删除
        deleted_user = db.get_user(user_id)
        assert deleted_user is None
    
    def test_create_post_with_user(self, db):
        """测试创建文章（需要用户存在）"""
        # 先创建用户
        user = db.create_user("author", "author@example.com")
        user_id = user["id"]
        
        # 创建文章
        post = db.create_post(user_id, "Test Title", "Test Content")
        
        # 验证文章数据
        assert post["id"] == 1
        assert post["user_id"] == user_id
        assert post["title"] == "Test Title"
        assert post["content"] == "Test Content"
    
    def test_get_posts_by_user(self, db):
        """测试获取用户的所有文章"""
        # 创建用户
        user = db.create_user("author", "author@example.com")
        user_id = user["id"]
        
        # 创建多篇文章
        db.create_post(user_id, "Post 1", "Content 1")
        db.create_post(user_id, "Post 2", "Content 2")
        db.create_post(user_id, "Post 3", "Content 3")
        
        # 获取用户的文章
        posts = db.get_posts_by_user(user_id)
        
        # 验证
        assert len(posts) == 3
        assert posts[0]["title"] == "Post 1"
        assert posts[1]["title"] == "Post 2"
        assert posts[2]["title"] == "Post 3"


class TestUserServiceIntegration:
    """用户服务集成测试"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库"""
        database = Database()
        yield database
        database.clear()
    
    @pytest.fixture
    def user_service(self, db):
        """创建用户服务"""
        return UserService(db)
    
    def test_register_user_success(self, user_service):
        """测试成功注册用户"""
        user = user_service.register_user("newuser", "new@example.com")
        
        assert user["username"] == "newuser"
        assert user["email"] == "new@example.com"
        assert user["id"] is not None
    
    def test_register_duplicate_username(self, user_service):
        """测试注册重复用户名"""
        # 注册第一个用户
        user_service.register_user("testuser", "test1@example.com")
        
        # 尝试注册相同用户名
        with pytest.raises(ValueError, match="用户名 testuser 已存在"):
            user_service.register_user("testuser", "test2@example.com")
    
    def test_register_invalid_email(self, user_service):
        """测试注册无效邮箱"""
        with pytest.raises(ValueError, match="邮箱格式无效"):
            user_service.register_user("testuser", "invalidemail")
    
    def test_get_user_profile(self, user_service):
        """测试获取用户资料"""
        # 注册用户
        registered_user = user_service.register_user("testuser", "test@example.com")
        user_id = registered_user["id"]
        
        # 获取用户资料
        profile = user_service.get_user_profile(user_id)
        
        assert profile["username"] == "testuser"
        assert profile["email"] == "test@example.com"
    
    def test_update_user_email(self, user_service):
        """测试更新用户邮箱"""
        # 注册用户
        user = user_service.register_user("testuser", "old@example.com")
        user_id = user["id"]
        
        # 更新邮箱
        updated_user = user_service.update_user_email(user_id, "new@example.com")
        
        assert updated_user["email"] == "new@example.com"


class TestPostServiceIntegration:
    """文章服务集成测试"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库"""
        database = Database()
        yield database
        database.clear()
    
    @pytest.fixture
    def user_service(self, db):
        """创建用户服务"""
        return UserService(db)
    
    @pytest.fixture
    def post_service(self, db):
        """创建文章服务"""
        return PostService(db)
    
    @pytest.fixture
    def test_user(self, user_service):
        """创建测试用户"""
        return user_service.register_user("testauthor", "author@example.com")
    
    def test_create_post_success(self, post_service, test_user):
        """测试成功创建文章"""
        post = post_service.create_post(
            test_user["id"],
            "My First Post",
            "This is the content"
        )
        
        assert post["title"] == "My First Post"
        assert post["content"] == "This is the content"
        assert post["user_id"] == test_user["id"]
    
    def test_create_post_empty_title(self, post_service, test_user):
        """测试创建空标题文章"""
        with pytest.raises(ValueError, match="标题和内容不能为空"):
            post_service.create_post(test_user["id"], "", "Content")
    
    def test_create_post_nonexistent_user(self, post_service):
        """测试为不存在的用户创建文章"""
        with pytest.raises(ValueError, match="用户 999 不存在"):
            post_service.create_post(999, "Title", "Content")
    
    def test_get_user_posts(self, post_service, test_user):
        """测试获取用户的所有文章"""
        user_id = test_user["id"]
        
        # 创建多篇文章
        post_service.create_post(user_id, "Post 1", "Content 1")
        post_service.create_post(user_id, "Post 2", "Content 2")
        
        # 获取文章
        posts = post_service.get_user_posts(user_id)
        
        assert len(posts) == 2
        assert posts[0]["title"] == "Post 1"
        assert posts[1]["title"] == "Post 2"


class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库"""
        database = Database()
        yield database
        database.clear()
    
    @pytest.fixture
    def services(self, db):
        """创建所有服务"""
        return {
            "user": UserService(db),
            "post": PostService(db)
        }
    
    def test_complete_user_post_workflow(self, services):
        """测试完整的用户-文章工作流"""
        user_service = services["user"]
        post_service = services["post"]
        
        # 1. 注册用户
        user = user_service.register_user("blogger", "blogger@example.com")
        user_id = user["id"]
        
        # 2. 验证用户已创建
        profile = user_service.get_user_profile(user_id)
        assert profile["username"] == "blogger"
        
        # 3. 创建文章
        post1 = post_service.create_post(user_id, "First Post", "Hello World")
        post2 = post_service.create_post(user_id, "Second Post", "Another post")
        
        # 4. 获取用户的所有文章
        posts = post_service.get_user_posts(user_id)
        assert len(posts) == 2
        
        # 5. 更新用户邮箱
        updated_user = user_service.update_user_email(user_id, "newblogger@example.com")
        assert updated_user["email"] == "newblogger@example.com"
        
        # 6. 验证文章仍然关联到用户
        posts_after_update = post_service.get_user_posts(user_id)
        assert len(posts_after_update) == 2
    
    def test_multiple_users_workflow(self, services):
        """测试多用户工作流"""
        user_service = services["user"]
        post_service = services["post"]
        
        # 创建多个用户
        user1 = user_service.register_user("user1", "user1@example.com")
        user2 = user_service.register_user("user2", "user2@example.com")
        
        # 每个用户创建文章
        post_service.create_post(user1["id"], "User1 Post", "Content 1")
        post_service.create_post(user2["id"], "User2 Post", "Content 2")
        
        # 验证每个用户只能看到自己的文章
        user1_posts = post_service.get_user_posts(user1["id"])
        user2_posts = post_service.get_user_posts(user2["id"])
        
        assert len(user1_posts) == 1
        assert len(user2_posts) == 1
        assert user1_posts[0]["title"] == "User1 Post"
        assert user2_posts[0]["title"] == "User2 Post"


# ============================================================================
# 运行说明
# ============================================================================

"""
运行所有集成测试：
    pytest 02_integration_testing.py -v

运行特定测试类：
    pytest 02_integration_testing.py::TestUserServiceIntegration -v

显示详细输出：
    pytest 02_integration_testing.py -v -s

关键概念：
1. 集成测试验证多个组件之间的交互
2. 使用 fixture 创建和清理测试数据
3. 测试完整的业务流程
4. 验证数据在不同层之间的正确传递
5. 测试边界条件和错误处理

集成测试 vs 单元测试：
- 单元测试：测试单个函数或类，快速、独立
- 集成测试：测试多个组件的交互，更接近真实场景
- 集成测试通常比单元测试慢，但能发现组件间的问题
"""
