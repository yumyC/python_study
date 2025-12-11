#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 基础教程

本教程介绍如何使用 Selenium 处理 JavaScript 渲染的网页。
Selenium 可以控制真实的浏览器，处理动态内容和用户交互。

作者: Python学习课程
日期: 2024
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException
)
import time
import json
from datetime import datetime


def setup_chrome_driver():
    """
    设置 Chrome 浏览器驱动
    配置浏览器选项和参数
    """
    print("=== 设置 Chrome 驱动 ===")
    
    # Chrome 选项配置
    chrome_options = Options()
    
    # 基础选项
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # 窗口大小
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 用户代理
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # 禁用图片加载（可选，提高速度）
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    
    # 无头模式（可选）
    # chrome_options.add_argument('--headless')
    
    try:
        # 使用 webdriver-manager 自动管理驱动
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
    except ImportError:
        print("建议安装 webdriver-manager: pip install webdriver-manager")
        # 手动指定驱动路径
        # service = Service('/path/to/chromedriver')
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)
    
    # 设置隐式等待
    driver.implicitly_wait(10)
    
    print(f"浏览器版本: {driver.capabilities['browserVersion']}")
    print(f"驱动版本: {driver.capabilities['chrome']['chromedriverVersion']}")
    
    return driver


def basic_navigation():
    """
    基础导航操作
    演示如何打开网页、导航和获取页面信息
    """
    print("\n=== 基础导航操作 ===")
    
    driver = setup_chrome_driver()
    
    try:
        # 打开网页
        url = "https://httpbin.org/forms/post"
        driver.get(url)
        print(f"当前 URL: {driver.current_url}")
        print(f"页面标题: {driver.title}")
        
        # 获取页面源码
        page_source = driver.page_source
        print(f"页面源码长度: {len(page_source)} 字符")
        
        # 窗口操作
        print(f"窗口大小: {driver.get_window_size()}")
        driver.maximize_window()
        print("窗口已最大化")
        
        # 截图
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"截图已保存: {screenshot_path}")
        
        # 浏览器导航
        driver.get("https://httpbin.org/")
        print(f"导航到新页面: {driver.current_url}")
        
        # 后退
        driver.back()
        print(f"后退到: {driver.current_url}")
        
        # 前进
        driver.forward()
        print(f"前进到: {driver.current_url}")
        
        # 刷新
        driver.refresh()
        print("页面已刷新")
        
    finally:
        driver.quit()


def element_location():
    """
    元素定位方法
    演示各种元素定位策略
    """
    print("\n=== 元素定位方法 ===")
    
    driver = setup_chrome_driver()
    
    try:
        # 打开测试页面
        driver.get("https://httpbin.org/forms/post")
        
        # 1. 通过 ID 定位
        try:
            element = driver.find_element(By.ID, "custname")
            print(f"通过 ID 找到元素: {element.tag_name}")
        except NoSuchElementException:
            print("未找到指定 ID 的元素")
        
        # 2. 通过 Name 定位
        try:
            element = driver.find_element(By.NAME, "custname")
            print(f"通过 Name 找到元素: {element.get_attribute('name')}")
        except NoSuchElementException:
            print("未找到指定 Name 的元素")
        
        # 3. 通过 Class Name 定位
        try:
            elements = driver.find_elements(By.CLASS_NAME, "form-control")
            print(f"通过 Class Name 找到 {len(elements)} 个元素")
        except NoSuchElementException:
            print("未找到指定 Class 的元素")
        
        # 4. 通过 Tag Name 定位
        input_elements = driver.find_elements(By.TAG_NAME, "input")
        print(f"找到 {len(input_elements)} 个 input 元素")
        
        # 5. 通过 CSS 选择器定位
        try:
            element = driver.find_element(By.CSS_SELECTOR, "input[name='custname']")
            print(f"通过 CSS 选择器找到元素: {element.tag_name}")
        except NoSuchElementException:
            print("CSS 选择器未找到元素")
        
        # 6. 通过 XPath 定位
        try:
            element = driver.find_element(By.XPATH, "//input[@name='custname']")
            print(f"通过 XPath 找到元素: {element.tag_name}")
        except NoSuchElementException:
            print("XPath 未找到元素")
        
        # 7. 通过链接文本定位
        try:
            driver.get("https://httpbin.org/")
            link = driver.find_element(By.LINK_TEXT, "HTTP Methods")
            print(f"找到链接: {link.text}")
        except NoSuchElementException:
            print("未找到指定链接文本")
        
        # 8. 通过部分链接文本定位
        try:
            link = driver.find_element(By.PARTIAL_LINK_TEXT, "HTTP")
            print(f"找到部分匹配链接: {link.text}")
        except NoSuchElementException:
            print("未找到部分匹配的链接")
        
    finally:
        driver.quit()


def form_interaction():
    """
    表单交互操作
    演示如何填写表单、点击按钮等
    """
    print("\n=== 表单交互操作 ===")
    
    driver = setup_chrome_driver()
    
    try:
        # 打开表单页面
        driver.get("https://httpbin.org/forms/post")
        
        # 填写文本输入框
        name_input = driver.find_element(By.NAME, "custname")
        name_input.clear()  # 清空现有内容
        name_input.send_keys("张三")
        print("已填写姓名")
        
        # 填写邮箱
        email_input = driver.find_element(By.NAME, "custemail")
        email_input.clear()
        email_input.send_keys("zhangsan@example.com")
        print("已填写邮箱")
        
        # 选择下拉框
        try:
            size_select = Select(driver.find_element(By.NAME, "size"))
            size_select.select_by_visible_text("Medium")
            print("已选择尺寸")
        except NoSuchElementException:
            print("未找到尺寸选择框")
        
        # 选择单选按钮
        try:
            radio_button = driver.find_element(By.CSS_SELECTOR, "input[name='topping'][value='bacon']")
            radio_button.click()
            print("已选择单选按钮")
        except NoSuchElementException:
            print("未找到单选按钮")
        
        # 选择复选框
        try:
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[name='topping'][type='checkbox']")
            for checkbox in checkboxes[:2]:  # 选择前两个
                if not checkbox.is_selected():
                    checkbox.click()
            print("已选择复选框")
        except NoSuchElementException:
            print("未找到复选框")
        
        # 填写文本域
        try:
            textarea = driver.find_element(By.NAME, "comments")
            textarea.clear()
            textarea.send_keys("这是一个测试评论")
            print("已填写评论")
        except NoSuchElementException:
            print("未找到评论框")
        
        # 提交表单
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        print("表单已提交")
        
        # 等待页面加载并获取结果
        time.sleep(2)
        print(f"提交后的 URL: {driver.current_url}")
        
    finally:
        driver.quit()


def wait_strategies():
    """
    等待策略
    演示显式等待和隐式等待的使用
    """
    print("\n=== 等待策略 ===")
    
    driver = setup_chrome_driver()
    
    try:
        # 打开页面
        driver.get("https://httpbin.org/delay/3")
        
        # 显式等待示例
        wait = WebDriverWait(driver, 10)
        
        # 等待元素出现
        try:
            element = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("页面加载完成")
        except TimeoutException:
            print("等待超时")
        
        # 等待元素可点击
        driver.get("https://httpbin.org/")
        try:
            clickable_element = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "HTTP Methods"))
            )
            print("元素可点击")
        except TimeoutException:
            print("元素等待超时")
        
        # 等待文本出现
        try:
            wait.until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "httpbin")
            )
            print("指定文本已出现")
        except TimeoutException:
            print("文本等待超时")
        
        # 自定义等待条件
        def page_title_contains(title):
            def _predicate(driver):
                return title.lower() in driver.title.lower()
            return _predicate
        
        try:
            wait.until(page_title_contains("httpbin"))
            print("页面标题包含指定文本")
        except TimeoutException:
            print("自定义条件等待超时")
        
    finally:
        driver.quit()


def javascript_execution():
    """
    JavaScript 执行
    演示如何在页面中执行 JavaScript 代码
    """
    print("\n=== JavaScript 执行 ===")
    
    driver = setup_chrome_driver()
    
    try:
        driver.get("https://httpbin.org/")
        
        # 执行简单的 JavaScript
        title = driver.execute_script("return document.title;")
        print(f"通过 JS 获取标题: {title}")
        
        # 滚动页面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("页面已滚动到底部")
        
        time.sleep(1)
        
        # 滚动到顶部
        driver.execute_script("window.scrollTo(0, 0);")
        print("页面已滚动到顶部")
        
        # 获取页面信息
        page_info = driver.execute_script("""
            return {
                url: window.location.href,
                title: document.title,
                width: window.innerWidth,
                height: window.innerHeight,
                userAgent: navigator.userAgent
            };
        """)
        
        print("页面信息:")
        for key, value in page_info.items():
            print(f"  {key}: {value}")
        
        # 修改页面内容
        driver.execute_script("""
            var h1 = document.querySelector('h1');
            if (h1) {
                h1.style.color = 'red';
                h1.textContent = '页面已被修改';
            }
        """)
        print("页面内容已修改")
        
        time.sleep(2)
        
        # 创建新元素
        driver.execute_script("""
            var div = document.createElement('div');
            div.innerHTML = '<h2 style="color: blue;">这是通过 JS 添加的内容</h2>';
            document.body.appendChild(div);
        """)
        print("已添加新元素")
        
        time.sleep(2)
        
    finally:
        driver.quit()


def advanced_interactions():
    """
    高级交互操作
    演示鼠标操作、键盘操作等高级功能
    """
    print("\n=== 高级交互操作 ===")
    
    driver = setup_chrome_driver()
    
    try:
        driver.get("https://httpbin.org/")
        
        # 创建 ActionChains 对象
        actions = ActionChains(driver)
        
        # 鼠标悬停
        try:
            element = driver.find_element(By.LINK_TEXT, "HTTP Methods")
            actions.move_to_element(element).perform()
            print("鼠标悬停操作完成")
            time.sleep(1)
        except NoSuchElementException:
            print("未找到悬停目标元素")
        
        # 右键点击
        try:
            actions.context_click(element).perform()
            print("右键点击完成")
            time.sleep(1)
            
            # 按 ESC 键关闭右键菜单
            actions.send_keys(Keys.ESCAPE).perform()
        except:
            print("右键点击失败")
        
        # 双击
        try:
            actions.double_click(element).perform()
            print("双击操作完成")
            time.sleep(1)
        except:
            print("双击操作失败")
        
        # 键盘操作
        driver.get("https://httpbin.org/forms/post")
        
        try:
            name_input = driver.find_element(By.NAME, "custname")
            name_input.click()
            
            # 输入文本
            actions.send_keys("测试用户").perform()
            
            # 全选文本
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            
            # 复制文本
            actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
            
            # 移动到下一个输入框
            actions.send_keys(Keys.TAB).perform()
            
            # 粘贴文本
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            
            print("键盘操作完成")
            time.sleep(2)
            
        except NoSuchElementException:
            print("未找到输入框")
        
        # 拖拽操作（如果页面支持）
        # source = driver.find_element(By.ID, "source")
        # target = driver.find_element(By.ID, "target")
        # actions.drag_and_drop(source, target).perform()
        
    finally:
        driver.quit()


def handle_alerts_and_windows():
    """
    处理弹窗和多窗口
    演示如何处理 JavaScript 弹窗和多个浏览器窗口
    """
    print("\n=== 处理弹窗和多窗口 ===")
    
    driver = setup_chrome_driver()
    
    try:
        # 处理 JavaScript 弹窗
        driver.get("data:text/html,<html><body><button onclick='alert(\"这是一个警告框\")'>点击弹出警告</button></body></html>")
        
        # 点击按钮触发弹窗
        button = driver.find_element(By.TAG_NAME, "button")
        button.click()
        
        # 等待弹窗出现并处理
        try:
            wait = WebDriverWait(driver, 5)
            alert = wait.until(EC.alert_is_present())
            
            print(f"弹窗文本: {alert.text}")
            alert.accept()  # 点击确定
            print("弹窗已处理")
            
        except TimeoutException:
            print("未检测到弹窗")
        
        # 处理确认框
        driver.get("data:text/html,<html><body><button onclick='confirm(\"确认删除吗？\")'>确认对话框</button></body></html>")
        
        button = driver.find_element(By.TAG_NAME, "button")
        button.click()
        
        try:
            alert = wait.until(EC.alert_is_present())
            print(f"确认框文本: {alert.text}")
            alert.dismiss()  # 点击取消
            print("确认框已取消")
            
        except TimeoutException:
            print("未检测到确认框")
        
        # 处理输入框
        driver.get("data:text/html,<html><body><button onclick='prompt(\"请输入您的姓名：\")'>输入对话框</button></body></html>")
        
        button = driver.find_element(By.TAG_NAME, "button")
        button.click()
        
        try:
            alert = wait.until(EC.alert_is_present())
            print(f"输入框文本: {alert.text}")
            alert.send_keys("测试用户")
            alert.accept()
            print("输入框已填写并确认")
            
        except TimeoutException:
            print("未检测到输入框")
        
        # 处理多窗口
        driver.get("https://httpbin.org/")
        
        # 获取当前窗口句柄
        main_window = driver.current_window_handle
        print(f"主窗口句柄: {main_window}")
        
        # 打开新窗口（通过 JavaScript）
        driver.execute_script("window.open('https://httpbin.org/html', '_blank');")
        
        # 等待新窗口出现
        time.sleep(2)
        
        # 获取所有窗口句柄
        all_windows = driver.window_handles
        print(f"所有窗口数量: {len(all_windows)}")
        
        # 切换到新窗口
        for window in all_windows:
            if window != main_window:
                driver.switch_to.window(window)
                print(f"切换到新窗口: {driver.title}")
                break
        
        # 在新窗口中操作
        print(f"新窗口 URL: {driver.current_url}")
        
        # 关闭当前窗口
        driver.close()
        
        # 切换回主窗口
        driver.switch_to.window(main_window)
        print(f"切换回主窗口: {driver.title}")
        
    finally:
        driver.quit()


def scrape_dynamic_content():
    """
    爬取动态内容示例
    演示如何处理 AJAX 加载的内容
    """
    print("\n=== 爬取动态内容示例 ===")
    
    driver = setup_chrome_driver()
    
    try:
        # 创建一个包含动态内容的测试页面
        html_content = """
        <html>
        <head>
            <title>动态内容测试</title>
            <script>
                function loadContent() {
                    setTimeout(function() {
                        document.getElementById('content').innerHTML = 
                            '<div class="item">动态加载的内容1</div>' +
                            '<div class="item">动态加载的内容2</div>' +
                            '<div class="item">动态加载的内容3</div>';
                    }, 2000);
                }
                
                window.onload = function() {
                    loadContent();
                };
            </script>
        </head>
        <body>
            <h1>动态内容页面</h1>
            <button onclick="loadContent()">重新加载内容</button>
            <div id="content">正在加载...</div>
        </body>
        </html>
        """
        
        # 使用 data URL 加载页面
        data_url = f"data:text/html;charset=utf-8,{html_content}"
        driver.get(data_url)
        
        print(f"页面标题: {driver.title}")
        
        # 等待动态内容加载
        wait = WebDriverWait(driver, 10)
        
        try:
            # 等待内容区域不再显示"正在加载..."
            wait.until_not(
                EC.text_to_be_present_in_element((By.ID, "content"), "正在加载...")
            )
            
            # 等待具体的动态元素出现
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "item"))
            )
            
            print("动态内容已加载")
            
            # 提取动态加载的内容
            items = driver.find_elements(By.CLASS_NAME, "item")
            print(f"找到 {len(items)} 个动态项目:")
            
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item.text}")
            
            # 点击按钮重新加载
            reload_button = driver.find_element(By.TAG_NAME, "button")
            reload_button.click()
            print("点击重新加载按钮")
            
            # 再次等待内容更新
            time.sleep(3)
            
            # 重新获取内容
            items = driver.find_elements(By.CLASS_NAME, "item")
            print(f"重新加载后找到 {len(items)} 个项目")
            
        except TimeoutException:
            print("等待动态内容超时")
        
    finally:
        driver.quit()


def selenium_best_practices():
    """
    Selenium 最佳实践
    """
    practices = {
        "性能优化": [
            "使用无头模式提高速度",
            "禁用图片和CSS加载",
            "设置合理的超时时间",
            "复用浏览器实例",
            "使用显式等待而非sleep"
        ],
        
        "稳定性提升": [
            "使用 WebDriverWait 等待元素",
            "处理 StaleElementReferenceException",
            "实现重试机制",
            "正确处理异常",
            "及时关闭浏览器资源"
        ],
        
        "反检测技巧": [
            "使用真实的 User-Agent",
            "随机化操作时间间隔",
            "模拟人类行为模式",
            "避免检测特征",
            "使用代理IP"
        ],
        
        "代码质量": [
            "封装常用操作",
            "使用页面对象模式",
            "编写可维护的选择器",
            "添加详细的日志",
            "实现配置管理"
        ]
    }
    
    return practices


def main():
    """
    主函数，运行所有示例
    """
    print("Selenium 基础教程")
    print("=" * 50)
    
    try:
        # 检查是否安装了必要的库
        try:
            import selenium
            print(f"Selenium 版本: {selenium.__version__}")
        except ImportError:
            print("请安装 Selenium: pip install selenium")
            return
        
        # 运行示例（注释掉避免实际执行）
        # basic_navigation()
        # element_location()
        # form_interaction()
        # wait_strategies()
        # javascript_execution()
        # advanced_interactions()
        # handle_alerts_and_windows()
        # scrape_dynamic_content()
        
        print("\n=== Selenium 最佳实践 ===")
        practices = selenium_best_practices()
        for category, items in practices.items():
            print(f"\n{category}:")
            for item in items:
                print(f"  - {item}")
        
        print("\n=== 安装说明 ===")
        print("1. 安装 Selenium: pip install selenium")
        print("2. 安装 webdriver-manager: pip install webdriver-manager")
        print("3. 或手动下载 ChromeDriver 并配置路径")
        print("4. 确保 Chrome 浏览器已安装")
        
        print("\n注意: 示例代码已注释，取消注释后可运行")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. Selenium 基础概念
   - WebDriver: 浏览器驱动接口
   - WebElement: 页面元素对象
   - 浏览器自动化控制
   - JavaScript 执行能力

2. 元素定位策略
   - ID, Name, Class Name
   - Tag Name, CSS Selector
   - XPath, Link Text
   - 选择合适的定位方法

3. 等待策略
   - 隐式等待: implicitly_wait()
   - 显式等待: WebDriverWait + Expected Conditions
   - 自定义等待条件
   - 避免使用 time.sleep()

4. 高级功能
   - JavaScript 执行
   - 鼠标和键盘操作
   - 多窗口处理
   - 弹窗处理
   - 截图和录制

5. 最佳实践
   - 合理配置浏览器选项
   - 使用页面对象模式
   - 实现异常处理
   - 资源管理和清理
   - 性能优化技巧

使用场景:
- 处理 JavaScript 渲染的页面
- 模拟用户交互行为
- 自动化测试
- 处理复杂的表单提交
- 绕过简单的反爬机制

注意事项:
- 资源消耗较大
- 速度相对较慢
- 需要安装浏览器驱动
- 容易被检测
- 需要处理各种异常情况
"""