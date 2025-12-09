"""
Mock 技术示例

本模块演示如何使用 Mock 技术进行测试，包括：
- Mock 的基本概念
- unittest.mock 模块的使用
- Mock 对象的创建和配置
- Patch 装饰器
- 验证 Mock 调用

运行测试：
    pytest 04_mocking.py -v
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Optional, List
import requests


# ============================================================================
# 被测试的代码
# ============================================================================

class EmailService:
    """邮件服务"""
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """发送邮件（实际会调用外部 API）"""
        # 实际实现会调用 SMTP 服务器或邮件 API
        # 这里简化处理
        print(f"发送邮件到 {to}: {subject}")
        return True


class SMSService:
    """短信服务"""
    
    def send_sms(self, phone: str, message: str) -> dict:
        """发送短信（实际会调用外部 API）"""
        # 实际实现会调用短信 API
        print(f"发送短信到 {phone}: {message}")
        return {"status": "sent", "message_id": "12345"}


class NotificationService:
    """通知服务"""
    
    def __init__(self, email_service: EmailService, sms_service: SMSService):
        self.email_service = email_service
        self.sms_service = sms_service
    
    def notify_user(self, user: dict, message: str) -> dict:
        """通知用户"""
        results = {}
        
        # 发送邮件
        if user.get("email"):
            email_sent = self.email_service.send_email(
                user["email"],
                "通知",
                message
            )
            results["email"] = email_sent
        
        # 发送短信
        if user.get("phone"):
            sms_result = self.sms_service.send_sms(
                user["phone"],
                message
            )
            results["sms"] = sms_result
        
        return results


class WeatherAPI:
    """天气 API 客户端"""
    
    def get_weather(self, city: str) -> dict:
        """获取天气信息（调用外部 API）"""
        # 实际会调用真实的天气 API
        url = f"https://api.weather.com/v1/weather?city={city}"
        response = requests.get(url)
        return response.json()


class WeatherService:
    """天气服务"""
    
    def __init__(self, api: WeatherAPI):
        self.api = api
    
    def get_temperature(self, city: str) -> Optional[float]:
        """获取温度"""
        try:
            weather_data = self.api.get_weather(city)
            return weather_data.get("temperature")
        except Exception as e:
            print(f"获取天气失败: {e}")
            return None
    
    def is_good_weather(self, city: str) -> bool:
        """判断是否好天气"""
        temp = self.get_temperature(city)
        if temp is None:
            return False
        return 15 <= temp <= 25


class Database:
    """数据库类"""
    
    def connect(self):
        """连接数据库"""
        print("连接数据库...")
    
    def query(self, sql: str) -> List[dict]:
        """执行查询"""
        print(f"执行查询: {sql}")
        return []
    
    def close(self):
        """关闭连接"""
        print("关闭数据库连接...")


class UserRepository:
    """用户仓储"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """根据 ID 获取用户"""
        results = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return results[0] if results else None
    
    def get_all_users(self) -> List[dict]:
        """获取所有用户"""
        return self.db.query("SELECT * FROM users")


# ============================================================================
# Mock 测试示例
# ============================================================================

# 1. 基本 Mock 对象
def test_basic_mock():
    """测试基本 Mock 对象"""
    # 创建 Mock 对象
    mock_obj = Mock()
    
    # Mock 对象可以调用任何方法
    mock_obj.some_method()
    mock_obj.another_method("arg1", "arg2")
    
    # 验证方法被调用
    mock_obj.some_method.assert_called_once()
    mock_obj.another_method.assert_called_once_with("arg1", "arg2")


def test_mock_return_value():
    """测试 Mock 返回值"""
    # 创建 Mock 并设置返回值
    mock_func = Mock(return_value=42)
    
    # 调用 Mock
    result = mock_func()
    
    # 验证返回值
    assert result == 42
    mock_func.assert_called_once()


def test_mock_side_effect():
    """测试 Mock 副作用"""
    # 使用 side_effect 返回不同的值
    mock_func = Mock(side_effect=[1, 2, 3])
    
    assert mock_func() == 1
    assert mock_func() == 2
    assert mock_func() == 3


def test_mock_exception():
    """测试 Mock 抛出异常"""
    # 使用 side_effect 抛出异常
    mock_func = Mock(side_effect=ValueError("测试异常"))
    
    with pytest.raises(ValueError, match="测试异常"):
        mock_func()


# 2. Mock 邮件服务
def test_notification_with_mock_email():
    """使用 Mock 测试通知服务"""
    # 创建 Mock 邮件服务
    mock_email = Mock(spec=EmailService)
    mock_email.send_email.return_value = True
    
    # 创建 Mock 短信服务
    mock_sms = Mock(spec=SMSService)
    mock_sms.send_sms.return_value = {"status": "sent", "message_id": "123"}
    
    # 创建通知服务
    notification_service = NotificationService(mock_email, mock_sms)
    
    # 测试通知
    user = {"email": "test@example.com", "phone": "1234567890"}
    result = notification_service.notify_user(user, "测试消息")
    
    # 验证邮件服务被调用
    mock_email.send_email.assert_called_once_with(
        "test@example.com",
        "通知",
        "测试消息"
    )
    
    # 验证短信服务被调用
    mock_sms.send_sms.assert_called_once_with(
        "1234567890",
        "测试消息"
    )
    
    # 验证结果
    assert result["email"] is True
    assert result["sms"]["status"] == "sent"


# 3. 使用 patch 装饰器
@patch('requests.get')
def test_weather_service_with_patch(mock_get):
    """使用 patch 测试天气服务"""
    # 配置 Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "temperature": 20.5,
        "condition": "sunny"
    }
    mock_get.return_value = mock_response
    
    # 创建服务
    api = WeatherAPI()
    service = WeatherService(api)
    
    # 测试
    temp = service.get_temperature("Beijing")
    
    # 验证
    assert temp == 20.5
    mock_get.assert_called_once()


@patch('requests.get')
def test_weather_service_good_weather(mock_get):
    """测试好天气判断"""
    # 配置 Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {"temperature": 22.0}
    mock_get.return_value = mock_response
    
    # 创建服务
    api = WeatherAPI()
    service = WeatherService(api)
    
    # 测试
    assert service.is_good_weather("Shanghai") is True


@patch('requests.get')
def test_weather_service_bad_weather(mock_get):
    """测试坏天气判断"""
    # 配置 Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {"temperature": 35.0}
    mock_get.return_value = mock_response
    
    # 创建服务
    api = WeatherAPI()
    service = WeatherService(api)
    
    # 测试
    assert service.is_good_weather("Guangzhou") is False


@patch('requests.get')
def test_weather_service_api_error(mock_get):
    """测试 API 错误处理"""
    # 配置 Mock 抛出异常
    mock_get.side_effect = requests.RequestException("网络错误")
    
    # 创建服务
    api = WeatherAPI()
    service = WeatherService(api)
    
    # 测试
    temp = service.get_temperature("Beijing")
    assert temp is None


# 4. 使用 patch 作为上下文管理器
def test_patch_as_context_manager():
    """使用 patch 作为上下文管理器"""
    api = WeatherAPI()
    service = WeatherService(api)
    
    with patch('requests.get') as mock_get:
        # 配置 Mock
        mock_response = Mock()
        mock_response.json.return_value = {"temperature": 18.0}
        mock_get.return_value = mock_response
        
        # 测试
        temp = service.get_temperature("Shenzhen")
        assert temp == 18.0


# 5. Mock 数据库
def test_user_repository_with_mock_db():
    """使用 Mock 测试用户仓储"""
    # 创建 Mock 数据库
    mock_db = Mock(spec=Database)
    mock_db.query.return_value = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"}
    ]
    
    # 创建仓储
    repo = UserRepository(mock_db)
    
    # 测试获取用户
    user = repo.get_user_by_id(1)
    
    # 验证
    assert user["name"] == "Alice"
    mock_db.query.assert_called_once_with("SELECT * FROM users WHERE id = 1")


def test_user_repository_no_user():
    """测试用户不存在的情况"""
    # 创建 Mock 数据库
    mock_db = Mock(spec=Database)
    mock_db.query.return_value = []
    
    # 创建仓储
    repo = UserRepository(mock_db)
    
    # 测试
    user = repo.get_user_by_id(999)
    
    # 验证
    assert user is None


def test_user_repository_get_all_users():
    """测试获取所有用户"""
    # 创建 Mock 数据库
    mock_db = Mock(spec=Database)
    mock_db.query.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
    ]
    
    # 创建仓储
    repo = UserRepository(mock_db)
    
    # 测试
    users = repo.get_all_users()
    
    # 验证
    assert len(users) == 3
    assert users[0]["name"] == "Alice"
    mock_db.query.assert_called_once_with("SELECT * FROM users")


# 6. 验证 Mock 调用
def test_mock_call_verification():
    """测试 Mock 调用验证"""
    mock_func = Mock()
    
    # 调用多次
    mock_func(1, 2)
    mock_func(3, 4)
    mock_func(5, 6)
    
    # 验证调用次数
    assert mock_func.call_count == 3
    
    # 验证调用参数
    mock_func.assert_any_call(1, 2)
    mock_func.assert_any_call(3, 4)
    
    # 验证所有调用
    expected_calls = [call(1, 2), call(3, 4), call(5, 6)]
    mock_func.assert_has_calls(expected_calls)


# 7. MagicMock 示例
def test_magic_mock():
    """测试 MagicMock"""
    # MagicMock 支持魔术方法
    mock_obj = MagicMock()
    
    # 可以使用魔术方法
    mock_obj.__str__.return_value = "Mocked String"
    mock_obj.__len__.return_value = 42
    
    assert str(mock_obj) == "Mocked String"
    assert len(mock_obj) == 42


def test_magic_mock_iteration():
    """测试 MagicMock 迭代"""
    mock_list = MagicMock()
    mock_list.__iter__.return_value = iter([1, 2, 3])
    
    result = list(mock_list)
    assert result == [1, 2, 3]


# 8. patch.object 示例
def test_patch_object():
    """使用 patch.object 修改对象的方法"""
    email_service = EmailService()
    sms_service = SMSService()
    notification_service = NotificationService(email_service, sms_service)
    
    with patch.object(email_service, 'send_email', return_value=True) as mock_send:
        user = {"email": "test@example.com"}
        notification_service.notify_user(user, "测试")
        
        mock_send.assert_called_once()


# 9. 多个 patch
@patch('requests.get')
@patch.object(EmailService, 'send_email')
def test_multiple_patches(mock_email, mock_get):
    """测试多个 patch"""
    # 配置 Mock
    mock_email.return_value = True
    mock_response = Mock()
    mock_response.json.return_value = {"temperature": 20}
    mock_get.return_value = mock_response
    
    # 测试代码
    email_service = EmailService()
    result = email_service.send_email("test@example.com", "主题", "内容")
    
    assert result is True
    mock_email.assert_called_once()


# 10. Mock 属性
def test_mock_attributes():
    """测试 Mock 属性"""
    mock_obj = Mock()
    
    # 设置属性
    mock_obj.name = "Test"
    mock_obj.value = 42
    
    # 验证属性
    assert mock_obj.name == "Test"
    assert mock_obj.value == 42


def test_mock_configure():
    """测试 Mock 配置"""
    # 使用 configure_mock 配置多个属性
    mock_obj = Mock()
    mock_obj.configure_mock(
        name="Test",
        value=42,
        method=Mock(return_value="result")
    )
    
    assert mock_obj.name == "Test"
    assert mock_obj.value == 42
    assert mock_obj.method() == "result"


# ============================================================================
# 运行说明
# ============================================================================

"""
运行所有测试：
    pytest 04_mocking.py -v

运行特定测试：
    pytest 04_mocking.py::test_notification_with_mock_email -v

关键概念：
1. Mock 用于模拟外部依赖（API、数据库、文件系统等）
2. 使用 Mock 可以隔离测试，提高测试速度
3. patch 装饰器用于临时替换对象
4. 验证 Mock 的调用次数和参数
5. MagicMock 支持魔术方法

Mock vs 真实对象：
- Mock: 快速、可控、隔离
- 真实对象: 慢、依赖外部、集成测试

何时使用 Mock：
1. 外部 API 调用（HTTP 请求）
2. 数据库操作
3. 文件系统操作
4. 时间相关的操作
5. 随机数生成
6. 第三方服务

何时不使用 Mock：
1. 测试核心业务逻辑
2. 简单的纯函数
3. 集成测试（需要测试真实交互）

最佳实践：
1. 只 Mock 外部依赖
2. 不要 Mock 被测试的代码
3. 验证 Mock 的调用
4. 使用 spec 参数确保 Mock 的接口正确
5. 保持 Mock 简单，不要过度配置
"""
