"""
Flask CRUD 项目启动脚本

运行此脚本启动 Flask 开发服务器。

运行方式:
    python run.py
"""

from app import create_app, db
from app.models import Product

# 创建应用实例
app = create_app()


def init_sample_data():
    """初始化示例数据"""
    with app.app_context():
        # 检查是否已有数据
        if Product.query.count() == 0:
            # 创建示例产品
            products = [
                Product(
                    name='笔记本电脑',
                    description='高性能办公笔记本，适合开发和设计工作',
                    price=5999.00,
                    stock=50,
                    category='电子产品',
                    is_active=True
                ),
                Product(
                    name='无线鼠标',
                    description='人体工学设计，舒适握感',
                    price=99.00,
                    stock=200,
                    category='电子产品',
                    is_active=True
                ),
                Product(
                    name='机械键盘',
                    description='青轴机械键盘，打字手感极佳',
                    price=399.00,
                    stock=100,
                    category='电子产品',
                    is_active=True
                ),
                Product(
                    name='显示器',
                    description='27英寸 4K 显示器',
                    price=2999.00,
                    stock=30,
                    category='电子产品',
                    is_active=True
                ),
                Product(
                    name='办公椅',
                    description='人体工学办公椅，久坐不累',
                    price=1299.00,
                    stock=20,
                    category='家具',
                    is_active=True
                ),
                Product(
                    name='台灯',
                    description='护眼台灯，可调节亮度',
                    price=199.00,
                    stock=150,
                    category='家具',
                    is_active=True
                ),
                Product(
                    name='水杯',
                    description='保温杯，304不锈钢',
                    price=89.00,
                    stock=300,
                    category='生活用品',
                    is_active=True
                ),
                Product(
                    name='笔记本',
                    description='A5 活页笔记本',
                    price=29.00,
                    stock=500,
                    category='文具',
                    is_active=True
                ),
            ]
            
            db.session.add_all(products)
            db.session.commit()
            
            print("✅ 示例数据初始化成功！")
            print(f"📦 已创建 {len(products)} 个示例产品")


@app.shell_context_processor
def make_shell_context():
    """
    Flask Shell 上下文
    
    在 Flask Shell 中自动导入常用对象。
    使用方式: flask shell
    """
    return {
        'db': db,
        'Product': Product
    }


@app.cli.command()
def initdb():
    """
    初始化数据库命令
    
    使用方式: flask initdb
    """
    db.create_all()
    init_sample_data()
    print("✅ 数据库初始化完成！")


@app.cli.command()
def dropdb():
    """
    删除数据库命令
    
    使用方式: flask dropdb
    """
    db.drop_all()
    print("✅ 数据库已删除！")


if __name__ == '__main__':
    # 初始化示例数据
    init_sample_data()
    
    # 启动开发服务器
    print("\n" + "="*60)
    print("🚀 Flask CRUD 示例项目")
    print("="*60)
    print("📍 访问地址: http://127.0.0.1:5000")
    print("📖 API 文档: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000
    )
