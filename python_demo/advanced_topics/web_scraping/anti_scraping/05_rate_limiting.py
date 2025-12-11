#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
频率限制应对教程

本教程介绍如何应对网站的频率限制和反爬机制，包括请求频率控制、
智能延迟、分布式请求等技术。

作者: Python学习课程
日期: 2024
"""

import time
import random
import threading
from collections import deque, defaultdict
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json
from datetime import datetime, timedelta
import math


class RateLimiter:
    """
    频率限制器
    """
    
    def __init__(self, max_requests=10, time_window=60):
        """
        初始化频率限制器
        
        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口大小（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = threading.Lock()
    
    def acquire(self):
        """
        获取请求许可
        """
        with self.lock:
            current_time = time.time()
            
            # 清理过期的请求记录
            while self.requests and current_time - self.requests[0] > self.time_window:
                self.requests.popleft()
            
            # 检查是否超过限制
            if len(self.requests) >= self.max_requests:
                # 计算需要等待的时间
                oldest_request = self.requests[0]
                wait_time = self.time_window - (current_time - oldest_request)
                return False, wait_time
            
            # 记录当前请求
            self.requests.append(current_time)
            return True, 0
    
    def wait_if_needed(self):
        """
        如果需要则等待
        """
        allowed, wait_time = self.acquire()
        
        if not allowed:
            print(f"频率限制触发，等待 {wait_time:.2f} 秒...")
            time.sleep(wait_time + 0.1)  # 额外等待0.1秒确保安全
            return self.wait_if_needed()  # 递归重试
        
        return True


class AdaptiveRateLimiter:
    """
    自适应频率限制器
    """
    
    def __init__(self, initial_delay=1.0, max_delay=60.0, backoff_factor=2.0):
        """
        初始化自适应频率限制器
        
        Args:
            initial_delay: 初始延迟时间
            max_delay: 最大延迟时间
            backoff_factor: 退避因子
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.current_delay = initial_delay
        self.success_count = 0
        self.failure_count = 0
        self.lock = threading.Lock()
    
    def record_success(self):
        """
        记录成功请求
        """
        with self.lock:
            self.success_count += 1
            self.failure_count = 0  # 重置失败计数
            
            # 成功时逐渐减少延迟
            if self.success_count >= 5:  # 连续5次成功
                self.current_delay = max(
                    self.initial_delay,
                    self.current_delay * 0.8  # 减少20%
                )
                self.success_count = 0
    
    def record_failure(self, error_type='unknown'):
        """
        记录失败请求
        
        Args:
            error_type: 错误类型 (rate_limit, timeout, server_error, etc.)
        """
        with self.lock:
            self.failure_count += 1
            self.success_count = 0  # 重置成功计数
            
            # 根据错误类型调整延迟
            if error_type == 'rate_limit':
                # 频率限制错误，大幅增加延迟
                self.current_delay = min(
                    self.max_delay,
                    self.current_delay * self.backoff_factor
                )
            elif error_type == 'server_error':
                # 服务器错误，适度增加延迟
                self.current_delay = min(
                    self.max_delay,
                    self.current_delay * 1.5
                )
            else:
                # 其他错误，小幅增加延迟
                self.current_delay = min(
                    self.max_delay,
                    self.current_delay * 1.2
                )
    
    def get_delay(self):
        """
        获取当前延迟时间
        """
        with self.lock:
            # 添加随机抖动，避免请求同步
            jitter = random.uniform(0.8, 1.2)
            return self.current_delay * jitter
    
    def wait(self):
        """
        等待适当的时间
        """
        delay = self.get_delay()
        print(f"自适应延迟: {delay:.2f} 秒")
        time.sleep(delay)


class DistributedRateLimiter:
    """
    分布式频率限制器
    """
    
    def __init__(self, total_rate=100, worker_count=5):
        """
        初始化分布式频率限制器
        
        Args:
            total_rate: 总的请求频率（每分钟）
            worker_count: 工作线程数量
        """
        self.total_rate = total_rate
        self.worker_count = worker_count
        self.rate_per_worker = total_rate / worker_count
        self.worker_limiters = {}
        
        # 为每个工作线程创建独立的限制器
        for i in range(worker_count):
            self.worker_limiters[i] = RateLimiter(
                max_requests=int(self.rate_per_worker),
                time_window=60
            )
    
    def get_worker_limiter(self, worker_id):
        """
        获取指定工作线程的限制器
        """
        return self.worker_limiters.get(worker_id % self.worker_count)
    
    def acquire(self, worker_id):
        """
        为指定工作线程获取请求许可
        """
        limiter = self.get_worker_limiter(worker_id)
        return limiter.acquire()


class SmartRequestScheduler:
    """
    智能请求调度器
    """
    
    def __init__(self):
        self.request_queue = queue.PriorityQueue()
        self.rate_limiter = AdaptiveRateLimiter()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited': 0,
            'start_time': time.time()
        }
    
    def add_request(self, url, priority=1, **kwargs):
        """
        添加请求到队列
        
        Args:
            url: 请求URL
            priority: 优先级（数字越小优先级越高）
            **kwargs: 其他请求参数
        """
        request_item = (priority, time.time(), url, kwargs)
        self.request_queue.put(request_item)
    
    def execute_request(self, url, **kwargs):
        """
        执行单个请求
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 等待适当的时间
                self.rate_limiter.wait()
                
                # 发送请求
                response = self.session.get(url, timeout=10, **kwargs)
                
                # 更新统计
                self.stats['total_requests'] += 1
                
                # 检查响应状态
                if response.status_code == 200:
                    self.rate_limiter.record_success()
                    self.stats['successful_requests'] += 1
                    return response
                
                elif response.status_code == 429:  # Too Many Requests
                    self.rate_limiter.record_failure('rate_limit')
                    self.stats['rate_limited'] += 1
                    
                    # 检查 Retry-After 头部
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        wait_time = int(retry_after)
                        print(f"服务器要求等待 {wait_time} 秒")
                        time.sleep(wait_time)
                    
                elif 500 <= response.status_code < 600:
                    self.rate_limiter.record_failure('server_error')
                    self.stats['failed_requests'] += 1
                
                else:
                    self.rate_limiter.record_failure('client_error')
                    self.stats['failed_requests'] += 1
                    break  # 客户端错误不重试
                
            except requests.exceptions.Timeout:
                self.rate_limiter.record_failure('timeout')
                print(f"请求超时，重试 {attempt + 1}/{max_retries}")
                
            except requests.exceptions.ConnectionError:
                self.rate_limiter.record_failure('connection_error')
                print(f"连接错误，重试 {attempt + 1}/{max_retries}")
                
            except Exception as e:
                self.rate_limiter.record_failure('unknown')
                print(f"未知错误: {e}")
                break
        
        self.stats['failed_requests'] += 1
        return None
    
    def process_queue(self, max_workers=3):
        """
        处理请求队列
        """
        print(f"开始处理请求队列，工作线程数: {max_workers}")
        
        def worker(worker_id):
            """工作线程函数"""
            while True:
                try:
                    # 获取请求（超时1秒）
                    priority, timestamp, url, kwargs = self.request_queue.get(timeout=1)
                    
                    print(f"工作线程 {worker_id} 处理: {url}")
                    
                    # 执行请求
                    response = self.execute_request(url, **kwargs)
                    
                    if response:
                        print(f"  成功: {response.status_code}")
                    else:
                        print(f"  失败")
                    
                    # 标记任务完成
                    self.request_queue.task_done()
                    
                except queue.Empty:
                    # 队列为空，退出
                    break
                except Exception as e:
                    print(f"工作线程 {worker_id} 出错: {e}")
        
        # 启动工作线程
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(max_workers)]
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"工作线程异常: {e}")
    
    def get_stats(self):
        """
        获取统计信息
        """
        elapsed_time = time.time() - self.stats['start_time']
        
        return {
            **self.stats,
            'elapsed_time': elapsed_time,
            'requests_per_second': self.stats['total_requests'] / elapsed_time if elapsed_time > 0 else 0,
            'success_rate': self.stats['successful_requests'] / self.stats['total_requests'] if self.stats['total_requests'] > 0 else 0
        }


def rate_limiting_demo():
    """
    频率限制演示
    """
    print("=== 频率限制演示 ===")
    
    # 创建频率限制器（每分钟最多5个请求）
    limiter = RateLimiter(max_requests=5, time_window=60)
    
    # 模拟快速发送请求
    test_urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/get',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/headers',
        'https://httpbin.org/ip',
        'https://httpbin.org/uuid',  # 这个会触发频率限制
        'https://httpbin.org/json',
        'https://httpbin.org/status/200'
    ]
    
    print(f"测试 {len(test_urls)} 个请求，频率限制: 5请求/分钟")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n请求 {i}: {url}")
        
        # 检查频率限制
        limiter.wait_if_needed()
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            print(f"  响应: {response.status_code}, 耗时: {elapsed:.2f}s")
            
        except Exception as e:
            print(f"  请求失败: {e}")


def adaptive_rate_limiting_demo():
    """
    自适应频率限制演示
    """
    print("\n=== 自适应频率限制演示 ===")
    
    # 创建自适应限制器
    adaptive_limiter = AdaptiveRateLimiter(
        initial_delay=0.5,
        max_delay=10.0,
        backoff_factor=2.0
    )
    
    # 模拟不同的响应情况
    scenarios = [
        ('success', 'https://httpbin.org/status/200'),
        ('success', 'https://httpbin.org/get'),
        ('rate_limit', 'https://httpbin.org/status/429'),  # 模拟频率限制
        ('success', 'https://httpbin.org/json'),
        ('server_error', 'https://httpbin.org/status/500'),  # 模拟服务器错误
        ('success', 'https://httpbin.org/uuid'),
        ('success', 'https://httpbin.org/headers'),
    ]
    
    print("模拟不同响应情况的自适应调整:")
    
    for scenario_type, url in scenarios:
        print(f"\n场景: {scenario_type}")
        
        # 等待自适应延迟
        adaptive_limiter.wait()
        
        try:
            if scenario_type == 'rate_limit':
                # 模拟频率限制响应
                print("  模拟 429 Too Many Requests")
                adaptive_limiter.record_failure('rate_limit')
                
            elif scenario_type == 'server_error':
                # 模拟服务器错误
                print("  模拟 500 Server Error")
                adaptive_limiter.record_failure('server_error')
                
            else:
                # 正常请求
                response = requests.get(url, timeout=5)
                print(f"  响应: {response.status_code}")
                
                if response.status_code == 200:
                    adaptive_limiter.record_success()
                else:
                    adaptive_limiter.record_failure('client_error')
                    
        except Exception as e:
            print(f"  请求异常: {e}")
            adaptive_limiter.record_failure('timeout')
        
        print(f"  当前延迟: {adaptive_limiter.current_delay:.2f}s")


def smart_scheduler_demo():
    """
    智能调度器演示
    """
    print("\n=== 智能请求调度器演示 ===")
    
    # 创建智能调度器
    scheduler = SmartRequestScheduler()
    
    # 添加不同优先级的请求
    high_priority_urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/json',
    ]
    
    medium_priority_urls = [
        'https://httpbin.org/user-agent',
        'https://httpbin.org/headers',
        'https://httpbin.org/ip',
    ]
    
    low_priority_urls = [
        'https://httpbin.org/uuid',
        'https://httpbin.org/base64/aGVsbG8gd29ybGQ=',
        'https://httpbin.org/delay/1',
    ]
    
    # 添加高优先级请求
    for url in high_priority_urls:
        scheduler.add_request(url, priority=1)
    
    # 添加中等优先级请求
    for url in medium_priority_urls:
        scheduler.add_request(url, priority=2)
    
    # 添加低优先级请求
    for url in low_priority_urls:
        scheduler.add_request(url, priority=3)
    
    print(f"已添加 {len(high_priority_urls + medium_priority_urls + low_priority_urls)} 个请求到队列")
    
    # 处理队列
    scheduler.process_queue(max_workers=2)
    
    # 显示统计信息
    stats = scheduler.get_stats()
    print(f"\n=== 执行统计 ===")
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功请求: {stats['successful_requests']}")
    print(f"失败请求: {stats['failed_requests']}")
    print(f"频率限制: {stats['rate_limited']}")
    print(f"成功率: {stats['success_rate']:.2%}")
    print(f"平均速率: {stats['requests_per_second']:.2f} 请求/秒")
    print(f"总耗时: {stats['elapsed_time']:.2f} 秒")


def advanced_rate_limiting_techniques():
    """
    高级频率限制技术
    """
    print("\n=== 高级频率限制技术 ===")
    
    # 技术1: 令牌桶算法
    def token_bucket_demo():
        print("\n技术1: 令牌桶算法")
        
        class TokenBucket:
            def __init__(self, capacity=10, refill_rate=1):
                """
                令牌桶算法实现
                
                Args:
                    capacity: 桶容量
                    refill_rate: 令牌补充速率（每秒）
                """
                self.capacity = capacity
                self.tokens = capacity
                self.refill_rate = refill_rate
                self.last_refill = time.time()
                self.lock = threading.Lock()
            
            def consume(self, tokens=1):
                """
                消费令牌
                
                Args:
                    tokens: 需要消费的令牌数
                
                Returns:
                    bool: 是否成功消费
                """
                with self.lock:
                    # 补充令牌
                    now = time.time()
                    elapsed = now - self.last_refill
                    self.tokens = min(
                        self.capacity,
                        self.tokens + elapsed * self.refill_rate
                    )
                    self.last_refill = now
                    
                    # 检查是否有足够令牌
                    if self.tokens >= tokens:
                        self.tokens -= tokens
                        return True
                    else:
                        return False
            
            def wait_for_tokens(self, tokens=1):
                """
                等待足够的令牌
                """
                while not self.consume(tokens):
                    # 计算等待时间
                    wait_time = (tokens - self.tokens) / self.refill_rate
                    print(f"等待令牌，预计 {wait_time:.2f} 秒")
                    time.sleep(min(wait_time, 1.0))  # 最多等待1秒后重试
        
        # 演示令牌桶
        bucket = TokenBucket(capacity=5, refill_rate=2)  # 每秒补充2个令牌
        
        print("令牌桶演示 (容量: 5, 补充速率: 2/秒):")
        
        for i in range(8):
            print(f"请求 {i+1}:")
            
            if bucket.consume(1):
                print(f"  成功获取令牌，剩余: {bucket.tokens:.1f}")
            else:
                print(f"  令牌不足，等待补充...")
                bucket.wait_for_tokens(1)
                print(f"  获取令牌成功，剩余: {bucket.tokens:.1f}")
            
            # 模拟请求处理时间
            time.sleep(0.2)
    
    # 技术2: 滑动窗口算法
    def sliding_window_demo():
        print("\n技术2: 滑动窗口算法")
        
        class SlidingWindowLimiter:
            def __init__(self, max_requests=10, window_size=60, sub_windows=6):
                """
                滑动窗口限制器
                
                Args:
                    max_requests: 窗口内最大请求数
                    window_size: 窗口大小（秒）
                    sub_windows: 子窗口数量
                """
                self.max_requests = max_requests
                self.window_size = window_size
                self.sub_window_size = window_size / sub_windows
                self.sub_windows = [0] * sub_windows
                self.current_window = 0
                self.last_update = time.time()
                self.lock = threading.Lock()
            
            def is_allowed(self):
                """
                检查是否允许请求
                """
                with self.lock:
                    now = time.time()
                    
                    # 更新窗口
                    elapsed = now - self.last_update
                    windows_to_shift = int(elapsed / self.sub_window_size)
                    
                    if windows_to_shift > 0:
                        # 移动窗口
                        for _ in range(min(windows_to_shift, len(self.sub_windows))):
                            self.current_window = (self.current_window + 1) % len(self.sub_windows)
                            self.sub_windows[self.current_window] = 0
                        
                        self.last_update = now
                    
                    # 检查总请求数
                    total_requests = sum(self.sub_windows)
                    
                    if total_requests < self.max_requests:
                        self.sub_windows[self.current_window] += 1
                        return True
                    else:
                        return False
        
        # 演示滑动窗口
        limiter = SlidingWindowLimiter(max_requests=5, window_size=10, sub_windows=5)
        
        print("滑动窗口演示 (5请求/10秒，5个子窗口):")
        
        for i in range(8):
            allowed = limiter.is_allowed()
            status = "允许" if allowed else "拒绝"
            print(f"请求 {i+1}: {status}")
            
            if not allowed:
                print("  等待窗口滑动...")
                time.sleep(2)  # 等待窗口滑动
    
    # 技术3: 分布式限流
    def distributed_limiting_demo():
        print("\n技术3: 分布式限流")
        
        class DistributedLimiter:
            def __init__(self, node_id, total_limit=100, node_count=5):
                """
                分布式限流器
                
                Args:
                    node_id: 节点ID
                    total_limit: 总限制
                    node_count: 节点数量
                """
                self.node_id = node_id
                self.total_limit = total_limit
                self.node_count = node_count
                self.local_limit = total_limit // node_count
                self.local_counter = 0
                self.global_counter = 0  # 在实际应用中，这应该是共享存储
                self.last_reset = time.time()
                self.window_size = 60  # 1分钟窗口
            
            def is_allowed(self):
                """
                检查是否允许请求
                """
                now = time.time()
                
                # 重置计数器（每分钟）
                if now - self.last_reset > self.window_size:
                    self.local_counter = 0
                    self.global_counter = 0  # 在实际应用中需要同步
                    self.last_reset = now
                
                # 检查本地限制
                if self.local_counter >= self.local_limit:
                    return False
                
                # 检查全局限制（简化版本）
                estimated_global = self.local_counter * self.node_count
                if estimated_global >= self.total_limit:
                    return False
                
                self.local_counter += 1
                return True
        
        # 演示分布式限流
        nodes = [
            DistributedLimiter(node_id=i, total_limit=20, node_count=3)
            for i in range(3)
        ]
        
        print("分布式限流演示 (总限制: 20, 3个节点):")
        
        for round_num in range(3):
            print(f"\n轮次 {round_num + 1}:")
            
            for node in nodes:
                for req in range(3):  # 每个节点发送3个请求
                    allowed = node.is_allowed()
                    status = "✓" if allowed else "✗"
                    print(f"  节点{node.node_id} 请求{req+1}: {status} (本地计数: {node.local_counter})")
    
    # 执行演示
    token_bucket_demo()
    sliding_window_demo()
    distributed_limiting_demo()


def main():
    """
    主函数，运行所有示例
    """
    print("频率限制应对教程")
    print("=" * 50)
    
    try:
        # 1. 基础频率限制演示
        rate_limiting_demo()
        
        # 2. 自适应频率限制演示
        adaptive_rate_limiting_demo()
        
        # 3. 智能调度器演示
        smart_scheduler_demo()
        
        # 4. 高级技术演示
        advanced_rate_limiting_techniques()
        
        print(f"\n=== 频率限制应对最佳实践 ===")
        best_practices = [
            "1. 实现智能延迟机制",
            "2. 监控响应状态码",
            "3. 使用自适应算法",
            "4. 实现请求队列管理",
            "5. 分布式请求调度",
            "6. 遵守 Retry-After 头部",
            "7. 实现指数退避算法",
            "8. 监控请求成功率",
            "9. 使用多种限流算法",
            "10. 建立请求优先级机制"
        ]
        
        for practice in best_practices:
            print(f"  {practice}")
        
        print(f"\n=== 常见限流机制识别 ===")
        rate_limit_indicators = [
            "• HTTP 429 Too Many Requests",
            "• HTTP 503 Service Unavailable",
            "• Retry-After 响应头",
            "• X-RateLimit-* 系列头部",
            "• 响应时间突然增加",
            "• 连接被重置或超时",
            "• 返回验证码页面",
            "• IP 被临时封禁"
        ]
        
        for indicator in rate_limit_indicators:
            print(f"  {indicator}")
        
        print(f"\n=== 应对策略 ===")
        strategies = [
            "• 降低请求频率",
            "• 使用代理轮换",
            "• 实现智能重试",
            "• 分散请求时间",
            "• 模拟人类行为",
            "• 维持会话状态",
            "• 监控服务器响应",
            "• 建立请求配额管理"
        ]
        
        for strategy in strategies:
            print(f"  {strategy}")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. 频率限制类型
   - 固定窗口限制
   - 滑动窗口限制
   - 令牌桶算法
   - 漏桶算法
   - 分布式限流

2. 检测机制
   - HTTP 状态码监控
   - 响应时间分析
   - 错误率统计
   - 服务器响应头分析
   - 连接状态监控

3. 应对策略
   - 自适应延迟
   - 指数退避
   - 请求队列管理
   - 优先级调度
   - 分布式请求

4. 高级技术
   - 智能调度算法
   - 机器学习预测
   - 动态参数调整
   - 多层限流策略
   - 实时监控告警

5. 最佳实践
   - 遵守服务器指示
   - 实现优雅降级
   - 监控关键指标
   - 建立熔断机制
   - 合理设置超时

算法选择:
- 令牌桶: 允许突发流量
- 漏桶: 平滑输出流量
- 固定窗口: 实现简单
- 滑动窗口: 更精确控制
- 分布式: 多节点协调

监控指标:
- 请求成功率
- 平均响应时间
- 错误率分布
- 限流触发频率
- 队列长度

工具和库:
- asyncio: 异步编程
- aiohttp: 异步HTTP客户端
- redis: 分布式计数器
- prometheus: 监控指标
- grafana: 可视化面板

注意事项:
- 尊重服务器资源
- 避免恶意攻击
- 遵守使用条款
- 保护服务稳定性
- 合理使用技术
"""