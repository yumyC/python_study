"""
测试夹具 (Fixtures) 示例

本模块演示 pytest fixtures 的使用，包括：
- Fixture 的基本概念
- Fixture 的作用域
- Fixture 的依赖和组合
- 内置 fixture
- 参数化 fixture

运行测试：
    pytest 03_test_fixtures.py -v
"""

import pytest
import tempfile
import os
from pathlib import Path


# ============================================================================
# 被测试的代码
# ============================================================================

class FileManager:
    """文件管理器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_file(self, filename: str, content: str):
        """创建文件"""
        file_path = self.base_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def read_file(self, filename: str) -> str:
        """读取文件"""
        file_path = self.base_path / filename
        return file_path.read_text(encoding='utf-8')
    
    def list_files(self):
        """列出所有文件"""
        return [f.name for f in self.base_path.iterdir() if f.is_file()]
    
    def delete_file(self, filename: str):
        """删除文件"""
        file_path = self.base_path / filename
        if file_path.exists():
            file_path.unlink()


class ShoppingCart:
    """购物车"""
    
    def __init__(self):
        self.items = []
    
    def add_item(self, name: str, price: float, quantity: int = 1):
        """添加商品"""
        self.items.append({
            "name": name,
            "price": price,
            "quantity": quantity
        })
    
    def get_total(self) -> float:
        """计算总价"""
        return sum(item["price"] * item["quantity"] for item in self.items)
    
    def get_item_count(self) -> int:
        """获取商品数量"""
        return sum(item["quantity"] for item in self.items)
    
    def clear(self):
        """清空购物车"""
        self.items = []


# ============================================================================
# Fixture 示例
# ============================================================================

# 1. 基本 Fixture
@pytest.fixture
def sample_data():
    """提供测试数据"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    }


def test_with_sample_data(sample_data):
    """使用 fixture 的测试"""
    assert sample_data["name"] == "Test User"
    assert sample_data["email"] == "test@example.com"
    assert sample_data["age"] == 25


# 2. Fixture 的 Setup 和 Teardown
@pytest.fixture
def temp_directory():
    """创建临时目录，测试后清理"""
    # Setup: 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"\n创建临时目录: {temp_dir}")
    
    # 提供给测试使用
    yield temp_dir
    
    # Teardown: 清理临时目录
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\n清理临时目录: {temp_dir}")


def test_with_temp_directory(temp_directory):
    """使用临时目录的测试"""
    # 在临时目录中创建文件
    test_file = Path(temp_directory) / "test.txt"
    test_file.write_text("Hello, World!")
    
    # 验证文件存在
    assert test_file.exists()
    assert test_file.read_text() == "Hello, World!"


# 3. Fixture 作用域
@pytest.fixture(scope="function")
def function_scope_fixture():
    """函数级别作用域（默认）- 每个测试函数都会创建新实例"""
    print("\n[Function] Setup")
    yield "function data"
    print("\n[Function] Teardown")


@pytest.fixture(scope="class")
def class_scope_fixture():
    """类级别作用域 - 每个测试类创建一次"""
    print("\n[Class] Setup")
    yield "class data"
    print("\n[Class] Teardown")


@pytest.fixture(scope="module")
def module_scope_fixture():
    """模块级别作用域 - 每个模块创建一次"""
    print("\n[Module] Setup")
    yield "module data"
    print("\n[Module] Teardown")


@pytest.fixture(scope="session")
def session_scope_fixture():
    """会话级别作用域 - 整个测试会话创建一次"""
    print("\n[Session] Setup")
    yield "session data"
    print("\n[Session] Teardown")


class TestFixtureScopes:
    """测试 fixture 作用域"""
    
    def test_scope_1(self, function_scope_fixture, class_scope_fixture):
        """第一个测试"""
        assert function_scope_fixture == "function data"
        assert class_scope_fixture == "class data"
    
    def test_scope_2(self, function_scope_fixture, class_scope_fixture):
        """第二个测试"""
        assert function_scope_fixture == "function data"
        assert class_scope_fixture == "class data"


# 4. Fixture 依赖
@pytest.fixture
def database_connection():
    """模拟数据库连接"""
    print("\n连接数据库")
    connection = {"connected": True, "db": "test_db"}
    yield connection
    print("\n关闭数据库连接")


@pytest.fixture
def database_session(database_connection):
    """依赖于数据库连接的会话"""
    print("\n创建数据库会话")
    session = {"connection": database_connection, "session_id": "abc123"}
    yield session
    print("\n关闭数据库会话")


def test_with_database_session(database_session):
    """使用数据库会话的测试"""
    assert database_session["connection"]["connected"] is True
    assert database_session["session_id"] == "abc123"


# 5. 自动使用的 Fixture
@pytest.fixture(autouse=True)
def reset_environment():
    """自动在每个测试前后运行"""
    print("\n[AutoUse] 测试前准备")
    yield
    print("\n[AutoUse] 测试后清理")


# 6. 参数化 Fixture
@pytest.fixture(params=[1, 2, 3])
def number_fixture(request):
    """参数化 fixture - 测试会运行多次"""
    return request.param


def test_with_parametrized_fixture(number_fixture):
    """使用参数化 fixture 的测试"""
    assert number_fixture > 0
    assert number_fixture <= 3


@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def database_type(request):
    """不同数据库类型的 fixture"""
    return request.param


def test_database_compatibility(database_type):
    """测试不同数据库的兼容性"""
    assert database_type in ["sqlite", "postgresql", "mysql"]
    print(f"\n测试数据库类型: {database_type}")


# 7. 实际应用示例 - 文件管理器测试
@pytest.fixture
def file_manager(temp_directory):
    """创建文件管理器实例"""
    return FileManager(temp_directory)


class TestFileManager:
    """文件管理器测试"""
    
    def test_create_file(self, file_manager):
        """测试创建文件"""
        file_path = file_manager.create_file("test.txt", "Hello")
        assert file_path.exists()
        assert file_manager.read_file("test.txt") == "Hello"
    
    def test_list_files(self, file_manager):
        """测试列出文件"""
        file_manager.create_file("file1.txt", "Content 1")
        file_manager.create_file("file2.txt", "Content 2")
        
        files = file_manager.list_files()
        assert len(files) == 2
        assert "file1.txt" in files
        assert "file2.txt" in files
    
    def test_delete_file(self, file_manager):
        """测试删除文件"""
        file_manager.create_file("temp.txt", "Temporary")
        file_manager.delete_file("temp.txt")
        
        files = file_manager.list_files()
        assert "temp.txt" not in files


# 8. 实际应用示例 - 购物车测试
@pytest.fixture
def empty_cart():
    """创建空购物车"""
    return ShoppingCart()


@pytest.fixture
def cart_with_items():
    """创建包含商品的购物车"""
    cart = ShoppingCart()
    cart.add_item("Apple", 1.5, 3)
    cart.add_item("Banana", 0.8, 5)
    return cart


class TestShoppingCart:
    """购物车测试"""
    
    def test_empty_cart(self, empty_cart):
        """测试空购物车"""
        assert empty_cart.get_total() == 0
        assert empty_cart.get_item_count() == 0
    
    def test_add_item(self, empty_cart):
        """测试添加商品"""
        empty_cart.add_item("Orange", 2.0, 2)
        assert empty_cart.get_total() == 4.0
        assert empty_cart.get_item_count() == 2
    
    def test_cart_with_items(self, cart_with_items):
        """测试预填充的购物车"""
        # Apple: 1.5 * 3 = 4.5
        # Banana: 0.8 * 5 = 4.0
        # Total: 8.5
        assert cart_with_items.get_total() == 8.5
        assert cart_with_items.get_item_count() == 8
    
    def test_clear_cart(self, cart_with_items):
        """测试清空购物车"""
        cart_with_items.clear()
        assert cart_with_items.get_total() == 0
        assert cart_with_items.get_item_count() == 0


# 9. 内置 Fixture 示例
def test_tmp_path(tmp_path):
    """使用 pytest 内置的 tmp_path fixture"""
    # tmp_path 是一个 Path 对象，指向临时目录
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    
    assert test_file.exists()
    assert test_file.read_text() == "Test content"


def test_capsys(capsys):
    """使用 capsys 捕获标准输出"""
    print("Hello, World!")
    print("This is a test")
    
    # 捕获输出
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
    assert "This is a test" in captured.out


def test_monkeypatch(monkeypatch):
    """使用 monkeypatch 修改环境变量"""
    # 设置环境变量
    monkeypatch.setenv("TEST_VAR", "test_value")
    
    # 验证环境变量
    assert os.environ.get("TEST_VAR") == "test_value"
    
    # 测试后会自动恢复


# 10. Fixture 工厂模式
@pytest.fixture
def make_user():
    """用户工厂 fixture"""
    users = []
    
    def _make_user(name, email, age=18):
        user = {
            "id": len(users) + 1,
            "name": name,
            "email": email,
            "age": age
        }
        users.append(user)
        return user
    
    yield _make_user
    
    # 清理
    users.clear()


def test_user_factory(make_user):
    """使用工厂 fixture 创建多个用户"""
    user1 = make_user("Alice", "alice@example.com", 25)
    user2 = make_user("Bob", "bob@example.com", 30)
    
    assert user1["id"] == 1
    assert user2["id"] == 2
    assert user1["name"] == "Alice"
    assert user2["name"] == "Bob"


# ============================================================================
# conftest.py 说明
# ============================================================================

"""
conftest.py 文件：

在实际项目中，通常会创建 conftest.py 文件来存放共享的 fixtures。
conftest.py 中的 fixtures 可以被同目录及子目录的所有测试文件使用。

示例 conftest.py 内容：

```python
import pytest

@pytest.fixture
def db_connection():
    # 创建数据库连接
    conn = create_connection()
    yield conn
    # 关闭连接
    conn.close()

@pytest.fixture
def api_client():
    # 创建 API 客户端
    client = APIClient()
    yield client
    # 清理
    client.cleanup()
```

目录结构示例：
tests/
├── conftest.py          # 根级别 fixtures
├── test_users.py
├── test_posts.py
└── integration/
    ├── conftest.py      # 集成测试专用 fixtures
    └── test_api.py
"""


# ============================================================================
# 运行说明
# ============================================================================

"""
运行所有测试：
    pytest 03_test_fixtures.py -v -s

运行特定测试类：
    pytest 03_test_fixtures.py::TestShoppingCart -v

关键概念：
1. Fixture 用于提供测试数据和资源
2. 使用 yield 实现 setup 和 teardown
3. Fixture 有不同的作用域：function, class, module, session
4. Fixture 可以相互依赖
5. 使用 autouse=True 自动应用 fixture
6. 参数化 fixture 可以运行多次测试
7. conftest.py 用于共享 fixtures

常用内置 Fixtures：
- tmp_path: 临时目录（Path 对象）
- tmpdir: 临时目录（py.path.local 对象）
- capsys: 捕获标准输出和错误
- caplog: 捕获日志
- monkeypatch: 修改对象、环境变量等
- request: 访问测试请求信息
"""
