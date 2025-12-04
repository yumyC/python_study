"""
Flask 模板示例

演示如何使用 Jinja2 模板引擎渲染动态页面。

学习要点:
1. 模板渲染基础
2. 变量传递和显示
3. 控制结构（循环、条件）
4. 模板继承
5. 过滤器使用

注意: 需要创建 templates 文件夹和模板文件
本示例使用内联模板演示，实际项目应使用独立的模板文件

运行方式:
    python 03_templates.py
"""

from flask import Flask, render_template_string, render_template
from datetime import datetime
import os

app = Flask(__name__)

# 配置模板文件夹（默认是 templates）
app.template_folder = 'templates'


# ============ 基本模板渲染 ============

@app.route('/')
def index():
    """首页：使用内联模板"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask 模板示例</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            ul { line-height: 1.8; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Flask 模板示例</h1>
        <h2>可用页面：</h2>
        <ul>
            <li><a href="/hello/张三">变量渲染示例</a></li>
            <li><a href="/users">循环示例</a></li>
            <li><a href="/conditional">条件判断示例</a></li>
            <li><a href="/filters">过滤器示例</a></li>
            <li><a href="/inheritance">模板继承示例</a></li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(template)


# ============ 变量渲染 ============

@app.route('/hello/<name>')
def hello(name):
    """演示变量传递和渲染"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hello {{ name }}</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>你好, {{ name }}!</h1>
        <p>当前时间: {{ current_time }}</p>
        <p>访问次数: {{ visit_count }}</p>
        
        <h2>用户信息:</h2>
        <ul>
            <li>姓名: {{ user.name }}</li>
            <li>年龄: {{ user.age }}</li>
            <li>邮箱: {{ user.email }}</li>
        </ul>
        
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """
    
    # 传递变量到模板
    return render_template_string(
        template,
        name=name,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        visit_count=42,
        user={
            'name': name,
            'age': 25,
            'email': f'{name}@example.com'
        }
    )


# ============ 循环 ============

@app.route('/users')
def users():
    """演示 for 循环"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>用户列表</title>
        <meta charset="utf-8">
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>用户列表</h1>
        
        {% if users %}
            <table>
                <thead>
                    <tr>
                        <th>序号</th>
                        <th>姓名</th>
                        <th>年龄</th>
                        <th>城市</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ user.name }}</td>
                        <td>{{ user.age }}</td>
                        <td>{{ user.city }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <p>共 {{ users|length }} 个用户</p>
        {% else %}
            <p>暂无用户数据</p>
        {% endif %}
        
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """
    
    users_data = [
        {'name': '张三', 'age': 25, 'city': '北京'},
        {'name': '李四', 'age': 30, 'city': '上海'},
        {'name': '王五', 'age': 28, 'city': '广州'},
        {'name': '赵六', 'age': 35, 'city': '深圳'},
    ]
    
    return render_template_string(template, users=users_data)


# ============ 条件判断 ============

@app.route('/conditional')
def conditional():
    """演示条件判断"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>条件判断示例</title>
        <meta charset="utf-8">
        <style>
            .success { color: green; }
            .warning { color: orange; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>条件判断示例</h1>
        
        <h2>用户状态:</h2>
        {% if is_logged_in %}
            <p class="success">✓ 已登录</p>
            <p>欢迎回来, {{ username }}!</p>
        {% else %}
            <p class="error">✗ 未登录</p>
            <p>请先登录</p>
        {% endif %}
        
        <h2>分数评级:</h2>
        {% if score >= 90 %}
            <p class="success">优秀 ({{ score }}分)</p>
        {% elif score >= 80 %}
            <p class="success">良好 ({{ score }}分)</p>
        {% elif score >= 60 %}
            <p class="warning">及格 ({{ score }}分)</p>
        {% else %}
            <p class="error">不及格 ({{ score }}分)</p>
        {% endif %}
        
        <h2>权限检查:</h2>
        <ul>
            {% if 'read' in permissions %}
                <li class="success">✓ 可以读取</li>
            {% endif %}
            
            {% if 'write' in permissions %}
                <li class="success">✓ 可以写入</li>
            {% endif %}
            
            {% if 'delete' in permissions %}
                <li class="success">✓ 可以删除</li>
            {% else %}
                <li class="error">✗ 不能删除</li>
            {% endif %}
        </ul>
        
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """
    
    return render_template_string(
        template,
        is_logged_in=True,
        username='张三',
        score=85,
        permissions=['read', 'write']
    )


# ============ 过滤器 ============

@app.route('/filters')
def filters():
    """演示常用过滤器"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>过滤器示例</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Jinja2 过滤器示例</h1>
        
        <h2>字符串过滤器:</h2>
        <ul>
            <li>原始: {{ text }}</li>
            <li>大写: {{ text|upper }}</li>
            <li>小写: {{ text|lower }}</li>
            <li>首字母大写: {{ text|capitalize }}</li>
            <li>标题格式: {{ text|title }}</li>
            <li>长度: {{ text|length }}</li>
            <li>截断: {{ text|truncate(10) }}</li>
        </ul>
        
        <h2>列表过滤器:</h2>
        <ul>
            <li>原始: {{ numbers }}</li>
            <li>长度: {{ numbers|length }}</li>
            <li>第一个: {{ numbers|first }}</li>
            <li>最后一个: {{ numbers|last }}</li>
            <li>求和: {{ numbers|sum }}</li>
            <li>排序: {{ numbers|sort }}</li>
            <li>反转: {{ numbers|reverse|list }}</li>
            <li>连接: {{ items|join(', ') }}</li>
        </ul>
        
        <h2>默认值:</h2>
        <ul>
            <li>有值: {{ value1|default('默认值') }}</li>
            <li>无值: {{ value2|default('默认值') }}</li>
            <li>空字符串: {{ value3|default('默认值', true) }}</li>
        </ul>
        
        <h2>安全过滤器:</h2>
        <div>
            <p>不安全 (转义): {{ html_content }}</p>
            <p>安全 (不转义): {{ html_content|safe }}</p>
        </div>
        
        <h2>日期格式化:</h2>
        <p>当前时间: {{ now|string }}</p>
        
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """
    
    return render_template_string(
        template,
        text='hello flask',
        numbers=[3, 1, 4, 1, 5, 9, 2, 6],
        items=['Python', 'Flask', 'Jinja2'],
        value1='有值',
        value2=None,
        value3='',
        html_content='<strong>粗体文本</strong>',
        now=datetime.now()
    )


# ============ 模板继承 ============

@app.route('/inheritance')
def inheritance():
    """演示模板继承"""
    
    # 基础模板
    base_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}默认标题{% endblock %}</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; }
            header { background: #333; color: white; padding: 20px; }
            nav { background: #666; padding: 10px; }
            nav a { color: white; margin-right: 15px; text-decoration: none; }
            main { padding: 20px; }
            footer { background: #333; color: white; padding: 10px; text-align: center; }
        </style>
    </head>
    <body>
        <header>
            <h1>{% block header %}网站标题{% endblock %}</h1>
        </header>
        
        <nav>
            <a href="/">首页</a>
            <a href="/users">用户</a>
            <a href="/about">关于</a>
        </nav>
        
        <main>
            {% block content %}
            <p>默认内容</p>
            {% endblock %}
        </main>
        
        <footer>
            {% block footer %}
            <p>&copy; 2024 Flask 学习示例</p>
            {% endblock %}
        </footer>
    </body>
    </html>
    """
    
    # 子模板（继承基础模板）
    child_template = """
    {% extends base_template %}
    
    {% block title %}模板继承示例{% endblock %}
    
    {% block header %}Flask 模板继承{% endblock %}
    
    {% block content %}
        <h2>模板继承示例</h2>
        <p>这个页面继承自基础模板，重写了部分区块。</p>
        
        <h3>模板继承的优点:</h3>
        <ul>
            <li>代码复用：避免重复编写相同的 HTML 结构</li>
            <li>易于维护：修改基础模板会影响所有子模板</li>
            <li>结构清晰：页面结构一目了然</li>
            <li>灵活性高：子模板可以选择性重写区块</li>
        </ul>
        
        <h3>常用指令:</h3>
        <ul>
            <li><code>{% raw %}{% extends 'base.html' %}{% endraw %}</code> - 继承基础模板</li>
            <li><code>{% raw %}{% block name %}...{% endblock %}{% endraw %}</code> - 定义可重写区块</li>
            <li><code>{% raw %}{{ super() }}{% endraw %}</code> - 保留父模板的内容</li>
        </ul>
        
        <p><a href="/">返回首页</a></p>
    {% endblock %}
    """
    
    # 注意：实际项目中应该使用 render_template() 和独立的模板文件
    # 这里为了演示方便使用内联模板
    from jinja2 import Template, Environment, BaseLoader
    
    env = Environment(loader=BaseLoader())
    env.globals['base_template'] = base_template
    
    template = env.from_string(child_template)
    return template.render()


# ============ 自定义过滤器 ============

@app.template_filter('reverse_string')
def reverse_string(s):
    """自定义过滤器：反转字符串"""
    return s[::-1]


@app.route('/custom-filter')
def custom_filter():
    """演示自定义过滤器"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>自定义过滤器</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>自定义过滤器示例</h1>
        <p>原始文本: {{ text }}</p>
        <p>反转后: {{ text|reverse_string }}</p>
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """
    return render_template_string(template, text='Hello Flask')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)


"""
知识点总结:

1. 模板渲染
   - render_template('file.html'): 渲染模板文件
   - render_template_string(string): 渲染模板字符串
   - 传递变量: render_template('file.html', var=value)

2. 变量输出
   - {{ variable }}: 输出变量
   - {{ dict.key }}: 访问字典
   - {{ list[0] }}: 访问列表

3. 控制结构
   - {% if condition %}: 条件判断
   - {% for item in list %}: 循环
   - {% elif %}, {% else %}: 分支
   - loop.index: 循环索引（从1开始）
   - loop.index0: 循环索引（从0开始）

4. 常用过滤器
   - 字符串: upper, lower, capitalize, title, length, truncate
   - 列表: first, last, sum, sort, reverse, join
   - 其他: default, safe, length

5. 模板继承
   - {% extends 'base.html' %}: 继承基础模板
   - {% block name %}: 定义可重写区块
   - {{ super() }}: 保留父模板内容

6. 注释
   - {# 这是注释 #}: 模板注释（不会输出到 HTML）

7. 自定义过滤器
   - @app.template_filter('name'): 注册自定义过滤器

实际项目建议:
- 将模板文件放在 templates 文件夹
- 使用模板继承减少重复代码
- 静态文件（CSS、JS、图片）放在 static 文件夹
- 使用 url_for('static', filename='style.css') 引用静态文件

下一步:
- 学习数据库集成（04_database_integration.py）
- 了解表单处理
- 学习会话管理
"""

