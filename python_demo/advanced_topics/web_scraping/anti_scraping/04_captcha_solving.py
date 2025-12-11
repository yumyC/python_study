#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证码识别教程

本教程介绍如何识别和处理各种类型的验证码，包括图片验证码、
滑块验证码、点击验证码等常见的反爬验证机制。

作者: Python学习课程
日期: 2024
"""

import requests
import base64
import json
import time
import random
from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pytesseract
import os


class CaptchaSolver:
    """
    验证码解决器
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def solve_text_captcha(self, image_data, method='tesseract'):
        """
        解决文本验证码
        """
        print(f"=== 解决文本验证码 (方法: {method}) ===")
        
        try:
            # 将图片数据转换为 PIL Image
            if isinstance(image_data, str):
                # Base64 编码的图片
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            image = Image.open(io.BytesIO(image_bytes))
            
            if method == 'tesseract':
                return self.solve_with_tesseract(image)
            elif method == 'opencv':
                return self.solve_with_opencv(image)
            elif method == 'api':
                return self.solve_with_api(image_bytes)
            else:
                return self.solve_with_tesseract(image)
                
        except Exception as e:
            print(f"验证码识别失败: {e}")
            return None
    
    def solve_with_tesseract(self, image):
        """
        使用 Tesseract OCR 识别验证码
        """
        try:
            # 图片预处理
            processed_image = self.preprocess_image(image)
            
            # OCR 识别
            # 配置 Tesseract 参数
            config = '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            
            text = pytesseract.image_to_string(processed_image, config=config)
            result = text.strip().replace(' ', '').replace('\n', '')
            
            print(f"Tesseract 识别结果: {result}")
            return result
            
        except Exception as e:
            print(f"Tesseract 识别失败: {e}")
            print("提示: 需要安装 Tesseract OCR")
            print("Windows: 下载安装包并配置环境变量")
            print("Linux: sudo apt-get install tesseract-ocr")
            print("macOS: brew install tesseract")
            return None
    
    def solve_with_opencv(self, image):
        """
        使用 OpenCV 进行图像处理和识别
        """
        try:
            # 转换为 OpenCV 格式
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 图像预处理
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # 降噪
            denoised = cv2.medianBlur(binary, 3)
            
            # 转换回 PIL 格式
            processed_image = Image.fromarray(denoised)
            
            # 使用 Tesseract 识别处理后的图像
            config = '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            text = pytesseract.image_to_string(processed_image, config=config)
            result = text.strip().replace(' ', '').replace('\n', '')
            
            print(f"OpenCV + Tesseract 识别结果: {result}")
            return result
            
        except Exception as e:
            print(f"OpenCV 处理失败: {e}")
            return None
    
    def solve_with_api(self, image_bytes):
        """
        使用第三方 API 识别验证码
        """
        print("使用第三方 API 识别验证码...")
        
        # 这里演示几个常见的验证码识别 API
        
        # 1. 2captcha API (示例)
        def solve_with_2captcha(image_data):
            api_key = "your_2captcha_api_key"
            
            # 提交验证码
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                'method': 'base64',
                'key': api_key,
                'body': base64.b64encode(image_data).decode()
            }
            
            # 这里只是示例，实际需要有效的 API key
            print("模拟 2captcha API 调用...")
            return "DEMO123"  # 模拟返回结果
        
        # 2. 打码平台 API (示例)
        def solve_with_dama2(image_data):
            username = "your_username"
            password = "your_password"
            
            print("模拟打码平台 API 调用...")
            return "DEMO456"  # 模拟返回结果
        
        # 选择 API 服务
        result = solve_with_2captcha(image_bytes)
        print(f"API 识别结果: {result}")
        
        return result
    
    def preprocess_image(self, image):
        """
        图像预处理
        """
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 调整大小 (放大以提高识别率)
        width, height = image.size
        if width < 200:
            new_width = width * 3
            new_height = height * 3
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # 增强对比度
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    def solve_slider_captcha(self, background_image, slider_image):
        """
        解决滑块验证码
        """
        print("=== 解决滑块验证码 ===")
        
        try:
            # 使用模板匹配找到滑块位置
            bg_array = np.array(background_image)
            slider_array = np.array(slider_image)
            
            # 转换为灰度图
            bg_gray = cv2.cvtColor(bg_array, cv2.COLOR_RGB2GRAY)
            slider_gray = cv2.cvtColor(slider_array, cv2.COLOR_RGB2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(bg_gray, slider_gray, cv2.TM_CCOEFF_NORMED)
            
            # 找到最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 计算滑动距离
            slider_x = max_loc[0]
            
            print(f"检测到滑块位置: x={slider_x}")
            return slider_x
            
        except Exception as e:
            print(f"滑块验证码解决失败: {e}")
            return None
    
    def solve_click_captcha(self, image, instruction):
        """
        解决点击验证码 (如：点击图中的文字)
        """
        print(f"=== 解决点击验证码: {instruction} ===")
        
        try:
            # 这里需要更复杂的图像识别算法
            # 简化演示：随机生成点击坐标
            width, height = image.size
            
            # 根据指令类型生成不同的点击策略
            if "文字" in instruction or "字" in instruction:
                # 文字识别点击
                click_points = self.find_text_regions(image)
            elif "图标" in instruction or "标志" in instruction:
                # 图标识别点击
                click_points = self.find_icon_regions(image)
            else:
                # 默认策略：随机点击
                click_points = [(random.randint(50, width-50), random.randint(50, height-50))]
            
            print(f"生成点击坐标: {click_points}")
            return click_points
            
        except Exception as e:
            print(f"点击验证码解决失败: {e}")
            return []
    
    def find_text_regions(self, image):
        """
        查找图像中的文字区域
        """
        try:
            # 使用 Tesseract 获取文字位置
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            click_points = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # 置信度阈值
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    click_points.append((x, y))
            
            return click_points[:3]  # 最多返回3个点击点
            
        except Exception as e:
            print(f"文字区域识别失败: {e}")
            # 返回随机点击点作为备选
            width, height = image.size
            return [(random.randint(50, width-50), random.randint(50, height-50))]
    
    def find_icon_regions(self, image):
        """
        查找图像中的图标区域
        """
        try:
            # 使用 OpenCV 进行轮廓检测
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            click_points = []
            for contour in contours:
                # 计算轮廓的边界框
                x, y, w, h = cv2.boundingRect(contour)
                
                # 过滤太小或太大的区域
                if 20 < w < 100 and 20 < h < 100:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    click_points.append((center_x, center_y))
            
            return click_points[:3]  # 最多返回3个点击点
            
        except Exception as e:
            print(f"图标区域识别失败: {e}")
            # 返回随机点击点作为备选
            width, height = image.size
            return [(random.randint(50, width-50), random.randint(50, height-50))]


def generate_demo_captcha():
    """
    生成演示用的验证码图片
    """
    print("=== 生成演示验证码 ===")
    
    def create_text_captcha():
        """创建文本验证码"""
        # 生成随机文本
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = ''.join(random.choices(chars, k=5))
        
        # 创建图片
        width, height = 200, 80
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # 尝试使用系统字体
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # 绘制文字
        text_width = draw.textlength(text, font=font)
        x = (width - text_width) // 2
        y = (height - 36) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        # 添加噪声线条
        for _ in range(5):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill='gray', width=2)
        
        # 添加噪声点
        for _ in range(100):
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            draw.point((x, y), fill='lightgray')
        
        return image, text
    
    def create_slider_captcha():
        """创建滑块验证码"""
        # 背景图
        bg_width, bg_height = 300, 150
        background = Image.new('RGB', (bg_width, bg_height), color='lightblue')
        bg_draw = ImageDraw.Draw(background)
        
        # 绘制背景图案
        for _ in range(20):
            x1, y1 = random.randint(0, bg_width), random.randint(0, bg_height)
            x2, y2 = random.randint(0, bg_width), random.randint(0, bg_height)
            bg_draw.line([(x1, y1), (x2, y2)], fill='blue', width=1)
        
        # 滑块缺口位置
        gap_x = random.randint(50, bg_width - 100)
        gap_y = random.randint(20, bg_height - 60)
        gap_width, gap_height = 50, 40
        
        # 在背景上挖出缺口
        bg_draw.rectangle([gap_x, gap_y, gap_x + gap_width, gap_y + gap_height], fill='white')
        
        # 创建滑块
        slider = Image.new('RGB', (gap_width, gap_height), color='orange')
        slider_draw = ImageDraw.Draw(slider)
        slider_draw.rectangle([0, 0, gap_width-1, gap_height-1], outline='red', width=2)
        
        return background, slider, gap_x
    
    # 生成不同类型的验证码
    text_captcha, text_answer = create_text_captcha()
    slider_bg, slider_piece, slider_answer = create_slider_captcha()
    
    # 保存图片
    text_captcha.save('demo_text_captcha.png')
    slider_bg.save('demo_slider_bg.png')
    slider_piece.save('demo_slider_piece.png')
    
    print(f"文本验证码答案: {text_answer}")
    print(f"滑块验证码答案: {slider_answer}")
    
    return {
        'text_captcha': text_captcha,
        'text_answer': text_answer,
        'slider_bg': slider_bg,
        'slider_piece': slider_piece,
        'slider_answer': slider_answer
    }


def selenium_captcha_demo():
    """
    使用 Selenium 处理验证码的演示
    """
    print("\n=== Selenium 验证码处理演示 ===")
    
    # 设置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 模拟访问包含验证码的页面
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>验证码测试页面</title>
        </head>
        <body>
            <h1>验证码测试</h1>
            <form>
                <div>
                    <label>验证码:</label>
                    <img id="captcha-image" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" 
                         width="200" height="80" style="border: 1px solid #ccc;">
                </div>
                <div>
                    <input type="text" id="captcha-input" placeholder="请输入验证码">
                    <button type="button" onclick="refreshCaptcha()">刷新</button>
                </div>
                <div>
                    <button type="submit">提交</button>
                </div>
            </form>
            
            <script>
                function refreshCaptcha() {
                    // 模拟刷新验证码
                    document.getElementById('captcha-image').src = 
                        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
                }
            </script>
        </body>
        </html>
        """
        
        # 使用 data URL 加载页面
        data_url = f"data:text/html;charset=utf-8,{html_content}"
        driver.get(data_url)
        
        print("页面加载完成")
        
        # 查找验证码图片元素
        captcha_img = driver.find_element(By.ID, "captcha-image")
        
        # 获取验证码图片
        captcha_src = captcha_img.get_attribute('src')
        print(f"验证码图片 src: {captcha_src[:50]}...")
        
        # 模拟验证码识别过程
        print("模拟验证码识别...")
        recognized_text = "DEMO123"  # 模拟识别结果
        
        # 输入验证码
        captcha_input = driver.find_element(By.ID, "captcha-input")
        captcha_input.send_keys(recognized_text)
        
        print(f"已输入验证码: {recognized_text}")
        
        # 模拟提交
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print("准备提交表单...")
        
        driver.quit()
        
    except Exception as e:
        print(f"Selenium 演示失败: {e}")


def advanced_captcha_techniques():
    """
    高级验证码处理技术
    """
    print("\n=== 高级验证码处理技术 ===")
    
    # 技术1: 机器学习验证码识别
    def ml_captcha_recognition():
        print("\n技术1: 机器学习验证码识别")
        
        print("机器学习验证码识别流程:")
        steps = [
            "1. 收集大量验证码样本",
            "2. 手动标注正确答案",
            "3. 图像预处理和特征提取",
            "4. 训练深度学习模型 (CNN)",
            "5. 模型验证和优化",
            "6. 部署模型进行实时识别"
        ]
        
        for step in steps:
            print(f"  {step}")
        
        print("\n推荐框架:")
        frameworks = [
            "• TensorFlow/Keras: 深度学习框架",
            "• PyTorch: 研究友好的深度学习框架",
            "• OpenCV: 图像处理库",
            "• scikit-learn: 传统机器学习",
            "• CAPTCHA datasets: 公开数据集"
        ]
        
        for framework in frameworks:
            print(f"  {framework}")
    
    # 技术2: 验证码绕过策略
    def captcha_bypass_strategies():
        print("\n技术2: 验证码绕过策略")
        
        strategies = {
            "Cookie 复用": "保存通过验证后的 Cookie，重复使用",
            "会话保持": "维持长连接，避免触发验证码",
            "行为模拟": "模拟真实用户行为，降低检测概率",
            "频率控制": "控制请求频率，避免触发反爬机制",
            "IP 轮换": "使用代理池，分散请求来源",
            "浏览器指纹": "模拟真实浏览器环境",
            "验证码池": "预先解决验证码，建立答案池",
            "API 接口": "寻找不需要验证码的 API 接口"
        }
        
        for strategy, description in strategies.items():
            print(f"  {strategy}: {description}")
    
    # 技术3: 自动化验证码处理
    def automated_captcha_handling():
        print("\n技术3: 自动化验证码处理")
        
        class AutoCaptchaHandler:
            def __init__(self):
                self.solver = CaptchaSolver()
                self.retry_count = 3
                self.success_rate = 0.0
                self.total_attempts = 0
                self.successful_attempts = 0
            
            def handle_captcha(self, captcha_element, input_element):
                """自动处理验证码"""
                
                for attempt in range(self.retry_count):
                    try:
                        print(f"验证码处理尝试 {attempt + 1}/{self.retry_count}")
                        
                        # 获取验证码图片
                        captcha_image = self.get_captcha_image(captcha_element)
                        
                        # 识别验证码
                        result = self.solver.solve_text_captcha(captcha_image)
                        
                        if result:
                            # 输入验证码
                            input_element.clear()
                            input_element.send_keys(result)
                            
                            # 提交并验证结果
                            if self.verify_captcha_result():
                                self.successful_attempts += 1
                                print(f"验证码识别成功: {result}")
                                return True
                            else:
                                print(f"验证码识别错误: {result}")
                        
                        # 刷新验证码
                        self.refresh_captcha()
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"验证码处理出错: {e}")
                    
                    finally:
                        self.total_attempts += 1
                
                # 更新成功率
                if self.total_attempts > 0:
                    self.success_rate = self.successful_attempts / self.total_attempts
                
                return False
            
            def get_captcha_image(self, element):
                """获取验证码图片"""
                # 这里应该实现获取图片的逻辑
                return b"fake_image_data"
            
            def verify_captcha_result(self):
                """验证验证码结果"""
                # 这里应该实现验证逻辑
                return random.choice([True, False])  # 模拟50%成功率
            
            def refresh_captcha(self):
                """刷新验证码"""
                print("刷新验证码...")
                time.sleep(0.5)
            
            def get_statistics(self):
                """获取统计信息"""
                return {
                    'total_attempts': self.total_attempts,
                    'successful_attempts': self.successful_attempts,
                    'success_rate': self.success_rate
                }
        
        # 演示自动化处理
        handler = AutoCaptchaHandler()
        
        # 模拟处理多个验证码
        for i in range(5):
            print(f"\n处理第 {i+1} 个验证码:")
            success = handler.handle_captcha(None, None)
            print(f"结果: {'成功' if success else '失败'}")
        
        # 显示统计信息
        stats = handler.get_statistics()
        print(f"\n统计信息:")
        print(f"  总尝试次数: {stats['total_attempts']}")
        print(f"  成功次数: {stats['successful_attempts']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
    
    # 执行演示
    ml_captcha_recognition()
    captcha_bypass_strategies()
    automated_captcha_handling()


def main():
    """
    主函数，运行所有示例
    """
    print("验证码识别教程")
    print("=" * 50)
    
    try:
        # 1. 生成演示验证码
        demo_captchas = generate_demo_captcha()
        
        # 2. 创建验证码解决器
        solver = CaptchaSolver()
        
        # 3. 测试文本验证码识别
        print("\n=== 测试文本验证码识别 ===")
        
        # 将 PIL 图像转换为字节数据
        img_byte_arr = io.BytesIO()
        demo_captchas['text_captcha'].save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # 尝试不同的识别方法
        methods = ['tesseract', 'opencv', 'api']
        for method in methods:
            try:
                result = solver.solve_text_captcha(img_byte_arr, method=method)
                actual = demo_captchas['text_answer']
                
                if result:
                    accuracy = "正确" if result.upper() == actual.upper() else "错误"
                    print(f"{method} 方法: {result} ({accuracy})")
                else:
                    print(f"{method} 方法: 识别失败")
                    
            except Exception as e:
                print(f"{method} 方法出错: {e}")
        
        # 4. 测试滑块验证码
        print(f"\n=== 测试滑块验证码识别 ===")
        try:
            slider_x = solver.solve_slider_captcha(
                demo_captchas['slider_bg'], 
                demo_captchas['slider_piece']
            )
            
            actual_x = demo_captchas['slider_answer']
            
            if slider_x is not None:
                error = abs(slider_x - actual_x)
                accuracy = "准确" if error < 10 else f"误差 {error} 像素"
                print(f"识别位置: {slider_x}, 实际位置: {actual_x} ({accuracy})")
            else:
                print("滑块识别失败")
                
        except Exception as e:
            print(f"滑块验证码测试失败: {e}")
        
        # 5. Selenium 演示
        selenium_captcha_demo()
        
        # 6. 高级技术
        advanced_captcha_techniques()
        
        print(f"\n=== 验证码处理最佳实践 ===")
        best_practices = [
            "1. 优先尝试绕过验证码",
            "2. 使用多种识别方法",
            "3. 实现自动重试机制",
            "4. 建立验证码样本库",
            "5. 训练专用识别模型",
            "6. 监控识别成功率",
            "7. 合理控制请求频率",
            "8. 保持会话状态",
            "9. 使用第三方识别服务",
            "10. 定期更新识别算法"
        ]
        
        for practice in best_practices:
            print(f"  {practice}")
        
        # 清理演示文件
        demo_files = ['demo_text_captcha.png', 'demo_slider_bg.png', 'demo_slider_piece.png']
        for file in demo_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"清理文件: {file}")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. 验证码类型
   - 文本验证码: 数字、字母、汉字
   - 图片验证码: 点击、拖拽、选择
   - 滑块验证码: 拼图、轨迹验证
   - 行为验证码: 鼠标轨迹、时间分析
   - 语音验证码: 音频识别

2. 识别技术
   - OCR 技术: Tesseract, PaddleOCR
   - 图像处理: OpenCV, PIL
   - 机器学习: CNN, RNN
   - 模板匹配: 特征点检测
   - 第三方服务: 2captcha, 打码平台

3. 处理策略
   - 图像预处理: 降噪、二值化、增强
   - 多方法结合: 提高识别率
   - 自动重试: 处理识别失败
   - 结果验证: 确认识别正确性

4. 绕过技术
   - 会话保持: 避免触发验证码
   - 行为模拟: 降低检测概率
   - 接口发现: 寻找无验证码接口
   - Cookie 复用: 重用验证状态

5. 高级应用
   - 深度学习模型训练
   - 自动化处理流程
   - 成功率统计分析
   - 成本效益优化

工具和库:
- pytesseract: OCR 识别
- opencv-python: 图像处理
- PIL/Pillow: 图像操作
- selenium: 浏览器自动化
- tensorflow/pytorch: 深度学习
- requests: HTTP 请求

第三方服务:
- 2captcha: 人工识别服务
- Anti-Captcha: 自动识别服务
- 打码平台: 国内识别服务
- DeathByCaptcha: 识别服务

实施建议:
1. 评估验证码复杂度
2. 选择合适的识别方法
3. 建立完整的处理流程
4. 监控和优化成功率
5. 考虑成本和效率平衡

注意事项:
- 遵守网站使用条款
- 不要恶意攻击验证系统
- 保护用户隐私和数据
- 合理使用识别服务
- 避免过度依赖自动化
"""