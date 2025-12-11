"""
员工管理 API

提供员工的 CRUD 操作、搜索和分页功能
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.auth import require_permission
from app.models import Employee, Position, Role
from app import db

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/employees', methods=['GET'])
@require_permission('/employees', 'view')
def get_employees(current_user):
    """
    获取员工列表
    
    查询参数:
        - page: 页码（默认1）
        - per_page: 每页数量（默认10）
        - search: 搜索关键词（搜索姓名、用户名、邮箱）
        - position_id: 岗位ID筛选
        - role_id: 角色ID筛选
        - status: 状态筛选（active/inactive）
    
    响应:
        {
            "employees": [员工列表],
            "pagination": {分页信息}
        }
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '').strip()
        position_id = request.args.get('position_id')
        role_id = request.args.get('role_id')
        status = request.args.get('status')
        
        # 构建查询
        query = Employee.query
        
        # 搜索条件
        if search:
            query = query.filter(
                or_(
                    Employee.full_name.contains(search),
                    Employee.username.contains(search),
                    Employee.email.contains(search)
                )
            )
        
        # 岗位筛选
        if position_id:
            query = query.filter(Employee.position_id == position_id)
        
        # 角色筛选
        if role_id:
            query = query.filter(Employee.role_id == role_id)
        
        # 状态筛选
        if status:
            from app.models.employee import EmployeeStatus
            if status == 'active':
                query = query.filter(Employee.status == EmployeeStatus.ACTIVE)
            elif status == 'inactive':
                query = query.filter(Employee.status == EmployeeStatus.INACTIVE)
        
        # 分页查询
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 构建响应数据
        employees = []
        for employee in pagination.items:
            employee_data = employee.to_dict()
            employees.append(employee_data)
        
        return jsonify({
            'employees': employees,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_EMPLOYEES_ERROR',
                'message': f'获取员工列表失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@employees_bp.route('/employees/<employee_id>', methods=['GET'])
@require_permission('/employees', 'view')
def get_employee(employee_id, current_user):
    """
    获取单个员工信息
    
    路径参数:
        employee_id: 员工ID
    
    响应:
        {
            "employee": {员工信息}
        }
    """
    try:
        employee = Employee.query.filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': {
                    'code': 'EMPLOYEE_NOT_FOUND',
                    'message': '员工不存在',
                    'status_code': 404
                }
            }), 404
        
        return jsonify({
            'employee': employee.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_EMPLOYEE_ERROR',
                'message': f'获取员工信息失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@employees_bp.route('/employees', methods=['POST'])
@require_permission('/employees', 'create')
def create_employee(current_user):
    """
    创建员工
    
    请求体:
        {
            "username": "用户名",
            "email": "邮箱",
            "password": "密码",
            "full_name": "姓名",
            "position_id": "岗位ID（可选）",
            "role_id": "角色ID（可选）"
        }
    
    响应:
        {
            "message": "员工创建成功",
            "employee": {员工信息}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求体不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'{field} 不能为空',
                        'status_code': 400
                    }
                }), 400
        
        # 验证岗位是否存在
        position_id = data.get('position_id')
        if position_id:
            position = Position.query.filter_by(id=position_id).first()
            if not position:
                return jsonify({
                    'error': {
                        'code': 'POSITION_NOT_FOUND',
                        'message': '指定的岗位不存在',
                        'status_code': 400
                    }
                }), 400
        
        # 验证角色是否存在
        role_id = data.get('role_id')
        if role_id:
            role = Role.query.filter_by(id=role_id).first()
            if not role:
                return jsonify({
                    'error': {
                        'code': 'ROLE_NOT_FOUND',
                        'message': '指定的角色不存在',
                        'status_code': 400
                    }
                }), 400
        
        # 检查用户名是否已存在
        if Employee.query.filter_by(username=data['username']).first():
            return jsonify({
                'error': {
                    'code': 'USERNAME_EXISTS',
                    'message': '用户名已存在',
                    'status_code': 400
                }
            }), 400
        
        # 检查邮箱是否已存在
        if Employee.query.filter_by(email=data['email']).first():
            return jsonify({
                'error': {
                    'code': 'EMAIL_EXISTS',
                    'message': '邮箱已存在',
                    'status_code': 400
                }
            }), 400
        
        # 创建员工
        employee = Employee(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            position_id=position_id,
            role_id=role_id
        )
        employee.set_password(data['password'])
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'message': '员工创建成功',
            'employee': employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'CREATE_EMPLOYEE_ERROR',
                'message': f'创建员工失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@employees_bp.route('/employees/<employee_id>', methods=['PUT'])
@require_permission('/employees', 'update')
def update_employee(employee_id, current_user):
    """
    更新员工信息
    
    路径参数:
        employee_id: 员工ID
    
    请求体:
        {
            "email": "邮箱（可选）",
            "full_name": "姓名（可选）",
            "position_id": "岗位ID（可选）",
            "role_id": "角色ID（可选）",
            "status": "状态（可选）"
        }
    
    响应:
        {
            "message": "员工信息更新成功",
            "employee": {员工信息}
        }
    """
    try:
        employee = Employee.query.filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': {
                    'code': 'EMPLOYEE_NOT_FOUND',
                    'message': '员工不存在',
                    'status_code': 404
                }
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求体不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 更新邮箱
        if 'email' in data:
            # 检查邮箱是否已被其他用户使用
            existing = Employee.query.filter(
                Employee.email == data['email'],
                Employee.id != employee_id
            ).first()
            if existing:
                return jsonify({
                    'error': {
                        'code': 'EMAIL_EXISTS',
                        'message': '邮箱已被其他用户使用',
                        'status_code': 400
                    }
                }), 400
            employee.email = data['email']
        
        # 更新姓名
        if 'full_name' in data:
            employee.full_name = data['full_name']
        
        # 更新岗位
        if 'position_id' in data:
            position_id = data['position_id']
            if position_id:
                position = Position.query.filter_by(id=position_id).first()
                if not position:
                    return jsonify({
                        'error': {
                            'code': 'POSITION_NOT_FOUND',
                            'message': '指定的岗位不存在',
                            'status_code': 400
                        }
                    }), 400
            employee.position_id = position_id
        
        # 更新角色
        if 'role_id' in data:
            role_id = data['role_id']
            if role_id:
                role = Role.query.filter_by(id=role_id).first()
                if not role:
                    return jsonify({
                        'error': {
                            'code': 'ROLE_NOT_FOUND',
                            'message': '指定的角色不存在',
                            'status_code': 400
                        }
                    }), 400
            employee.role_id = role_id
        
        # 更新状态
        if 'status' in data:
            from app.models.employee import EmployeeStatus
            status = data['status']
            if status == 'active':
                employee.status = EmployeeStatus.ACTIVE
            elif status == 'inactive':
                employee.status = EmployeeStatus.INACTIVE
            else:
                return jsonify({
                    'error': {
                        'code': 'INVALID_STATUS',
                        'message': '状态值无效，只能是 active 或 inactive',
                        'status_code': 400
                    }
                }), 400
        
        db.session.commit()
        
        return jsonify({
            'message': '员工信息更新成功',
            'employee': employee.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_EMPLOYEE_ERROR',
                'message': f'更新员工信息失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@employees_bp.route('/employees/<employee_id>', methods=['DELETE'])
@require_permission('/employees', 'delete')
def delete_employee(employee_id, current_user):
    """
    删除员工
    
    路径参数:
        employee_id: 员工ID
    
    响应:
        {
            "message": "员工删除成功"
        }
    """
    try:
        employee = Employee.query.filter_by(id=employee_id).first()
        
        if not employee:
            return jsonify({
                'error': {
                    'code': 'EMPLOYEE_NOT_FOUND',
                    'message': '员工不存在',
                    'status_code': 404
                }
            }), 404
        
        # 不能删除自己
        if str(employee.id) == str(current_user.id):
            return jsonify({
                'error': {
                    'code': 'CANNOT_DELETE_SELF',
                    'message': '不能删除自己的账户',
                    'status_code': 400
                }
            }), 400
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'message': '员工删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'DELETE_EMPLOYEE_ERROR',
                'message': f'删除员工失败: {str(e)}',
                'status_code': 500
            }
        }), 500