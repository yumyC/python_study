# 新闻爬虫项目

## 项目简介

这是一个综合性的新闻爬虫项目，演示了如何使用 Python 爬虫技术从多个新闻网站抓取新闻数据。项目集成了反爬技术、数据处理、存储等完整的爬虫解决方案。

## 功能特性

- **多站点支持**: 支持多个新闻网站的数据抓取
- **反爬技术**: 集成 User-Agent 轮换、代理池、频率控制等反爬技术
- **数据清洗**: 自动清洗和标准化新闻数据
- **多格式存储**: 支持 JSON、CSV、数据库等多种存储格式
- **增量更新**: 支持增量抓取，避免重复数据
- **监控告警**: 实时监控爬虫状态和数据质量

## 技术栈

- **爬虫框架**: requests, BeautifulSoup, Scrapy
- **反爬技术**: fake-useragent, proxy-rotator
- **数据处理**: pandas, numpy
- **数据存储**: SQLite, MongoDB, Redis
- **任务调度**: APScheduler
- **监控日志**: logging, prometheus

## 项目结构

```
project1_news_scraper/
├── README.md                   # 项目说明
├── requirements.txt            # 依赖包
├── config/                     # 配置文件
│   ├── settings.py            # 主配置
│   ├── sites.json             # 网站配置
│   └── logging.conf           # 日志配置
├── src/                       # 源代码
│   ├── __init__.py
│   ├── scrapers/              # 爬虫模块
│   │   ├── __init__.py
│   │   ├── base_scraper.py    # 基础爬虫类
│   │   ├── news_scraper.py    # 新闻爬虫
│   │   └── site_scrapers/     # 各站点爬虫
│   ├── utils/                 # 工具模块
│   │   ├── __init__.py
│   │   ├── anti_spider.py     # 反爬工具
│   │   ├── data_processor.py  # 数据处理
│   │   └── storage.py         # 数据存储
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   └── news_model.py      # 新闻数据模型
│   └── main.py                # 主程序入口
├── data/                      # 数据目录
│   ├── raw/                   # 原始数据
│   ├── processed/             # 处理后数据
│   └── exports/               # 导出数据
├── logs/                      # 日志目录
├── tests/                     # 测试代码
│   ├── __init__.py
│   ├── test_scrapers.py
│   └── test_utils.py
└── scripts/                   # 脚本工具
    ├── deploy.sh              # 部署脚本
    └── monitor.py             # 监控脚本
```

## 安装和使用

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

编辑 `config/settings.py` 文件，配置数据库连接、代理设置等：

```python
# 数据库配置
DATABASE = {
    'type': 'sqlite',
    'path': 'data/news.db'
}

# 代理配置
PROXY_SETTINGS = {
    'enabled': True,
    'pool_size': 10,
    'rotation_interval': 5
}

# 爬虫配置
SCRAPER_SETTINGS = {
    'delay_range': (1, 3),
    'max_retries': 3,
    'timeout': 30
}
```

### 3. 运行爬虫

```bash
# 运行单个网站爬虫
python src/main.py --site example_news

# 运行所有网站爬虫
python src/main.py --all

# 增量更新模式
python src/main.py --incremental

# 指定输出格式
python src/main.py --output json --file data/exports/news.json
```

### 4. 监控和管理

```bash
# 查看爬虫状态
python scripts/monitor.py --status

# 查看数据统计
python scripts/monitor.py --stats

# 清理旧数据
python scripts/monitor.py --cleanup --days 30
```

## 配置说明

### 网站配置 (config/sites.json)

```json
{
  "example_news": {
    "name": "示例新闻网站",
    "base_url": "https://example-news.com",
    "list_url": "https://example-news.com/news/list",
    "selectors": {
      "title": "h1.news-title",
      "content": "div.news-content",
      "author": "span.author",
      "publish_time": "time.publish-date",
      "category": "span.category"
    },
    "pagination": {
      "type": "url_param",
      "param": "page",
      "max_pages": 100
    },
    "rate_limit": {
      "requests_per_minute": 30,
      "delay_range": [1, 3]
    }
  }
}
```

### 反爬配置

```python
ANTI_SPIDER_CONFIG = {
    'user_agent': {
        'enabled': True,
        'rotation': True,
        'custom_agents': []
    },
    'proxy': {
        'enabled': False,
        'pool_file': 'config/proxy_pool.txt',
        'test_url': 'https://httpbin.org/ip'
    },
    'cookies': {
        'enabled': True,
        'persist': True,
        'file': 'data/cookies.json'
    },
    'rate_limiting': {
        'enabled': True,
        'adaptive': True,
        'base_delay': 1.0
    }
}
```

## 数据模型

### 新闻数据结构

```python
class NewsItem:
    def __init__(self):
        self.id = None              # 唯一标识
        self.title = ""             # 标题
        self.content = ""           # 内容
        self.summary = ""           # 摘要
        self.author = ""            # 作者
        self.source = ""            # 来源网站
        self.category = ""          # 分类
        self.tags = []              # 标签
        self.publish_time = None    # 发布时间
        self.crawl_time = None      # 抓取时间
        self.url = ""               # 原文链接
        self.image_urls = []        # 图片链接
        self.view_count = 0         # 浏览量
        self.comment_count = 0      # 评论数
```

## 扩展开发

### 添加新的新闻网站

1. 在 `config/sites.json` 中添加网站配置
2. 在 `src/scrapers/site_scrapers/` 中创建专用爬虫类
3. 继承 `BaseScraper` 并实现必要的方法

```python
from src.scrapers.base_scraper import BaseScraper

class CustomNewsScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.site_name = "custom_news"
    
    def parse_news_list(self, response):
        """解析新闻列表页"""
        # 实现具体的解析逻辑
        pass
    
    def parse_news_detail(self, response):
        """解析新闻详情页"""
        # 实现具体的解析逻辑
        pass
```

### 自定义数据处理

在 `src/utils/data_processor.py` 中添加自定义处理函数：

```python
def custom_text_cleaner(text):
    """自定义文本清理函数"""
    # 实现文本清理逻辑
    return cleaned_text

def extract_keywords(content):
    """提取关键词"""
    # 实现关键词提取逻辑
    return keywords
```

## 监控和告警

### 数据质量监控

- 抓取成功率监控
- 数据完整性检查
- 重复数据检测
- 异常数据识别

### 性能监控

- 请求响应时间
- 内存使用情况
- 网络连接状态
- 存储空间使用

### 告警机制

- 爬虫异常停止告警
- 数据质量异常告警
- 系统资源告警
- 反爬检测告警

## 最佳实践

1. **遵守 robots.txt**: 检查并遵守网站的爬虫协议
2. **合理控制频率**: 避免对目标网站造成过大压力
3. **数据去重**: 实现有效的数据去重机制
4. **异常处理**: 完善的异常处理和恢复机制
5. **日志记录**: 详细的日志记录便于问题排查
6. **定期维护**: 定期检查和更新爬虫规则

## 常见问题

### Q: 如何处理动态加载的内容？
A: 可以使用 Selenium 或分析 AJAX 请求，直接调用 API 接口。

### Q: 如何应对反爬机制？
A: 使用代理轮换、User-Agent 伪造、请求频率控制等技术。

### Q: 如何提高爬虫效率？
A: 使用异步请求、合理的并发控制、缓存机制等。

### Q: 数据存储选择建议？
A: 小规模数据用 SQLite，大规模数据用 MongoDB 或 PostgreSQL。

## 法律声明

本项目仅用于学习和研究目的，使用时请：

- 遵守目标网站的使用条款
- 遵守相关法律法规
- 不要用于商业用途
- 尊重网站的 robots.txt 协议
- 不要对网站造成过大负担

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础爬虫功能
- 反爬技术集成
- 数据存储支持

### v1.1.0 (2024-01-15)
- 添加增量更新功能
- 优化数据处理性能
- 增加监控告警功能
- 修复已知问题