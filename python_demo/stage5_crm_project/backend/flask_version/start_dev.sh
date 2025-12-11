#!/bin/bash

# Flask CRM 开发环境启动脚本

echo "启动 Flask CRM 开发环境..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "复制环境变量配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置相应参数"
fi

# 初始化数据库
echo "初始化数据库..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('数据库表创建完成')
"

# 创建示例数据
echo "创建示例数据..."
python -c "
from app import create_app, db
from app.auth import AuthService
from app.models import Position, Role, Menu, Employee

app = create_app()
with app.app_context():
    # 创建示例岗位
    if not Position.query.first():
        positions = [
            Position(name='CEO', code='CEO', description='首席执行官', level=1),
            Position(name='CTO', code='CTO', description='首席技术官', level=2),
            Position(name='开发经理', code='DEV_MGR', description='开发团队经理', level=3),
            Position(name='高级开发工程师', code='SR_DEV', description='高级开发工程师', level=4),
            Position(name='开发工程师', code='DEV', description='开发工程师', level=5),
        ]
        
        for position in positions:
            db.session.add(position)
        
        db.session.commit()
        print('示例岗位创建完成')
    
    # 创建示例角色
    if not Role.query.first():
        roles = [
            Role(name='超级管理员', code='SUPER_ADMIN', description='系统超级管理员'),
            Role(name='管理员', code='ADMIN', description='系统管理员'),
            Role(name='经理', code='MANAGER', description='部门经理'),
            Role(name='员工', code='EMPLOYEE', description='普通员工'),
        ]
        
        for role in roles:
            db.session.add(role)
        
        db.session.commit()
        print('示例角色创建完成')
    
    # 创建示例菜单
    if not Menu.query.first():
        menus = [
            Menu(name='系统管理', path='/system', icon='system', sort_order=1),
            Menu(name='员工管理', path='/employees', icon='user', sort_order=2),
            Menu(name='岗位管理', path='/positions', icon='position', sort_order=3),
            Menu(name='工作日志', path='/work-logs', icon='log', sort_order=4),
        ]
        
        for menu in menus:
            db.session.add(menu)
        
        db.session.commit()
        print('示例菜单创建完成')
    
    # 创建示例用户
    if not Employee.query.first():
        admin_role = Role.query.filter_by(code='SUPER_ADMIN').first()
        ceo_position = Position.query.filter_by(code='CEO').first()
        
        admin_user = AuthService.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            full_name='系统管理员',
            position_id=ceo_position.id if ceo_position else None,
            role_id=admin_role.id if admin_role else None
        )
        
        print('示例用户创建完成')
        print('管理员账号: admin / admin123')
    
    print('所有示例数据创建完成')
"

echo ""
echo "🚀 Flask CRM 开发环境准备完成！"
echo ""
echo "启动应用:"
echo "  python app.py"
echo ""
echo "或者使用 Flask CLI:"
echo "  flask run --host=0.0.0.0 --port=5000"
echo ""
echo "默认管理员账号:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "API 地址:"
echo "  http://localhost:5000"
echo ""
echo "测试脚本:"
echo "  python test_flask_crm.py"
echo ""