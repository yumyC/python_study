"""
Celery 基础示例

本示例演示：
1. Celery 应用的配置和初始化
2. 创建简单的异步任务
3. 调用异步任务的不同方式
4. 获取任务执行结果
5. 查询任务状态

运行说明：
1. 安装依赖：pip install celery redis
2. 启动 Redis：docker run -d -p 6379:6379 redis:latest
3. 启动 Worker：celery -A 01_celery_basics worker --loglevel=info
4. 在另一个终端运行：python 01_celery_basics.py
"""

from celery import Celery
import time
from datetime import datetime

# ============================================================================
# Celery 应用配置
# ============================================================================

# 创建 Celery 应用实例
# broker: 消息代理，用于存储和分发任务
# backend: 结果后端，用于存储任务执行结果
app = Celery(
    'celery_basics',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 配置 Celery
app.conf.update(
    # 任务序列化格式
    task_serializer='json',
    # 接受的内容类型
    accept_content=['json'],
    # 结果序列化格式
    result_serializer='json',
    # 时区设置
    timezone='Asia/Shanghai',
    # 启用 UTC
    enable_utc=True,
    # 追踪任务开始状态
    task_track_started=True,
    # 任务结果过期时间（秒）
    result_expires=3600,
)


# ============================================================================
# 基础任务示例
# ============================================================================

@app.task(name='celery_basics.add')
def add(x, y):
    """
    简单的加法任务
    
    这是最基本的 Celery 任务示例
    使用 @app.task 装饰器将普通函数转换为 Celery 任务
    """
    print(f"执行加法任务: {x} + {y}")
    return x + y


@app.task(name='celery_basics.multiply')
def multiply(x, y):
    """
    乘法任务
    
    演示任务的基本结构
    """
    print(f"执行乘法任务: {x} * {y}")
    result = x * y
    return result


@app.task(name='celery_basics.long_running_task')
def long_running_task(duration):
    """
    模拟长时间运行的任务
    
    Args:
        duration: 任务执行时间（秒）
    
    Returns:
        任务完成信息
    """
    print(f"开始执行长时间任务，预计耗时 {duration} 秒")
    start_time = time.time()
    
    # 模拟耗时操作
    time.sleep(duration)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    result = {
        'duration': duration,
        'actual_time': elapsed,
        'completed_at': datetime.now().isoformat()
    }
    
    print(f"长时间任务完成，实际耗时 {elapsed:.2f} 秒")
    return result


@app.task(name='celery_basics.process_data', bind=True)
def process_data(self, data):
    """
    数据处理任务（带进度更新）
    
    bind=True 允许任务访问自身实例（self）
    可以用于更新任务状态、获取任务 ID 等
    
    Args:
        data: 要处理的数据列表
    
    Returns:
        处理结果
    """
    total = len(data)
    results = []
    
    print(f"开始处理 {total} 条数据，任务 ID: {self.request.id}")
    
    for i, item in enumerate(data):
        # 模拟数据处理
        time.sleep(0.5)
        processed = item * 2
        results.append(processed)
        
        # 更新任务进度
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total,
                'percent': int((i + 1) / total * 100)
            }
        )
        
        print(f"处理进度: {i + 1}/{total}")
    
    return {
        'processed_count': total,
        'results': results,
        'task_id': self.request.id
    }


@app.task(name='celery_basics.send_email')
def send_email(to, subject, body):
    """
    模拟发送邮件任务
    
    这是异步任务的典型应用场景
    发送邮件通常需要较长时间，不应该阻塞主请求
    """
    print(f"准备发送邮件到: {to}")
    print(f"主题: {subject}")
    
    # 模拟邮件发送过程
    time.sleep(2)
    
    result = {
        'to': to,
        'subject': subject,
        'status': 'sent',
        'sent_at': datetime.now().isoformat()
    }
    
    print(f"邮件发送成功: {to}")
    return result


@app.task(name='celery_basics.generate_report')
def generate_report(user_id, report_type):
    """
    模拟生成报表任务
    
    报表生成通常涉及大量数据查询和计算
    适合作为异步任务执行
    """
    print(f"开始生成报表 - 用户: {user_id}, 类型: {report_type}")
    
    # 模拟报表生成过程
    time.sleep(3)
    
    report = {
        'user_id': user_id,
        'report_type': report_type,
        'file_name': f'report_{user_id}_{report_type}_{int(time.time())}.pdf',
        'generated_at': datetime.now().isoformat(),
        'status': 'completed'
    }
    
    print(f"报表生成完成: {report['file_name']}")
    return report


# ============================================================================
# 任务调用示例
# ============================================================================

def demo_basic_task_call():
    """演示基本的任务调用"""
    print("\n" + "="*60)
    print("示例 1: 基本任务调用")
    print("="*60)
    
    # 使用 delay() 方法调用任务（最简单的方式）
    result = add.delay(4, 6)
    
    print(f"任务已提交，任务 ID: {result.id}")
    print(f"任务状态: {result.status}")
    
    # 等待任务完成并获取结果
    print("等待任务完成...")
    value = result.get(timeout=10)  # 最多等待 10 秒
    
    print(f"任务完成，结果: {value}")
    print(f"最终状态: {result.status}")


def demo_apply_async():
    """演示使用 apply_async() 调用任务"""
    print("\n" + "="*60)
    print("示例 2: 使用 apply_async() 调用任务")
    print("="*60)
    
    # apply_async() 提供更多控制选项
    result = multiply.apply_async(
        args=(5, 8),  # 任务参数
        countdown=3,  # 延迟 3 秒执行
    )
    
    print(f"任务已提交，将在 3 秒后执行")
    print(f"任务 ID: {result.id}")
    
    # 等待任务完成
    print("等待任务完成...")
    value = result.get(timeout=15)
    
    print(f"任务完成，结果: {value}")


def demo_task_status():
    """演示任务状态查询"""
    print("\n" + "="*60)
    print("示例 3: 任务状态查询")
    print("="*60)
    
    # 提交一个长时间运行的任务
    result = long_running_task.delay(5)
    
    print(f"任务已提交，任务 ID: {result.id}")
    
    # 轮询任务状态
    while not result.ready():
        print(f"任务状态: {result.status}")
        time.sleep(1)
    
    # 任务完成
    if result.successful():
        print(f"任务成功完成")
        print(f"结果: {result.result}")
    else:
        print(f"任务失败")
        print(f"错误: {result.result}")


def demo_progress_tracking():
    """演示任务进度追踪"""
    print("\n" + "="*60)
    print("示例 4: 任务进度追踪")
    print("="*60)
    
    # 提交数据处理任务
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = process_data.delay(data)
    
    print(f"任务已提交，任务 ID: {result.id}")
    print("追踪任务进度...")
    
    # 轮询任务进度
    while not result.ready():
        if result.state == 'PROGRESS':
            meta = result.info
            print(f"进度: {meta.get('percent', 0)}% ({meta.get('current', 0)}/{meta.get('total', 0)})")
        else:
            print(f"任务状态: {result.state}")
        
        time.sleep(1)
    
    # 获取最终结果
    final_result = result.get()
    print(f"\n任务完成！")
    print(f"处理了 {final_result['processed_count']} 条数据")
    print(f"结果: {final_result['results']}")


def demo_multiple_tasks():
    """演示同时提交多个任务"""
    print("\n" + "="*60)
    print("示例 5: 同时提交多个任务")
    print("="*60)
    
    # 提交多个任务
    tasks = []
    
    # 发送多封邮件
    emails = [
        ('user1@example.com', '欢迎', '欢迎使用我们的服务'),
        ('user2@example.com', '通知', '您有新的消息'),
        ('user3@example.com', '提醒', '请完成您的个人资料'),
    ]
    
    for to, subject, body in emails:
        result = send_email.delay(to, subject, body)
        tasks.append(result)
        print(f"已提交邮件任务: {to} (ID: {result.id})")
    
    # 等待所有任务完成
    print("\n等待所有任务完成...")
    for i, result in enumerate(tasks):
        value = result.get(timeout=30)
        print(f"任务 {i+1} 完成: {value['to']} - {value['status']}")
    
    print("\n所有邮件发送完成！")


def demo_report_generation():
    """演示报表生成任务"""
    print("\n" + "="*60)
    print("示例 6: 报表生成任务")
    print("="*60)
    
    # 提交报表生成任务
    result = generate_report.delay(
        user_id='user_123',
        report_type='monthly_sales'
    )
    
    print(f"报表生成任务已提交，任务 ID: {result.id}")
    print("等待报表生成...")
    
    # 等待任务完成
    report = result.get(timeout=30)
    
    print(f"\n报表生成完成！")
    print(f"文件名: {report['file_name']}")
    print(f"生成时间: {report['generated_at']}")


def demo_async_result_methods():
    """演示 AsyncResult 的各种方法"""
    print("\n" + "="*60)
    print("示例 7: AsyncResult 方法演示")
    print("="*60)
    
    # 提交任务
    result = add.delay(10, 20)
    
    print(f"任务 ID: {result.id}")
    print(f"任务名称: {result.name}")
    
    # 检查任务是否完成
    print(f"任务是否完成: {result.ready()}")
    
    # 检查任务是否成功
    print(f"任务是否成功: {result.successful()}")
    
    # 获取任务状态
    print(f"任务状态: {result.status}")
    
    # 等待任务完成
    result.get(timeout=10)
    
    print(f"\n任务完成后:")
    print(f"任务是否完成: {result.ready()}")
    print(f"任务是否成功: {result.successful()}")
    print(f"任务状态: {result.status}")
    print(f"任务结果: {result.result}")


# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   Celery 基础示例                            ║
    ║                                                              ║
    ║  确保已经启动 Redis 和 Celery Worker:                       ║
    ║  1. docker run -d -p 6379:6379 redis:latest                 ║
    ║  2. celery -A 01_celery_basics worker --loglevel=info       ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 运行所有示例
        demo_basic_task_call()
        demo_apply_async()
        demo_task_status()
        demo_progress_tracking()
        demo_multiple_tasks()
        demo_report_generation()
        demo_async_result_methods()
        
        print("\n" + "="*60)
        print("所有示例执行完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("1. Redis 服务正在运行")
        print("2. Celery Worker 已启动")
        print("3. 已安装必要的依赖: pip install celery redis")
