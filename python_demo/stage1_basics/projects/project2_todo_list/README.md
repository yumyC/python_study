# 项目2: 待办事项列表

## 项目简介

这是一个功能完整的待办事项管理系统，支持任务的增删改查，并将数据持久化保存到文件中。

## 功能特性

- ✅ 添加任务：支持标题、描述和优先级
- ✅ 查看任务：显示所有任务或仅未完成任务
- ✅ 完成任务：标记任务为已完成
- ✅ 删除任务：删除不需要的任务
- ✅ 清除已完成：批量清除已完成的任务
- ✅ 统计信息：显示任务完成情况
- ✅ 数据持久化：自动保存到 JSON 文件

## 运行说明

### 前置要求

- Python 3.6 或更高版本

### 运行程序

```bash
python todo.py
```

### 数据文件

程序会在当前目录创建 `tasks.json` 文件来保存任务数据。

## 使用方法

1. 运行程序后，会显示主菜单
2. 选择相应的操作编号
3. 根据提示输入信息
4. 任务会自动保存到文件
5. 下次运行时会自动加载之前的任务

## 示例操作

```
欢迎使用待办事项管理系统！

========================================
待办事项管理系统
========================================
1. 添加任务
2. 查看所有任务
3. 查看未完成任务
4. 标记任务完成
5. 删除任务
6. 清除已完成任务
7. 查看统计信息
0. 退出
========================================
请选择操作 (0-7): 1
请输入任务标题: 学习 Python
请输入任务描述 (可选): 完成基础教程
选择优先级:
1. 高
2. 中
3. 低
请选择 (1-3, 默认为中): 1
✓ 任务已添加: 学习 Python
```

## 代码结构

```
project2_todo_list/
├── todo.py          # 主程序文件
├── README.md        # 项目说明文档
└── tasks.json       # 任务数据文件（自动生成）
```

## 核心代码说明

### Task 类

```python
class Task:
    def __init__(self, title, description="", priority="中"):
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.created_at = datetime.now()
    
    def to_dict(self):
        # 转换为字典，用于 JSON 序列化
        pass
    
    @classmethod
    def from_dict(cls, data):
        # 从字典创建任务，用于 JSON 反序列化
        pass
```

### TodoList 类

```python
class TodoList:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()  # 启动时加载任务
    
    def save_tasks(self):
        # 保存任务到 JSON 文件
        pass
    
    def load_tasks(self):
        # 从 JSON 文件加载任务
        pass
```

## 学习要点

### 1. 面向对象设计
- Task 类：封装单个任务的数据和行为
- TodoList 类：管理任务列表和文件操作
- 类方法 (@classmethod)：用于对象的创建

### 2. 文件操作
- JSON 序列化和反序列化
- 文件读写
- 数据持久化

### 3. 数据结构
- 列表操作：添加、删除、过滤
- 字典操作：数据转换
- 列表推导式：过滤任务

### 4. 日期时间处理
- datetime 模块的使用
- 时间戳格式化

### 5. 用户交互
- 菜单驱动的程序设计
- 输入验证
- 确认操作

## 数据格式

### tasks.json 示例

```json
[
  {
    "title": "学习 Python",
    "description": "完成基础教程",
    "priority": "高",
    "completed": false,
    "created_at": "2024-01-01 10:00:00"
  },
  {
    "title": "写项目文档",
    "description": "",
    "priority": "中",
    "completed": true,
    "created_at": "2024-01-01 11:00:00"
  }
]
```

## 扩展练习

### 初级扩展
1. 添加任务编辑功能
2. 支持任务搜索
3. 添加截止日期

### 中级扩展
1. 支持任务分类（标签）
2. 任务排序（按优先级、日期）
3. 导出任务到 CSV 文件

### 高级扩展
1. 实现图形界面
2. 添加提醒功能
3. 支持多用户
4. 云端同步

## 常见问题

### Q: 数据保存在哪里？
A: 保存在程序目录下的 `tasks.json` 文件中

### Q: 如何备份数据？
A: 复制 `tasks.json` 文件即可

### Q: 删除任务可以恢复吗？
A: 当前版本不支持恢复，建议在删除前确认

### Q: 可以同时运行多个实例吗？
A: 可以，但会共享同一个数据文件，可能导致数据冲突

## 相关知识点

- 类和对象
- 文件读写
- JSON 处理
- 日期时间
- 列表操作
- 字典操作
- 异常处理
- 用户输入

## 下一步

完成这个项目后，可以继续学习：
- [项目1: 计算器](../project1_calculator/)
- [项目3: 文件管理器](../project3_file_manager/)
- 学习数据库（SQLite）来替代 JSON 文件
