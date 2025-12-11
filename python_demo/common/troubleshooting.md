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

---

## 常见问题解答 (FAQ)

### 学习相关问题

#### Q1: 我完全没有编程经验，能学会 Python 吗？
**A**: 完全可以！本课程从零基础开始设计，循序渐进。只要：
- 保持学习热情和耐心
- 按照课程顺序学习，不要跳跃
- 多动手实践，运行每一个示例代码
- 遇到问题及时查阅文档或寻求帮助

#### Q2: 需要多长时间才能完成整个课程？
**A**: 因人而异，一般需要 4-6 个月：
- **第一阶段**: 2-4 周（Python 基础）
- **第二阶段**: 4-6 周（Web 框架与数据库）
- **第三阶段**: 3-4 周（企业特性）
- **第四阶段**: 2-3 周（测试与 CI/CD）
- **第五阶段**: 4-6 周（CRM 实战项目）

建议每天学习 2-3 小时，每周 5-6 天。

#### Q3: 学完后能找到工作吗？
**A**: 如果认真完成所有阶段，你将具备：
- Python 后端开发能力
- Web API 开发经验
- 数据库操作技能
- 企业级项目经验（CRM 系统）
- 完整的作品集

这些技能足以胜任初级到中级的 Python 开发岗位。

#### Q4: 需要什么样的电脑配置？
**A**: 基本配置即可：
- **操作系统**: Windows 10+、macOS 10.14+、Ubuntu 18.04+
- **内存**: 8GB 以上（推荐 16GB）
- **存储**: 至少 10GB 可用空间
- **处理器**: 双核以上

### 技术选择问题

#### Q5: FastAPI 和 Flask 应该学哪个？
**A**: 建议两个都学，但可以有侧重：
- **FastAPI**: 现代化、高性能、自动文档生成，适合 API 开发
- **Flask**: 简单灵活、生态丰富、学习曲线平缓

**建议顺序**: 先学 Flask 理解基础概念，再学 FastAPI 体验现代特性。

#### Q6: 数据库应该选择哪个？
**A**: 根据学习阶段选择：
- **学习阶段**: SQLite（无需安装，简单易用）
- **开发环境**: PostgreSQL（功能强大，开源免费）
- **生产环境**: PostgreSQL 或 MySQL（根据团队技术栈）

#### Q7: 需要学习前端吗？
**A**: 本课程主要专注后端开发，但：
- 第五阶段提供了前端示例（Vue.js）
- 理解前后端分离架构很重要
- 如果想成为全栈开发者，建议额外学习前端

### 环境配置问题

#### Q8: PyCharm 和 VSCode 选哪个？
**A**: 都是优秀的 IDE，选择建议：
- **PyCharm**: 功能强大，专为 Python 设计，适合新手
- **VSCode**: 轻量级，扩展丰富，适合有经验的开发者

**推荐**: 初学者使用 PyCharm Community 版（免费）。

#### Q9: 虚拟环境是必须的吗？
**A**: 强烈建议使用虚拟环境：
- 避免不同项目间的依赖冲突
- 保持系统 Python 环境的干净
- 便于项目部署和分享
- 这是 Python 开发的最佳实践

#### Q10: 如何在多个 Python 版本间切换？
**A**: 推荐使用版本管理工具：
```bash
# pyenv (Linux/Mac)
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0

# 或者使用 conda
conda create -n py311 python=3.11
conda activate py311
```

### 学习方法问题

#### Q11: 代码看得懂但写不出来怎么办？
**A**: 这是正常现象，解决方法：
1. **多敲代码**: 不要只看，要亲自敲一遍
2. **模仿练习**: 先模仿示例代码，再尝试修改
3. **小步快跑**: 从简单功能开始，逐步增加复杂度
4. **反复练习**: 同一个概念多写几遍加深印象

#### Q12: 遇到错误就卡住了怎么办？
**A**: 培养调试思维：
1. **仔细阅读错误信息**: 错误信息通常包含解决线索
2. **定位问题**: 确定错误发生在哪一行
3. **搜索错误**: 复制错误信息到搜索引擎
4. **简化问题**: 将复杂问题分解为简单问题
5. **寻求帮助**: 查阅文档或询问社区

#### Q13: 如何提高编程思维？
**A**: 系统性训练：
1. **算法练习**: 在 LeetCode 等平台练习
2. **项目实践**: 完成课程中的所有项目
3. **代码阅读**: 阅读优秀开源项目的代码
4. **技术分享**: 写技术博客或参与讨论
5. **持续学习**: 关注技术发展趋势

### 项目开发问题

#### Q14: 如何设计数据库表结构？
**A**: 遵循设计原则：
1. **需求分析**: 明确要存储什么数据
2. **实体关系**: 确定表之间的关系
3. **规范化**: 避免数据冗余
4. **索引优化**: 为常查询字段添加索引
5. **扩展性**: 考虑未来可能的需求变化

#### Q15: API 设计有什么最佳实践？
**A**: RESTful API 设计原则：
1. **资源导向**: URL 表示资源，HTTP 方法表示操作
2. **状态码**: 使用合适的 HTTP 状态码
3. **版本控制**: 为 API 添加版本号
4. **文档完善**: 提供详细的 API 文档
5. **错误处理**: 统一的错误响应格式

#### Q16: 如何处理用户认证和权限？
**A**: 推荐方案：
1. **JWT Token**: 无状态认证，适合分布式系统
2. **RBAC 模型**: 基于角色的权限控制
3. **密码安全**: 使用 bcrypt 等安全哈希算法
4. **HTTPS**: 生产环境必须使用 HTTPS
5. **输入验证**: 严格验证所有用户输入

### 部署运维问题

#### Q17: 如何部署 Python Web 应用？
**A**: 常见部署方案：
1. **开发环境**: 直接运行（uvicorn/flask run）
2. **测试环境**: Docker 容器化部署
3. **生产环境**: 
   - 使用 Gunicorn + Nginx
   - 或者 Docker + Kubernetes
   - 云服务（AWS、阿里云等）

#### Q18: 如何监控应用性能？
**A**: 监控策略：
1. **日志监控**: 使用 ELK Stack 或类似工具
2. **性能监控**: APM 工具（如 New Relic、Datadog）
3. **健康检查**: 实现 /health 端点
4. **错误追踪**: 使用 Sentry 等错误追踪服务
5. **指标收集**: Prometheus + Grafana

#### Q19: 如何优化数据库性能？
**A**: 优化策略：
1. **索引优化**: 为常查询字段添加索引
2. **查询优化**: 避免 N+1 查询问题
3. **连接池**: 使用数据库连接池
4. **缓存**: Redis 缓存热点数据
5. **分页**: 大数据量查询使用分页

### 职业发展问题

#### Q20: Python 开发者的职业路径是什么？
**A**: 多种发展方向：
1. **后端开发**: Web API、微服务架构
2. **全栈开发**: 前后端都能开发
3. **数据工程**: 数据处理、ETL 开发
4. **DevOps**: 自动化运维、CI/CD
5. **架构师**: 系统设计、技术选型

#### Q21: 如何准备技术面试？
**A**: 面试准备：
1. **基础知识**: Python 语法、数据结构、算法
2. **框架经验**: FastAPI/Flask 项目经验
3. **数据库**: SQL 查询、数据库设计
4. **系统设计**: 高并发、分布式系统
5. **项目经验**: 准备详细的项目介绍

#### Q22: 如何持续学习和成长？
**A**: 学习建议：
1. **技术博客**: 定期写技术总结
2. **开源贡献**: 参与开源项目
3. **技术社区**: 参加技术会议和聚会
4. **在线课程**: 学习新技术和框架
5. **实践项目**: 不断做新的项目练手

### 工具使用问题

#### Q23: 推荐哪些开发工具？
**A**: 工具推荐：
1. **IDE**: PyCharm Professional、VSCode
2. **版本控制**: Git + GitHub/GitLab
3. **API 测试**: Postman、Insomnia
4. **数据库工具**: DBeaver、pgAdmin
5. **容器化**: Docker Desktop
6. **云服务**: AWS、阿里云、腾讯云

#### Q24: 如何管理项目依赖？
**A**: 依赖管理最佳实践：
1. **虚拟环境**: 每个项目独立环境
2. **requirements.txt**: 固定依赖版本
3. **pip-tools**: 更好的依赖管理
4. **Poetry**: 现代化的依赖管理工具
5. **定期更新**: 关注安全更新

#### Q25: 代码质量如何保证？
**A**: 质量保证措施：
1. **代码规范**: 使用 Black、flake8
2. **类型检查**: 使用 mypy
3. **单元测试**: pytest 测试框架
4. **代码审查**: Pull Request 流程
5. **CI/CD**: 自动化测试和部署

---

## 学习资源推荐

### 官方文档
- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [FastAPI 文档](https://fastapi.tiangolo.com/zh/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

### 在线学习平台
- [菜鸟教程](https://www.runoob.com/python3/python3-tutorial.html)
- [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400)
- [Real Python](https://realpython.com/)
- [Python.org 教程](https://docs.python.org/zh-cn/3/tutorial/)

### 练习平台
- [LeetCode](https://leetcode.cn/) - 算法练习
- [HackerRank](https://www.hackerrank.com/) - 编程挑战
- [Codewars](https://www.codewars.com/) - 代码练习
- [牛客网](https://www.nowcoder.com/) - 面试准备

### 技术社区
- [Stack Overflow](https://stackoverflow.com/questions/tagged/python)
- [Reddit Python](https://www.reddit.com/r/Python/)
- [Python 中文社区](https://python-chinese.org/)
- [掘金 Python 标签](https://juejin.cn/tag/Python)

### 推荐书籍
- 《Python编程：从入门到实践》
- 《流畅的Python》
- 《Effective Python》
- 《Python Web开发实战》
- 《架构整洁之道》

---

**提示**: 本指南会持续更新，添加更多常见问题和解决方案。如果你有其他问题，欢迎反馈！
