"""
LlamaIndex 数据摄取详解

本文件介绍 LlamaIndex 中的数据摄取和预处理：
1. 多种数据源的连接
2. 数据加载器的使用
3. 文档预处理和转换
4. 批量数据处理
5. 数据管道构建

学习目标：
- 掌握不同数据源的接入方法
- 理解数据预处理的重要性
- 学会构建数据摄取管道
- 了解数据质量控制方法
"""

import os
import json
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from llama_index.core import (
        Document, 
        SimpleDirectoryReader,
        Settings
    )
    from llama_index.readers.file import (
        PDFReader,
        DocxReader,
        CSVReader
    )
    from llama_index.core.node_parser import (
        SimpleNodeParser,
        SentenceSplitter,
        TokenTextSplitter
    )
    from llama_index.core.llms import MockLLM
    
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    print("LlamaIndex 未安装，请运行: pip install llama-index")
    LLAMAINDEX_AVAILABLE = False

def demo_text_file_ingestion():
    """演示文本文件数据摄取"""
    print("=== 文本文件数据摄取演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 创建示例文本文件
    sample_texts = {
        "ai_overview.txt": """
人工智能概述

人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，
旨在创建能够执行通常需要人类智能的任务的系统。

AI的主要分支包括：
1. 机器学习 - 从数据中学习模式
2. 自然语言处理 - 理解和生成人类语言
3. 计算机视觉 - 理解和分析图像
4. 机器人学 - 物理世界中的智能行为

AI技术正在改变各个行业，从医疗保健到金融，从教育到娱乐。
        """,
        "python_guide.txt": """
Python编程指南

Python是一种高级、解释型编程语言，以其简洁的语法和强大的功能而闻名。

Python的特点：
- 语法简洁明了
- 跨平台兼容性
- 丰富的标准库
- 活跃的社区支持
- 广泛的应用领域

Python应用领域：
1. Web开发（Django, Flask, FastAPI）
2. 数据科学（Pandas, NumPy, Matplotlib）
3. 人工智能（TensorFlow, PyTorch, Scikit-learn）
4. 自动化脚本
5. 桌面应用开发
        """,
        "ml_basics.txt": """
机器学习基础

机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。

机器学习类型：
1. 监督学习 - 使用标记数据进行训练
2. 无监督学习 - 从未标记数据中发现模式
3. 强化学习 - 通过与环境交互学习

常见算法：
- 线性回归
- 决策树
- 随机森林
- 支持向量机
- 神经网络

机器学习流程：
数据收集 → 数据预处理 → 模型训练 → 模型评估 → 模型部署
        """
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建文件
        for filename, content in sample_texts.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
        
        try:
            # 使用 SimpleDirectoryReader 读取所有文件
            reader = SimpleDirectoryReader(temp_dir)
            documents = reader.load_data()
            
            print(f"成功加载 {len(documents)} 个文档")
            
            for doc in documents:
                filename = os.path.basename(doc.metadata.get('file_path', '未知文件'))
                word_count = len(doc.text.split())
                print(f"- {filename}: {word_count} 词")
                print(f"  预览: {doc.text[:100]}...")
                print()
        
        except Exception as e:
            print(f"文本文件摄取失败: {e}")

def demo_csv_data_ingestion():
    """演示CSV数据摄取"""
    print("=== CSV数据摄取演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 创建示例CSV数据
    csv_data = """姓名,职位,技能,经验年限,项目数量
张三,软件工程师,"Python,JavaScript,SQL",5,12
李四,数据科学家,"Python,R,机器学习,统计学",3,8
王五,前端开发,"HTML,CSS,Vue.js,React",4,15
赵六,产品经理,"需求分析,项目管理,用户研究",6,20
钱七,DevOps工程师,"Docker,Kubernetes,AWS,CI/CD",4,10
孙八,UI设计师,"Figma,Sketch,用户体验设计",3,25"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_file = os.path.join(temp_dir, "employees.csv")
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        try:
            # 方法1: 使用 SimpleDirectoryReader（会将CSV转换为文本）
            reader = SimpleDirectoryReader(temp_dir)
            documents = reader.load_data()
            
            print("方法1 - SimpleDirectoryReader:")
            for doc in documents:
                if 'csv' in doc.metadata.get('file_path', ''):
                    print(f"CSV内容预览: {doc.text[:200]}...")
            
            # 方法2: 手动处理CSV数据
            import csv
            structured_docs = []
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for i, row in enumerate(csv_reader):
                    # 将每行转换为文档
                    text = f"员工信息：{row['姓名']}是一名{row['职位']}，"
                    text += f"拥有{row['经验年限']}年经验，"
                    text += f"掌握技能：{row['技能']}，"
                    text += f"参与过{row['项目数量']}个项目。"
                    
                    doc = Document(
                        text=text,
                        metadata={
                            "source": "employees.csv",
                            "row_id": i,
                            "name": row['姓名'],
                            "position": row['职位'],
                            "experience": row['经验年限']
                        }
                    )
                    structured_docs.append(doc)
            
            print(f"\n方法2 - 结构化处理:")
            print(f"创建了 {len(structured_docs)} 个结构化文档")
            for doc in structured_docs[:2]:  # 只显示前2个
                print(f"- {doc.text}")
                print(f"  元数据: {doc.metadata}")
        
        except Exception as e:
            print(f"CSV数据摄取失败: {e}")
    
    print()

def demo_json_data_ingestion():
    """演示JSON数据摄取"""
    print("=== JSON数据摄取演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 创建示例JSON数据
    json_data = {
        "company": "TechCorp",
        "departments": [
            {
                "name": "研发部",
                "description": "负责产品研发和技术创新",
                "teams": [
                    {
                        "name": "后端团队",
                        "technologies": ["Python", "Java", "Go"],
                        "projects": ["用户系统", "支付系统", "推荐引擎"]
                    },
                    {
                        "name": "前端团队", 
                        "technologies": ["React", "Vue.js", "TypeScript"],
                        "projects": ["管理后台", "移动端应用", "数据可视化"]
                    }
                ]
            },
            {
                "name": "数据部",
                "description": "负责数据分析和机器学习",
                "teams": [
                    {
                        "name": "数据科学团队",
                        "technologies": ["Python", "R", "SQL"],
                        "projects": ["用户画像", "销售预测", "风险控制"]
                    }
                ]
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file = os.path.join(temp_dir, "company.json")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        try:
            # 方法1: 直接读取JSON文件
            reader = SimpleDirectoryReader(temp_dir)
            documents = reader.load_data()
            
            print("方法1 - 直接读取:")
            for doc in documents:
                if 'json' in doc.metadata.get('file_path', ''):
                    print(f"JSON内容预览: {doc.text[:200]}...")
            
            # 方法2: 结构化处理JSON
            structured_docs = []
            
            # 处理公司信息
            company_doc = Document(
                text=f"公司名称：{json_data['company']}",
                metadata={"source": "company.json", "type": "company_info"}
            )
            structured_docs.append(company_doc)
            
            # 处理部门信息
            for dept in json_data['departments']:
                dept_text = f"部门：{dept['name']}。{dept['description']}。"
                
                # 处理团队信息
                for team in dept['teams']:
                    team_text = f"团队：{team['name']}，"
                    team_text += f"使用技术：{', '.join(team['technologies'])}，"
                    team_text += f"负责项目：{', '.join(team['projects'])}。"
                    
                    doc = Document(
                        text=dept_text + team_text,
                        metadata={
                            "source": "company.json",
                            "type": "team_info",
                            "department": dept['name'],
                            "team": team['name']
                        }
                    )
                    structured_docs.append(doc)
            
            print(f"\n方法2 - 结构化处理:")
            print(f"创建了 {len(structured_docs)} 个结构化文档")
            for doc in structured_docs:
                print(f"- {doc.text}")
                print(f"  类型: {doc.metadata.get('type', '未知')}")
        
        except Exception as e:
            print(f"JSON数据摄取失败: {e}")
    
    print()

def demo_web_data_ingestion():
    """演示网页数据摄取"""
    print("=== 网页数据摄取演示 ===")
    
    print("网页数据摄取方法:")
    print("1. 使用 WebReader 直接读取网页")
    print("2. 使用 BeautifulSoup 解析HTML")
    print("3. 使用 Selenium 处理动态内容")
    print("4. 使用 RSS/API 获取结构化数据")
    
    # 模拟网页内容处理
    html_content = """
    <html>
    <head><title>AI技术博客</title></head>
    <body>
        <h1>深度学习入门指南</h1>
        <p>深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的复杂模式。</p>
        
        <h2>神经网络基础</h2>
        <p>神经网络由多个层组成，包括输入层、隐藏层和输出层。</p>
        
        <h2>常用框架</h2>
        <ul>
            <li>TensorFlow - Google开发的开源框架</li>
            <li>PyTorch - Facebook开发的动态框架</li>
            <li>Keras - 高级API，易于使用</li>
        </ul>
    </body>
    </html>
    """
    
    try:
        from bs4 import BeautifulSoup
        
        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题和内容
        title = soup.find('title').text if soup.find('title') else "无标题"
        
        # 提取段落
        paragraphs = [p.text for p in soup.find_all('p')]
        
        # 提取列表项
        list_items = [li.text for li in soup.find_all('li')]
        
        # 创建文档
        content = f"标题: {title}\n\n"
        content += "内容:\n" + "\n".join(paragraphs)
        if list_items:
            content += "\n\n要点:\n" + "\n".join(f"- {item}" for item in list_items)
        
        web_doc = Document(
            text=content,
            metadata={
                "source": "web_page",
                "title": title,
                "type": "blog_post"
            }
        )
        
        print("网页内容提取结果:")
        print(f"标题: {title}")
        print(f"内容长度: {len(content)} 字符")
        print(f"提取的段落数: {len(paragraphs)}")
        print(f"提取的列表项: {len(list_items)}")
        
    except ImportError:
        print("需要安装 BeautifulSoup: pip install beautifulsoup4")
    except Exception as e:
        print(f"网页数据处理失败: {e}")
    
    print()

def demo_document_transformation():
    """演示文档转换和预处理"""
    print("=== 文档转换和预处理演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 创建原始文档
    raw_documents = [
        Document(
            text="   Python是一种编程语言。    它很容易学习。Python用于Web开发、数据科学和AI。   ",
            metadata={"source": "intro.txt", "quality": "low"}
        ),
        Document(
            text="机器学习算法包括：线性回归、决策树、随机森林、支持向量机、神经网络等。这些算法各有特点和适用场景。",
            metadata={"source": "ml_guide.txt", "quality": "high"}
        )
    ]
    
    print("原始文档:")
    for i, doc in enumerate(raw_documents):
        print(f"{i+1}. 长度: {len(doc.text)} 字符")
        print(f"   内容: '{doc.text}'")
        print(f"   质量: {doc.metadata['quality']}")
    
    # 文档清理和转换
    def clean_document(doc: Document) -> Document:
        """清理文档内容"""
        # 去除多余空格
        cleaned_text = ' '.join(doc.text.split())
        
        # 添加处理信息到元数据
        new_metadata = doc.metadata.copy()
        new_metadata['processed'] = True
        new_metadata['original_length'] = len(doc.text)
        new_metadata['cleaned_length'] = len(cleaned_text)
        
        return Document(text=cleaned_text, metadata=new_metadata)
    
    # 应用清理
    cleaned_documents = [clean_document(doc) for doc in raw_documents]
    
    print("\n清理后的文档:")
    for i, doc in enumerate(cleaned_documents):
        print(f"{i+1}. 长度: {len(doc.text)} 字符")
        print(f"   内容: '{doc.text}'")
        print(f"   原始长度: {doc.metadata['original_length']}")
        print(f"   清理后长度: {doc.metadata['cleaned_length']}")
    
    print()

def demo_node_parsing():
    """演示节点解析"""
    print("=== 节点解析演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 创建长文档
    long_document = Document(
        text="""
        人工智能发展历程
        
        人工智能的发展可以分为几个重要阶段。第一阶段是符号主义时期（1950-1970年），
        这个时期的研究主要集中在符号推理和专家系统上。
        
        第二阶段是机器学习兴起（1980-2000年），随着计算能力的提升，
        机器学习算法开始受到关注。神经网络、决策树等算法得到了发展。
        
        第三阶段是深度学习革命（2000年至今），深度学习的突破带来了人工智能的新一轮发展。
        卷积神经网络、循环神经网络等技术在图像识别、自然语言处理等领域取得了重大进展。
        
        未来展望：人工智能将继续快速发展，在更多领域发挥重要作用。
        同时，我们也需要关注AI的伦理和安全问题。
        """,
        metadata={"source": "ai_history.txt"}
    )
    
    print(f"原始文档长度: {len(long_document.text)} 字符")
    
    try:
        # 1. 简单节点解析器
        simple_parser = SimpleNodeParser()
        simple_nodes = simple_parser.get_nodes_from_documents([long_document])
        
        print(f"\n简单解析器结果: {len(simple_nodes)} 个节点")
        for i, node in enumerate(simple_nodes[:2]):  # 只显示前2个
            print(f"节点 {i+1}: {len(node.text)} 字符")
            print(f"内容: {node.text[:100]}...")
        
        # 2. 句子分割器
        sentence_splitter = SentenceSplitter(
            chunk_size=200,  # 每块最大200字符
            chunk_overlap=20  # 重叠20字符
        )
        sentence_nodes = sentence_splitter.get_nodes_from_documents([long_document])
        
        print(f"\n句子分割器结果: {len(sentence_nodes)} 个节点")
        for i, node in enumerate(sentence_nodes):
            print(f"节点 {i+1}: {len(node.text)} 字符")
            print(f"内容: {node.text.strip()[:80]}...")
        
        # 3. Token分割器（如果可用）
        try:
            token_splitter = TokenTextSplitter(
                chunk_size=100,  # 100个token
                chunk_overlap=10
            )
            token_nodes = token_splitter.get_nodes_from_documents([long_document])
            
            print(f"\nToken分割器结果: {len(token_nodes)} 个节点")
            for i, node in enumerate(token_nodes[:2]):
                print(f"节点 {i+1}: {len(node.text)} 字符")
                print(f"内容: {node.text.strip()[:80]}...")
        
        except Exception as e:
            print(f"\nToken分割器不可用: {e}")
    
    except Exception as e:
        print(f"节点解析失败: {e}")
    
    print()

def demo_batch_processing():
    """演示批量数据处理"""
    print("=== 批量数据处理演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 模拟大量文档
    def generate_sample_documents(count: int) -> List[Document]:
        """生成示例文档"""
        topics = [
            "Python编程", "机器学习", "深度学习", "数据科学", 
            "Web开发", "移动开发", "云计算", "区块链"
        ]
        
        documents = []
        for i in range(count):
            topic = topics[i % len(topics)]
            text = f"这是关于{topic}的第{i+1}篇文档。{topic}是一个重要的技术领域，有着广泛的应用前景。"
            
            doc = Document(
                text=text,
                metadata={
                    "doc_id": i,
                    "topic": topic,
                    "batch": i // 10,  # 每10个文档一批
                    "created_at": f"2024-01-{(i % 30) + 1:02d}"
                }
            )
            documents.append(doc)
        
        return documents
    
    # 生成测试文档
    sample_docs = generate_sample_documents(25)
    print(f"生成了 {len(sample_docs)} 个示例文档")
    
    # 批量处理统计
    def analyze_documents(docs: List[Document]) -> Dict[str, Any]:
        """分析文档集合"""
        stats = {
            "total_docs": len(docs),
            "total_chars": sum(len(doc.text) for doc in docs),
            "topics": {},
            "batches": {},
            "avg_length": 0
        }
        
        for doc in docs:
            # 统计主题
            topic = doc.metadata.get("topic", "未知")
            stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
            
            # 统计批次
            batch = doc.metadata.get("batch", 0)
            stats["batches"][batch] = stats["batches"].get(batch, 0) + 1
        
        if stats["total_docs"] > 0:
            stats["avg_length"] = stats["total_chars"] / stats["total_docs"]
        
        return stats
    
    # 执行分析
    analysis = analyze_documents(sample_docs)
    
    print("\n批量处理分析结果:")
    print(f"文档总数: {analysis['total_docs']}")
    print(f"总字符数: {analysis['total_chars']}")
    print(f"平均长度: {analysis['avg_length']:.1f} 字符")
    print(f"主题分布: {dict(list(analysis['topics'].items())[:5])}")  # 显示前5个
    print(f"批次分布: {dict(list(analysis['batches'].items())[:3])}")  # 显示前3个
    
    # 过滤和分组
    python_docs = [doc for doc in sample_docs if doc.metadata.get("topic") == "Python编程"]
    print(f"\nPython相关文档: {len(python_docs)} 个")
    
    # 按批次分组
    batch_groups = {}
    for doc in sample_docs:
        batch = doc.metadata.get("batch", 0)
        if batch not in batch_groups:
            batch_groups[batch] = []
        batch_groups[batch].append(doc)
    
    print(f"批次分组: {len(batch_groups)} 个批次")
    for batch_id, docs in list(batch_groups.items())[:3]:  # 显示前3个批次
        print(f"  批次 {batch_id}: {len(docs)} 个文档")
    
    print()

def main():
    """主函数"""
    print("LlamaIndex 数据摄取学习")
    print("=" * 50)
    
    # 检查依赖
    if not LLAMAINDEX_AVAILABLE:
        print("⚠️  LlamaIndex 未安装")
        print("请运行: pip install llama-index")
        print()
    
    # 运行演示
    demo_text_file_ingestion()
    demo_csv_data_ingestion()
    demo_json_data_ingestion()
    demo_web_data_ingestion()
    demo_document_transformation()
    demo_node_parsing()
    demo_batch_processing()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 支持多种数据源和格式")
    print("2. 数据预处理提高质量和一致性")
    print("3. 节点解析优化检索效果")
    print("4. 批量处理提高效率")
    print("5. 元数据丰富文档信息")
    print("6. 灵活的转换和过滤机制")

if __name__ == "__main__":
    main()