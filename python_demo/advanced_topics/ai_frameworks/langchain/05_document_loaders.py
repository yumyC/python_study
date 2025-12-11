"""
LangChain 文档加载器详解

本文件介绍 LangChain 中的文档加载和处理：
1. 各种文档加载器的使用
2. 文本分割器 (Text Splitters)
3. 文档预处理和清理
4. 批量文档处理
5. 自定义文档加载器

学习目标：
- 掌握不同格式文档的加载方法
- 理解文本分割的重要性和策略
- 学会处理大量文档数据
- 了解文档预处理的最佳实践
"""

import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path

from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    JSONLoader,
    DirectoryLoader,
    WebBaseLoader,
    UnstructuredHTMLLoader
)
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    SpacyTextSplitter
)
from langchain.schema import Document

def demo_text_loader():
    """演示文本文件加载器"""
    print("=== 文本文件加载器演示 ===")
    
    # 创建示例文本文件
    sample_text = """
    人工智能简介
    
    人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
    它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
    可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
    """
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(sample_text)
        temp_file_path = f.name
    
    try:
        # 使用文本加载器
        loader = TextLoader(temp_file_path, encoding='utf-8')
        documents = loader.load()
        
        print(f"加载的文档数量: {len(documents)}")
        print(f"文档内容预览: {documents[0].page_content[:100]}...")
        print(f"文档元数据: {documents[0].metadata}")
        
    finally:
        # 清理临时文件
        os.unlink(temp_file_path)
    
    print()

def demo_csv_loader():
    """演示CSV文件加载器"""
    print("=== CSV文件加载器演示 ===")
    
    # 创建示例CSV数据
    csv_data = """姓名,年龄,职业,技能
张三,28,软件工程师,Python、JavaScript、SQL
李四,32,数据科学家,Python、R、机器学习
王五,25,前端开发,HTML、CSS、Vue.js
赵六,30,产品经理,需求分析、项目管理、用户研究"""
    
    # 创建临时CSV文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_data)
        temp_csv_path = f.name
    
    try:
        # 使用CSV加载器
        loader = CSVLoader(
            file_path=temp_csv_path,
            csv_args={
                'delimiter': ',',
                'quotechar': '"',
            }
        )
        documents = loader.load()
        
        print(f"加载的文档数量: {len(documents)}")
        for i, doc in enumerate(documents[:2]):  # 只显示前2个
            print(f"文档 {i+1}:")
            print(f"  内容: {doc.page_content}")
            print(f"  元数据: {doc.metadata}")
        
    finally:
        os.unlink(temp_csv_path)
    
    print()

def demo_json_loader():
    """演示JSON文件加载器"""
    print("=== JSON文件加载器演示 ===")
    
    import json
    
    # 创建示例JSON数据
    json_data = {
        "articles": [
            {
                "title": "Python编程入门",
                "content": "Python是一种高级编程语言，语法简洁明了，适合初学者学习。",
                "author": "张三",
                "tags": ["编程", "Python", "入门"]
            },
            {
                "title": "机器学习基础",
                "content": "机器学习是人工智能的一个重要分支，通过算法让计算机从数据中学习。",
                "author": "李四",
                "tags": ["机器学习", "AI", "算法"]
            }
        ]
    }
    
    # 创建临时JSON文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
        temp_json_path = f.name
    
    try:
        # 使用JSON加载器
        loader = JSONLoader(
            file_path=temp_json_path,
            jq_schema='.articles[]',  # 使用jq语法提取数组中的每个元素
            text_content=False  # 加载整个JSON对象
        )
        documents = loader.load()
        
        print(f"加载的文档数量: {len(documents)}")
        for i, doc in enumerate(documents):
            print(f"文档 {i+1}:")
            print(f"  内容: {doc.page_content[:100]}...")
            print(f"  元数据: {doc.metadata}")
        
    finally:
        os.unlink(temp_json_path)
    
    print()

def demo_directory_loader():
    """演示目录加载器"""
    print("=== 目录加载器演示 ===")
    
    # 创建临时目录和文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建几个示例文件
        files_data = {
            "doc1.txt": "这是第一个文档的内容。包含一些关于Python的信息。",
            "doc2.txt": "这是第二个文档。讨论机器学习的基础概念。",
            "readme.md": "# 项目说明\n\n这是一个示例项目，用于演示文档加载。"
        }
        
        for filename, content in files_data.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 使用目录加载器
        loader = DirectoryLoader(
            temp_dir,
            glob="*.txt",  # 只加载.txt文件
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        
        documents = loader.load()
        
        print(f"加载的文档数量: {len(documents)}")
        for doc in documents:
            filename = os.path.basename(doc.metadata['source'])
            print(f"文件: {filename}")
            print(f"  内容: {doc.page_content[:50]}...")
    
    print()

def demo_web_loader():
    """演示网页加载器"""
    print("=== 网页加载器演示 ===")
    
    # 注意：这个演示需要网络连接
    try:
        # 加载一个简单的网页（使用httpbin作为示例）
        urls = ["https://httpbin.org/html"]
        
        loader = WebBaseLoader(urls)
        documents = loader.load()
        
        print(f"加载的文档数量: {len(documents)}")
        if documents:
            print(f"网页内容预览: {documents[0].page_content[:200]}...")
            print(f"元数据: {documents[0].metadata}")
        
    except Exception as e:
        print(f"网页加载失败（可能是网络问题）: {e}")
        print("这是正常的，因为演示环境可能没有网络连接")
    
    print()

def demo_text_splitters():
    """演示文本分割器"""
    print("=== 文本分割器演示 ===")
    
    # 示例长文本
    long_text = """
    人工智能的发展历程可以分为几个重要阶段。

    第一阶段（1950-1970年）：符号主义时期
    这个时期的研究主要集中在符号推理和专家系统上。科学家们试图通过编程让计算机模拟人类的逻辑思维过程。

    第二阶段（1980-2000年）：机器学习兴起
    随着计算能力的提升，机器学习算法开始受到关注。神经网络、决策树等算法得到了发展。

    第三阶段（2000年至今）：深度学习革命
    深度学习的突破带来了人工智能的新一轮发展。卷积神经网络、循环神经网络等技术在图像识别、自然语言处理等领域取得了重大进展。

    未来展望
    人工智能将继续快速发展，在更多领域发挥重要作用。同时，我们也需要关注AI的伦理和安全问题。
    """
    
    # 1. 字符分割器
    print("1. 字符分割器:")
    char_splitter = CharacterTextSplitter(
        separator="\n\n",  # 按段落分割
        chunk_size=200,    # 每块最大200字符
        chunk_overlap=20   # 重叠20字符
    )
    char_chunks = char_splitter.split_text(long_text)
    
    for i, chunk in enumerate(char_chunks):
        print(f"  块 {i+1}: {chunk.strip()[:50]}...")
    
    print(f"  总共分割成 {len(char_chunks)} 块\n")
    
    # 2. 递归字符分割器
    print("2. 递归字符分割器:")
    recursive_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "。", "，", " "],  # 分割符优先级
        chunk_size=150,
        chunk_overlap=15
    )
    recursive_chunks = recursive_splitter.split_text(long_text)
    
    for i, chunk in enumerate(recursive_chunks[:3]):  # 只显示前3块
        print(f"  块 {i+1}: {chunk.strip()[:50]}...")
    
    print(f"  总共分割成 {len(recursive_chunks)} 块\n")
    
    # 3. Token分割器（需要tiktoken库）
    try:
        print("3. Token分割器:")
        token_splitter = TokenTextSplitter(
            chunk_size=50,    # 50个token
            chunk_overlap=5
        )
        token_chunks = token_splitter.split_text(long_text)
        
        for i, chunk in enumerate(token_chunks[:2]):
            print(f"  块 {i+1}: {chunk.strip()[:50]}...")
        
        print(f"  总共分割成 {len(token_chunks)} 块")
        
    except ImportError:
        print("  Token分割器需要安装 tiktoken 库")
    
    print()

def demo_document_processing():
    """演示文档处理流程"""
    print("=== 文档处理流程演示 ===")
    
    # 创建示例文档
    documents = [
        Document(
            page_content="Python是一种高级编程语言。它的语法简洁明了，适合初学者学习。Python在数据科学、Web开发、人工智能等领域都有广泛应用。",
            metadata={"source": "python_intro.txt", "category": "编程"}
        ),
        Document(
            page_content="机器学习是人工智能的一个重要分支。它通过算法让计算机从数据中学习模式，而不需要明确编程。常见的机器学习算法包括线性回归、决策树、神经网络等。",
            metadata={"source": "ml_basics.txt", "category": "AI"}
        )
    ]
    
    print("原始文档:")
    for i, doc in enumerate(documents):
        print(f"文档 {i+1}:")
        print(f"  来源: {doc.metadata['source']}")
        print(f"  类别: {doc.metadata['category']}")
        print(f"  内容: {doc.page_content[:50]}...")
    
    # 文档分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=10
    )
    
    split_docs = text_splitter.split_documents(documents)
    
    print(f"\n分割后的文档数量: {len(split_docs)}")
    for i, doc in enumerate(split_docs):
        print(f"分块 {i+1}:")
        print(f"  内容: {doc.page_content[:50]}...")
        print(f"  元数据: {doc.metadata}")
    
    print()

def demo_custom_loader():
    """演示自定义文档加载器"""
    print("=== 自定义文档加载器演示 ===")
    
    from langchain.document_loaders.base import BaseLoader
    
    class ConfigLoader(BaseLoader):
        """自定义配置文件加载器"""
        
        def __init__(self, file_path: str):
            self.file_path = file_path
        
        def load(self) -> List[Document]:
            """加载配置文件"""
            documents = []
            
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                current_section = None
                section_content = []
                
                for line in lines:
                    line = line.strip()
                    
                    # 检查是否是节标题
                    if line.startswith('[') and line.endswith(']'):
                        # 保存前一个节
                        if current_section and section_content:
                            doc = Document(
                                page_content='\n'.join(section_content),
                                metadata={
                                    'source': self.file_path,
                                    'section': current_section,
                                    'type': 'config'
                                }
                            )
                            documents.append(doc)
                        
                        # 开始新节
                        current_section = line[1:-1]  # 去掉方括号
                        section_content = []
                    
                    elif line and not line.startswith('#'):  # 忽略空行和注释
                        section_content.append(line)
                
                # 保存最后一个节
                if current_section and section_content:
                    doc = Document(
                        page_content='\n'.join(section_content),
                        metadata={
                            'source': self.file_path,
                            'section': current_section,
                            'type': 'config'
                        }
                    )
                    documents.append(doc)
                
            except Exception as e:
                print(f"加载配置文件失败: {e}")
            
            return documents
    
    # 创建示例配置文件
    config_content = """# 应用配置文件
[database]
host=localhost
port=5432
name=myapp
user=admin

[redis]
host=localhost
port=6379
db=0

[logging]
level=INFO
file=/var/log/app.log
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False, encoding='utf-8') as f:
        f.write(config_content)
        temp_config_path = f.name
    
    try:
        # 使用自定义加载器
        loader = ConfigLoader(temp_config_path)
        documents = loader.load()
        
        print(f"加载的配置节数量: {len(documents)}")
        for doc in documents:
            print(f"节: {doc.metadata['section']}")
            print(f"  内容: {doc.page_content}")
            print()
        
    finally:
        os.unlink(temp_config_path)

def demo_batch_processing():
    """演示批量文档处理"""
    print("=== 批量文档处理演示 ===")
    
    # 模拟批量处理多个文档
    def process_documents(documents: List[Document]) -> Dict[str, Any]:
        """处理文档并返回统计信息"""
        stats = {
            'total_docs': len(documents),
            'total_chars': 0,
            'total_words': 0,
            'categories': {},
            'sources': set()
        }
        
        for doc in documents:
            # 统计字符和单词
            content = doc.page_content
            stats['total_chars'] += len(content)
            stats['total_words'] += len(content.split())
            
            # 统计来源
            if 'source' in doc.metadata:
                stats['sources'].add(doc.metadata['source'])
            
            # 统计类别
            if 'category' in doc.metadata:
                category = doc.metadata['category']
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        stats['sources'] = list(stats['sources'])
        return stats
    
    # 创建示例文档集合
    sample_docs = [
        Document(
            page_content="Python编程语言介绍...",
            metadata={"source": "python.txt", "category": "编程"}
        ),
        Document(
            page_content="机器学习算法概述...",
            metadata={"source": "ml.txt", "category": "AI"}
        ),
        Document(
            page_content="数据结构与算法...",
            metadata={"source": "algorithms.txt", "category": "编程"}
        ),
        Document(
            page_content="深度学习神经网络...",
            metadata={"source": "dl.txt", "category": "AI"}
        )
    ]
    
    # 处理文档
    stats = process_documents(sample_docs)
    
    print("批量处理结果:")
    print(f"文档总数: {stats['total_docs']}")
    print(f"总字符数: {stats['total_chars']}")
    print(f"总单词数: {stats['total_words']}")
    print(f"文档来源: {', '.join(stats['sources'])}")
    print(f"类别分布: {stats['categories']}")
    print()

def main():
    """主函数"""
    print("LangChain 文档加载器学习")
    print("=" * 50)
    
    # 运行演示
    demo_text_loader()
    demo_csv_loader()
    demo_json_loader()
    demo_directory_loader()
    demo_web_loader()
    demo_text_splitters()
    demo_document_processing()
    demo_custom_loader()
    demo_batch_processing()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 不同格式的文档需要不同的加载器")
    print("2. 文本分割是处理长文档的关键步骤")
    print("3. 合适的分割策略可以提高检索效果")
    print("4. 文档元数据有助于组织和过滤")
    print("5. 自定义加载器可以处理特殊格式")
    print("6. 批量处理提高了处理效率")

if __name__ == "__main__":
    main()