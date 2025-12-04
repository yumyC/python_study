# Flask CRUD 示例项目

这是一个完整的 Flask CRUD（增删改查）应用示例，演示了如何使用 Flask 和 SQLAlchemy 构建 RESTful API。

## 📋 项目简介

本项目实现了一个产品管理系统，包含以下功能：

- ✅ 创建产品（Create）
- ✅ 读取产品列表和详情（Read）
- ✅ 更新产品信息（Update）
- ✅ 删除产品（Delete）
- ✅ 分页查询
- ✅ 条件过滤
- ✅ 数据验证
- ✅ 错误处理

## 🏗️ 项目结构

```
crud_project/
├── app/                    # 应用包
│   ├── __init__.py        # 应用工厂和配置
│   ├── models.py          # 数据模型
│   └── views.py           # 视图函数和路由
├── run.py                 # 启动脚本
├── requirements.txt       # 项目依赖
└── README.md             # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行项目

```bash
python run.py
```

服务器将在 `http://127.0.0.1:5000` 启动。

### 3. 访问 API 文档

在浏览器中打开 `http://127.0.0.1:5000`，查看完整的 API 文档和测试命令。

## 📚 API 端点

### 获取产品列表

```bash
GET /api/products

# 示例
curl http://127.0.0.1:5000/api/products

# 分页查询
curl "http://127.0.0.1:5000/api/products?page=1&per_page=5"

# 按分类过滤
curl "http://127.0.0.1:5000/api/products?category=电子产品"
```

### 获取单个产品

```bash
GET /api/products/<id>

# 示例
curl http://127.0.0.1:5000/api/products/1
```

### 创建产品

```bash
POST /api/products

# 示例
curl -X POST http://127.0.0.1:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新产品",
    "description": "产品描述",
    "price": 99.99,
    "stock": 100,
    "category": "电子产品"
  }'
```

### 更新产品

```bash
PUT /api/products/<id>

# 示例
curl -X PUT http://127.0.0.1:5000/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 89.99,
    "stock": 150
  }'
```

### 删除产品

```bash
DELETE /api/products/<id>

# 示例
curl -X DELETE http://127.0.0.1:5000/api/products/1
```

## 🎯 学习要点

### 1. 应用工厂模式

使用 `create_app()` 函数创建应用实例，便于测试和配置管理：

```python
def create_app():
    app = Flask(__name__)
    # 配置和初始化
    return app
```

### 2. 蓝图（Blueprint）

使用蓝图组织路由，使代码结构更清晰：

```python
bp = Blueprint('main', __name__)

@bp.route('/api/products')
def get_products():
    # ...
```

### 3. ORM 模型

使用 SQLAlchemy 定义数据模型：

```python
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # ...
```

### 4. RESTful API 设计

遵循 REST 规范设计 API：

- `GET /api/products` - 获取列表
- `GET /api/products/<id>` - 获取详情
- `POST /api/products` - 创建资源
- `PUT /api/products/<id>` - 更新资源
- `DELETE /api/products/<id>` - 删除资源

### 5. 数据验证

在创建和更新时验证输入数据：

```python
if not data or 'name' not in data:
    return jsonify({'error': '缺少必填字段'}), 400
```

### 6. 错误处理

使用错误处理器统一处理错误：

```python
@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源未找到'}), 404
```

### 7. 分页查询

使用 SQLAlchemy 的 `paginate()` 方法实现分页：

```python
pagination = Product.query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)
```

## 🛠️ 数据库操作

### 使用 Flask Shell

```bash
# 进入 Flask Shell
flask shell

# 在 Shell 中操作数据库
>>> from app.models import Product
>>> products = Product.query.all()
>>> print(products)
```

### 使用 CLI 命令

```bash
# 初始化数据库
flask initdb

# 删除数据库
flask dropdb
```

## 📝 代码规范

本项目遵循以下规范：

- ✅ PEP 8 代码风格
- ✅ 详细的代码注释
- ✅ 清晰的函数文档字符串
- ✅ 合理的错误处理
- ✅ RESTful API 设计规范

## 🔧 配置说明

### 数据库配置

默认使用 SQLite 数据库，配置在 `app/__init__.py` 中：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crud_app.db'
```

如需使用其他数据库，可修改为：

```python
# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:pass@localhost/dbname'

# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

### 开发模式配置

在 `run.py` 中配置开发服务器：

```python
app.run(
    debug=True,          # 开启调试模式
    host='127.0.0.1',    # 监听地址
    port=5000            # 端口号
)
```

## 🎓 扩展学习

完成本项目后，可以尝试以下扩展：

1. **添加用户认证**：实现 JWT 或 Session 认证
2. **添加权限控制**：不同用户有不同的操作权限
3. **添加数据库迁移**：使用 Flask-Migrate 管理数据库版本
4. **添加单元测试**：使用 pytest 编写测试用例
5. **添加 API 文档**：使用 Flask-RESTX 或 Swagger
6. **添加缓存**：使用 Flask-Caching 提高性能
7. **添加日志**：记录操作日志和错误日志
8. **部署到生产环境**：使用 Gunicorn + Nginx

## 📖 相关资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy 文档](https://flask-sqlalchemy.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [RESTful API 设计指南](https://restfulapi.net/)
- [HTTP 状态码](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status)

## ❓ 常见问题

### 1. 如何重置数据库？

```bash
flask dropdb
flask initdb
```

### 2. 如何修改端口号？

在 `run.py` 中修改 `port` 参数：

```python
app.run(debug=True, host='127.0.0.1', port=8000)
```

### 3. 如何查看 SQL 语句？

在 `app/__init__.py` 中设置：

```python
app.config['SQLALCHEMY_ECHO'] = True
```

### 4. 如何添加新的字段？

1. 在 `app/models.py` 中的 `Product` 模型添加字段
2. 删除旧数据库：`flask dropdb`
3. 重新初始化：`flask initdb`

（生产环境应使用数据库迁移工具）

## 📄 许可证

本项目仅用于学习目的。

## 🤝 贡献

欢迎提出问题和改进建议！
