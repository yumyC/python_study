"""
Python 基础教程 03: 函数

本教程涵盖:
- 函数定义和调用
- 参数类型（位置参数、默认参数、关键字参数、可变参数）
- 返回值
- 作用域
- Lambda 函数
- 装饰器基础
"""

# ============================================================
# 1. 函数定义和调用
# ============================================================

print("=" * 50)
print("函数定义和调用:")
print("=" * 50)

# 基本函数定义
def greet():
    """打招呼函数"""
    print("你好，欢迎学习 Python！")

# 调用函数
greet()

# 带参数的函数
def greet_person(name):
    """向指定人打招呼"""
    print(f"你好，{name}！")

greet_person("张三")
greet_person("李四")

# 带返回值的函数
def add(a, b):
    """计算两个数的和"""
    return a + b

result = add(5, 3)
print(f"5 + 3 = {result}")

# ============================================================
# 2. 参数类型
# ============================================================

print("\n" + "=" * 50)
print("参数类型:")
print("=" * 50)

# 位置参数
def introduce(name, age, city):
    """自我介绍"""
    print(f"我叫{name}，今年{age}岁，来自{city}")

introduce("王五", 25, "北京")

# 默认参数
def greet_with_time(name, time="早上"):
    """带时间的问候"""
    print(f"{time}好，{name}！")

greet_with_time("张三")  # 使用默认值
greet_with_time("李四", "晚上")  # 覆盖默认值

# 关键字参数
def create_profile(name, age, city, occupation):
    """创建个人资料"""
    return {
        "name": name,
        "age": age,
        "city": city,
        "occupation": occupation
    }

# 使用关键字参数，顺序可以不同
profile = create_profile(
    city="上海",
    name="赵六",
    occupation="工程师",
    age=30
)
print(f"个人资料: {profile}")

# 可变位置参数 (*args)
def sum_all(*numbers):
    """计算所有数字的和"""
    total = 0
    for num in numbers:
        total += num
    return total

print(f"sum_all(1, 2, 3) = {sum_all(1, 2, 3)}")
print(f"sum_all(1, 2, 3, 4, 5) = {sum_all(1, 2, 3, 4, 5)}")

# 可变关键字参数 (**kwargs)
def print_info(**info):
    """打印所有信息"""
    for key, value in info.items():
        print(f"  {key}: {value}")

print("学生信息:")
print_info(name="孙七", age=22, major="计算机科学", gpa=3.8)

# 混合使用参数
def complex_function(pos1, pos2, default1="默认值", *args, **kwargs):
    """演示混合参数"""
    print(f"位置参数: {pos1}, {pos2}")
    print(f"默认参数: {default1}")
    print(f"可变位置参数: {args}")
    print(f"可变关键字参数: {kwargs}")

print("\n混合参数示例:")
complex_function(1, 2, "自定义", 3, 4, 5, key1="value1", key2="value2")

# ============================================================
# 3. 返回值
# ============================================================

print("\n" + "=" * 50)
print("返回值:")
print("=" * 50)

# 返回单个值
def square(x):
    """计算平方"""
    return x ** 2

print(f"5 的平方: {square(5)}")

# 返回多个值（实际返回元组）
def get_min_max(numbers):
    """返回列表的最小值和最大值"""
    return min(numbers), max(numbers)

nums = [3, 7, 2, 9, 1, 5]
min_val, max_val = get_min_max(nums)
print(f"列表 {nums} 的最小值: {min_val}, 最大值: {max_val}")

# 返回字典
def calculate_stats(numbers):
    """计算统计信息"""
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }

stats = calculate_stats([1, 2, 3, 4, 5])
print(f"统计信息: {stats}")

# 没有返回值（返回 None）
def print_message(message):
    """只打印消息，不返回值"""
    print(message)

result = print_message("这是一条消息")
print(f"返回值: {result}")  # None

# ============================================================
# 4. 作用域
# ============================================================

print("\n" + "=" * 50)
print("作用域:")
print("=" * 50)

# 全局变量
global_var = "我是全局变量"

def test_scope():
    """测试作用域"""
    local_var = "我是局部变量"
    print(f"函数内部 - 全局变量: {global_var}")
    print(f"函数内部 - 局部变量: {local_var}")

test_scope()
print(f"函数外部 - 全局变量: {global_var}")
# print(local_var)  # 错误：局部变量在函数外不可访问

# 修改全局变量
counter = 0

def increment():
    """增加计数器"""
    global counter  # 声明使用全局变量
    counter += 1
    print(f"计数器: {counter}")

increment()
increment()
increment()

# 嵌套函数和闭包
def outer_function(x):
    """外部函数"""
    def inner_function(y):
        """内部函数"""
        return x + y
    return inner_function

add_5 = outer_function(5)
print(f"\n闭包示例:")
print(f"add_5(3) = {add_5(3)}")
print(f"add_5(10) = {add_5(10)}")

# ============================================================
# 5. Lambda 函数
# ============================================================

print("\n" + "=" * 50)
print("Lambda 函数:")
print("=" * 50)

# 基本 lambda 函数
square = lambda x: x ** 2
print(f"lambda 平方: square(4) = {square(4)}")

# 多参数 lambda
add = lambda x, y: x + y
print(f"lambda 加法: add(3, 5) = {add(3, 5)}")

# lambda 在排序中的应用
students = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 78}
]

# 按分数排序
sorted_students = sorted(students, key=lambda s: s["score"], reverse=True)
print("\n按分数排序:")
for student in sorted_students:
    print(f"  {student['name']}: {student['score']}")

# lambda 在 map() 中的应用
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(f"\nmap() 示例: {numbers} -> {squared}")

# lambda 在 filter() 中的应用
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(f"filter() 示例: {numbers} -> {even_numbers}")

# ============================================================
# 6. 装饰器基础
# ============================================================

print("\n" + "=" * 50)
print("装饰器基础:")
print("=" * 50)

# 简单装饰器
def my_decorator(func):
    """简单装饰器"""
    def wrapper():
        print("函数执行前")
        func()
        print("函数执行后")
    return wrapper

@my_decorator
def say_hello():
    """被装饰的函数"""
    print("Hello!")

say_hello()

# 带参数的装饰器
def decorator_with_args(func):
    """处理带参数的函数"""
    def wrapper(*args, **kwargs):
        print(f"调用函数: {func.__name__}")
        print(f"参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"返回值: {result}")
        return result
    return wrapper

@decorator_with_args
def multiply(a, b):
    """乘法函数"""
    return a * b

print("\n带参数的装饰器:")
multiply(3, 4)

# 计时装饰器
import time

def timer(func):
    """计算函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

@timer
def slow_function():
    """模拟耗时操作"""
    time.sleep(0.1)
    return "完成"

print("\n计时装饰器:")
slow_function()

# ============================================================
# 7. 文档字符串和类型提示
# ============================================================

print("\n" + "=" * 50)
print("文档字符串和类型提示:")
print("=" * 50)

def calculate_area(length: float, width: float) -> float:
    """
    计算矩形面积
    
    Args:
        length: 矩形长度
        width: 矩形宽度
    
    Returns:
        矩形面积
    
    Examples:
        >>> calculate_area(5, 3)
        15.0
    """
    return length * width

# 查看文档字符串
print(f"函数文档:\n{calculate_area.__doc__}")

# 使用函数
area = calculate_area(5.0, 3.0)
print(f"面积: {area}")

# ============================================================
# 8. 实际应用示例
# ============================================================

print("\n" + "=" * 50)
print("实际应用示例:")
print("=" * 50)

# 示例1：数据验证函数
def validate_email(email):
    """简单的邮箱验证"""
    if "@" in email and "." in email:
        return True
    return False

emails = ["test@example.com", "invalid.email", "user@domain.org"]
print("邮箱验证:")
for email in emails:
    is_valid = validate_email(email)
    print(f"  {email}: {'有效' if is_valid else '无效'}")

# 示例2：数据处理管道
def clean_text(text):
    """清理文本"""
    return text.strip().lower()

def remove_punctuation(text):
    """移除标点符号"""
    import string
    return text.translate(str.maketrans('', '', string.punctuation))

def count_words(text):
    """统计单词数"""
    return len(text.split())

def process_text(text):
    """文本处理管道"""
    text = clean_text(text)
    text = remove_punctuation(text)
    word_count = count_words(text)
    return text, word_count

print("\n文本处理:")
original = "  Hello, World! This is Python.  "
processed, count = process_text(original)
print(f"原文: '{original}'")
print(f"处理后: '{processed}'")
print(f"单词数: {count}")

# 示例3：递归函数
def factorial(n):
    """计算阶乘"""
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

print("\n阶乘计算:")
for i in range(6):
    print(f"  {i}! = {factorial(i)}")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("""
函数要点:
1. 使用 def 定义函数
2. 参数类型:
   - 位置参数: def func(a, b)
   - 默认参数: def func(a, b=10)
   - 可变位置参数: def func(*args)
   - 可变关键字参数: def func(**kwargs)
3. 使用 return 返回值
4. 作用域: 局部变量、全局变量、闭包
5. Lambda: 匿名函数，lambda x: x + 1
6. 装饰器: 修改函数行为，@decorator
7. 文档字符串: 使用三引号编写函数说明

最佳实践:
- 函数应该只做一件事
- 使用有意义的函数名
- 添加文档字符串
- 使用类型提示（Python 3.5+）
- 避免过多参数（建议不超过5个）
""")
