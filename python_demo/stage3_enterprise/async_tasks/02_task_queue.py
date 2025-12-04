"""
任务队列示例

本示例演示：
1. 配置多个任务队列
2. 设置任务优先级
3. 任务路由规则
4. 任务重试机制
5. Worker 队列绑定

运行说明：
1. 安装依赖：pip install celery redis
2. 启动 Redis：docker run -d -p 6379:6379 redis:latest
3. 启动不同队列的 Worker：
   - 高优先级队列：celery -A 02_task_queue worker -Q high_priority --loglevel=info -n high_worker@%h
   - 默认队列：celery -A 02_task_queue worker -Q default --loglevel=info -n default_worker@%h
   - 低优先级队列：celery -A 02_task_queue worker -Q low_priority --loglevel=info -n low_worker@%h
4. 运行示例：python 02_task_queue.py
"""

from celery import Celery
from kombu import Queue, Exchange
import time
from datetime import datetime
import random

# ============================================================================
# Celery 应用配置
# ============================================================================

app = Celery(
    'task_queue',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 定义交换机
default_exchange = Exchange('default', type='direct')

# 配置任务队列
app.conf.task_queues = (
    # 高优先级队列
    Queue('high_priority', exchange=default_exchange, routing_key='high'),
    # 默认队列
    Queue('default', exchange=default_exchange, routing_key='default'),
    # 低优先级队列
    Queue('low_priority', exchange=default_exchange, routing_key='low'),
)

# 默认队列
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# 任务路由规则
app.conf.task_routes = {
    # 紧急任务路由到高优先级队列
    'task_queue.urgent_notification': {'queue': 'high_priority'},
    'task_queue.critical_alert': {'queue': 'high_priority'},
    
    # 普通任务路由到默认队列
    'task_queue.process_order': {'queue': 'default'},
    'task_queue.update_inventory': {'queue': 'default'},
    
    # 批量任务路由到低优先级队列
    'task_queue.batch_export': {'queue': 'low_priority'},
    'task_queue.cleanup_old_data': {'queue': 'low_priority'},
}

# 其他配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    # Worker 配置
    worker_prefetch_multiplier=4,  # Worker 预取任务数
    worker_max_tasks_per_child=1000,  # Worker 重启前执行的任务数
)


# ============================================================================
# 高优先级任务
# ============================================================================

@app.task(name='task_queue.urgent_notification', bind=True)
def urgent_notification(self, user_id, message):
    """
    紧急通知任务（高优先级）
    
    这类任务需要立即处理，不能延迟
    """
    print(f"[高优先级] 发送紧急通知 - 任务 ID: {self.request.id}")
    print(f"用户: {user_id}, 消息: {message}")
    
    # 模拟发送通知
    time.sleep(1)
    
    result = {
        'task_id': self.request.id,
        'user_id': user_id,
        'message': message,
        'priority': 'high',
        'sent_at': datetime.now().isoformat(),
        'status': 'sent'
    }
    
    print(f"[高优先级] 紧急通知发送完成")
    return result


@app.task(name='task_queue.critical_alert', bind=True, max_retries=3)
def critical_alert(self, alert_type, details):
    """
    关键告警任务（高优先级，带重试）
    
    这类任务非常重要，失败后会自动重试
    """
    print(f"[高优先级] 处理关键告警 - 任务 ID: {self.request.id}")
    print(f"告警类型: {alert_type}")
    
    try:
        # 模拟可能失败的操作
        if random.random() < 0.3:  # 30% 概率失败
            raise Exception("告警发送失败")
        
        time.sleep(1)
        
        result = {
            'task_id': self.request.id,
            'alert_type': alert_type,
            'details': details,
            'priority': 'critical',
            'processed_at': datetime.now().isoformat(),
            'status': 'success'
        }
        
        print(f"[高优先级] 关键告警处理完成")
        return result
        
    except Exception as exc:
        print(f"[高优先级] 告警处理失败，准备重试...")
        # 5 秒后重试
        raise self.retry(exc=exc, countdown=5)


# ============================================================================
# 默认优先级任务
# ============================================================================

@app.task(name='task_queue.process_order', bind=True)
def process_order(self, order_id, items):
    """
    处理订单任务（默认优先级）
    
    这是常规业务任务，按正常优先级处理
    """
    print(f"[默认优先级] 处理订单 - 任务 ID: {self.request.id}")
    print(f"订单 ID: {order_id}, 商品数量: {len(items)}")
    
    # 模拟订单处理
    time.sleep(2)
    
    result = {
        'task_id': self.request.id,
        'order_id': order_id,
        'items_count': len(items),
        'total_amount': sum(item.get('price', 0) for item in items),
        'priority': 'normal',
        'processed_at': datetime.now().isoformat(),
        'status': 'completed'
    }
    
    print(f"[默认优先级] 订单处理完成")
    return result


@app.task(name='task_queue.update_inventory', bind=True, max_retries=5)
def update_inventory(self, product_id, quantity):
    """
    更新库存任务（默认优先级，带重试）
    
    库存更新可能因为并发冲突失败，需要重试机制
    """
    print(f"[默认优先级] 更新库存 - 任务 ID: {self.request.id}")
    print(f"产品 ID: {product_id}, 数量: {quantity}")
    
    try:
        # 模拟可能失败的库存更新
        if random.random() < 0.2:  # 20% 概率失败
            raise Exception("库存更新冲突")
        
        time.sleep(1)
        
        result = {
            'task_id': self.request.id,
            'product_id': product_id,
            'quantity': quantity,
            'priority': 'normal',
            'updated_at': datetime.now().isoformat(),
            'status': 'success'
        }
        
        print(f"[默认优先级] 库存更新完成")
        return result
        
    except Exception as exc:
        print(f"[默认优先级] 库存更新失败，准备重试...")
        # 指数退避重试：2, 4, 8, 16, 32 秒
        retry_countdown = 2 ** self.request.retries
        raise self.retry(exc=exc, countdown=retry_countdown, max_retries=5)


# ============================================================================
# 低优先级任务
# ============================================================================

@app.task(name='task_queue.batch_export', bind=True)
def batch_export(self, export_type, filters):
    """
    批量导出任务（低优先级）
    
    这类任务耗时较长，但不紧急，可以在系统空闲时处理
    """
    print(f"[低优先级] 批量导出 - 任务 ID: {self.request.id}")
    print(f"导出类型: {export_type}")
    
    # 模拟数据导出过程
    total_records = 10000
    batch_size = 1000
    
    for i in range(0, total_records, batch_size):
        # 模拟批量处理
        time.sleep(0.5)
        
        # 更新进度
        progress = min((i + batch_size) / total_records * 100, 100)
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + batch_size,
                'total': total_records,
                'percent': int(progress)
            }
        )
        
        print(f"[低优先级] 导出进度: {int(progress)}%")
    
    result = {
        'task_id': self.request.id,
        'export_type': export_type,
        'records_count': total_records,
        'file_name': f'export_{export_type}_{int(time.time())}.xlsx',
        'priority': 'low',
        'completed_at': datetime.now().isoformat(),
        'status': 'completed'
    }
    
    print(f"[低优先级] 批量导出完成")
    return result


@app.task(name='task_queue.cleanup_old_data', bind=True)
def cleanup_old_data(self, days_old):
    """
    清理旧数据任务（低优先级）
    
    这类维护任务可以在系统负载低时执行
    """
    print(f"[低优先级] 清理旧数据 - 任务 ID: {self.request.id}")
    print(f"清理 {days_old} 天前的数据")
    
    # 模拟数据清理
    time.sleep(3)
    
    result = {
        'task_id': self.request.id,
        'days_old': days_old,
        'deleted_count': random.randint(100, 1000),
        'priority': 'low',
        'completed_at': datetime.now().isoformat(),
        'status': 'completed'
    }
    
    print(f"[低优先级] 数据清理完成，删除 {result['deleted_count']} 条记录")
    return result


# ============================================================================
# 自定义队列任务
# ============================================================================

@app.task(name='task_queue.custom_queue_task', bind=True)
def custom_queue_task(self, data):
    """
    自定义队列任务
    
    可以在调用时动态指定队列
    """
    print(f"[自定义队列] 处理任务 - 任务 ID: {self.request.id}")
    print(f"队列: {self.request.delivery_info.get('routing_key', 'unknown')}")
    
    time.sleep(1)
    
    result = {
        'task_id': self.request.id,
        'data': data,
        'queue': self.request.delivery_info.get('routing_key', 'unknown'),
        'processed_at': datetime.now().isoformat()
    }
    
    return result


# ============================================================================
# 任务调用示例
# ============================================================================

def demo_priority_queues():
    """演示不同优先级的任务队列"""
    print("\n" + "="*60)
    print("示例 1: 不同优先级的任务队列")
    print("="*60)
    
    # 提交高优先级任务
    print("\n提交高优先级任务...")
    high_task = urgent_notification.delay('user_001', '系统紧急维护通知')
    print(f"高优先级任务已提交: {high_task.id}")
    
    # 提交默认优先级任务
    print("\n提交默认优先级任务...")
    normal_task = process_order.delay('order_123', [
        {'name': '商品A', 'price': 100},
        {'name': '商品B', 'price': 200}
    ])
    print(f"默认优先级任务已提交: {normal_task.id}")
    
    # 提交低优先级任务
    print("\n提交低优先级任务...")
    low_task = cleanup_old_data.delay(30)
    print(f"低优先级任务已提交: {low_task.id}")
    
    # 等待任务完成
    print("\n等待任务完成...")
    print(f"高优先级任务结果: {high_task.get(timeout=30)}")
    print(f"默认优先级任务结果: {normal_task.get(timeout=30)}")
    print(f"低优先级任务结果: {low_task.get(timeout=30)}")


def demo_task_retry():
    """演示任务重试机制"""
    print("\n" + "="*60)
    print("示例 2: 任务重试机制")
    print("="*60)
    
    # 提交可能失败的任务
    print("\n提交关键告警任务（可能失败并重试）...")
    task = critical_alert.delay('system_error', {'error_code': 500, 'message': '服务器错误'})
    print(f"任务已提交: {task.id}")
    
    # 等待任务完成（可能经过多次重试）
    print("等待任务完成（观察重试过程）...")
    try:
        result = task.get(timeout=60)
        print(f"\n任务最终成功: {result}")
    except Exception as e:
        print(f"\n任务最终失败: {e}")


def demo_batch_tasks():
    """演示批量提交任务"""
    print("\n" + "="*60)
    print("示例 3: 批量提交任务")
    print("="*60)
    
    tasks = []
    
    # 批量提交订单处理任务
    print("\n批量提交订单处理任务...")
    for i in range(5):
        order_id = f"order_{i+1:03d}"
        items = [
            {'name': f'商品{j+1}', 'price': random.randint(50, 500)}
            for j in range(random.randint(1, 5))
        ]
        task = process_order.delay(order_id, items)
        tasks.append(task)
        print(f"已提交订单 {order_id}: {task.id}")
    
    # 等待所有任务完成
    print("\n等待所有任务完成...")
    for i, task in enumerate(tasks):
        result = task.get(timeout=60)
        print(f"订单 {i+1} 处理完成: {result['order_id']} - 总金额: {result['total_amount']}")


def demo_export_with_progress():
    """演示带进度的导出任务"""
    print("\n" + "="*60)
    print("示例 4: 带进度的导出任务")
    print("="*60)
    
    # 提交导出任务
    print("\n提交批量导出任务...")
    task = batch_export.delay('users', {'status': 'active'})
    print(f"任务已提交: {task.id}")
    
    # 追踪进度
    print("\n追踪导出进度...")
    while not task.ready():
        if task.state == 'PROGRESS':
            meta = task.info
            print(f"进度: {meta.get('percent', 0)}% ({meta.get('current', 0)}/{meta.get('total', 0)})")
        else:
            print(f"任务状态: {task.state}")
        
        time.sleep(1)
    
    # 获取结果
    result = task.get()
    print(f"\n导出完成！")
    print(f"文件名: {result['file_name']}")
    print(f"记录数: {result['records_count']}")


def demo_custom_queue():
    """演示自定义队列"""
    print("\n" + "="*60)
    print("示例 5: 动态指定队列")
    print("="*60)
    
    # 使用 apply_async 动态指定队列
    print("\n提交任务到不同队列...")
    
    # 提交到高优先级队列
    task1 = custom_queue_task.apply_async(
        args=[{'type': 'urgent'}],
        queue='high_priority'
    )
    print(f"任务提交到高优先级队列: {task1.id}")
    
    # 提交到默认队列
    task2 = custom_queue_task.apply_async(
        args=[{'type': 'normal'}],
        queue='default'
    )
    print(f"任务提交到默认队列: {task2.id}")
    
    # 提交到低优先级队列
    task3 = custom_queue_task.apply_async(
        args=[{'type': 'batch'}],
        queue='low_priority'
    )
    print(f"任务提交到低优先级队列: {task3.id}")
    
    # 等待结果
    print("\n等待任务完成...")
    print(f"任务 1 结果: {task1.get(timeout=30)}")
    print(f"任务 2 结果: {task2.get(timeout=30)}")
    print(f"任务 3 结果: {task3.get(timeout=30)}")


def demo_inventory_update_retry():
    """演示库存更新的重试机制"""
    print("\n" + "="*60)
    print("示例 6: 库存更新重试（指数退避）")
    print("="*60)
    
    # 提交多个库存更新任务
    print("\n提交库存更新任务...")
    tasks = []
    for i in range(3):
        task = update_inventory.delay(f'product_{i+1}', random.randint(1, 100))
        tasks.append(task)
        print(f"已提交库存更新任务: {task.id}")
    
    # 等待所有任务完成
    print("\n等待任务完成（观察重试过程）...")
    for i, task in enumerate(tasks):
        try:
            result = task.get(timeout=120)
            print(f"任务 {i+1} 成功: {result['product_id']} - 数量: {result['quantity']}")
        except Exception as e:
            print(f"任务 {i+1} 失败: {e}")


# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   任务队列示例                               ║
    ║                                                              ║
    ║  确保已经启动 Redis 和多个 Celery Worker:                   ║
    ║  1. docker run -d -p 6379:6379 redis:latest                 ║
    ║  2. celery -A 02_task_queue worker -Q high_priority \\       ║
    ║     --loglevel=info -n high_worker@%h                        ║
    ║  3. celery -A 02_task_queue worker -Q default \\             ║
    ║     --loglevel=info -n default_worker@%h                     ║
    ║  4. celery -A 02_task_queue worker -Q low_priority \\        ║
    ║     --loglevel=info -n low_worker@%h                         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 运行所有示例
        demo_priority_queues()
        demo_task_retry()
        demo_batch_tasks()
        demo_export_with_progress()
        demo_custom_queue()
        demo_inventory_update_retry()
        
        print("\n" + "="*60)
        print("所有示例执行完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("1. Redis 服务正在运行")
        print("2. 已启动不同队列的 Celery Worker")
        print("3. 已安装必要的依赖: pip install celery redis")
