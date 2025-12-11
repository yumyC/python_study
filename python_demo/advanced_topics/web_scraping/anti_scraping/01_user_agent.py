#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User-Agent 处理教程

本教程介绍如何处理和伪造 User-Agent 来绕过基于用户代理的反爬机制。
包括 User-Agent 轮换、真实浏览器模拟、检测规避等技术。

作者: Python学习课程
日期: 2024
"""

import requests
import random
import time
import json
from fake_useragent import UserAgent
import re
from collections import defaultdict


class UserAgentManager:
    """
    User-Agent 管理器
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.ua_pool = []
        self.usage_stats = defaultdict(int)
        self.blocked_uas = set()
        
        # 初始化 User-Agent 池
        self.init_ua_pool()
    
    def init_ua_pool(self):
        """
        初始化 User-Agent 池
        """
        print("=== 初始化 User-Agent 池 ===")
        
        # 手动定义的真实 User-Agent
        manual_uas = [
            # Chrome (Windows)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Chrome (macOS)
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox (Windows)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox (macOS)
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            
            # Safari (macOS)
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            
            # Edge (Windows)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            
            # Mobile Chrome (Android)
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Mobile Safari (iOS)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        ]
        
        self.ua_pool.extend(manual_uas)
        
        # 尝试使用 fake-useragent 库
        try:
            ua = UserAgent()
            
            # 添加不同浏览器的 User-Agent
            browsers = ['chrome', 'firefox', 'safari', 'edge']
            for browser in browsers:
                for _ in range(5):  # 每个浏览器添加5个
                    try:
                        if browser == 'chrome':
                            user_agent = ua.chrome
                        elif browser == 'firefox':
                            user_agent = ua.firefox
                        elif browser == 'safari':
                            user_agent = ua.safari
                        elif browser == 'edge':
                            user_agent = ua.edge
                        
                        if user_agent not in self.ua_pool:
                            self.ua_pool.append(user_agent)
                    except:
                        continue
                        
        except ImportError:
            print("提示: 安装 fake-useragent 可获得更多 User-Agent")
            print("pip install fake-useragent")
        except Exception as e:
            print(f"fake-useragent 初始化失败: {e}")
        
        print(f"User-Agent 池初始化完成，共 {len(self.ua_pool)} 个")
        
        # 显示部分 User-Agent
        print("示例 User-Agent:")
        for i, ua in enumerate(self.ua_pool[:3]):
            print(f"  {i+1}. {ua}")
    
    def get_random_ua(self):
        """
        获取随机 User-Agent
        """
        if not self.ua_pool:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        # 过滤掉被阻止的 User-Agent
        available_uas = [ua for ua in self.ua_pool if ua not in self.blocked_uas]
        
        if not available_uas:
            print("警告: 所有 User-Agent 都被阻止，重置阻止列表")
            self.blocked_uas.clear()
            available_uas = self.ua_pool
        
        ua = random.choice(available_uas)
        self.usage_stats[ua] += 1
        
        return ua
    
    def get_ua_by_browser(self, browser_type):
        """
        根据浏览器类型获取 User-Agent
        """
        browser_patterns = {
            'chrome': r'Chrome/[\d.]+',
            'firefox': r'Firefox/[\d.]+',
            'safari': r'Safari/[\d.]+',
            'edge': r'Edg/[\d.]+',
            'mobile': r'Mobile',
            'android': r'Android',
            'iphone': r'iPhone',
            'ipad': r'iPad'
        }
        
        pattern = browser_patterns.get(browser_type.lower())
        if not pattern:
            return self.get_random_ua()
        
        matching_uas = [ua for ua in self.ua_pool if re.search(pattern, ua)]
        
        if matching_uas:
            return random.choice(matching_uas)
        else:
            return self.get_random_ua()
    
    def mark_ua_blocked(self, ua):
        """
        标记 User-Agent 为被阻止
        """
        self.blocked_uas.add(ua)
        print(f"User-Agent 被标记为阻止: {ua[:50]}...")
    
    def get_usage_stats(self):
        """
        获取使用统计
        """
        return dict(self.usage_stats)
    
    def test_ua_detection(self, test_url="https://httpbin.org/user-agent"):
        """
        测试 User-Agent 检测
        """
        print(f"\n=== 测试 User-Agent 检测 ===")
        print(f"测试 URL: {test_url}")
        
        test_results = []
        
        # 测试不同类型的 User-Agent
        test_cases = [
            ('默认 requests', requests.Session().headers.get('User-Agent', 'python-requests')),
            ('Chrome', self.get_ua_by_browser('chrome')),
            ('Firefox', self.get_ua_by_browser('firefox')),
            ('Safari', self.get_ua_by_browser('safari')),
            ('Mobile', self.get_ua_by_browser('mobile')),
            ('随机', self.get_random_ua())
        ]
        
        for test_name, ua in test_cases:
            try:
                headers = {'User-Agent': ua}
                response = requests.get(test_url, headers=headers, timeout=10)
                
                result = {
                    'test_name': test_name,
                    'user_agent': ua,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_size': len(response.content)
                }
                
                # 尝试解析响应
                try:
                    json_data = response.json()
                    result['server_received_ua'] = json_data.get('user-agent', '')
                except:
                    result['server_received_ua'] = 'N/A'
                
                test_results.append(result)
                
                print(f"{test_name}: {response.status_code} - {ua[:50]}...")
                
                # 添加延迟避免请求过快
                time.sleep(1)
                
            except Exception as e:
                print(f"{test_name} 测试失败: {e}")
                test_results.append({
                    'test_name': test_name,
                    'user_agent': ua,
                    'success': False,
                    'error': str(e)
                })
        
        return test_results


def analyze_ua_fingerprinting():
    """
    分析 User-Agent 指纹识别
    """
    print("\n=== User-Agent 指纹识别分析 ===")
    
    # 常见的可疑 User-Agent 特征
    suspicious_patterns = [
        r'python-requests',  # Python requests 库
        r'urllib',           # Python urllib
        r'curl',             # curl 工具
        r'wget',             # wget 工具
        r'scrapy',           # Scrapy 框架
        r'bot',              # 包含 bot 的
        r'spider',           # 包含 spider 的
        r'crawler',          # 包含 crawler 的
        r'headless',         # 无头浏览器
        r'phantom',          # PhantomJS
        r'selenium',         # Selenium
    ]
    
    # 测试 User-Agent
    test_uas = [
        'python-requests/2.28.1',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Scrapy/2.5.1 (+https://scrapy.org)',
        'curl/7.68.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    print("User-Agent 可疑性分析:")
    
    for ua in test_uas:
        suspicious_score = 0
        detected_patterns = []
        
        for pattern in suspicious_patterns:
            if re.search(pattern, ua, re.IGNORECASE):
                suspicious_score += 1
                detected_patterns.append(pattern)
        
        risk_level = "低"
        if suspicious_score >= 3:
            risk_level = "高"
        elif suspicious_score >= 1:
            risk_level = "中"
        
        print(f"\nUser-Agent: {ua}")
        print(f"可疑评分: {suspicious_score}/10")
        print(f"风险等级: {risk_level}")
        if detected_patterns:
            print(f"检测到的模式: {', '.join(detected_patterns)}")
    
    # User-Agent 完整性检查
    print(f"\n=== User-Agent 完整性检查 ===")
    
    def check_ua_consistency(ua):
        """
        检查 User-Agent 的一致性
        """
        issues = []
        
        # 检查版本号一致性
        chrome_versions = re.findall(r'Chrome/([\d.]+)', ua)
        safari_versions = re.findall(r'Safari/([\d.]+)', ua)
        webkit_versions = re.findall(r'AppleWebKit/([\d.]+)', ua)
        
        if len(chrome_versions) > 1 and chrome_versions[0] != chrome_versions[1]:
            issues.append("Chrome 版本号不一致")
        
        # 检查操作系统和浏览器匹配
        if 'Windows' in ua and 'Safari' in ua and 'Chrome' not in ua:
            if 'Edge' not in ua:
                issues.append("Windows 系统不太可能单独使用 Safari")
        
        # 检查移动端标识
        if 'Mobile' in ua and 'Windows NT' in ua:
            issues.append("Windows NT 不应该有 Mobile 标识")
        
        # 检查架构一致性
        if 'WOW64' in ua and 'x64' in ua:
            issues.append("WOW64 和 x64 不应该同时出现")
        
        return issues
    
    consistency_test_uas = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Mobile; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ]
    
    for ua in consistency_test_uas:
        issues = check_ua_consistency(ua)
        print(f"\nUser-Agent: {ua[:60]}...")
        if issues:
            print(f"发现问题: {'; '.join(issues)}")
        else:
            print("一致性检查通过")


def ua_rotation_strategies():
    """
    User-Agent 轮换策略
    """
    print("\n=== User-Agent 轮换策略 ===")
    
    ua_manager = UserAgentManager()
    
    # 策略1: 随机轮换
    def random_rotation_strategy():
        print("\n策略1: 随机轮换")
        for i in range(5):
            ua = ua_manager.get_random_ua()
            print(f"  请求 {i+1}: {ua[:60]}...")
    
    # 策略2: 按浏览器类型轮换
    def browser_type_rotation():
        print("\n策略2: 按浏览器类型轮换")
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        for i, browser in enumerate(browsers):
            ua = ua_manager.get_ua_by_browser(browser)
            print(f"  {browser.title()}: {ua[:60]}...")
    
    # 策略3: 时间间隔轮换
    def time_based_rotation():
        print("\n策略3: 时间间隔轮换")
        print("每隔一定时间更换 User-Agent")
        
        rotation_interval = 10  # 秒
        last_rotation_time = 0
        current_ua = ua_manager.get_random_ua()
        
        for i in range(3):
            current_time = time.time()
            
            if current_time - last_rotation_time > rotation_interval:
                current_ua = ua_manager.get_random_ua()
                last_rotation_time = current_time
                print(f"  时间 {i*5}s: 更换 UA - {current_ua[:50]}...")
            else:
                print(f"  时间 {i*5}s: 保持 UA - {current_ua[:50]}...")
    
    # 策略4: 会话级轮换
    def session_based_rotation():
        print("\n策略4: 会话级轮换")
        print("每个会话使用固定的 User-Agent")
        
        sessions = []
        for i in range(3):
            session = requests.Session()
            ua = ua_manager.get_random_ua()
            session.headers.update({'User-Agent': ua})
            sessions.append((f"会话{i+1}", session, ua))
            print(f"  会话 {i+1}: {ua[:50]}...")
        
        return sessions
    
    # 执行策略演示
    random_rotation_strategy()
    browser_type_rotation()
    time_based_rotation()
    sessions = session_based_rotation()
    
    return sessions


def advanced_ua_techniques():
    """
    高级 User-Agent 技术
    """
    print("\n=== 高级 User-Agent 技术 ===")
    
    # 技术1: 动态生成 User-Agent
    def generate_dynamic_ua():
        print("\n技术1: 动态生成 User-Agent")
        
        # Chrome 版本范围
        chrome_versions = ['119.0.0.0', '120.0.0.0', '121.0.0.0']
        webkit_versions = ['537.36']
        
        # 操作系统选项
        os_options = [
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; Win64; x64',
            'Macintosh; Intel Mac OS X 10_15_7',
            'X11; Linux x86_64'
        ]
        
        for i in range(3):
            chrome_ver = random.choice(chrome_versions)
            webkit_ver = random.choice(webkit_versions)
            os_info = random.choice(os_options)
            
            ua = f'Mozilla/5.0 ({os_info}) AppleWebKit/{webkit_ver} (KHTML, like Gecko) Chrome/{chrome_ver} Safari/{webkit_ver}'
            print(f"  生成 {i+1}: {ua}")
    
    # 技术2: User-Agent 与其他头部的一致性
    def consistent_headers():
        print("\n技术2: 保持头部一致性")
        
        ua_configs = {
            'chrome_windows': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            },
            'firefox_windows': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1'
            },
            'safari_macos': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            }
        }
        
        for browser, headers in ua_configs.items():
            print(f"\n  {browser.replace('_', ' ').title()} 配置:")
            for key, value in headers.items():
                print(f"    {key}: {value}")
    
    # 技术3: User-Agent 黑名单检测
    def detect_ua_blacklist():
        print("\n技术3: User-Agent 黑名单检测")
        
        # 模拟检测逻辑
        blacklist_keywords = [
            'python', 'requests', 'urllib', 'scrapy', 'bot', 'crawler',
            'spider', 'curl', 'wget', 'headless', 'phantom', 'selenium'
        ]
        
        test_uas = [
            'python-requests/2.28.1',
            'Mozilla/5.0 (compatible; Googlebot/2.1)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Scrapy/2.5.1 (+https://scrapy.org)',
        ]
        
        for ua in test_uas:
            is_blocked = any(keyword in ua.lower() for keyword in blacklist_keywords)
            status = "阻止" if is_blocked else "允许"
            print(f"    {status}: {ua}")
    
    # 执行技术演示
    generate_dynamic_ua()
    consistent_headers()
    detect_ua_blacklist()


def main():
    """
    主函数，运行所有示例
    """
    print("User-Agent 处理教程")
    print("=" * 50)
    
    try:
        # 1. 创建 User-Agent 管理器
        ua_manager = UserAgentManager()
        
        # 2. 测试 User-Agent 检测
        test_results = ua_manager.test_ua_detection()
        
        # 3. 分析指纹识别
        analyze_ua_fingerprinting()
        
        # 4. 轮换策略
        sessions = ua_rotation_strategies()
        
        # 5. 高级技术
        advanced_ua_techniques()
        
        # 6. 使用统计
        print(f"\n=== 使用统计 ===")
        stats = ua_manager.get_usage_stats()
        if stats:
            print(f"User-Agent 使用次数:")
            for ua, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {count}次: {ua[:60]}...")
        
        print(f"\n=== 最佳实践建议 ===")
        best_practices = [
            "1. 使用真实浏览器的 User-Agent",
            "2. 定期更新 User-Agent 池",
            "3. 保持请求头的一致性",
            "4. 避免使用明显的爬虫标识",
            "5. 实现智能轮换策略",
            "6. 监控被阻止的 User-Agent",
            "7. 结合其他反检测技术"
        ]
        
        for practice in best_practices:
            print(f"  {practice}")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. User-Agent 基础知识
   - User-Agent 的作用和结构
   - 不同浏览器的 UA 特征
   - 移动端和桌面端的区别
   - 版本号和兼容性信息

2. 反爬检测机制
   - 黑名单关键词检测
   - UA 格式一致性检查
   - 请求头组合验证
   - 行为模式分析

3. 伪造技术
   - 真实 UA 收集和维护
   - 动态 UA 生成
   - 轮换策略设计
   - 一致性保持

4. 高级技巧
   - 浏览器指纹模拟
   - 请求头完整性
   - 时间和频率控制
   - 会话级别管理

5. 检测规避
   - 避免可疑关键词
   - 模拟真实用户行为
   - 多样化请求模式
   - 智能错误处理

工具和库:
- fake-useragent: 自动获取真实 UA
- user-agents: UA 解析和生成
- requests: HTTP 请求库
- selenium: 浏览器自动化

实施策略:
1. 建立 UA 池管理系统
2. 实现智能轮换机制
3. 监控检测和阻止情况
4. 定期更新 UA 数据
5. 结合其他反检测手段

注意事项:
- 使用最新的真实 UA
- 保持请求头一致性
- 避免过于频繁的切换
- 监控网站的检测机制变化
- 遵守网站使用条款
"""