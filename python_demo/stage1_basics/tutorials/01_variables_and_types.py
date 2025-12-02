"""
Python 基础教程 01: 变量和数据类型

本教程涵盖:
- 变量的定义和命名规则
- Python 的基本数据类型
- 类型转换
- 基本运算符
"""

# ============================================================
# 1. 变量定义
# ============================================================

# Python 是动态类型语言，不需要声明变量类型
name = "张三"  # 字符串
age = 25  # 整数
height = 1.75  # 浮点数
is_student = True  # 布尔值

print("变量示例:")
print(f"姓名: {name}, 年龄: {age}, 身高: {height}m, 是否学生: {is_student}")
print()

# 变量命名规则:
# 1. 只能包含字母、数字和下划线
# 2. 不能以数字开头
# 3. 不能使用 Python 关键字
# 4. 区分大小写
# 5. 推荐使用小写字母和下划线（snake_case）

user_name = "正确的命名"  # 推荐
userName = "驼峰命名"  # 也可以，但不推荐
# 2user = "错误"  # 错误：不能以数字开头
# class = "错误"  # 错误：class 是关键字

# ============================================================
# 2. 数字类型
# ============================================================

print("=" * 50)
print("数字类型:")
print("=" * 50)

# 整数 (int)
integer_num = 100
negative_num = -50
large_num = 1_000_000  # 可以使用下划线分隔，提高可读性

print(f"整数: {integer_num}, {negative_num}, {large_num}")

# 浮点数 (float)
float_num = 3.14
scientific_num = 1.5e3  # 科学计数法，等于 1500.0

print(f"浮点数: {float_num}, {scientific_num}")

# 复数 (complex)
complex_num = 3 + 4j
print(f"复数: {complex_num}")

# 数字运算
a = 10
b = 3

print(f"\n数字运算 (a={a}, b={b}):")
print(f"加法: {a} + {b} = {a + b}")
print(f"减法: {a} - {b} = {a - b}")
print(f"乘法: {a} * {b} = {a * b}")
print(f"除法: {a} / {b} = {a / b}")  # 结果是浮点数
print(f"整除: {a} // {b} = {a // b}")  # 向下取整
print(f"取余: {a} % {b} = {a % b}")
print(f"幂运算: {a} ** {b} = {a ** b}")

# ============================================================
# 3. 字符串类型 (str)
# ============================================================

print("\n" + "=" * 50)
print("字符串类型:")
print("=" * 50)

# 字符串定义
single_quote = '单引号字符串'
double_quote = "双引号字符串"
triple_quote = """三引号字符串
可以跨越多行"""

print(single_quote)
print(double_quote)
print(triple_quote)

# 字符串操作
text = "Python Programming"

print(f"\n字符串操作:")
print(f"原字符串: {text}")
print(f"长度: {len(text)}")
print(f"转大写: {text.upper()}")
print(f"转小写: {text.lower()}")
print(f"首字母大写: {text.capitalize()}")
print(f"替换: {text.replace('Python', 'Java')}")

# 字符串索引和切片
print(f"\n字符串索引和切片:")
print(f"第一个字符: {text[0]}")
print(f"最后一个字符: {text[-1]}")
print(f"前6个字符: {text[0:6]}")
print(f"从第7个到结尾: {text[7:]}")
print(f"倒数5个字符: {text[-5:]}")

# 字符串拼接
first_name = "张"
last_name = "三"
full_name = first_name + last_name
print(f"\n字符串拼接: {full_name}")

# 字符串格式化
name = "李四"
age = 30
# 方法1: f-string (推荐，Python 3.6+)
message1 = f"我叫{name}，今年{age}岁"
# 方法2: format()
message2 = "我叫{}，今年{}岁".format(name, age)
# 方法3: % 格式化（旧式）
message3 = "我叫%s，今年%d岁" % (name, age)

print(f"\n字符串格式化:")
print(message1)
print(message2)
print(message3)

# ============================================================
# 4. 布尔类型 (bool)
# ============================================================

print("\n" + "=" * 50)
print("布尔类型:")
print("=" * 50)

is_active = True
is_deleted = False

print(f"is_active: {is_active}")
print(f"is_deleted: {is_deleted}")

# 布尔运算
print(f"\n布尔运算:")
print(f"True and False = {True and False}")
print(f"True or False = {True or False}")
print(f"not True = {not True}")

# 比较运算符返回布尔值
x = 5
y = 10

print(f"\n比较运算 (x={x}, y={y}):")
print(f"x == y: {x == y}")  # 等于
print(f"x != y: {x != y}")  # 不等于
print(f"x > y: {x > y}")  # 大于
print(f"x < y: {x < y}")  # 小于
print(f"x >= y: {x >= y}")  # 大于等于
print(f"x <= y: {x <= y}")  # 小于等于

# ============================================================
# 5. 列表 (list)
# ============================================================

print("\n" + "=" * 50)
print("列表类型:")
print("=" * 50)

# 列表是可变的有序集合
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "文本", 3.14, True]  # 可以包含不同类型

print(f"水果列表: {fruits}")
print(f"数字列表: {numbers}")
print(f"混合列表: {mixed}")

# 列表操作
print(f"\n列表操作:")
print(f"第一个水果: {fruits[0]}")
print(f"最后一个水果: {fruits[-1]}")
print(f"列表长度: {len(fruits)}")

# 添加元素
fruits.append("西瓜")  # 在末尾添加
print(f"添加后: {fruits}")

# 插入元素
fruits.insert(1, "草莓")  # 在索引1处插入
print(f"插入后: {fruits}")

# 删除元素
fruits.remove("香蕉")  # 删除指定元素
print(f"删除后: {fruits}")

# 列表切片
print(f"前3个元素: {fruits[0:3]}")

# ============================================================
# 6. 元组 (tuple)
# ============================================================

print("\n" + "=" * 50)
print("元组类型:")
print("=" * 50)

# 元组是不可变的有序集合
coordinates = (10, 20)
person = ("张三", 25, "北京")

print(f"坐标: {coordinates}")
print(f"个人信息: {person}")

# 元组解包
x, y = coordinates
name, age, city = person
print(f"\n元组解包:")
print(f"x={x}, y={y}")
print(f"姓名={name}, 年龄={age}, 城市={city}")

# 注意：元组不可修改
# coordinates[0] = 15  # 这会报错

# ============================================================
# 7. 字典 (dict)
# ============================================================

print("\n" + "=" * 50)
print("字典类型:")
print("=" * 50)

# 字典是键值对的集合
student = {
    "name": "王五",
    "age": 22,
    "major": "计算机科学",
    "gpa": 3.8
}

print(f"学生信息: {student}")

# 访问字典
print(f"\n访问字典:")
print(f"姓名: {student['name']}")
print(f"年龄: {student.get('age')}")  # 推荐使用 get()，不存在时返回 None

# 修改字典
student["age"] = 23
student["email"] = "wangwu@example.com"  # 添加新键值对
print(f"\n修改后: {student}")

# 字典操作
print(f"\n字典操作:")
print(f"所有键: {student.keys()}")
print(f"所有值: {student.values()}")
print(f"所有键值对: {student.items()}")

# ============================================================
# 8. 集合 (set)
# ============================================================

print("\n" + "=" * 50)
print("集合类型:")
print("=" * 50)

# 集合是无序的不重复元素集
numbers_set = {1, 2, 3, 4, 5}
fruits_set = {"苹果", "香蕉", "橙子"}

print(f"数字集合: {numbers_set}")
print(f"水果集合: {fruits_set}")

# 集合会自动去重
duplicate_set = {1, 2, 2, 3, 3, 3}
print(f"去重后: {duplicate_set}")

# 集合操作
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}

print(f"\n集合运算:")
print(f"A: {set_a}")
print(f"B: {set_b}")
print(f"并集: {set_a | set_b}")
print(f"交集: {set_a & set_b}")
print(f"差集: {set_a - set_b}")

# ============================================================
# 9. None 类型
# ============================================================

print("\n" + "=" * 50)
print("None 类型:")
print("=" * 50)

# None 表示空值或无值
result = None
print(f"result 的值: {result}")
print(f"result 是 None: {result is None}")

# ============================================================
# 10. 类型转换
# ============================================================

print("\n" + "=" * 50)
print("类型转换:")
print("=" * 50)

# 字符串转数字
str_num = "123"
int_num = int(str_num)
float_num = float(str_num)
print(f"字符串 '{str_num}' 转整数: {int_num}")
print(f"字符串 '{str_num}' 转浮点数: {float_num}")

# 数字转字符串
num = 456
str_num = str(num)
print(f"数字 {num} 转字符串: '{str_num}'")

# 列表、元组、集合互转
my_list = [1, 2, 3, 2, 1]
my_tuple = tuple(my_list)
my_set = set(my_list)  # 会去重

print(f"\n容器类型转换:")
print(f"列表: {my_list}")
print(f"转元组: {my_tuple}")
print(f"转集合: {my_set}")

# ============================================================
# 11. 类型检查
# ============================================================

print("\n" + "=" * 50)
print("类型检查:")
print("=" * 50)

var = 42
print(f"变量值: {var}")
print(f"类型: {type(var)}")
print(f"是整数: {isinstance(var, int)}")
print(f"是字符串: {isinstance(var, str)}")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("""
Python 主要数据类型:
1. 数字: int, float, complex
2. 字符串: str
3. 布尔: bool
4. 列表: list (可变)
5. 元组: tuple (不可变)
6. 字典: dict (键值对)
7. 集合: set (无序不重复)
8. 空值: None

记住:
- 列表使用 []，可变
- 元组使用 ()，不可变
- 字典使用 {}，键值对
- 集合使用 {}，无序不重复
""")
