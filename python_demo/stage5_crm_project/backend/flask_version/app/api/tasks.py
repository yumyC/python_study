"""
异步任务 API

提供异步任务的管理和状态查询功能
"""

from flask import Blueprint, request, jsonify
from app.auth import require_permission
from app.tasks.work_log_tasks import export_work_logs_task
from app.tasks.celery_app import celery

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks/export-work-logs', methods=['POST'])
@require_permission('/work-logs', 'view')
def start_export_work_logs(current_user):
    """启动工作日志导出任务"""
    try:
        data = request.get_json() or {}
        
        # 获取导出参数
        employee_id = data.get('employee_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # 启动异步任务
        task = export_work_logs_task.delay(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            user_id=str(current_user.id)
        )
        
        return jsonify({
            'message': '导出任务已启动',
            'task_id': task.id,
            'status': 'PENDING'
        }), 202
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'START_EXPORT_ERROR',
                'message': f'启动导出任务失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@tasks_bp.route('/tasks/<task_id>/status', methods=['GET'])
@require_permission('/work-logs', 'view')
def get_task_status(task_id, current_user):
    """获取任务状态"""
    try:
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'PENDING',
                'message': '任务等待执行'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'status': 'PROGRESS',
                'message': '任务执行中',
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'status': 'SUCCESS',
                'message': '任务执行成功',
                'result': task.info
            }
        else:
            # 任务失败
            response = {
                'task_id': task_id,
                'status': task.state,
                'message': '任务执行失败',
                'error': str(task.info)
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_TASK_STATUS_ERROR',
                'message': f'获取任务状态失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@tasks_bp.route('/tasks/<task_id>/download', methods=['GET'])
@require_permission('/work-logs', 'view')
def download_task_result(task_id, current_user):
    """下载任务结果文件"""
    try:
        task = celery.AsyncResult(task_id)
        
        if task.state != 'SUCCESS':
            return jsonify({
                'error': {
                    'code': 'TASK_NOT_COMPLETED',
                    'message': '任务尚未完成或执行失败',
                    'status_code': 400
                }
            }), 400
        
        result = task.info
        file_path = result.get('file_path')
        
        if not file_path:
            return jsonify({
                'error': {
                    'code': 'FILE_NOT_FOUND',
                    'message': '文件不存在',
                    'status_code': 404
                }
            }), 404
        
        from flask import send_file
        import os
        
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=result.get('filename', 'export.xlsx')
            )
        else:
            return jsonify({
                'error': {
                    'code': 'FILE_NOT_FOUND',
                    'message': '文件不存在',
                    'status_code': 404
                }
            }), 404
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DOWNLOAD_ERROR',
                'message': f'下载文件失败: {str(e)}',
                'status_code': 500
            }
        }), 500