"""
Python 基础教程 05: 模块和包

本教程涵盖:
- 模块的导入和使用
- 创建自定义模块
- 包的概念和使用
- 常用标准库模块
- __name__ 和 __main__
"""

# ============================================================
# 1. 导入模块
# ============================================================

print("=" * 50)
print("导入模块:")
print("=" * 50)

# 方式1：导入整个模块
import math
print(f"圆周率: {math.pi}")
print(f"平方根: {math.sqrt(16)}")

# 方式2：导入特定函数或变量
from math import pi, sqrt, pow
print(f"使用 from import: pi = {pi}, sqrt(25) = {sqrt(25)}")

# 方式3：导入所有内容（不推荐）
# from math import *

# 方式4：使用别名
import math as m
print(f"使用别名: m.pi = {m.pi}")

from math import sqrt as square_root
print(f"函数别名: square_root(36) = {square_root(36)}")

# ============================================================
# 2. 常用标准库模块
# ============================================================

print("\n" + "=" * 50)
print("常用标准库模块:")
print("=" * 50)

# datetime - 日期和时间
from datetime import datetime, date, timedelta

now = datetime.now()
print(f"\n当前时间: {now}")
print(f"今天日期: {date.today()}")

tomorrow = date.today() + timedelta(days=1)
print(f"明天日期: {tomorrow}")

# random - 随机数
import random

print(f"\n随机整数 (1-10): {random.randint(1, 10)}")
print(f"随机浮点数 (0-1): {random.random()}")

colors = ["红", "绿", "蓝", "黄"]
print(f"随机选择: {random.choice(colors)}")

numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(f"打乱列表: {numbers}")

# os - 操作系统接口
import os

print(f"\n当前工作目录: {os.getcwd()}")
print(f"操作系统: {os.name}")
# print(f"环境变量 PATH: {os.environ.get('PATH')}")

# sys - 系统相关
import sys

print(f"\nPython 版本: {sys.version}")
print(f"平台: {sys.platform}")

# json - JSON 处理
import json

data = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

json_string = json.dumps(data, ensure_ascii=False)
print(f"\nJSON 字符串: {json_string}")

parsed_data = json.loads(json_string)
print(f"解析 JSON: {parsed_data}")

# collections - 容器数据类型
from collections import Counter, defaultdict, namedtuple

# Counter: 计数器
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
word_count = Counter(words)
print(f"\n单词计数: {word_count}")
print(f"最常见的2个: {word_count.most_common(2)}")

# defaultdict: 带默认值的字典
scores = defaultdict(int)
scores["张三"] += 10
scores["李四"] += 20
print(f"默认字典: {dict(scores)}")

# namedtuple: 命名元组
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(f"命名元组: x={p.x}, y={p.y}")

# itertools - 迭代工具
from itertools import count, cycle, repeat, chain

print(f"\nitertools 示例:")
print(f"count(10, 2) 前5个: {list(zip(range(5), count(10, 2)))}")
print(f"chain 合并: {list(chain([1, 2], [3, 4], [5, 6]))}")

# re - 正则表达式
import re

text = "我的邮箱是 user@example.com 和 test@domain.org"
emails = re.findall(r'\S+@\S+', text)
print(f"\n提取邮箱: {emails}")

# pathlib - 路径操作（现代方式）
from pathlib import Path

current_file = Path(__file__)
print(f"\n当前文件: {current_file.name}")
print(f"父目录: {current_file.parent}")

# ============================================================
# 3. 创建自定义模块
# ============================================================

print("\n" + "=" * 50)
print("创建自定义模块:")
print("=" * 50)

print("""
创建自定义模块步骤:

1. 创建 .py 文件，例如 mymodule.py:

# mymodule.py
def greet(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

PI = 3.14159

2. 在其他文件中导入:

import mymodule
print(mymodule.greet("张三"))
print(mymodule.add(5, 3))
print(mymodule.PI)

或者:

from mymodule import greet, add
print(greet("李四"))
print(add(10, 20))
""")

# ============================================================
# 4. 包的概念
# ============================================================

print("\n" + "=" * 50)
print("包的概念:")
print("=" * 50)

print("""
包是包含多个模块的目录，必须包含 __init__.py 文件。

目录结构示例:

mypackage/
├── __init__.py
├── module1.py
├── module2.py
└── subpackage/
    ├── __init__.py
    └── module3.py

使用包:

# 导入包中的模块
from mypackage import module1
from mypackage.subpackage import module3

# 导入特定函数
from mypackage.module1 import function_name

# __init__.py 可以包含初始化代码
# 也可以定义 __all__ 列表控制 from package import * 的行为
""")

# ============================================================
# 5. __name__ 和 __main__
# ============================================================

print("\n" + "=" * 50)
print("__name__ 和 __main__:")
print("=" * 50)

print(f"当前模块的 __name__: {__name__}")

print("""
__name__ 的作用:
- 当模块被直接运行时，__name__ == '__main__'
- 当模块被导入时，__name__ == 模块名

常见用法:

# mymodule.py
def main():
    print("这是主函数")

if __name__ == '__main__':
    # 只有直接运行此文件时才执行
    main()

这样可以:
1. 将模块作为脚本运行
2. 也可以被其他模块导入而不执行测试代码
""")

# ============================================================
# 6. 模块搜索路径
# ============================================================

print("\n" + "=" * 50)
print("模块搜索路径:")
print("=" * 50)

print("Python 搜索模块的顺序:")
print("1. 当前目录")
print("2. PYTHONPATH 环境变量指定的目录")
print("3. Python 标准库目录")
print("4. site-packages 目录（第三方包）")

print(f"\n实际搜索路径:")
for i, path in enumerate(sys.path[:5], 1):
    print(f"  {i}. {path}")

# ============================================================
# 7. 实用工具函数示例
# ============================================================

print("\n" + "=" * 50)
print("实用工具函数示例:")
print("=" * 50)

# 文件操作工具
def read_file(filename):
    """读取文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"文件 {filename} 不存在"

def write_file(filename, content):
    """写入文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# 数据验证工具
def is_valid_email(email):
    """简单的邮箱验证"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """简单的手机号验证（中国）"""
    import re
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

# 测试工具函数
print("邮箱验证:")
emails = ["test@example.com", "invalid.email", "user@domain.org"]
for email in emails:
    print(f"  {email}: {'有效' if is_valid_email(email) else '无效'}")

print("\n手机号验证:")
phones = ["13812345678", "12345678901", "18900001111"]
for phone in phones:
    print(f"  {phone}: {'有效' if is_valid_phone(phone) else '无效'}")

# 时间工具
def format_datetime(dt=None):
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_age(birth_date):
    """根据出生日期计算年龄"""
    today = date.today()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age

print(f"\n当前时间: {format_datetime()}")

birth = date(2000, 5, 15)
print(f"出生日期 {birth} 的年龄: {get_age(birth)} 岁")

# ============================================================
# 8. 第三方包管理
# ============================================================

print("\n" + "=" * 50)
print("第三方包管理:")
print("=" * 50)

print("""
使用 pip 管理第三方包:

# 安装包
pip install requests
pip install flask==2.3.0  # 安装特定版本

# 升级包
pip install --upgrade requests

# 卸载包
pip uninstall requests

# 查看已安装的包
pip list
pip freeze

# 从 requirements.txt 安装
pip install -r requirements.txt

# 生成 requirements.txt
pip freeze > requirements.txt

常用第三方包:
- requests: HTTP 请求
- flask/django: Web 框架
- pandas: 数据分析
- numpy: 科学计算
- pytest: 测试框架
- pillow: 图像处理
- beautifulsoup4: 网页解析
""")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("""
模块和包要点:

1. 导入方式:
   - import module
   - from module import function
   - import module as alias

2. 标准库常用模块:
   - math: 数学函数
   - datetime: 日期时间
   - random: 随机数
   - os: 操作系统接口
   - sys: 系统相关
   - json: JSON 处理
   - re: 正则表达式
   - collections: 容器类型
   - itertools: 迭代工具

3. 创建模块:
   - 创建 .py 文件
   - 定义函数、类、变量
   - 使用 if __name__ == '__main__' 添加测试代码

4. 创建包:
   - 创建目录
   - 添加 __init__.py
   - 组织多个模块

5. 最佳实践:
   - 使用有意义的模块名
   - 一个模块专注一个功能
   - 添加文档字符串
   - 使用 __all__ 控制导出
   - 避免循环导入
""")
