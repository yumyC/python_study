"""
视图函数和路由

定义应用的所有路由和视图函数，实现 CRUD 操作。
"""

from flask import Blueprint, jsonify, request, render_template_string
from app import db
from app.models import Product

# 创建蓝图
bp = Blueprint('main', __name__)


# ============ 首页和文档 ============

@bp.route('/')
def index():
    """首页 - API 文档"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask CRUD 示例项目</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            .endpoint {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background-color: #61affe; color: white; }
            .post { background-color: #49cc90; color: white; }
            .put { background-color: #fca130; color: white; }
            .delete { background-color: #f93e3e; color: white; }
            code {
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            pre {
                background-color: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🚀 Flask CRUD 示例项目</h1>
        <p>这是一个完整的 Flask CRUD 应用示例，演示了产品管理的增删改查操作。</p>
        
        <h2>📚 API 端点</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <a href="/api/products"><code>/api/products</code></a>
            <p>获取所有产品列表（支持分页和过滤）</p>
            <p><strong>查询参数：</strong></p>
            <ul>
                <li><code>page</code> - 页码（默认：1）</li>
                <li><code>per_page</code> - 每页数量（默认：10）</li>
                <li><code>category</code> - 按分类过滤</li>
                <li><code>is_active</code> - 按状态过滤（true/false）</li>
            </ul>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <a href="/api/products/1"><code>/api/products/&lt;id&gt;</code></a>
            <p>获取单个产品详情</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/products</code>
            <p>创建新产品</p>
            <p><strong>请求体示例：</strong></p>
            <pre>{
    "name": "产品名称",
    "description": "产品描述",
    "price": 99.99,
    "stock": 100,
    "category": "电子产品"
}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method put">PUT</span>
            <code>/api/products/&lt;id&gt;</code>
            <p>更新产品信息</p>
            <p><strong>请求体示例：</strong></p>
            <pre>{
    "name": "新产品名称",
    "price": 89.99,
    "stock": 150
}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method delete">DELETE</span>
            <code>/api/products/&lt;id&gt;</code>
            <p>删除产品</p>
        </div>
        
        <h2>🧪 测试命令</h2>
        
        <h3>1. 获取所有产品</h3>
        <pre>curl http://127.0.0.1:5000/api/products</pre>
        
        <h3>2. 创建产品</h3>
        <pre>curl -X POST http://127.0.0.1:5000/api/products \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "笔记本电脑",
    "description": "高性能办公笔记本",
    "price": 5999.00,
    "stock": 50,
    "category": "电子产品"
  }'</pre>
        
        <h3>3. 获取单个产品</h3>
        <pre>curl http://127.0.0.1:5000/api/products/1</pre>
        
        <h3>4. 更新产品</h3>
        <pre>curl -X PUT http://127.0.0.1:5000/api/products/1 \\
  -H "Content-Type: application/json" \\
  -d '{
    "price": 5499.00,
    "stock": 45
  }'</pre>
        
        <h3>5. 删除产品</h3>
        <pre>curl -X DELETE http://127.0.0.1:5000/api/products/1</pre>
        
        <h3>6. 分页查询</h3>
        <pre>curl "http://127.0.0.1:5000/api/products?page=1&per_page=5"</pre>
        
        <h3>7. 按分类过滤</h3>
        <pre>curl "http://127.0.0.1:5000/api/products?category=电子产品"</pre>
        
        <h2>📖 学习要点</h2>
        <ul>
            <li>✅ RESTful API 设计规范</li>
            <li>✅ Flask 蓝图（Blueprint）的使用</li>
            <li>✅ SQLAlchemy ORM 数据库操作</li>
            <li>✅ 请求数据验证和错误处理</li>
            <li>✅ JSON 数据序列化</li>
            <li>✅ 分页和过滤功能实现</li>
            <li>✅ HTTP 状态码的正确使用</li>
        </ul>
        
        <h2>🔗 相关资源</h2>
        <ul>
            <li><a href="https://flask.palletsprojects.com/" target="_blank">Flask 官方文档</a></li>
            <li><a href="https://flask-sqlalchemy.palletsprojects.com/" target="_blank">Flask-SQLAlchemy 文档</a></li>
            <li><a href="https://restfulapi.net/" target="_blank">RESTful API 设计指南</a></li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(template)


# ============ CRUD 操作 ============

@bp.route('/api/products', methods=['GET'])
def get_products():
    """
    获取产品列表
    
    支持分页和过滤功能。
    
    查询参数:
        page (int): 页码，默认 1
        per_page (int): 每页数量，默认 10
        category (str): 按分类过滤
        is_active (bool): 按状态过滤
    
    返回:
        JSON: 产品列表和分页信息
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', type=str)
    is_active = request.args.get('is_active', type=str)
    
    # 构建查询
    query = Product.query
    
    # 应用过滤条件
    if category:
        query = query.filter_by(category=category)
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)
    
    # 排序：最新创建的在前
    query = query.order_by(Product.created_at.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 构建响应
    return jsonify({
        'success': True,
        'data': [product.to_dict() for product in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })


@bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    获取单个产品详情
    
    参数:
        product_id (int): 产品 ID
    
    返回:
        JSON: 产品详情
    """
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'success': True,
        'data': product.to_dict()
    })


@bp.route('/api/products', methods=['POST'])
def create_product():
    """
    创建新产品
    
    请求体:
        {
            "name": "产品名称",
            "description": "产品描述",
            "price": 99.99,
            "stock": 100,
            "category": "分类"
        }
    
    返回:
        JSON: 创建的产品信息
    """
    # 获取 JSON 数据
    data = request.get_json()
    
    # 验证必填字段
    if not data:
        return jsonify({
            'success': False,
            'error': '请提供 JSON 数据'
        }), 400
    
    required_fields = ['name', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'缺少必填字段: {field}'
            }), 400
    
    # 验证数据类型
    try:
        price = float(data['price'])
        if price < 0:
            return jsonify({
                'success': False,
                'error': '价格不能为负数'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': '价格必须是数字'
        }), 400
    
    # 验证库存
    stock = data.get('stock', 0)
    try:
        stock = int(stock)
        if stock < 0:
            return jsonify({
                'success': False,
                'error': '库存不能为负数'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': '库存必须是整数'
        }), 400
    
    # 创建产品
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=price,
        stock=stock,
        category=data.get('category', ''),
        is_active=data.get('is_active', True)
    )
    
    # 保存到数据库
    try:
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '产品创建成功',
            'data': product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建失败: {str(e)}'
        }), 500


@bp.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """
    更新产品信息
    
    参数:
        product_id (int): 产品 ID
    
    请求体:
        {
            "name": "新名称",
            "price": 89.99,
            ...
        }
    
    返回:
        JSON: 更新后的产品信息
    """
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': '请提供要更新的数据'
        }), 400
    
    # 更新字段
    if 'name' in data:
        product.name = data['name']
    
    if 'description' in data:
        product.description = data['description']
    
    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({
                    'success': False,
                    'error': '价格不能为负数'
                }), 400
            product.price = price
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': '价格必须是数字'
            }), 400
    
    if 'stock' in data:
        try:
            stock = int(data['stock'])
            if stock < 0:
                return jsonify({
                    'success': False,
                    'error': '库存不能为负数'
                }), 400
            product.stock = stock
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': '库存必须是整数'
            }), 400
    
    if 'category' in data:
        product.category = data['category']
    
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])
    
    # 保存更改
    try:
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '产品更新成功',
            'data': product.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500


@bp.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    删除产品
    
    参数:
        product_id (int): 产品 ID
    
    返回:
        JSON: 删除结果
    """
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '产品删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500


# ============ 错误处理 ============

@bp.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'error': '资源未找到'
    }), 404


@bp.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500
