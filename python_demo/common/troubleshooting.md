# 故障排除指南

本指南收集了学习过程中常见的问题和解决方案，帮助你快速解决遇到的困难。

## 目录

- [环境搭建问题](#环境搭建问题)
- [Python 基础问题](#python-基础问题)
- [Web 框架问题](#web-框架问题)
- [数据库问题](#数据库问题)
- [依赖安装问题](#依赖安装问题)
- [IDE 配置问题](#ide-配置问题)
- [运行错误问题](#运行错误问题)
- [性能问题](#性能问题)

---

## 环境搭建问题

### 问题 1: Python 版本不匹配

**症状**: 运行代码时提示 Python 版本过低

**解决方案**:
```bash
# 检查当前 Python 版本
python --version
python3 --version

# 本课程需要 Python 3.9 或更高版本
# 如果版本过低，请从官网下载最新版本
# https://www.python.org/downloads/
```

### 问题 2: pip 命令不可用

**症状**: 执行 `pip` 命令时提示 "command not found"

**解决方案**:
```bash
# 尝试使用 pip3
pip3 --version

# 或者使用 python -m pip
python -m pip --version
python3 -m pip --version

# 如果仍然不可用，重新安装 pip
python -m ensurepip --upgrade
```

### 问题 3: 虚拟环境创建失败

**症状**: 执行 `python -m venv venv` 失败

**解决方案**:
```bash
# 确保安装了 venv 模块
# Ubuntu/Debian
sudo apt-get install python3-venv

# 或者使用 virtualenv
pip install virtualenv
virtualenv venv

# 激活虚拟环境
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 问题 4: 虚拟环境激活后仍使用全局 Python

**症状**: 激活虚拟环境后，`which python` 仍指向系统 Python

**解决方案**:
```bash
# 确认虚拟环境已激活（命令行前应有 (venv) 标识）
# 如果没有，重新激活
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 验证 Python 路径
which python    # Linux/Mac
where python    # Windows

# 应该指向虚拟环境中的 Python
```

---

## Python 基础问题

### 问题 5: 缩进错误 (IndentationError)

**症状**: `IndentationError: unexpected indent`

**解决方案**:
```python
# 错误示例
def my_function():
print("Hello")  # 缩进不正确

# 正确示例
def my_function():
    print("Hello")  # 使用 4 个空格缩进

# 建议：
# 1. 统一使用 4 个空格缩进（不要使用 Tab）
# 2. 配置 IDE 自动转换 Tab 为空格
# 3. 使用代码格式化工具（如 black）
```

### 问题 6: 模块导入失败 (ModuleNotFoundError)

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 1. 确认虚拟环境已激活
source venv/bin/activate

# 2. 安装缺失的模块
pip install xxx

# 3. 如果是自定义模块，检查文件路径和 __init__.py
# 4. 检查 PYTHONPATH 环境变量
echo $PYTHONPATH

# 5. 在代码中添加路径（临时方案）
import sys
sys.path.append('/path/to/your/module')
```

### 问题 7: 编码错误 (UnicodeDecodeError)

**症状**: `UnicodeDecodeError: 'utf-8' codec can't decode byte`

**解决方案**:
```python
# 读取文件时指定编码
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 如果文件编码未知，尝试其他编码
encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
for encoding in encodings:
    try:
        with open('file.txt', 'r', encoding=encoding) as f:
            content = f.read()
        break
    except UnicodeDecodeError:
        continue
```

---

## Web 框架问题

### 问题 8: FastAPI 启动失败

**症状**: 运行 `uvicorn main:app` 时报错

**解决方案**:
```bash
# 1. 确认安装了 uvicorn
pip install uvicorn[standard]

# 2. 检查文件名和应用实例名称
# 如果文件名是 main.py，应用实例是 app
uvicorn main:app --reload

# 3. 指定主机和端口
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. 检查代码中是否有语法错误
python main.py  # 先用 Python 检查语法
```

### 问题 9: Flask 应用无法访问

**症状**: Flask 应用启动后，浏览器无法访问

**解决方案**:
```python
# 确保设置了正确的 host
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# 或者使用环境变量
# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run --host=0.0.0.0 --port=5000
```

### 问题 10: CORS 错误

**症状**: 前端请求 API 时提示 CORS 错误

**解决方案**:
```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有来源
# 或者指定来源
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
```

### 问题 11: 请求体解析失败

**症状**: FastAPI 无法解析 JSON 请求体

**解决方案**:
```python
# 确保使用了正确的 Pydantic 模型
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item

# 前端请求时确保设置正确的 Content-Type
# Content-Type: application/json
```

---

## 数据库问题

### 问题 12: 数据库连接失败

**症状**: `sqlalchemy.exc.OperationalError: could not connect to server`

**解决方案**:
```python
# 1. 检查数据库服务是否运行
# PostgreSQL
sudo systemctl status postgresql

# MySQL
sudo systemctl status mysql

# 2. 检查连接字符串
# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

# MySQL
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/dbname"

# SQLite（开发环境）
DATABASE_URL = "sqlite:///./test.db"

# 3. 检查防火墙和端口
netstat -tuln | grep 5432  # PostgreSQL
netstat -tuln | grep 3306  # MySQL
```

### 问题 13: 表不存在错误

**症状**: `sqlalchemy.exc.ProgrammingError: relation "table_name" does not exist`

**解决方案**:
```python
# 1. 创建所有表
from database import engine, Base
from models import User, Item  # 导入所有模型

Base.metadata.create_all(bind=engine)

# 2. 或者使用 Alembic 进行数据库迁移
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 问题 14: 数据库锁定错误 (SQLite)

**症状**: `sqlite3.OperationalError: database is locked`

**解决方案**:
```python
# SQLite 不适合高并发场景
# 开发环境解决方案：

# 1. 增加超时时间
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False, "timeout": 30}
)

# 2. 生产环境建议使用 PostgreSQL 或 MySQL
```

---

## 依赖安装问题

### 问题 15: pip 安装速度慢

**症状**: pip 安装包时速度很慢或超时

**解决方案**:
```bash
# 使用国内镜像源
# 临时使用
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 或者编辑 ~/.pip/pip.conf (Linux/Mac)
# 或 %APPDATA%\pip\pip.ini (Windows)
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 16: 依赖冲突

**症状**: `ERROR: pip's dependency resolver does not currently take into account all the packages`

**解决方案**:
```bash
# 1. 升级 pip
pip install --upgrade pip

# 2. 使用 requirements.txt 指定版本
pip install -r requirements.txt

# 3. 创建新的虚拟环境
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 使用 pip-tools 管理依赖
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt
```

### 问题 17: 某些包安装失败

**症状**: 安装 mysqlclient、psycopg2 等包时编译失败

**解决方案**:
```bash
# mysqlclient 需要 MySQL 开发库
# Ubuntu/Debian
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# 或者使用纯 Python 实现
pip install pymysql

# psycopg2 需要 PostgreSQL 开发库
# Ubuntu/Debian
sudo apt-get install libpq-dev

# 或者使用二进制版本
pip install psycopg2-binary
```

---

## IDE 配置问题

### 问题 18: PyCharm 无法识别虚拟环境

**症状**: PyCharm 提示找不到模块，但命令行可以运行

**解决方案**:
1. 打开 PyCharm Settings/Preferences
2. 进入 Project > Python Interpreter
3. 点击齿轮图标 > Add
4. 选择 Existing Environment
5. 选择虚拟环境中的 Python 解释器
   - Linux/Mac: `venv/bin/python`
   - Windows: `venv\Scripts\python.exe`

### 问题 19: VSCode 无法激活虚拟环境

**症状**: VSCode 终端无法自动激活虚拟环境

**解决方案**:
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Python: Select Interpreter"
3. 选择虚拟环境中的 Python 解释器
4. 重新打开终端，应该会自动激活

或者手动配置 `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

### 问题 20: 代码格式化不一致

**症状**: 团队成员代码格式不统一

**解决方案**:
```bash
# 安装 black 格式化工具
pip install black

# 格式化代码
black .

# 配置 pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39']

# 配置 IDE 自动格式化
# PyCharm: Settings > Tools > Black
# VSCode: 安装 Black Formatter 扩展
```

---

## 运行错误问题

### 问题 21: 端口已被占用

**症状**: `OSError: [Errno 48] Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
# Linux/Mac
lsof -i :8000
netstat -tuln | grep 8000

# Windows
netstat -ano | findstr :8000

# 杀死进程
# Linux/Mac
kill -9 <PID>

# Windows
taskkill /PID <PID> /F

# 或者使用其他端口
uvicorn main:app --port 8001
```

### 问题 22: 环境变量未加载

**症状**: 代码中读取环境变量返回 None

**解决方案**:
```python
# 1. 使用 python-dotenv 加载 .env 文件
pip install python-dotenv

# 在代码开头
from dotenv import load_dotenv
load_dotenv()

import os
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. 创建 .env 文件
# DATABASE_URL=postgresql://user:pass@localhost/db
# SECRET_KEY=your-secret-key

# 3. 确保 .env 文件在正确的位置
# 通常在项目根目录
```

### 问题 23: 异步函数调用错误

**症状**: `RuntimeWarning: coroutine was never awaited`

**解决方案**:
```python
# 错误示例
async def get_data():
    return "data"

result = get_data()  # 错误：没有 await

# 正确示例
result = await get_data()  # 在异步函数中使用 await

# 或者在同步代码中
import asyncio
result = asyncio.run(get_data())
```

---

## 性能问题

### 问题 24: API 响应慢

**症状**: API 请求响应时间过长

**解决方案**:
```python
# 1. 使用数据库连接池
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# 2. 添加数据库索引
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # 添加索引

# 3. 使用异步数据库驱动
# pip install asyncpg  # PostgreSQL
# pip install aiomysql  # MySQL

# 4. 实现缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_settings():
    return Settings()

# 5. 使用 Redis 缓存
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

### 问题 25: 内存占用过高

**症状**: 应用运行一段时间后内存持续增长

**解决方案**:
```python
# 1. 及时关闭数据库连接
from contextlib import contextmanager

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. 分页查询大量数据
def get_users(skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# 3. 使用生成器处理大文件
def read_large_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield line

# 4. 定期清理缓存
import gc
gc.collect()
```

---

## 常用调试技巧

### 使用 print 调试
```python
# 基础调试
print(f"变量值: {variable}")
print(f"类型: {type(variable)}")

# 使用 pprint 格式化输出
from pprint import pprint
pprint(complex_dict)
```

### 使用 logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 使用 pdb 调试器
```python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # 设置断点
    y = x * 2
    return y

# 常用命令：
# n (next): 下一行
# s (step): 进入函数
# c (continue): 继续执行
# p variable: 打印变量
# q (quit): 退出调试
```

### 使用 IDE 调试器
- PyCharm: 点击行号设置断点，点击 Debug 按钮
- VSCode: 点击行号设置断点，按 F5 开始调试

---

## 获取帮助

如果以上方案都无法解决你的问题：

1. **查阅官方文档**
   - [Python 文档](https://docs.python.org/zh-cn/3/)
   - [FastAPI 文档](https://fastapi.tiangolo.com/zh/)
   - [Flask 文档](https://flask.palletsprojects.com/)

2. **搜索错误信息**
   - 复制完整的错误信息到搜索引擎
   - 查看 Stack Overflow 相关问题

3. **查看项目 Issues**
   - GitHub 项目的 Issues 页面
   - 可能有人遇到过相同问题

4. **社区求助**
   - Python 中文社区
   - 相关技术论坛
   - 技术交流群

---

## 预防问题的最佳实践

1. **使用虚拟环境**: 每个项目独立的虚拟环境
2. **版本管理**: 使用 requirements.txt 固定依赖版本
3. **代码规范**: 遵循 PEP 8 编码规范
4. **错误处理**: 添加适当的异常处理
5. **日志记录**: 记录关键操作和错误信息
6. **单元测试**: 编写测试确保代码质量
7. **文档注释**: 为复杂逻辑添加注释
8. **版本控制**: 使用 Git 管理代码

---

**提示**: 本指南会持续更新，添加更多常见问题和解决方案。
