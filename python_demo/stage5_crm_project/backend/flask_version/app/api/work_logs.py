"""
工作日志管理 API

提供工作日志的 CRUD 操作和统计功能
"""

from flask import Blueprint, request, jsonify
from datetime import date, datetime
from app.auth import require_permission, require_self_or_permission
from app.models import WorkLog, Employee
from app import db

work_logs_bp = Blueprint('work_logs', __name__)


@work_logs_bp.route('/work-logs', methods=['GET'])
@require_permission('/work-logs', 'view')
def get_work_logs(current_user):
    """获取工作日志列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = WorkLog.query
        
        # 员工筛选
        if employee_id:
            query = query.filter(WorkLog.employee_id == employee_id)
        
        # 日期筛选
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(WorkLog.log_date >= start_date)
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '开始日期格式错误，应为 YYYY-MM-DD',
                        'status_code': 400
                    }
                }), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(WorkLog.log_date <= end_date)
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '结束日期格式错误，应为 YYYY-MM-DD',
                        'status_code': 400
                    }
                }), 400
        
        # 分页查询
        pagination = query.order_by(WorkLog.log_date.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 构建响应数据
        work_logs = []
        for log in pagination.items:
            log_data = log.to_dict()
            if log.employee:
                log_data['employee_name'] = log.employee.full_name
            work_logs.append(log_data)
        
        return jsonify({
            'work_logs': work_logs,
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
                'code': 'GET_WORK_LOGS_ERROR',
                'message': f'获取工作日志失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@work_logs_bp.route('/work-logs', methods=['POST'])
@require_permission('/work-logs', 'create')
def create_work_log(current_user):
    """创建工作日志"""
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
        if not data.get('work_content'):
            return jsonify({
                'error': {
                    'code': 'MISSING_WORK_CONTENT',
                    'message': '工作内容不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 解析日期
        log_date = data.get('log_date')
        if log_date:
            try:
                log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '日期格式错误，应为 YYYY-MM-DD',
                        'status_code': 400
                    }
                }), 400
        else:
            log_date = date.today()
        
        # 获取员工ID（可以是自己或指定的员工）
        employee_id = data.get('employee_id', str(current_user.id))
        
        # 验证员工是否存在
        employee = Employee.query.filter_by(id=employee_id).first()
        if not employee:
            return jsonify({
                'error': {
                    'code': 'EMPLOYEE_NOT_FOUND',
                    'message': '指定的员工不存在',
                    'status_code': 400
                }
            }), 400
        
        # 检查是否已存在当天的日志
        existing = WorkLog.query.filter_by(
            employee_id=employee_id,
            log_date=log_date
        ).first()
        
        if existing:
            return jsonify({
                'error': {
                    'code': 'LOG_EXISTS',
                    'message': '该员工当天已有工作日志',
                    'status_code': 400
                }
            }), 400
        
        # 创建工作日志
        work_log = WorkLog(
            employee_id=employee_id,
            log_date=log_date,
            work_content=data['work_content'],
            problems_encountered=data.get('problems_encountered'),
            tomorrow_plan=data.get('tomorrow_plan'),
            self_rating=data.get('self_rating')
        )
        
        # 设置完成状态
        status = data.get('completion_status', 'in_progress')
        from app.models.work_log import CompletionStatus
        if status == 'completed':
            work_log.completion_status = CompletionStatus.COMPLETED
        elif status == 'pending':
            work_log.completion_status = CompletionStatus.PENDING
        else:
            work_log.completion_status = CompletionStatus.IN_PROGRESS
        
        db.session.add(work_log)
        db.session.commit()
        
        return jsonify({
            'message': '工作日志创建成功',
            'work_log': work_log.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'CREATE_WORK_LOG_ERROR',
                'message': f'创建工作日志失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@work_logs_bp.route('/work-logs/<log_id>/rating', methods=['POST'])
@require_permission('/work-logs', 'update')
def rate_work_log(log_id, current_user):
    """为工作日志评分（上级操作）"""
    try:
        work_log = WorkLog.query.filter_by(id=log_id).first()
        
        if not work_log:
            return jsonify({
                'error': {
                    'code': 'WORK_LOG_NOT_FOUND',
                    'message': '工作日志不存在',
                    'status_code': 404
                }
            }), 404
        
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment')
        
        if rating is None:
            return jsonify({
                'error': {
                    'code': 'MISSING_RATING',
                    'message': '评分不能为空',
                    'status_code': 400
                }
            }), 400
        
        if not (1 <= rating <= 5):
            return jsonify({
                'error': {
                    'code': 'INVALID_RATING',
                    'message': '评分必须在1-5之间',
                    'status_code': 400
                }
            }), 400
        
        work_log.supervisor_rating = rating
        if comment:
            work_log.supervisor_comment = comment
        
        db.session.commit()
        
        return jsonify({
            'message': '评分成功',
            'work_log': work_log.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'RATE_WORK_LOG_ERROR',
                'message': f'评分失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@work_logs_bp.route('/work-logs/statistics', methods=['GET'])
@require_permission('/work-logs', 'view')
def get_work_log_statistics(current_user):
    """获取工作日志统计信息"""
    try:
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 解析日期
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                start_date = None
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                end_date = None
        
        # 如果没有指定日期范围，默认最近30天
        if not start_date or not end_date:
            from datetime import timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        
        # 获取统计信息
        stats = WorkLog.get_rating_statistics(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_STATISTICS_ERROR',
                'message': f'获取统计信息失败: {str(e)}',
                'status_code': 500
            }
        }), 500