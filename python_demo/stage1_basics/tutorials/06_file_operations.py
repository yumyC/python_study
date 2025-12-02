"""
Python 基础教程 06: 文件操作

本教程涵盖:
- 文件的打开和关闭
- 读取文件
- 写入文件
- 文件指针操作
- 上下文管理器
- 目录操作
- 路径处理
"""

import os
from pathlib import Path

# ============================================================
# 1. 文件的打开和关闭
# ============================================================

print("=" * 50)
print("文件的打开和关闭:")
print("=" * 50)

print("""
文件打开模式:
- 'r': 只读（默认）
- 'w': 写入（覆盖）
- 'a': 追加
- 'x': 创建新文件（文件存在则失败）
- 'b': 二进制模式
- 't': 文本模式（默认）
- '+': 读写模式

组合使用:
- 'rb': 二进制只读
- 'wb': 二进制写入
- 'r+': 读写
- 'w+': 读写（覆盖）
- 'a+': 追加读写
""")

# 基本方式（不推荐，需要手动关闭）
# file = open('example.txt', 'r')
# content = file.read()
# file.close()

# 推荐方式：使用 with 语句（自动关闭）
print("使用 with 语句打开文件（推荐）")

# ============================================================
# 2. 写入文件
# ============================================================

print("\n" + "=" * 50)
print("写入文件:")
print("=" * 50)

# 写入文本文件
filename = "demo_file.txt"

# 模式 'w': 覆盖写入
with open(filename, 'w', encoding='utf-8') as f:
    f.write("第一行文本\n")
    f.write("第二行文本\n")
    f.write("第三行文本\n")

print(f"已创建文件: {filename}")

# 模式 'a': 追加写入
with open(filename, 'a', encoding='utf-8') as f:
    f.write("追加的第四行\n")
    f.write("追加的第五行\n")

print(f"已追加内容到: {filename}")

# 写入多行
lines = [
    "这是第六行\n",
    "这是第七行\n",
    "这是第八行\n"
]

with open(filename, 'a', encoding='utf-8') as f:
    f.writelines(lines)

print(f"已写入多行到: {filename}")

# ============================================================
# 3. 读取文件
# ============================================================

print("\n" + "=" * 50)
print("读取文件:")
print("=" * 50)

# 方法1：读取整个文件
print("方法1: read() - 读取整个文件")
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 方法2：按行读取
print("\n方法2: readline() - 逐行读取")
with open(filename, 'r', encoding='utf-8') as f:
    line1 = f.readline()
    line2 = f.readline()
    print(f"第一行: {line1.strip()}")
    print(f"第二行: {line2.strip()}")

# 方法3：读取所有行到列表
print("\n方法3: readlines() - 读取所有行")
with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f"总共 {len(lines)} 行")
    for i, line in enumerate(lines[:3], 1):
        print(f"  行 {i}: {line.strip()}")

# 方法4：迭代文件对象（推荐，内存效率高）
print("\n方法4: 迭代文件对象（推荐）")
with open(filename, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if i <= 3:
            print(f"  行 {i}: {line.strip()}")

# 读取指定字节数
print("\n读取指定字节数:")
with open(filename, 'r', encoding='utf-8') as f:
    chunk = f.read(20)  # 读取前20个字符
    print(f"前20个字符: {chunk}")

# ============================================================
# 4. 文件指针操作
# ============================================================

print("\n" + "=" * 50)
print("文件指针操作:")
print("=" * 50)

with open(filename, 'r', encoding='utf-8') as f:
    # tell(): 获取当前指针位置
    print(f"初始位置: {f.tell()}")
    
    # 读取一些内容
    f.read(10)
    print(f"读取10字符后位置: {f.tell()}")
    
    # seek(): 移动指针
    f.seek(0)  # 移动到文件开头
    print(f"seek(0) 后位置: {f.tell()}")
    
    first_line = f.readline()
    print(f"从头读取第一行: {first_line.strip()}")

# ============================================================
# 5. 二进制文件操作
# ============================================================

print("\n" + "=" * 50)
print("二进制文件操作:")
print("=" * 50)

# 写入二进制文件
binary_file = "demo_binary.bin"
data = bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

with open(binary_file, 'wb') as f:
    f.write(data)

print(f"已写入二进制文件: {binary_file}")

# 读取二进制文件
with open(binary_file, 'rb') as f:
    binary_data = f.read()
    print(f"读取的二进制数据: {list(binary_data)}")

# ============================================================
# 6. 文件和目录检查
# ============================================================

print("\n" + "=" * 50)
print("文件和目录检查:")
print("=" * 50)

# 使用 os.path
print("使用 os.path:")
print(f"文件存在: {os.path.exists(filename)}")
print(f"是文件: {os.path.isfile(filename)}")
print(f"是目录: {os.path.isdir(filename)}")
print(f"文件大小: {os.path.getsize(filename)} 字节")
print(f"绝对路径: {os.path.abspath(filename)}")
print(f"文件名: {os.path.basename(filename)}")
print(f"目录名: {os.path.dirname(os.path.abspath(filename))}")

# 使用 pathlib（推荐，更现代）
print("\n使用 pathlib (推荐):")
file_path = Path(filename)
print(f"文件存在: {file_path.exists()}")
print(f"是文件: {file_path.is_file()}")
print(f"是目录: {file_path.is_dir()}")
print(f"文件大小: {file_path.stat().st_size} 字节")
print(f"绝对路径: {file_path.absolute()}")
print(f"文件名: {file_path.name}")
print(f"文件扩展名: {file_path.suffix}")
print(f"不含扩展名: {file_path.stem}")

# ============================================================
# 7. 目录操作
# ============================================================

print("\n" + "=" * 50)
print("目录操作:")
print("=" * 50)

# 创建目录
test_dir = "test_directory"

# 使用 os
if not os.path.exists(test_dir):
    os.mkdir(test_dir)
    print(f"创建目录: {test_dir}")

# 创建多级目录
nested_dir = "parent/child/grandchild"
os.makedirs(nested_dir, exist_ok=True)
print(f"创建多级目录: {nested_dir}")

# 列出目录内容
print(f"\n当前目录内容:")
for item in os.listdir('.')[:5]:
    print(f"  - {item}")

# 使用 pathlib
print(f"\n使用 pathlib 列出 Python 文件:")
current_path = Path('.')
for py_file in list(current_path.glob('*.py'))[:3]:
    print(f"  - {py_file.name}")

# 遍历目录树
print(f"\n遍历目录树（前5项）:")
count = 0
for root, dirs, files in os.walk('.'):
    if count >= 5:
        break
    print(f"目录: {root}")
    count += 1

# ============================================================
# 8. 文件操作实用函数
# ============================================================

print("\n" + "=" * 50)
print("文件操作实用函数:")
print("=" * 50)

def copy_file(source, destination):
    """复制文件"""
    with open(source, 'rb') as src:
        with open(destination, 'wb') as dst:
            dst.write(src.read())
    print(f"已复制: {source} -> {destination}")

def count_lines(filename):
    """统计文件行数"""
    with open(filename, 'r', encoding='utf-8') as f:
        return sum(1 for line in f)

def search_in_file(filename, keyword):
    """在文件中搜索关键词"""
    results = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if keyword in line:
                results.append((line_num, line.strip()))
    return results

def read_file_safe(filename, default=""):
    """安全读取文件（处理异常）"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filename}")
        return default
    except PermissionError:
        print(f"没有权限读取: {filename}")
        return default
    except Exception as e:
        print(f"读取文件出错: {e}")
        return default

# 测试实用函数
print(f"文件行数: {count_lines(filename)}")

search_results = search_in_file(filename, "第")
print(f"\n搜索 '第' 的结果:")
for line_num, line in search_results[:3]:
    print(f"  行 {line_num}: {line}")

# 复制文件
copy_file(filename, "demo_file_copy.txt")

# ============================================================
# 9. CSV 文件操作
# ============================================================

print("\n" + "=" * 50)
print("CSV 文件操作:")
print("=" * 50)

import csv

csv_file = "demo_data.csv"

# 写入 CSV
data = [
    ["姓名", "年龄", "城市"],
    ["张三", "25", "北京"],
    ["李四", "30", "上海"],
    ["王五", "28", "广州"]
]

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f"已创建 CSV 文件: {csv_file}")

# 读取 CSV
print("\n读取 CSV 文件:")
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(f"  {row}")

# 使用字典读写 CSV
print("\n使用 DictWriter:")
dict_data = [
    {"name": "赵六", "age": "32", "city": "深圳"},
    {"name": "孙七", "age": "27", "city": "杭州"}
]

with open(csv_file, 'a', newline='', encoding='utf-8') as f:
    fieldnames = ["name", "age", "city"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    for row in dict_data:
        writer.writerow(row)

# ============================================================
# 10. JSON 文件操作
# ============================================================

print("\n" + "=" * 50)
print("JSON 文件操作:")
print("=" * 50)

import json

json_file = "demo_data.json"

# 写入 JSON
data = {
    "students": [
        {"name": "张三", "age": 25, "courses": ["Python", "数据结构"]},
        {"name": "李四", "age": 30, "courses": ["算法", "数据库"]}
    ],
    "total": 2
}

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"已创建 JSON 文件: {json_file}")

# 读取 JSON
print("\n读取 JSON 文件:")
with open(json_file, 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)
    print(f"总学生数: {loaded_data['total']}")
    for student in loaded_data['students']:
        print(f"  {student['name']}: {', '.join(student['courses'])}")

# ============================================================
# 11. 异常处理
# ============================================================

print("\n" + "=" * 50)
print("文件操作异常处理:")
print("=" * 50)

def safe_file_operation(filename):
    """安全的文件操作示例"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        print(f"错误: 文件 '{filename}' 不存在")
    except PermissionError:
        print(f"错误: 没有权限访问 '{filename}'")
    except UnicodeDecodeError:
        print(f"错误: 文件编码问题")
    except Exception as e:
        print(f"未知错误: {e}")
    return None

# 测试异常处理
print("测试读取不存在的文件:")
safe_file_operation("nonexistent_file.txt")

# ============================================================
# 12. 清理演示文件
# ============================================================

print("\n" + "=" * 50)
print("清理演示文件:")
print("=" * 50)

# 删除创建的演示文件
demo_files = [filename, "demo_file_copy.txt", binary_file, csv_file, json_file]

for file in demo_files:
    if os.path.exists(file):
        os.remove(file)
        print(f"已删除: {file}")

# 删除创建的目录
import shutil
if os.path.exists(test_dir):
    os.rmdir(test_dir)
    print(f"已删除目录: {test_dir}")

if os.path.exists("parent"):
    shutil.rmtree("parent")
    print(f"已删除目录树: parent")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("""
文件操作要点:

1. 打开文件:
   - 使用 with 语句（推荐）
   - 指定编码 encoding='utf-8'
   - 选择正确的模式 ('r', 'w', 'a', 'b')

2. 读取文件:
   - read(): 读取全部
   - readline(): 读取一行
   - readlines(): 读取所有行
   - 迭代文件对象（推荐）

3. 写入文件:
   - write(): 写入字符串
   - writelines(): 写入多行

4. 路径操作:
   - os.path: 传统方式
   - pathlib.Path: 现代方式（推荐）

5. 目录操作:
   - os.mkdir(): 创建目录
   - os.makedirs(): 创建多级目录
   - os.listdir(): 列出目录内容
   - os.walk(): 遍历目录树

6. 特殊文件:
   - CSV: 使用 csv 模块
   - JSON: 使用 json 模块

7. 最佳实践:
   - 始终使用 with 语句
   - 处理异常
   - 指定编码
   - 使用 pathlib（Python 3.4+）
   - 大文件逐行处理
""")
