"""
Python 基础教程 02: 控制流

本教程涵盖:
- if/elif/else 条件语句
- for 循环
- while 循环
- break 和 continue
- pass 语句
- 列表推导式
"""

# ============================================================
# 1. if 条件语句
# ============================================================

print("=" * 50)
print("if 条件语句:")
print("=" * 50)

# 基本 if 语句
age = 18
if age >= 18:
    print(f"年龄 {age}，已成年")

# if-else 语句
score = 85
if score >= 60:
    print(f"分数 {score}，及格了")
else:
    print(f"分数 {score}，不及格")

# if-elif-else 语句
score = 75
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"分数 {score}，等级 {grade}")

# 多条件判断
temperature = 25
is_raining = False

if temperature > 30 and not is_raining:
    print("天气炎热且没下雨，适合游泳")
elif temperature > 20 and not is_raining:
    print("天气温暖且没下雨，适合散步")
elif is_raining:
    print("下雨了，待在室内")
else:
    print("天气较冷")

# 三元运算符（条件表达式）
age = 20
status = "成年人" if age >= 18 else "未成年人"
print(f"年龄 {age}，状态: {status}")

# ============================================================
# 2. for 循环
# ============================================================

print("\n" + "=" * 50)
print("for 循环:")
print("=" * 50)

# 遍历列表
fruits = ["苹果", "香蕉", "橙子", "葡萄"]
print("水果列表:")
for fruit in fruits:
    print(f"  - {fruit}")

# 遍历字符串
text = "Python"
print(f"\n遍历字符串 '{text}':")
for char in text:
    print(f"  {char}")

# 使用 range() 函数
print("\n使用 range(5):")
for i in range(5):  # 0 到 4
    print(f"  {i}")

print("\nrange(1, 6):")
for i in range(1, 6):  # 1 到 5
    print(f"  {i}")

print("\nrange(0, 10, 2):")
for i in range(0, 10, 2):  # 0 到 9，步长为 2
    print(f"  {i}")

# 遍历字典
student = {
    "name": "张三",
    "age": 22,
    "major": "计算机科学"
}

print("\n遍历字典的键:")
for key in student.keys():
    print(f"  {key}")

print("\n遍历字典的值:")
for value in student.values():
    print(f"  {value}")

print("\n遍历字典的键值对:")
for key, value in student.items():
    print(f"  {key}: {value}")

# enumerate() 函数：同时获取索引和值
print("\n使用 enumerate():")
colors = ["红色", "绿色", "蓝色"]
for index, color in enumerate(colors):
    print(f"  索引 {index}: {color}")

# 从 1 开始计数
print("\nenumerate() 从 1 开始:")
for index, color in enumerate(colors, start=1):
    print(f"  第 {index} 个颜色: {color}")

# zip() 函数：并行遍历多个序列
print("\n使用 zip():")
names = ["张三", "李四", "王五"]
ages = [25, 30, 28]
cities = ["北京", "上海", "广州"]

for name, age, city in zip(names, ages, cities):
    print(f"  {name}, {age}岁, 来自{city}")

# ============================================================
# 3. while 循环
# ============================================================

print("\n" + "=" * 50)
print("while 循环:")
print("=" * 50)

# 基本 while 循环
count = 0
print("倒计时:")
while count < 5:
    print(f"  {count}")
    count += 1

# while 循环实现累加
print("\n计算 1 到 10 的和:")
total = 0
number = 1
while number <= 10:
    total += number
    number += 1
print(f"  结果: {total}")

# 无限循环（需要 break 退出）
print("\n模拟用户输入（输入 'quit' 退出）:")
# 注意：这里用计数器模拟，实际应用中使用 input()
attempts = 0
while True:
    attempts += 1
    if attempts > 3:
        print("  模拟输入 'quit'")
        break
    print(f"  第 {attempts} 次循环")

# ============================================================
# 4. break 和 continue
# ============================================================

print("\n" + "=" * 50)
print("break 和 continue:")
print("=" * 50)

# break: 立即退出循环
print("使用 break 查找第一个偶数:")
numbers = [1, 3, 5, 8, 9, 10, 11]
for num in numbers:
    if num % 2 == 0:
        print(f"  找到第一个偶数: {num}")
        break

# continue: 跳过当前迭代，继续下一次
print("\n使用 continue 跳过奇数:")
for num in range(1, 11):
    if num % 2 != 0:
        continue  # 跳过奇数
    print(f"  偶数: {num}")

# 实际应用：过滤数据
print("\n过滤负数和零:")
numbers = [5, -2, 0, 8, -1, 3, 0, 7]
for num in numbers:
    if num <= 0:
        continue
    print(f"  正数: {num}")

# ============================================================
# 5. pass 语句
# ============================================================

print("\n" + "=" * 50)
print("pass 语句:")
print("=" * 50)

# pass 是空操作，用作占位符
print("pass 用作占位符:")
for i in range(3):
    if i == 1:
        pass  # 暂时不做任何事，但保持语法完整
    else:
        print(f"  i = {i}")

# pass 在函数和类定义中的使用
def future_function():
    """这个函数将来会实现"""
    pass  # 占位符，避免语法错误

class FutureClass:
    """这个类将来会实现"""
    pass

print("  pass 语句执行完毕（无输出）")

# ============================================================
# 6. 嵌套循环
# ============================================================

print("\n" + "=" * 50)
print("嵌套循环:")
print("=" * 50)

# 打印乘法表
print("九九乘法表:")
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}×{i}={i*j:2d}", end="  ")
    print()  # 换行

# 二维列表遍历
print("\n遍历二维列表:")
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

for row in matrix:
    for element in row:
        print(f"{element:2d}", end=" ")
    print()

# ============================================================
# 7. 列表推导式
# ============================================================

print("\n" + "=" * 50)
print("列表推导式:")
print("=" * 50)

# 基本列表推导式
squares = [x**2 for x in range(1, 6)]
print(f"平方数: {squares}")

# 带条件的列表推导式
even_numbers = [x for x in range(1, 11) if x % 2 == 0]
print(f"偶数: {even_numbers}")

# 对字符串列表进行操作
fruits = ["apple", "banana", "cherry"]
upper_fruits = [fruit.upper() for fruit in fruits]
print(f"大写水果: {upper_fruits}")

# 嵌套列表推导式
matrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]
print(f"矩阵:\n{matrix}")

# 带 if-else 的列表推导式
numbers = [1, 2, 3, 4, 5]
labels = ["偶数" if x % 2 == 0 else "奇数" for x in numbers]
print(f"数字标签: {labels}")

# ============================================================
# 8. 字典推导式
# ============================================================

print("\n" + "=" * 50)
print("字典推导式:")
print("=" * 50)

# 创建平方字典
squares_dict = {x: x**2 for x in range(1, 6)}
print(f"平方字典: {squares_dict}")

# 过滤字典
scores = {"张三": 85, "李四": 92, "王五": 78, "赵六": 95}
high_scores = {name: score for name, score in scores.items() if score >= 90}
print(f"高分学生: {high_scores}")

# ============================================================
# 9. 集合推导式
# ============================================================

print("\n" + "=" * 50)
print("集合推导式:")
print("=" * 50)

# 创建集合（自动去重）
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 5]
unique_squares = {x**2 for x in numbers}
print(f"唯一平方数: {unique_squares}")

# ============================================================
# 10. 实际应用示例
# ============================================================

print("\n" + "=" * 50)
print("实际应用示例:")
print("=" * 50)

# 示例1：查找列表中的最大值
numbers = [23, 45, 12, 67, 34, 89, 15]
max_num = numbers[0]
for num in numbers:
    if num > max_num:
        max_num = num
print(f"最大值: {max_num}")
print(f"使用内置函数: {max(numbers)}")

# 示例2：统计字符串中各字符出现次数
text = "hello world"
char_count = {}
for char in text:
    if char != ' ':  # 忽略空格
        char_count[char] = char_count.get(char, 0) + 1
print(f"\n字符统计: {char_count}")

# 示例3：过滤和转换数据
students = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 78},
    {"name": "赵六", "score": 95}
]

print("\n及格学生:")
for student in students:
    if student["score"] >= 80:
        print(f"  {student['name']}: {student['score']}分")

# 示例4：生成斐波那契数列
print("\n斐波那契数列（前10项）:")
fib = [0, 1]
for i in range(8):
    fib.append(fib[-1] + fib[-2])
print(f"  {fib}")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("""
控制流语句:
1. if/elif/else: 条件判断
2. for: 遍历序列
3. while: 条件循环
4. break: 退出循环
5. continue: 跳过当前迭代
6. pass: 占位符

推导式:
- 列表推导式: [expr for item in iterable if condition]
- 字典推导式: {key: value for item in iterable if condition}
- 集合推导式: {expr for item in iterable if condition}

常用函数:
- range(): 生成数字序列
- enumerate(): 获取索引和值
- zip(): 并行遍历多个序列
""")
