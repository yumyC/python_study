"""
定时任务示例

本示例演示：
1. 配置 Celery Beat 调度器
2. 创建定时任务
3. 创建周期性任务
4. 使用 Crontab 表达式
5. 动态添加和管理定时任务

运行说明：
1. 安装依赖：pip install celery redis
2. 启动 Redis：docker run -d -p 6379:6379 redis:latest
3. 启动 Worker：celery -A 03_scheduled_tasks worker --loglevel=info
4. 启动 Beat 调度器：celery -A 03_scheduled_tasks beat --loglevel=info
   或同时启动：celery -A 03_scheduled_tasks worker --beat --loglevel=info
5. 观察定时任务的执行
"""

from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import time

# ============================================================================
# Celery 应用配置
# ============================================================================

app = Celery(
    'scheduled_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 基础配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)

# ============================================================================
# 定时任务配置
# ============================================================================

app.conf.beat_schedule = {
    # 每 10 秒执行一次
    'heartbeat-every-10-seconds': {
        'task': 'scheduled_tasks.heartbeat',
        'schedule': 10.0,  # 秒
    },
    
    # 每分钟执行一次
    'check-system-every-minute': {
        'task': 'scheduled_tasks.check_system_health',
        'schedule': crontab(minute='*'),  # 每分钟
    },
    
    # 每小时执行一次（整点）
    'hourly-report': {
        'task': 'scheduled_tasks.generate_hourly_report',
        'schedule': crontab(minute=0, hour='*'),  # 每小时的第 0 分钟
    },
    
    # 每天凌晨 2 点执行
    'daily-backup': {
        'task': 'scheduled_tasks.daily_backup',
        'schedule': crontab(minute=0, hour=2),  # 每天 02:00
    },
    
    # 每周一早上 9 点执行
    'weekly-report': {
        'task': 'scheduled_tasks.generate_weekly_report',
        'schedule': crontab(minute=0, hour=9, day_of_week=1),  # 周一 09:00
    },
    
    # 每月 1 号凌晨 3 点执行
    'monthly-cleanup': {
        'task': 'scheduled_tasks.monthly_cleanup',
        'schedule': crontab(minute=0, hour=3, day_of_month=1),  # 每月 1 号 03:00
    },
    
    # 工作日每天早上 8 点执行
    'weekday-morning-task': {
        'task': 'scheduled_tasks.weekday_morning_task',
        'schedule': crontab(minute=0, hour=8, day_of_week='1-5'),  # 周一到周五 08:00
    },
    
    # 每 5 分钟执行一次
    'sync-data-every-5-minutes': {
        'task': 'scheduled_tasks.sync_data',
        'schedule': crontab(minute='*/5'),  # 每 5 分钟
    },
    
    # 每 30 分钟执行一次，带参数
    'cleanup-temp-files': {
        'task': 'scheduled_tasks.cleanup_temp_files',
        'schedule': crontab(minute='*/30'),
        'args': (7,),  # 清理 7 天前的文件
    },
}


# ============================================================================
# 定时任务定义
# ============================================================================

@app.task(name='scheduled_tasks.heartbeat', bind=True)
def heartbeat(self):
    """
    心跳任务 - 每 10 秒执行一次
    
    用于监控系统是否正常运行
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[心跳] {current_time} - 系统运行正常")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'status': 'healthy'
    }


@app.task(name='scheduled_tasks.check_system_health', bind=True)
def check_system_health(self):
    """
    系统健康检查 - 每分钟执行一次
    
    检查系统各项指标是否正常
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[健康检查] {current_time} - 执行系统健康检查")
    
    # 模拟健康检查
    health_status = {
        'cpu_usage': 45.2,
        'memory_usage': 62.8,
        'disk_usage': 38.5,
        'active_connections': 127,
        'status': 'healthy'
    }
    
    print(f"[健康检查] CPU: {health_status['cpu_usage']}%, "
          f"内存: {health_status['memory_usage']}%, "
          f"磁盘: {health_status['disk_usage']}%")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'health_status': health_status
    }


@app.task(name='scheduled_tasks.generate_hourly_report', bind=True)
def generate_hourly_report(self):
    """
    生成小时报表 - 每小时整点执行
    
    统计过去一小时的业务数据
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[小时报表] {current_time} - 生成小时报表")
    
    # 模拟报表生成
    report = {
        'period': 'hourly',
        'orders_count': 156,
        'revenue': 12580.50,
        'new_users': 23,
        'active_users': 489
    }
    
    print(f"[小时报表] 订单: {report['orders_count']}, "
          f"收入: {report['revenue']}, "
          f"新用户: {report['new_users']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'report': report
    }


@app.task(name='scheduled_tasks.daily_backup', bind=True)
def daily_backup(self):
    """
    每日备份 - 每天凌晨 2 点执行
    
    备份数据库和重要文件
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[每日备份] {current_time} - 开始执行每日备份")
    
    # 模拟备份过程
    time.sleep(2)
    
    backup_info = {
        'backup_type': 'daily',
        'database_size': '2.5 GB',
        'files_count': 15234,
        'backup_file': f'backup_daily_{datetime.now().strftime("%Y%m%d")}.tar.gz',
        'status': 'completed'
    }
    
    print(f"[每日备份] 备份完成 - 文件: {backup_info['backup_file']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'backup_info': backup_info
    }


@app.task(name='scheduled_tasks.generate_weekly_report', bind=True)
def generate_weekly_report(self):
    """
    生成周报 - 每周一早上 9 点执行
    
    统计上周的业务数据
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[周报] {current_time} - 生成周报")
    
    # 模拟周报生成
    report = {
        'period': 'weekly',
        'week_number': datetime.now().isocalendar()[1],
        'total_orders': 1250,
        'total_revenue': 98750.00,
        'new_users': 187,
        'churn_rate': 2.3
    }
    
    print(f"[周报] 第 {report['week_number']} 周 - "
          f"订单: {report['total_orders']}, "
          f"收入: {report['total_revenue']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'report': report
    }


@app.task(name='scheduled_tasks.monthly_cleanup', bind=True)
def monthly_cleanup(self):
    """
    月度清理 - 每月 1 号凌晨 3 点执行
    
    清理过期数据和临时文件
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[月度清理] {current_time} - 开始月度清理")
    
    # 模拟清理过程
    time.sleep(3)
    
    cleanup_result = {
        'cleanup_type': 'monthly',
        'deleted_records': 5678,
        'freed_space': '1.2 GB',
        'archived_files': 234,
        'status': 'completed'
    }
    
    print(f"[月度清理] 清理完成 - "
          f"删除记录: {cleanup_result['deleted_records']}, "
          f"释放空间: {cleanup_result['freed_space']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'cleanup_result': cleanup_result
    }


@app.task(name='scheduled_tasks.weekday_morning_task', bind=True)
def weekday_morning_task(self):
    """
    工作日早晨任务 - 工作日每天早上 8 点执行
    
    发送每日工作提醒和数据摘要
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    day_name = datetime.now().strftime('%A')
    print(f"[工作日任务] {current_time} ({day_name}) - 发送每日提醒")
    
    # 模拟发送提醒
    reminder = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'day_of_week': day_name,
        'pending_tasks': 12,
        'meetings_today': 3,
        'urgent_items': 2
    }
    
    print(f"[工作日任务] 待办任务: {reminder['pending_tasks']}, "
          f"今日会议: {reminder['meetings_today']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'reminder': reminder
    }


@app.task(name='scheduled_tasks.sync_data', bind=True)
def sync_data(self):
    """
    数据同步 - 每 5 分钟执行一次
    
    同步外部系统的数据
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[数据同步] {current_time} - 开始数据同步")
    
    # 模拟数据同步
    time.sleep(1)
    
    sync_result = {
        'synced_records': 45,
        'updated_records': 12,
        'new_records': 8,
        'failed_records': 0,
        'status': 'success'
    }
    
    print(f"[数据同步] 同步完成 - "
          f"同步: {sync_result['synced_records']}, "
          f"更新: {sync_result['updated_records']}, "
          f"新增: {sync_result['new_records']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'sync_result': sync_result
    }


@app.task(name='scheduled_tasks.cleanup_temp_files', bind=True)
def cleanup_temp_files(self, days_old):
    """
    清理临时文件 - 每 30 分钟执行一次
    
    Args:
        days_old: 清理多少天前的文件
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[清理临时文件] {current_time} - 清理 {days_old} 天前的临时文件")
    
    # 模拟文件清理
    cleanup_result = {
        'days_old': days_old,
        'files_deleted': 156,
        'space_freed': '450 MB',
        'status': 'completed'
    }
    
    print(f"[清理临时文件] 清理完成 - "
          f"删除文件: {cleanup_result['files_deleted']}, "
          f"释放空间: {cleanup_result['space_freed']}")
    
    return {
        'task_id': self.request.id,
        'timestamp': current_time,
        'cleanup_result': cleanup_result
    }


# ============================================================================
# 动态添加定时任务
# ============================================================================

@app.task(name='scheduled_tasks.add_periodic_task')
def add_periodic_task(task_name, task_path, schedule_type, **kwargs):
    """
    动态添加定时任务
    
    Args:
        task_name: 任务名称
        task_path: 任务路径
        schedule_type: 调度类型 ('interval' 或 'crontab')
        **kwargs: 调度参数
    """
    from celery.schedules import schedule
    
    print(f"[动态任务] 添加定时任务: {task_name}")
    
    # 这里只是示例，实际应用中需要使用数据库存储定时任务配置
    # 可以使用 django-celery-beat 或 celery-redbeat 等扩展
    
    return {
        'task_name': task_name,
        'task_path': task_path,
        'schedule_type': schedule_type,
        'status': 'added'
    }


# ============================================================================
# 一次性延迟任务
# ============================================================================

@app.task(name='scheduled_tasks.send_delayed_notification', bind=True)
def send_delayed_notification(self, user_id, message, delay_seconds):
    """
    延迟通知任务
    
    不是周期性任务，而是延迟执行的一次性任务
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[延迟通知] {current_time} - 发送延迟通知")
    print(f"用户: {user_id}, 消息: {message}, 延迟: {delay_seconds}秒")
    
    return {
        'task_id': self.request.id,
        'user_id': user_id,
        'message': message,
        'sent_at': current_time
    }


@app.task(name='scheduled_tasks.schedule_future_task', bind=True)
def schedule_future_task(self, task_data, execute_at):
    """
    计划未来任务
    
    在指定的时间点执行任务
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[未来任务] {current_time} - 执行计划任务")
    print(f"任务数据: {task_data}")
    print(f"计划时间: {execute_at}")
    
    return {
        'task_id': self.request.id,
        'task_data': task_data,
        'executed_at': current_time,
        'scheduled_for': execute_at
    }


# ============================================================================
# 任务调用示例
# ============================================================================

def demo_delayed_task():
    """演示延迟任务"""
    print("\n" + "="*60)
    print("示例 1: 延迟任务")
    print("="*60)
    
    # 5 秒后执行
    print("\n提交延迟任务（5 秒后执行）...")
    result = send_delayed_notification.apply_async(
        args=('user_001', '这是一条延迟通知', 5),
        countdown=5  # 5 秒后执行
    )
    
    print(f"任务已提交: {result.id}")
    print("等待任务执行...")
    
    task_result = result.get(timeout=30)
    print(f"任务执行完成: {task_result}")


def demo_scheduled_task():
    """演示在指定时间执行任务"""
    print("\n" + "="*60)
    print("示例 2: 指定时间执行任务")
    print("="*60)
    
    # 10 秒后的时间
    execute_time = datetime.now() + timedelta(seconds=10)
    
    print(f"\n提交任务，将在 {execute_time.strftime('%H:%M:%S')} 执行...")
    result = schedule_future_task.apply_async(
        args=({'action': 'send_report'}, execute_time.isoformat()),
        eta=execute_time  # 在指定时间执行
    )
    
    print(f"任务已提交: {result.id}")
    print("等待任务执行...")
    
    task_result = result.get(timeout=30)
    print(f"任务执行完成: {task_result}")


def demo_manual_trigger():
    """演示手动触发定时任务"""
    print("\n" + "="*60)
    print("示例 3: 手动触发定时任务")
    print("="*60)
    
    # 手动触发心跳任务
    print("\n手动触发心跳任务...")
    result = heartbeat.delay()
    print(f"任务结果: {result.get(timeout=10)}")
    
    # 手动触发健康检查
    print("\n手动触发健康检查...")
    result = check_system_health.delay()
    print(f"任务结果: {result.get(timeout=10)}")
    
    # 手动触发报表生成
    print("\n手动触发小时报表生成...")
    result = generate_hourly_report.delay()
    print(f"任务结果: {result.get(timeout=10)}")


# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   定时任务示例                               ║
    ║                                                              ║
    ║  确保已经启动 Redis、Worker 和 Beat 调度器:                 ║
    ║  1. docker run -d -p 6379:6379 redis:latest                 ║
    ║  2. celery -A 03_scheduled_tasks worker --loglevel=info     ║
    ║  3. celery -A 03_scheduled_tasks beat --loglevel=info       ║
    ║                                                              ║
    ║  或同时启动 Worker 和 Beat:                                  ║
    ║  celery -A 03_scheduled_tasks worker --beat --loglevel=info ║
    ║                                                              ║
    ║  启动后，定时任务会自动按计划执行                           ║
    ║  你也可以运行本脚本手动触发任务                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("\n定时任务配置:")
    print("-" * 60)
    for name, config in app.conf.beat_schedule.items():
        print(f"任务: {name}")
        print(f"  - 任务路径: {config['task']}")
        print(f"  - 调度: {config['schedule']}")
        if 'args' in config:
            print(f"  - 参数: {config['args']}")
        print()
    
    try:
        # 运行示例
        demo_delayed_task()
        demo_scheduled_task()
        demo_manual_trigger()
        
        print("\n" + "="*60)
        print("示例执行完成！")
        print("="*60)
        print("\n提示:")
        print("- 定时任务会在后台按计划自动执行")
        print("- 使用 Flower 监控工具可以查看任务执行情况")
        print("- 命令: celery -A 03_scheduled_tasks flower")
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("1. Redis 服务正在运行")
        print("2. Celery Worker 已启动")
        print("3. Celery Beat 调度器已启动")
        print("4. 已安装必要的依赖: pip install celery redis")
