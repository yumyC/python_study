"""
单元测试示例

本模块演示如何使用 pytest 编写单元测试，包括：
- 基本的测试函数
- 测试类的组织
- 断言方法
- 参数化测试
- 测试标记

运行测试：
    pytest 01_unit_testing.py -v
"""

import pytest


# ============================================================================
# 被测试的代码（通常在单独的模块中）
# ============================================================================

class Calculator:
    """简单的计算器类"""
    
    def add(self, a, b):
        """加法"""
        return a + b
    
    def subtract(self, a, b):
        """减法"""
        return a - b
    
    def multiply(self, a, b):
        """乘法"""
        return a * b
    
    def divide(self, a, b):
        """除法"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    def power(self, base, exponent):
        """幂运算"""
        return base ** exponent


def is_prime(n):
    """判断是否为质数"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def validate_email(email):
    """简单的邮箱验证"""
    if not email or '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if not parts[0] or not parts[1]:
        return False
    if '.' not in parts[1]:
        return False
    return True


# ============================================================================
# 测试代码
# ============================================================================

# 1. 基本测试函数
def test_calculator_add():
    """测试加法功能"""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5


def test_calculator_subtract():
    """测试减法功能"""
    calc = Calculator()
    result = calc.subtract(5, 3)
    assert result == 2


def test_calculator_multiply():
    """测试乘法功能"""
    calc = Calculator()
    result = calc.multiply(4, 3)
    assert result == 12


def test_calculator_divide():
    """测试除法功能"""
    calc = Calculator()
    result = calc.divide(10, 2)
    assert result == 5.0


def test_calculator_divide_by_zero():
    """测试除以零的异常处理"""
    calc = Calculator()
    # 使用 pytest.raises 检查是否抛出预期的异常
    with pytest.raises(ValueError, match="除数不能为零"):
        calc.divide(10, 0)


# 2. 使用测试类组织相关测试
class TestCalculator:
    """计算器测试类"""
    
    def test_add_positive_numbers(self):
        """测试正数加法"""
        calc = Calculator()
        assert calc.add(1, 2) == 3
        assert calc.add(10, 20) == 30
    
    def test_add_negative_numbers(self):
        """测试负数加法"""
        calc = Calculator()
        assert calc.add(-1, -2) == -3
        assert calc.add(-5, 3) == -2
    
    def test_add_zero(self):
        """测试零的加法"""
        calc = Calculator()
        assert calc.add(0, 5) == 5
        assert calc.add(5, 0) == 5
        assert calc.add(0, 0) == 0
    
    def test_power(self):
        """测试幂运算"""
        calc = Calculator()
        assert calc.power(2, 3) == 8
        assert calc.power(5, 2) == 25
        assert calc.power(10, 0) == 1


# 3. 参数化测试
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -5, 5),
    (100, 200, 300),
])
def test_add_parametrized(a, b, expected):
    """参数化测试加法 - 一次定义多个测试用例"""
    calc = Calculator()
    assert calc.add(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5.0),
    (9, 3, 3.0),
    (7, 2, 3.5),
    (1, 1, 1.0),
])
def test_divide_parametrized(a, b, expected):
    """参数化测试除法"""
    calc = Calculator()
    assert calc.divide(a, b) == expected


# 4. 测试质数判断函数
class TestPrimeNumber:
    """质数判断测试类"""
    
    @pytest.mark.parametrize("n, expected", [
        (2, True),
        (3, True),
        (5, True),
        (7, True),
        (11, True),
        (13, True),
    ])
    def test_prime_numbers(self, n, expected):
        """测试质数"""
        assert is_prime(n) == expected
    
    @pytest.mark.parametrize("n, expected", [
        (0, False),
        (1, False),
        (4, False),
        (6, False),
        (8, False),
        (9, False),
        (10, False),
    ])
    def test_non_prime_numbers(self, n, expected):
        """测试非质数"""
        assert is_prime(n) == expected


# 5. 测试邮箱验证函数
class TestEmailValidation:
    """邮箱验证测试类"""
    
    def test_valid_emails(self):
        """测试有效的邮箱地址"""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user@domain.co.uk") is True
        assert validate_email("admin@company.org") is True
    
    def test_invalid_emails(self):
        """测试无效的邮箱地址"""
        assert validate_email("") is False
        assert validate_email("notanemail") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@@example.com") is False
        assert validate_email("user@domain") is False


# 6. 使用测试标记
@pytest.mark.slow
def test_slow_operation():
    """标记为慢速测试"""
    # 模拟耗时操作
    import time
    time.sleep(0.1)
    assert True


@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    """跳过此测试"""
    assert False


@pytest.mark.skipif(pytest.__version__ < "7.0", reason="需要 pytest 7.0+")
def test_new_pytest_feature():
    """条件跳过测试"""
    assert True


@pytest.mark.xfail(reason="已知的 bug")
def test_known_bug():
    """预期失败的测试"""
    calc = Calculator()
    # 假设这是一个已知的 bug
    assert calc.add(0.1, 0.2) == 0.3  # 浮点数精度问题


# 7. 测试多个断言
def test_multiple_assertions():
    """一个测试中包含多个断言"""
    calc = Calculator()
    
    # 测试加法
    assert calc.add(1, 1) == 2
    
    # 测试减法
    assert calc.subtract(5, 3) == 2
    
    # 测试乘法
    assert calc.multiply(2, 3) == 6
    
    # 注意：如果前面的断言失败，后面的断言不会执行
    # 建议每个测试只测试一个概念


# 8. 测试字符串和集合
def test_string_operations():
    """测试字符串操作"""
    text = "Hello, World!"
    
    # 包含检查
    assert "Hello" in text
    assert "Goodbye" not in text
    
    # 开头和结尾
    assert text.startswith("Hello")
    assert text.endswith("!")
    
    # 长度
    assert len(text) == 13


def test_list_operations():
    """测试列表操作"""
    numbers = [1, 2, 3, 4, 5]
    
    # 长度
    assert len(numbers) == 5
    
    # 包含
    assert 3 in numbers
    assert 6 not in numbers
    
    # 相等性
    assert numbers == [1, 2, 3, 4, 5]
    
    # 排序
    assert sorted([3, 1, 2]) == [1, 2, 3]


# ============================================================================
# 运行说明
# ============================================================================

"""
运行所有测试：
    pytest 01_unit_testing.py -v

运行特定测试类：
    pytest 01_unit_testing.py::TestCalculator -v

运行特定测试函数：
    pytest 01_unit_testing.py::test_calculator_add -v

运行带标记的测试：
    pytest 01_unit_testing.py -m slow -v

跳过带标记的测试：
    pytest 01_unit_testing.py -m "not slow" -v

显示打印输出：
    pytest 01_unit_testing.py -s

生成覆盖率报告：
    pytest 01_unit_testing.py --cov=. --cov-report=html

关键概念：
1. 测试函数以 test_ 开头
2. 测试类以 Test 开头
3. 使用 assert 进行断言
4. 使用 pytest.raises 测试异常
5. 使用 @pytest.mark.parametrize 进行参数化测试
6. 使用标记（@pytest.mark）组织和过滤测试
"""
